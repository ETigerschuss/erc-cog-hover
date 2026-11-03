"""Stages 1–2: T4/T5 detectors and the multilevel-opponency local circuit of Ammer et al. 2023
(Figure 7 model; notebook `LPi_opponency_modelling`), applied along the local lattice axes of an
eye map.

Detector (per ommatidium and axis; Ammer notebook `calc_HRBL`): with A = rect(lp[i−1]),
B = rect(hp[i]), C = rect(lp[i+1]) the two opposite detectors are
    T_plus  = rect(A·B / (DC + C), DC)        preferred direction +axis
    T_minus = rect(C·B / (DC + A), DC)        preferred direction −axis
for the ON channel (T4-like, lp/hp of the photoreceptor signal) and the OFF channel (T5-like, of
1 − signal). rect(x, θ) = max(x − θ, 0). Lamina: interim = hp(x) + 0.1·x; L1 = rect(interim, 0);
L2 = rect(−(interim − 0.05), 0); τ_hp = 250 ms, τ_lp = 50 ms.

Local circuit (notebook `small_network`): six leaky units with τ = 20 ms,
units = [T_plus, T_minus, LPi_plus, LPi_minus, LPTC_plus, LPTC_minus];
    T_plus    ← −LT · rect(LPi_minus) + input_plus            (input = patch mean of rect(T4+T5))
    T_minus   ← −LT · rect(LPi_plus) + input_minus
    LPi_plus  ←  TL · rect(T_plus)  − LL · rect(LPi_minus)   (LPi fed by the +layer, inhibits −)
    LPi_minus ←  TL · rect(T_minus) − LL · rect(LPi_plus)
    LPTC_plus ←  TV · rect(T_plus)  − LV · rect(LPi_minus)   (the notebook's VS; PD = +axis)
    LPTC_minus←  TV · rect(T_minus) − LV · rect(LPi_plus)    (the notebook's Vx)
with the default gains LT = 0.5, TL = 1, LL = 1, TV = 1, LV = 1. Notebook mapping for the vertical
system: + = d (downward, layer 4), − = c (upward, layer 3), LPi_plus = LPi4-3, LPi_minus = LPi3-4.
Conductances onto an LPTC with PD = +axis (notebook `large_network`):
    g_exc = TV · mean_patches rect(T_plus),  g_inh = LV · mean_patches rect(LPi_minus),
    V = (40·g_exc − 20·g_inh) / (g_exc + g_inh + 1)      [mV, relative to rest; leak = 1].
Blocking conditions reproduce the notebook's `block_*` functions.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class CircuitParams:
    tau_hp: float = 0.25      # s
    tau_lp: float = 0.05      # s
    dt: float = 1.0 / 120.0   # s (notebook: 10 ms)
    DC: float = 0.02          # detector offset and threshold
    tau_net: float = 0.020    # s, all six units
    LT: float = 0.5
    TL: float = 1.0
    LL: float = 1.0
    TV: float = 1.0
    LV: float = 1.0
    HR: bool = False          # pure Hassenstein–Reichardt detector (no Barlow–Levick arm)
    E_exc: float = 40.0       # mV relative to rest
    E_inh: float = -20.0
    condition: str = "control"  # control | block_feedb | block_LT | block_LL | block_LV | block_LPi_plus | block_LPi_minus | block_T_minus

    def connM(self) -> np.ndarray:
        LT, TL, LL, TV, LV = self.LT, self.TL, self.LL, self.TV, self.LV
        M = np.array([[0, 0, 0, -LT, 0, 0],
                      [0, 0, -LT, 0, 0, 0],
                      [TL, 0, 0, -LL, 0, 0],
                      [0, TL, -LL, 0, 0, 0],
                      [TV, 0, 0, -LV, 0, 0],
                      [0, TV, -LV, 0, 0, 0]], dtype=float)
        c = self.condition
        if c == "block_feedb":
            M[0:2] = 0; M[2:4, 2:4] = 0
        elif c == "block_LT":
            M[0:2] = 0
        elif c == "block_LL":
            M[2:4, 2:4] = 0
        elif c == "block_LV":
            M[4:6, 2:4] = 0
        elif c == "block_LPi_plus":
            M[:, 2] = 0
        elif c == "block_LPi_minus":
            M[:, 3] = 0
        elif c == "block_T_minus":
            M[:, 1] = 0
        elif c != "control":
            raise ValueError(c)
        return M


def rect(x, thr=0.0):
    return np.maximum(x - thr, 0.0)


def lowpass(x, tau, dt):
    """First-order IIR low-pass along axis 0."""
    a = float(np.exp(-dt / tau))
    y = np.empty_like(x)
    y[0] = x[0]
    for t in range(1, x.shape[0]):
        y[t] = a * y[t - 1] + (1.0 - a) * x[t]
    return y


def lamina(x, p: CircuitParams):
    """Photoreceptor signal x (T, N) in [0, 1] -> (ON_lp, ON_hp, OFF_lp, OFF_hp)."""
    interim = (x - lowpass(x, p.tau_hp, p.dt)) + 0.1 * x
    on_hp = rect(interim, 0.0)
    off_hp = rect(-(interim - 0.05), 0.0)
    on_lp = lowpass(x, p.tau_lp, p.dt)
    off_lp = lowpass(1.0 - x, p.tau_lp, p.dt)
    return on_lp, on_hp, off_lp, off_hp


def detectors(samples: dict, axis: str, p: CircuitParams):
    """Three-arm detectors along one axis from the sampled signals {'c', axis+'-', axis+'+'}.
    Returns (T4_plus, T4_minus, T5_plus, T5_minus), each (T, N) ≥ 0."""
    on_lp_m, _, off_lp_m, _ = lamina(samples[axis + "-"], p)
    _, on_hp_c, _, off_hp_c = lamina(samples["c"], p)
    on_lp_p, _, off_lp_p, _ = lamina(samples[axis + "+"], p)
    out = []
    for A, B, C in ((on_lp_m, on_hp_c, on_lp_p), (off_lp_m, off_hp_c, off_lp_p)):
        A, B, C = rect(A), rect(B), rect(C)
        if p.HR:
            out += [A * B, C * B]
        else:
            out += [rect(A * B / (p.DC + C), p.DC), rect(C * B / (p.DC + A), p.DC)]
    return out[0], out[1], out[2], out[3]


def local_circuits(inp_plus, inp_minus, p: CircuitParams):
    """Run the six-unit network for every patch. inp_*: (T, n_patch) patch means of rect(T4+T5).
    Returns Vm of shape (T, 6, n_patch)."""
    M = p.connM()
    T, K = inp_plus.shape
    Vm = np.zeros((T, 6, K))
    Vinp = np.zeros((6, K))
    k = p.dt / p.tau_net
    for t in range(1, T):
        Vinp[0] = inp_plus[t - 1]; Vinp[1] = inp_minus[t - 1]
        total = M @ rect(Vm[t - 1]) + Vinp
        Vm[t] = Vm[t - 1] + k * (total - Vm[t - 1])
    return Vm


def membrane(g_exc, g_inh, p: CircuitParams):
    """Ammer conductance model: V [mV rel. rest] = (E_exc g_e + E_inh g_i)/(g_e + g_i + 1)."""
    return (p.E_exc * g_exc + p.E_inh * g_inh) / (g_exc + g_inh + 1.0)
