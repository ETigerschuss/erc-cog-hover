"""Controversial stimuli: find stimuli on which two circuit hypotheses disagree most.

Golan, Raju & Kriegeskorte (2020) PNAS. ALIstim used gradient descent on pixel stimuli.
Here we use a dependency-free (1+lambda) evolution strategy over a low-dimensional,
experimentally realisable stimulus space (patch position and size, direction, velocity).
"""
from __future__ import annotations

from typing import Callable

import numpy as np

from .emd import grating
from .snn import FIELD, Circuit, rmn_rates

PARAM_BOUNDS = {
    "row": (2.0, FIELD[0] - 2.0),
    "col": (2.0, FIELD[1] - 2.0),
    "radius": (2.5, 8.0),
    "direction": (0.0, 360.0),
    "velocity": (4.0, 40.0),
}


def render(p: dict, duration=0.5, dt=1 / 120) -> np.ndarray:
    return grating(p["direction"], FIELD, duration, dt, wavelength=8.0,
                   velocity=p["velocity"], patch=(p["row"], p["col"], p["radius"]))


def disagreement(a: Circuit, b: Circuit, readout: str, p: dict, dt=1 / 120) -> float:
    s = render(p, dt=dt)
    ra, rb = rmn_rates(a, s, dt), rmn_rates(b, s, dt)
    return abs(ra.get(readout, 0.0) - rb.get(readout, 0.0))


def search(a: Circuit, b: Circuit, readout: str = "MOI", generations: int = 15, lam: int = 6,
           seed: int = 0, objective: Callable | None = None) -> tuple[dict, float, list[float]]:
    rng = np.random.default_rng(seed)
    keys = list(PARAM_BOUNDS)
    lo = np.array([PARAM_BOUNDS[k][0] for k in keys])
    hi = np.array([PARAM_BOUNDS[k][1] for k in keys])
    f = objective or (lambda p: disagreement(a, b, readout, p))
    to_p = lambda x: dict(zip(keys, x))
    x = rng.uniform(lo, hi)
    best = float(f(to_p(x)))
    sigma = 0.25 * (hi - lo)
    history = [best]
    for _ in range(generations):
        cands = np.clip(x + sigma * rng.standard_normal((lam, len(keys))), lo, hi)
        scores = [float(f(to_p(c))) for c in cands]
        i = int(np.argmax(scores))
        if scores[i] > best:
            x, best = cands[i], scores[i]
            sigma *= 1.2
        else:
            sigma *= 0.85
        history.append(best)
    return to_p(x), best, history
