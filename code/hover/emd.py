"""Elementary motion detectors (NumPy port of the ALIstim HRBL front end).

Stimuli are arrays of shape (T, H, W) with values in [0, 1]: time, elevation, azimuth.
Filters are first-order IIR (exact discretisation of exp(-t/tau) kernels), so the
port needs nothing beyond NumPy. The differentiable PyTorch original is in
prior_work/ALIstimAXET_Final3_1.ipynb.
"""
from __future__ import annotations

import numpy as np


def lowpass(x: np.ndarray, tau: float, dt: float) -> np.ndarray:
    """First-order low-pass along axis 0 (time)."""
    a = np.exp(-dt / tau)
    y = np.empty_like(x, dtype=float)
    y[0] = x[0]
    for t in range(1, x.shape[0]):
        y[t] = a * y[t - 1] + (1.0 - a) * x[t]
    return y


def highpass(x: np.ndarray, tau: float, dt: float) -> np.ndarray:
    return x - lowpass(x, tau, dt)


def _shift(x: np.ndarray, axis: int) -> tuple[np.ndarray, np.ndarray]:
    """Return neighbouring photoreceptor pairs (a, b) along a spatial axis."""
    n = x.shape[axis]
    a = np.take(x, range(0, n - 1), axis=axis)
    b = np.take(x, range(1, n), axis=axis)
    return a, b


def on_off(x: np.ndarray, dt: float, tau_hp: float = 0.25, tau_lp: float = 0.05,
           dc: float = 0.1) -> tuple[np.ndarray, np.ndarray]:
    """Lamina-like band-pass, split into half-wave rectified ON and OFF channels
    (as in HRBL: interim = bp(x) + 0.1 x)."""
    bp = lowpass(highpass(x, tau_hp, dt), tau_lp, dt) + dc * x
    on = np.maximum(bp, 0.0)
    off = np.maximum(-(bp - 0.05), 0.0)
    return on, off


def hassenstein_reichardt(x: np.ndarray, dt: float, axis: int, tau: float = 0.05) -> np.ndarray:
    """Opponent HR correlator along a spatial axis (1 = elevation, 2 = azimuth).

    Positive output = motion toward increasing index on that axis.
    """
    a, b = _shift(x, axis)
    return lowpass(a, tau, dt) * b - a * lowpass(b, tau, dt)


def t4t5_layer(stim: np.ndarray, dt: float, tau: float = 0.05) -> dict[str, np.ndarray]:
    """ON (T4-like) + OFF (T5-like) HR detectors for the four cardinal directions.

    Returns spatially resolved, opponent-subtracted maps:
    'h' (rightward > 0) of shape (T, H, W-1) and 'v' (downward > 0) of shape (T, H-1, W).
    """
    on, off = on_off(stim, dt)
    h = hassenstein_reichardt(on, dt, axis=2, tau=tau) + hassenstein_reichardt(off, dt, axis=2, tau=tau)
    v = hassenstein_reichardt(on, dt, axis=1, tau=tau) + hassenstein_reichardt(off, dt, axis=1, tau=tau)
    return {"h": h, "v": v}


def grating(direction_deg: float, shape=(16, 32), duration=1.0, dt=1 / 120,
            wavelength=8.0, velocity=16.0, patch: tuple[float, float, float] | None = None) -> np.ndarray:
    """Drifting square-ish sine grating. Units: pixels and pixels/s.

    direction 0 = rightward (+azimuth), 90 = downward (+elevation; row index grows downward).
    `patch` = (row_centre, col_centre, radius) in pixels restricts the grating to a disc;
    the rest of the field is mean grey (0.5).
    """
    T = int(round(duration / dt))
    H, W = shape
    rr, cc = np.mgrid[0:H, 0:W].astype(float)
    th = np.deg2rad(direction_deg)
    proj = cc * np.cos(th) + rr * np.sin(th)
    t = np.arange(T)[:, None, None] * dt
    stim = 0.5 + 0.5 * np.sin(2 * np.pi * (proj[None] - velocity * t) / wavelength)
    if patch is not None:
        r0, c0, rad = patch
        mask = ((rr - r0) ** 2 + (cc - c0) ** 2) <= rad ** 2
        stim = np.where(mask[None], stim, 0.5)
    return stim
