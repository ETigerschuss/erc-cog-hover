"""Tier-1 biophysical circuit model, ported from the MESH viewer (github.com/ETigerschuss/MESH,
`skeleton_em_viewer.py`, "Tier 1 Circuit Model") to NumPy, with an optional male *Eristalis*
extension (HSNE and the MIO motor neuron) for hypothesis testing.

Equations and parameters follow the MESH implementation exactly (forward Euler, dt = 0.01 ms;
Hodgkin–Huxley gates; persistent Na+ as the tonic driver; graded LPTCs with K+ and T-type Ca2+;
low-pass-filtered bidirectional gap junctions). Numeric values are the MESH "calibrated preset"
(MOT ~120 Hz, MOS ~100 Hz at rest). The model is single-compartment; see the MESH README for the
provenance and caveats of each parameter.

Cells are driven by current injection, as in MESH. `mio_search.py` adds a visual front end that
turns a stimulus into LPTC currents.
"""
from __future__ import annotations

import numpy as np

try:  # numba makes the 100k-step Euler loop ~50x faster; the pure-NumPy path gives identical results
    from numba import njit
except Exception:  # pragma: no cover
    def njit(*a, **k):
        def deco(f):
            return f
        return deco if not a or not callable(a[0]) else a[0]

DT = 0.01          # ms
CM = 1.0
V_CA, V_NA, V_K = 120.0, 50.0, -77.0

# cell type codes
LPTC, MN = 0, 1

# ---- MESH calibrated preset (README "Key tuning parameters", skeleton_em_viewer.py header) ----
MN_PRESET = {
    "MOT": dict(Rin=260.0, VL=-58.81, gVT=0.0, gL=0.42, gNa=145.0, gK=52.68, gNaP=1.748, Ibias=2.84),
    "MOS": dict(Rin=360.0, VL=-62.76, gVT=0.0, gL=0.28, gNa=170.0, gK=45.60, gNaP=1.510, Ibias=2.10),
}
LPTC_PRESET = dict(gVT=0.5, gL=0.05, gK=2.0)
VS_RIN = [150.0, 140.0, 130.0, 120.0]
VS_VR = [-40.0, -45.0, -50.0, -55.0]
HS_RIN, HS_VR = 150.0, -45.0
G_CHAIN, C_CHAIN = 0.05, 0.05      # within-chain LPTC gap junctions (tau = 1 ms)
G_LPTC_MN, C_LPTC_MN = 0.1, 0.8    # LPTC <-> motor neuron gap junctions (tau = 8 ms)


def build_circuit(species: str = "drosophila", mio_from: str = "HSN", mio_params: str = "MOT",
                  g_lptc_mn: float = G_LPTC_MN, lptc_leak_scale: float = 1.0, w_vs_mos: float = 1.0,
                  w_mio: float = 1.0, gj_tau_ms: float | None = None):
    """Return the right-eye circuit as arrays.

    species: 'drosophila' (VS1-4, HSN, HSE, HSS, MOT, MOS) or 'eristalis_male' (adds HSNE and the
    MIO motor neuron) or 'eristalis_female' (adds HSNE only).
    mio_from: which LPTCs couple to the MIO motor neuron in the male: 'HSN' (hypothesis H2),
    'HSNE', 'HS' (all HS cells) or 'VS'.
    g_lptc_mn: LPTC<->motor-neuron gap-junction conductance (MESH default 0.1; in WP1 it becomes
    proportional to validated apposition area; `mio_search.calibrate_coupling` fits it to the RMN tuning range).
    lptc_leak_scale: multiplies the LPTC membrane conductance (gL and 1/Rin). The MESH preset gives
    the LPTCs a leak of 0.057, far below the gap-junction conductances, so the motor neurons would
    clamp them; large LPTCs have low input resistance, and a scale of ~20 makes them stiff graded
    voltage sources whose coupling coefficient onto the motor neurons is set by g_lptc_mn alone.
    w_vs_mos: relative conductance of the VS1-4 -> MOS junctions (per cell) versus HS -> MOS; Falt et
    al. assumed equal weights per cell; the model's fit to the MOS/MOT divergence predicts the ratio,
    to be tested against the junction areas measured in WP1.
    gj_tau_ms: time constant of the low-pass filter of the LPTC<->motor-neuron junctions (C = G·τ). The
    MESH preset (C = 0.8) gives ~1.6 ms at G = 0.5, which lets the motor-neuron spikes through as 10 mV
    spikelets in the LPTCs; 15 ms represents the cable distance between the junction site and the
    spike-initiation zone and leaves the rate-coded modulation unchanged.
    w_mio: conductance of the LPTC -> MIO junctions relative to the LPTC -> MOT/MOS junctions. With one
    coupled cell (HSN, hypothesis H2) and w_mio = 1 the MIO would be modulated a quarter as much as
    MOT (four HS cells); w_mio = 3 gives the three motor neurons comparable visual modulation (free
    parameter; WP1 junction areas, WP2 EMG).
    """
    names = ["VS1", "VS2", "VS3", "VS4", "HSN", "HSE", "HSS"]
    if species.startswith("eristalis"):
        names.append("HSNE")
    names += ["MOT", "MOS"]
    if species == "eristalis_male":
        names.append("MIO")
    n = len(names)
    idx = {nm: i for i, nm in enumerate(names)}
    ctype = np.array([MN if nm in ("MOT", "MOS", "MIO") else LPTC for nm in names], dtype=np.int64)
    P = np.zeros((n, 8))  # Rin, VL, gVT, gL, gNa, gK, gNaP, Ibias
    for i, nm in enumerate(names):
        if nm.startswith("VS"):
            k = int(nm[2]) - 1
            P[i] = [VS_RIN[k] / lptc_leak_scale, VS_VR[k], LPTC_PRESET["gVT"], LPTC_PRESET["gL"] * lptc_leak_scale, 0, LPTC_PRESET["gK"], 0, 0]
        elif nm.startswith("HS"):
            P[i] = [HS_RIN / lptc_leak_scale, HS_VR, LPTC_PRESET["gVT"], LPTC_PRESET["gL"] * lptc_leak_scale, 0, LPTC_PRESET["gK"], 0, 0]
        else:
            p = MN_PRESET["MOT" if nm == "MOT" else "MOS" if nm == "MOS" else mio_params]
            P[i] = [p["Rin"], p["VL"], p["gVT"], p["gL"], p["gNa"], p["gK"], p["gNaP"], p["Ibias"]]
    gj = []  # (a, b, G, C)
    for a, b in (("VS1", "VS2"), ("VS2", "VS3"), ("VS3", "VS4"), ("HSN", "HSE"), ("HSE", "HSS")):
        gj.append((idx[a], idx[b], G_CHAIN, C_CHAIN))
    if "HSNE" in idx:
        gj.append((idx["HSN"], idx["HSNE"], G_CHAIN, C_CHAIN))
    hs = [nm for nm in names if nm.startswith("HS")]
    c_of = (lambda g: g * gj_tau_ms) if gj_tau_ms else (lambda g: C_LPTC_MN * g / max(g_lptc_mn, 1e-9))
    for v in ("VS1", "VS2", "VS3", "VS4"):
        g = g_lptc_mn * w_vs_mos
        gj.append((idx[v], idx["MOS"], g, c_of(g)))
    for h in hs:
        gj.append((idx[h], idx["MOS"], g_lptc_mn, c_of(g_lptc_mn)))
        gj.append((idx[h], idx["MOT"], g_lptc_mn, c_of(g_lptc_mn)))
    if "MIO" in idx:
        src = {"HSN": ["HSN"], "HSNE": ["HSNE"], "HS": hs, "VS": ["VS1", "VS2", "VS3", "VS4"]}[mio_from]
        for s in src:
            g = g_lptc_mn * w_mio / len(src) ** 0.5
            gj.append((idx[s], idx["MIO"], g, c_of(g)))
    GJ = np.array(gj, dtype=np.float64).reshape(-1, 4)
    return names, ctype, P, GJ


@njit(cache=True)
def _simulate(ctype, P, GJ, I_ext, G_ext, E_rev, dt, noise, seed):
    """Forward-Euler simulation. I_ext: (n_steps, n_cells) injected current (same units as MESH).
    Returns V (n_steps, n_cells)."""
    np.random.seed(seed)
    n_steps, n = I_ext.shape
    V = np.empty((n_steps, n))
    v = P[:, 1].copy()
    hCa = np.empty(n); m = np.empty(n); h = np.empty(n); nn = np.empty(n)
    for i in range(n):
        x = v[i]
        hCa[i] = 1.0 / (1.0 + np.exp((x + 85.5) / 8.6))
        am = 1.0 if abs(x + 40.0) < 1e-7 else 0.1 * (x + 40.0) / (1.0 - np.exp(-(x + 40.0) / 10.0))
        bm = 4.0 * np.exp(-(x + 65.0) / 18.0)
        ah = 0.07 * np.exp(-(x + 65.0) / 20.0)
        bh = 1.0 / (1.0 + np.exp(-(x + 35.0) / 10.0))
        an = 0.1 if abs(x + 55.0) < 1e-7 else 0.01 * (x + 55.0) / (1.0 - np.exp(-(x + 55.0) / 10.0))
        bn = 0.125 * np.exp(-(x + 65.0) / 80.0)
        m[i] = am / (am + bm); h[i] = ah / (ah + bh); nn[i] = an / (an + bn)
    ngj = GJ.shape[0]
    Vf = np.zeros(ngj)
    for step in range(n_steps):
        Itot = np.zeros(n)
        # 1. gap junctions (bidirectional, low-pass filtered)
        for g in range(ngj):
            a = int(GJ[g, 0]); b = int(GJ[g, 1]); G = GJ[g, 2]; C = GJ[g, 3]
            tau = C / G if G > 1e-9 else 0.0
            raw = v[b] - v[a]
            if tau > 1e-9:
                Vf[g] += (raw - Vf[g]) / tau * dt
            else:
                Vf[g] = raw
            IA = G * Vf[g]
            Itot[a] += IA; Itot[b] -= IA
        # 2. external current, conductance drive, bias, noise
        for i in range(n):
            Itot[i] += I_ext[step, i] + P[i, 7]
            Itot[i] += G_ext[step, i, 0] * (E_rev[i, 0] - v[i]) + G_ext[step, i, 1] * (E_rev[i, 1] - v[i])
            if noise > 0:
                Itot[i] += noise * (np.random.random() * 2.0 - 1.0)
        # 3. step cells
        for i in range(n):
            x = v[i]
            Rin, VL, gVT, gL, gNa, gK, gNaP = P[i, 0], P[i, 1], P[i, 2], P[i, 3], P[i, 4], P[i, 5], P[i, 6]
            hInf = 1.0 / (1.0 + np.exp((x + 85.5) / 8.6))
            tauH = 40.0 + 30.0 / (1.0 + np.exp((x + 84.0) / 7.3)) * np.exp((x + 160.0) / 30.0)
            hCa[i] += (hInf - hCa[i]) / tauH * dt
            mCa = 1.0 / (1.0 + np.exp((-61.0 - x) / 4.2))
            iT = gVT * mCa ** 3 * hCa[i] * (x - V_CA)
            an = 0.1 if abs(x + 55.0) < 1e-7 else 0.01 * (x + 55.0) / (1.0 - np.exp(-(x + 55.0) / 10.0))
            bn = 0.125 * np.exp(-(x + 65.0) / 80.0)
            nn[i] += (an * (1.0 - nn[i]) - bn * nn[i]) * dt
            iK = gK * nn[i] ** 4 * (x - V_K)
            iL = (gL + 1.0 / Rin) * (x - VL)
            if ctype[i] == LPTC:
                v[i] = x + (-iT - iK - iL + Itot[i]) / CM * dt
            else:
                am = 1.0 if abs(x + 40.0) < 1e-7 else 0.1 * (x + 40.0) / (1.0 - np.exp(-(x + 40.0) / 10.0))
                bm = 4.0 * np.exp(-(x + 65.0) / 18.0)
                ah = 0.07 * np.exp(-(x + 65.0) / 20.0)
                bh = 1.0 / (1.0 + np.exp(-(x + 35.0) / 10.0))
                m[i] += (am * (1.0 - m[i]) - bm * m[i]) * dt
                h[i] += (ah * (1.0 - h[i]) - bh * h[i]) * dt
                iNa = gNa * m[i] ** 3 * h[i] * (x - V_NA)
                mNaP = 1.0 / (1.0 + np.exp(-(x + 52.0) / 5.0))
                iNaP = gNaP * mNaP * (x - V_NA)
                v[i] = x + (-iT - iNa - iK - iNaP - iL + Itot[i]) / CM * dt
            V[step, i] = v[i]
    return V


def simulate(circuit, I_ext_fn, t_total_ms: float, pre_roll_ms: float = 500.0, dt: float = DT,
             noise: float = 0.0, seed: int = 0, G_ext=None, E_rev=None):
    """Run the circuit. `I_ext_fn(t_ms) -> (n_cells,)` gives the injected current at time t
    (t counted from the end of the pre-roll); `G_ext[(step, cell, 0|1)]` an optional excitatory
    and inhibitory conductance drive with reversal potentials `E_rev[(cell, 0|1)]`
    (default: rest + 40 mV and rest − 20 mV, Ammer et al. 2023). Returns (t_ms, V) after the pre-roll."""
    names, ctype, P, GJ = circuit
    n = len(names)
    n_pre = int(round(pre_roll_ms / dt))
    n_run = int(round(t_total_ms / dt))
    I = np.zeros((n_pre + n_run, n))
    for k in range(n_run):
        I[n_pre + k] = I_ext_fn(k * dt)
    G = np.zeros((n_pre + n_run, n, 2))
    if G_ext is not None:   # (n_run, n, 2) conductance drive after the pre-roll
        G[n_pre:n_pre + G_ext.shape[0]] = G_ext[:n_run]
    if E_rev is None:   # Ammer et al. 2023: E_exc = rest + 40 mV, E_inh = rest - 20 mV
        E_rev = np.stack([P[:, 1] + 40.0, P[:, 1] - 20.0], axis=1)
    V = _simulate(ctype, P, GJ, I, G, np.asarray(E_rev, dtype=np.float64), dt, noise, seed)
    t = np.arange(n_run) * dt
    return t, V[n_pre:]


def spike_rate(v: np.ndarray, dt: float = DT, win_ms: float = 50.0, thresh: float = 0.0,
               kernel: str = "box"):
    """Firing rate (Hz) from a membrane-voltage trace (upward crossings of thresh), smoothed with a
    boxcar of `win_ms` or a Gaussian of sigma = win_ms (kernel='gauss')."""
    up = (v[1:] > thresh) & (v[:-1] <= thresh)
    spikes = np.concatenate([[False], up]).astype(float)
    if kernel == "gauss":
        sig = win_ms / dt
        x = np.arange(-int(4 * sig), int(4 * sig) + 1)
        k = np.exp(-0.5 * (x / sig) ** 2)
        k /= k.sum() * dt / 1000.0
    else:
        w = int(round(win_ms / dt))
        k = np.ones(w) / (w * dt / 1000.0)
    return np.convolve(spikes, k, mode="same")


def displacement(rates: dict, baseline: dict, pull_dirs_deg: dict, dt: float = DT, gain: float = 1.0):
    """Linear vector-sum oculomotor model (Falt et al. 2026): retinal shift = sum_i w_i * unit(theta_i),
    with w_i = (rate_i - baseline_i) / baseline_i. Returns the cumulative trajectory (n_steps, 2) in
    arbitrary units (x = front, y = up)."""
    n = len(next(iter(rates.values())))
    traj = np.zeros((n, 2))
    for nm, th in pull_dirs_deg.items():
        w = (rates[nm] - baseline[nm]) / max(baseline[nm], 1e-6)
        u = np.array([np.cos(np.deg2rad(th)), np.sin(np.deg2rad(th))])
        traj += np.outer(np.cumsum(w) * dt / 1000.0 * gain, u)
    return traj
