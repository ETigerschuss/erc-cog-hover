"""Stage 6: the three circuits and the end-to-end pipeline
stimulus movie → eye map → T4/T5 detectors → local opponency circuits → LPTC conductances →
Tier-1 electrical network (HH motor neurons) → retinal-shift vector.

Model variants:  Model("drosophila", "female")  ground truth (Falt et al. 2026)
                 Model("eristalis", "female")   hoverfly female (HSNE added)
                 Model("eristalis", "male", mio_from="HSN", mio_pull=θ)   + MIO, pull θ (anatomical frame)
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass, field

import numpy as np

from .eye import Sampler, build_eye, grid
from .hrbl import CircuitParams
from .lptc import FrontEnd, drosophila_lptcs, eristalis_lptcs
from .oculomotor import direction, pull_model
from .tier1_hh import DT, build_circuit, simulate, spike_rate

MOTOR = ("MOT", "MOS", "MIO")


@dataclass
class Model:
    species: str = "drosophila"
    sex: str = "female"
    mio_from: str = "HSN"
    mio_pull: float | None = None        # anatomical frame (Falt), male Eristalis only
    g_lptc_mn: float = 0.5               # LPTC↔RMN gap-junction conductance (MESH units)
    lptc_leak_scale: float = 50.0        # stiff LPTCs (see tier1_hh.build_circuit)
    w_vs_mos: float = 2.0                # VS1-4 -> MOS junction weight relative to HS -> MOS (fitted to Falt, see validate_falt)
    g_scale: float = 1.0                 # Ammer conductance units → multiples of the LPTC leak
    yaw_fraction: float = 0.4            # eye map: tilt of the +h axis field (Zhao 2025)
    circuit_params: CircuitParams = field(default_factory=CircuitParams)
    arena_rotation: float = 0.0          # deg, holder frame vs anatomical frame (Falt comparison)
    target_hz: float = 100.0             # tonic motor-neuron rate after bias calibration (0 = skip)
    pre_ms: float = 150.0
    post_ms: float = 100.0
    dt_frame: float = 1.0 / 120.0

    def __post_init__(self):
        self.circuit_params.dt = self.dt_frame
        self.eye = build_eye(self.species, self.sex, yaw_fraction=self.yaw_fraction)
        self.az_grid, self.el_grid = grid()
        self.sampler = Sampler(self.eye, self.az_grid, self.el_grid)
        specs = drosophila_lptcs() if self.species == "drosophila" else eristalis_lptcs(self.sex)
        self.front = FrontEnd(self.eye, specs, self.circuit_params)
        kind = "drosophila" if self.species == "drosophila" else f"eristalis_{self.sex}"
        self.circuit = build_circuit(kind, self.mio_from, g_lptc_mn=self.g_lptc_mn, lptc_leak_scale=self.lptc_leak_scale, w_vs_mos=self.w_vs_mos)
        self.names, _, self.P, _ = self.circuit
        self.pull = pull_model(self.mio_pull if "MIO" in self.names else None, self.arena_rotation)
        if self.target_hz > 0:
            self._calibrate_bias()
        # LPTC leak conductance in MESH units (gL + 1/Rin): Ammer's unit leak maps onto it
        self.g_leak = {nm: self.P[i, 3] + 1.0 / self.P[i, 0] for i, nm in enumerate(self.names)}

    def _tonic_rates(self, t_ms=400.0):
        n = len(self.names)
        _, V = simulate(self.circuit, lambda tm: np.zeros(n), t_ms, pre_roll_ms=500.0)
        return {nm: float(spike_rate(V[:, self.names.index(nm)], kernel="gauss")[int(100 / DT):].mean())
                for nm in self.motor_neurons}

    def _calibrate_bias(self, rounds=3, lo=-90.0, hi=15.0, steps=10):
        """Set each motor neuron's bias current so that its tonic rate at rest equals target_hz,
        compensating the tonic gap-junction current from the LPTCs (which depends on g_lptc_mn).
        Cached on disk by circuit parameters."""
        key = hashlib.md5(json.dumps([self.species, self.sex, self.mio_from, self.g_lptc_mn, self.lptc_leak_scale, self.w_vs_mos,
                                      self.target_hz, self.P.tolist()]).encode()).hexdigest()[:12]
        cache = pathlib.Path(__file__).with_name("_bias_cache.json")
        store = json.loads(cache.read_text()) if cache.exists() else {}
        if key in store:
            for nm, b in store[key].items():
                self.P[self.names.index(nm), 7] = b
            return
        for _ in range(rounds):
            for nm in self.motor_neurons:
                i = self.names.index(nm)
                a, b = lo, hi
                for _ in range(steps):
                    mid = 0.5 * (a + b)
                    self.P[i, 7] = mid
                    r = self._tonic_rates()[nm]
                    if r < self.target_hz:
                        a = mid
                    else:
                        b = mid
                self.P[i, 7] = 0.5 * (a + b)
        store[key] = {nm: float(self.P[self.names.index(nm), 7]) for nm in self.motor_neurons}
        cache.write_text(json.dumps(store, indent=1))

    @property
    def motor_neurons(self):
        return [n for n in self.names if n in MOTOR]

    @property
    def lptcs(self):
        return [n for n in self.names if n not in MOTOR]

    def front_end(self, movie):
        samples = self.sampler(movie)
        circuits = self.front.run_circuits(samples)
        return samples, circuits, self.front.conductances(circuits)

    def run(self, movie: np.ndarray, onset_s: float = 0.25, noise: float = 0.0, seed: int = 0) -> dict:
        """movie (T, n_el, n_az) in [0, 1]; motion starts at `onset_s` within the movie.
        Returns conductances, Tier-1 voltages, motor-neuron rates, LPTC responses and the retinal
        shift vector (mean over the motion period)."""
        samples, circuits, g = self.front_end(movie)
        T = movie.shape[0]
        n = len(self.names)
        stim_ms = T * self.dt_frame * 1000.0
        total = self.pre_ms + stim_ms + self.post_ms
        n_run = int(round(total / DT))
        G = np.zeros((n_run, n, 2))
        k0 = int(round(self.pre_ms / DT))
        k1 = k0 + int(round(stim_ms / DT))
        frame = np.clip(((np.arange(k0, k1) - k0) * DT / 1000.0 / self.dt_frame).astype(int), 0, T - 1)
        for nm, (ge, gi, _) in g.items():
            if nm not in self.names:
                continue
            i = self.names.index(nm)
            G[k0:k1, i, 0] = ge[frame] * self.g_leak[nm] * self.g_scale
            G[k0:k1, i, 1] = gi[frame] * self.g_leak[nm] * self.g_scale
        t, V = simulate(self.circuit, lambda tm: np.zeros(n), total, pre_roll_ms=500.0, noise=noise, seed=seed, G_ext=G)
        base = slice(int((self.pre_ms + onset_s * 1000 - 100) / DT), int((self.pre_ms + onset_s * 1000) / DT))
        resp = slice(int((self.pre_ms + onset_s * 1000 + 100) / DT), k1)
        rates, baseline, d_rate = {}, {}, {}
        for nm in self.motor_neurons:
            r = spike_rate(V[:, self.names.index(nm)], kernel="gauss", win_ms=25.0)
            rates[nm] = r
            baseline[nm] = float(r[base].mean())
            d_rate[nm] = float(r[resp].mean() - baseline[nm])
        lptc_dv = {nm: float(V[resp, self.names.index(nm)].mean() - V[base, self.names.index(nm)].mean()) for nm in self.lptcs}
        fb = slice(int(onset_s / self.dt_frame) - 10, int(onset_s / self.dt_frame))
        fr = slice(int(onset_s / self.dt_frame) + 12, T)
        ammer_dv = {nm: float(v[fr].mean() - v[fb].mean()) for nm, (_, _, v) in g.items()}
        vec = np.zeros(2)
        for nm, th in self.pull.items():
            if nm in d_rate:
                vec += d_rate[nm] / max(baseline[nm], 1e-6) * np.array([np.cos(np.deg2rad(th)), np.sin(np.deg2rad(th))])
        return dict(samples=samples, circuits=circuits, g=g, t=t, V=V, G=G, rates=rates, baseline=baseline,
                    d_rate=d_rate, lptc_dv=lptc_dv, ammer_dv=ammer_dv, shift_vec=vec,
                    shift_dir=direction(vec), shift_mag=float(np.linalg.norm(vec)), base=base, resp=resp)
