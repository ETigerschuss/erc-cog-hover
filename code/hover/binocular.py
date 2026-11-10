"""Both eyes: head-centred stimuli, a bilateral Tier-1 network and the MIO as a median muscle.

Hypothesis H2 (sharpened): the male's M. interocularis lies in the median plane, attaches to the
circumocular ridges of both eyes and pulls both retinae toward the midline (0° in each eye's own
anatomical frame: 0° anterior/medial, 90° dorsal). With one command for both limbs it is a vergence
actuator; with two commands the limbs can also act in push-pull. Both variants are built here:

    BinocularModel("eristalis", "male", mio="median")       one motor neuron, HSN of both sides
    BinocularModel("eristalis", "male", mio="independent")  one motor neuron per side
    BinocularModel("eristalis", "female")                   no MIO
    BinocularModel("drosophila", "female")

Geometry. Stimuli are defined in head-centred coordinates (ψ: azimuth, positive to the animal's
right; elevation). The right eye sees ψ ∈ [−20°, 165°] at its own azimuth az = ψ, the left eye sees
ψ ∈ [−165°, 20°] at az = −ψ (mirror image), so one right-eye front end serves both eyes. Each eye
may be given its own movie (dichoptic stimulation, e.g. a pattern that changes binocular disparity).
The two sides share no neurons except the median MIO motor neuron; heterolateral LPTC input
(H1, H2, Hu) and stimulus-dependent disparity geometry are not modelled in this version.

Readout, per eye in its own frame: a = anterior (medial) and d = dorsal component of the retinal
shift. Medial shift of both retinae: (a_R + a_L)/2 ("vergence" component; the lines of sight then
diverge, because photoreceptors sample inverted images). Conjugate horizontal shift toward the
animal's left: (a_R − a_L)/2 ("version").
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass

import numpy as np

from .eye import GRID_AZ, grating_movie
from .oculomotor import PULL_FALT, unit
from .species import Model
from .tier1_hh import DT, MN, MN_PRESET, build_circuit, simulate, spike_rate

PSI = np.arange(-GRID_AZ[1], GRID_AZ[1] + 1e-9, 1.0)        # head-centred azimuth grid, −165 … 165
_R = PSI >= GRID_AZ[0]                                       # columns seen by the right eye
_L = PSI <= -GRID_AZ[0]                                      # columns seen by the left eye (to be mirrored)


def split_eyes(movie_head_R, movie_head_L=None):
    """Head-centred movie(s) (T, n_el, len(PSI)) -> (right-eye movie, left-eye movie) in eye coordinates."""
    if movie_head_L is None:
        movie_head_L = movie_head_R
    return movie_head_R[:, :, _R], movie_head_L[:, :, _L][:, :, ::-1]


def build_bilateral(kind: str, mio: str = "none", mio_from: str = "HSN", g_lptc_mn=0.5, lptc_leak_scale=50.0,
                    w_vs_mos=2.0, w_mio=3.0, gj_tau_ms=15.0, chain_scale=1.0):
    """Two copies of the unilateral circuit (suffixes _R, _L) plus the MIO motor neuron(s)."""
    base = "drosophila" if kind == "drosophila" else "eristalis_female"   # the LPTC sets of both sexes are equal
    names1, ctype1, P1, GJ1 = build_circuit(base, mio_from, g_lptc_mn=g_lptc_mn, lptc_leak_scale=lptc_leak_scale,
                                            w_vs_mos=w_vs_mos, w_mio=w_mio, gj_tau_ms=gj_tau_ms, chain_scale=chain_scale)
    n1 = len(names1)
    names = [f"{nm}_R" for nm in names1] + [f"{nm}_L" for nm in names1]
    ctype = list(ctype1) + list(ctype1)
    P = [row.copy() for row in P1] + [row.copy() for row in P1]
    gj = [tuple(g) for g in GJ1] + [(a + n1, b + n1, G, C) for a, b, G, C in GJ1]
    p = MN_PRESET["MOT"]
    row = np.array([p["Rin"], p["VL"], p["gVT"], p["gL"], p["gNa"], p["gK"], p["gNaP"], p["Ibias"]])
    src = {"HSN": ["HSN"], "HSNE": ["HSNE"], "HS": [n for n in names1 if n.startswith("HS")],
           "VS": ["VS1", "VS2", "VS3", "VS4"]}[mio_from]
    if mio == "median":
        # one motor neuron for both limbs; the same total junction conductance as one independent
        # neuron, shared between the two sides
        names.append("MIO"); ctype.append(MN); P.append(row.copy())
        i = len(names) - 1
        for side in ("R", "L"):
            for s in src:
                g = g_lptc_mn * w_mio / 2.0 / len(src) ** 0.5
                gj.append((names.index(f"{s}_{side}"), i, g, g * gj_tau_ms))
    elif mio == "independent":
        for side in ("R", "L"):
            names.append(f"MIO_{side}"); ctype.append(MN); P.append(row.copy())
            i = len(names) - 1
            for s in src:
                g = g_lptc_mn * w_mio / len(src) ** 0.5
                gj.append((names.index(f"{s}_{side}"), i, g, g * gj_tau_ms))
    elif mio != "none":
        raise ValueError(mio)
    return names, np.array(ctype, dtype=np.int64), np.array(P), np.array(gj, dtype=np.float64).reshape(-1, 4)


@dataclass
class BinocularModel:
    species: str = "eristalis"
    sex: str = "male"
    mio: str | None = None               # "median" | "independent" | "none"; default: median for males
    mio_from: str = "HSN"
    mio_pull: float = 0.0                # own-eye anatomical frame; 0° = toward the midline
    g_lptc_mn: float = 0.5
    lptc_leak_scale: float = 50.0
    w_vs_mos: float = 2.0
    w_mio: float = 3.0
    gj_tau_ms: float = 15.0
    chain_scale: float = 1.0
    target_hz: float = 100.0
    pre_ms: float = 150.0
    post_ms: float = 100.0

    def __post_init__(self):
        if self.mio is None:
            self.mio = "median" if (self.species == "eristalis" and self.sex == "male") else "none"
        self.eye_model = Model(self.species, self.sex, target_hz=0, g_lptc_mn=self.g_lptc_mn,
                               lptc_leak_scale=self.lptc_leak_scale, w_vs_mos=self.w_vs_mos, w_mio=self.w_mio,
                               gj_tau_ms=self.gj_tau_ms, chain_scale=self.chain_scale)
        self.dt_frame = self.eye_model.dt_frame
        self.el_grid = self.eye_model.el_grid
        kind = "drosophila" if self.species == "drosophila" else f"eristalis_{self.sex}"
        self.circuit = build_bilateral(kind, self.mio, self.mio_from, self.g_lptc_mn, self.lptc_leak_scale,
                                       self.w_vs_mos, self.w_mio, self.gj_tau_ms, self.chain_scale)
        self.names, self.ctype, self.P, self.GJ = self.circuit
        self.g_leak = self.P[:, 3] + 1.0 / self.P[:, 0]
        self.motor_neurons = [n for n, c in zip(self.names, self.ctype) if c == MN]
        self.lptcs = [n for n, c in zip(self.names, self.ctype) if c != MN]
        if self.target_hz > 0:
            self._calibrate_bias()

    # ---------------------------------------------------------------- tonic rate calibration
    def _groups(self):
        """Motor neurons that must share a bias by left-right symmetry."""
        g = {}
        for nm in self.motor_neurons:
            g.setdefault(nm.split("_")[0], []).append(self.names.index(nm))
        return g

    def _tonic(self):
        n = len(self.names)
        _, V = simulate(self.circuit, lambda tm: np.zeros(n), 400.0, pre_roll_ms=500.0)
        return {nm: float(spike_rate(V[:, self.names.index(nm)], kernel="gauss")[int(100 / DT):].mean()) for nm in self.motor_neurons}

    def _calibrate_bias(self, rounds=2, lo=-90.0, hi=15.0, steps=9):
        key = "bi_" + hashlib.md5(json.dumps([self.species, self.sex, self.mio, self.mio_from, self.target_hz,
                                              self.P.tolist(), self.GJ.tolist()]).encode()).hexdigest()[:12]
        cache = pathlib.Path(__file__).with_name("_bias_cache.json")
        store = json.loads(cache.read_text()) if cache.exists() else {}
        groups = self._groups()
        if key in store:
            for gname, b in store[key].items():
                self.P[groups[gname], 7] = b
            return
        for _ in range(rounds):
            for gname, idx in groups.items():
                a, b = lo, hi
                probe = self.names[idx[0]]
                for _ in range(steps):
                    mid = 0.5 * (a + b)
                    self.P[idx, 7] = mid
                    if self._tonic()[probe] < self.target_hz:
                        a = mid
                    else:
                        b = mid
                self.P[idx, 7] = 0.5 * (a + b)
        store[key] = {gname: float(self.P[idx[0], 7]) for gname, idx in groups.items()}
        cache.write_text(json.dumps(store, indent=1))

    # ---------------------------------------------------------------- run
    def run(self, movie_R, movie_L, onset_s: float = 0.25, mio_gain: float = 1.0) -> dict:
        """movie_R, movie_L: each eye's movie in its own coordinates (use `split_eyes`). mio_gain = 0
        removes the MIO's mechanical action (in-silico tenotomy) without changing the network."""
        em = self.eye_model
        T = movie_R.shape[0]
        g = {"R": em.front_end(movie_R)[2], "L": em.front_end(movie_L)[2]}
        n = len(self.names)
        stim_ms = T * self.dt_frame * 1000.0
        total = self.pre_ms + stim_ms + self.post_ms
        G = np.zeros((int(round(total / DT)), n, 2))
        k0 = int(round(self.pre_ms / DT)); k1 = k0 + int(round(stim_ms / DT))
        frame = np.clip(((np.arange(k0, k1) - k0) * DT / 1000.0 / self.dt_frame).astype(int), 0, T - 1)
        for side in ("R", "L"):
            for nm, (ge, gi, _) in g[side].items():
                i = self.names.index(f"{nm}_{side}")
                G[k0:k1, i, 0] = ge[frame] * self.g_leak[i]
                G[k0:k1, i, 1] = gi[frame] * self.g_leak[i]
        t, V = simulate(self.circuit, lambda tm: np.zeros(n), total, pre_roll_ms=500.0, G_ext=G)
        base = slice(int((self.pre_ms + onset_s * 1000 - 100) / DT), int((self.pre_ms + onset_s * 1000) / DT))
        resp = slice(int((self.pre_ms + onset_s * 1000 + 100) / DT), k1)
        rates, baseline, d_rate = {}, {}, {}
        for nm in self.motor_neurons:
            r = spike_rate(V[:, self.names.index(nm)], kernel="gauss", win_ms=25.0)
            rates[nm] = r; baseline[nm] = float(r[base].mean()); d_rate[nm] = float(r[resp].mean() - baseline[nm])
        lptc_dv = {nm: float(V[resp, self.names.index(nm)].mean() - V[base, self.names.index(nm)].mean()) for nm in self.lptcs}
        shift = {}
        for side in ("R", "L"):
            v = np.zeros(2)
            for mus, th in PULL_FALT.items():
                nm = f"{mus}_{side}"
                v = v + d_rate[nm] / max(baseline[nm], 1e-6) * unit(th)
            mio_nm = "MIO" if "MIO" in d_rate else (f"MIO_{side}" if f"MIO_{side}" in d_rate else None)
            if mio_nm:
                v = v + mio_gain * d_rate[mio_nm] / max(baseline[mio_nm], 1e-6) * unit(self.mio_pull)
            shift[side] = v
        aR, dR = shift["R"]; aL, dL = shift["L"]
        return dict(t=t, V=V, rates=rates, baseline=baseline, d_rate=d_rate, lptc_dv=lptc_dv, shift=shift,
                    vec4=np.array([aR, dR, aL, dL]), medial=float((aR + aL) / 2), version=float((aR - aL) / 2),
                    dorsal=float((dR + dL) / 2), base=base, resp=resp)


# ---------------------------------------------------------------------- head-centred stimuli
def head_grating(model: BinocularModel, direction_deg, speed, wavelength=20.0, duration=1.0, contrast=1.0, onset=0.25):
    """Full-field grating in head coordinates: 0° = toward the animal's right, 90° = up."""
    return grating_movie(PSI, model.el_grid, direction_deg, speed, wavelength, duration, model.dt_frame,
                         contrast=contrast, onset=onset)


def rotation(model, speed=30.0, **kw):
    """Yaw rotation of the surround: everything drifts to the animal's right (front-to-back on the
    right eye, back-to-front on the left eye)."""
    return split_eyes(head_grating(model, 0.0, speed, **kw))


def expansion(model, speed=30.0, **kw):
    """Front-to-back motion on both sides (forward translation)."""
    a = head_grating(model, 0.0, speed, **kw); b = head_grating(model, 180.0, speed, **kw)
    w = (1.0 / (1.0 + np.exp(-PSI / 3.0)))[None, None, :]
    return split_eyes(b * (1 - w) + a * w)
