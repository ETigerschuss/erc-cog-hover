"""Stage 3: LPTC receptive fields on the eye map, local circuits per patch, conductance pooling.

An LPTC is specified by its weight map over the eye, the lattice axis it reads ('h' for HS types,
'v' for VS types) and the sign of its preferred direction along that axis (+1: +h = front-to-back,
+v = upward; −1: back-to-front, downward). Its excitatory conductance is the RF-weighted mean of
rect(T_PD) over the local circuits, its inhibitory conductance the weighted mean of rect(LPi_ND)
(Ammer et al. 2023 `large_network`).

Hoverfly HSN receptive fields follow Nordström et al. 2008, Fig. 2: female broad (azimuth −40…+20°,
elevation 0…50°, peak near (−10°, 25°)); male narrow (azimuth −15…+10°, elevation 5…45°, peak near
(0°, 25°)). HSNE: dorso-frontal, elevation 0…60°, azimuth 0…90° [verify]. Drosophila HS/VS fields:
thirds of the field for HSN/HSE/HSS, frontal-to-lateral columns for VS1–4 (Zhao 2025; Falt 2026).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .eye import EyeMap
from .hrbl import CircuitParams, detectors, local_circuits, membrane, rect


def gaussian_rf(az0, el0, saz, sel, tilt_deg=0.0):
    th = np.deg2rad(tilt_deg)

    def f(az, el):
        x, y = az - az0, el - el0
        u = x * np.cos(th) + y * np.sin(th)
        w = -x * np.sin(th) + y * np.cos(th)
        return np.exp(-0.5 * ((u / saz) ** 2 + (w / sel) ** 2))
    return f


def box_rf(az_range, el_range, soft=5.0):
    def f(az, el):
        a = 1 / (1 + np.exp(-(az - az_range[0]) / soft)) / (1 + np.exp((az - az_range[1]) / soft))
        e = 1 / (1 + np.exp(-(el - el_range[0]) / soft)) / (1 + np.exp((el - el_range[1]) / soft))
        return a * e
    return f


@dataclass
class LPTCSpec:
    name: str
    axis: str          # 'h' or 'v'
    pd_sign: int       # +1 or −1 along the axis
    rf: object         # callable (az, el) -> weight in [0, 1]
    note: str = ""


def drosophila_lptcs() -> list[LPTCSpec]:
    hs = [LPTCSpec("HSN", "h", +1, box_rf((-10, 150), (15, 70)), "dorsal third"),
          LPTCSpec("HSE", "h", +1, box_rf((-10, 150), (-20, 20)), "equatorial third"),
          LPTCSpec("HSS", "h", +1, box_rf((-10, 150), (-70, -15)), "ventral third")]
    vs = [LPTCSpec(f"VS{k + 1}", "v", -1, box_rf((lo, hi), (-60, 60)), "downward")
          for k, (lo, hi) in enumerate(((-10, 30), (25, 65), (60, 100), (95, 140)))]
    return hs + vs


def eristalis_lptcs(sex: str) -> list[LPTCSpec]:
    if sex == "male":
        hsn = LPTCSpec("HSN", "h", +1, gaussian_rf(0.0, 25.0, 9.0, 16.0), "male: narrow dorso-frontal (Nordström 2008)")
    else:
        hsn = LPTCSpec("HSN", "h", +1, gaussian_rf(-8.0, 25.0, 20.0, 20.0), "female: broad (Nordström 2008)")
    hsne = LPTCSpec("HSNE", "h", +1, box_rf((0, 90), (0, 60)), "dorso-frontal [verify PD]")
    rest = [LPTCSpec("HSE", "h", +1, box_rf((-10, 150), (-20, 20))),
            LPTCSpec("HSS", "h", +1, box_rf((-10, 150), (-70, -15)))]
    vs = [LPTCSpec(f"VS{k + 1}", "v", -1, box_rf((lo, hi), (-60, 60)))
          for k, (lo, hi) in enumerate(((-10, 30), (25, 65), (60, 100), (95, 140)))]
    return [hsn, hsne] + rest + vs


@dataclass
class FrontEnd:
    """Eye map + detectors + local circuits + receptive fields -> per-LPTC conductances."""
    eye: EyeMap
    specs: list[LPTCSpec]
    params: CircuitParams = field(default_factory=CircuitParams)

    def __post_init__(self):
        self.M = self.eye.patch_matrix()                     # (K, N)
        self.weights = {}
        for s in self.specs:
            w_omm = s.rf(self.eye.az, self.eye.el)
            w_patch = self.M @ w_omm                         # mean RF weight per patch
            self.weights[s.name] = w_patch / max(w_patch.sum(), 1e-9)

    def run_circuits(self, samples: dict) -> dict:
        """samples from eye.Sampler -> {'h': Vm, 'v': Vm} with Vm (T, 6, K)."""
        out = {}
        for axis in ("h", "v"):
            t4p, t4m, t5p, t5m = detectors(samples, axis, self.params)
            inp_plus = rect(t4p + t5p) @ self.M.T
            inp_minus = rect(t4m + t5m) @ self.M.T
            out[axis] = local_circuits(inp_plus, inp_minus, self.params)
        return out

    def conductances(self, circuits: dict) -> dict:
        """{name: (g_exc(t), g_inh(t), V_rel(t))}: RF-weighted means over patches (Ammer units)."""
        p = self.params
        res = {}
        for s in self.specs:
            Vm = circuits[s.axis]
            if s.pd_sign > 0:
                T_pd, LPi_nd = Vm[:, 0], Vm[:, 3]
            else:
                T_pd, LPi_nd = Vm[:, 1], Vm[:, 2]
            w = self.weights[s.name]
            g_e = p.TV * (rect(T_pd) @ w)
            g_i = p.LV * (rect(LPi_nd) @ w)
            res[s.name] = (g_e, g_i, membrane(g_e, g_i, p))
        return res

    def drive(self, samples: dict) -> dict:
        return self.conductances(self.run_circuits(samples))
