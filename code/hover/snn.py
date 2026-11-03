"""Tier-2 network: graded LPTCs coupled by gap junctions to spiking retinal motor neurons.

LPTCs (HS/VS) are passive (graded) compartments driven by spatially integrated T4/T5
signals within their receptive field. RMNs are leaky integrate-and-fire neurons. All
LPTC-LPTC and LPTC-RMN connections are **electrical**: I_i = sum_j g_ij (V_j - V_i).
This is the reduced form of the HH model in the MESH dev build.

Circuits:
  drosophila()           HS(N,E,S) chain + VS1-4 chain; MOT <- HS; MOS <- VS + HS
  eristalis(sex, moi_from)  adds HSNE; male adds RMN MOI driven by `moi_from`
                         (H2: 'HSN'; alternatives: 'HSNE', 'HS', 'VS')
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .emd import t4t5_layer

# Receptive fields on a (H, W) = (16, 32) field: rows 0 = dorsal, cols 0 = frontal midline.
FIELD = (16, 32)


def _rf(rows: tuple[int, int], cols: tuple[int, int]) -> np.ndarray:
    m = np.zeros(FIELD)
    m[rows[0]:rows[1], cols[0]:cols[1]] = 1.0
    return m


@dataclass
class Neuron:
    name: str
    kind: str                 # 'lptc' (graded) or 'rmn' (LIF)
    rf: np.ndarray | None = None
    channel: str = "h"        # 'h' or 'v' motion component
    sign: float = 1.0         # +1: preferred = rightward/downward


@dataclass
class Circuit:
    neurons: list[Neuron]
    gj: dict[tuple[str, str], float] = field(default_factory=dict)

    def index(self) -> dict[str, int]:
        return {n.name: i for i, n in enumerate(self.neurons)}

    def G(self) -> np.ndarray:
        idx, N = self.index(), len(self.neurons)
        G = np.zeros((N, N))
        for (a, b), g in self.gj.items():
            G[idx[a], idx[b]] = G[idx[b], idx[a]] = g
        return G


def _chain(names, g):
    return {(a, b): g for a, b in zip(names, names[1:])}


def drosophila() -> Circuit:
    hs = [Neuron("HSN", "lptc", _rf((0, 6), (0, 32)), "h", -1),
          Neuron("HSE", "lptc", _rf((5, 11), (0, 32)), "h", -1),
          Neuron("HSS", "lptc", _rf((10, 16), (0, 32)), "h", -1)]   # preferred: front-to-back
    vs = [Neuron(f"VS{i+1}", "lptc", _rf((0, 16), (8 * i, 8 * i + 8)), "v", 1) for i in range(4)]
    rmn = [Neuron("MOT", "rmn"), Neuron("MOS", "rmn")]
    gj = {**_chain([n.name for n in hs], 0.3), **_chain([n.name for n in vs], 0.3)}
    gj.update({(h.name, "MOT"): 0.25 for h in hs})
    gj.update({(v.name, "MOS"): 0.25 for v in vs})
    gj.update({("HSE", "MOS"): 0.08})
    return Circuit(hs + vs + rmn, gj)


def eristalis(sex: str = "male", moi_from: str = "HSN") -> Circuit:
    c = drosophila()
    hsn = c.neurons[0]
    if sex == "male":                       # dimorphic HSN: narrowed dorso-frontal RF [Nordström 2008]
        hsn.rf = _rf((0, 5), (0, 10))
    c.neurons.insert(1, Neuron("HSNE", "lptc", _rf((0, 8), (0, 16)), "h", -1))
    c.gj[("HSN", "HSNE")] = 0.3
    c.gj[("HSNE", "MOT")] = 0.25
    if sex == "male":
        c.neurons.append(Neuron("MOI", "rmn"))
        sources = {"HSN": ["HSN"], "HSNE": ["HSNE"], "HS": ["HSN", "HSNE", "HSE", "HSS"],
                   "VS": ["VS1", "VS2"]}[moi_from]
        for s in sources:
            c.gj[(s, "MOI")] = 0.35 / len(sources) ** 0.5
    return c


def lptc_drive(c: Circuit, stim: np.ndarray, dt: float, gain: float = 40.0) -> np.ndarray:
    """Input current (T, N) to each LPTC from T4/T5 maps inside its receptive field."""
    maps = t4t5_layer(stim, dt)
    T = stim.shape[0]
    I = np.zeros((T, len(c.neurons)))
    for i, n in enumerate(c.neurons):
        if n.kind != "lptc":
            continue
        m = maps[n.channel]
        rf = n.rf[:, :-1] if n.channel == "h" else n.rf[:-1, :]
        I[:, i] = gain * n.sign * (m * rf).sum(axis=(1, 2)) / max(rf.sum(), 1.0)
    return I


def simulate(c: Circuit, I_ext: np.ndarray, dt: float, tau_lptc=0.01, tau_rmn=0.008,
             v_th=1.0, v_reset=0.0, bias=0.6) -> dict[str, np.ndarray]:
    """Euler integration. Returns V (T, N) and spike counts per neuron."""
    T, N = I_ext.shape
    G = c.G()
    is_rmn = np.array([n.kind == "rmn" for n in c.neurons])
    tau = np.where(is_rmn, tau_rmn, tau_lptc)
    V = np.zeros(N)
    Vs = np.zeros((T, N))
    spikes = np.zeros(N)
    for t in range(T):
        I_gj = G @ V - G.sum(1) * V
        dV = (-V + I_ext[t] + I_gj + bias * is_rmn) / tau
        V = V + dt * dV
        fired = is_rmn & (V >= v_th)
        spikes += fired
        V = np.where(fired, v_reset, V)
        Vs[t] = V
    return {"V": Vs, "spikes": spikes}


def rmn_rates(c: Circuit, stim: np.ndarray, dt: float) -> dict[str, float]:
    out = simulate(c, lptc_drive(c, stim, dt), dt)
    dur = stim.shape[0] * dt
    return {n.name: out["spikes"][i] / dur for i, n in enumerate(c.neurons) if n.kind == "rmn"}


def preferred_direction(rates_by_dir: dict[float, float]) -> float:
    """Vector-sum preferred direction (deg) of baseline-subtracted rates."""
    d = np.array(list(rates_by_dir.keys()))
    r = np.array(list(rates_by_dir.values()))
    r = r - r.mean()
    z = (r * np.exp(1j * np.deg2rad(d))).sum()
    return float(np.rad2deg(np.angle(z)) % 360)
