"""Stage 5: oculomotor model (Falt et al. 2026) and reference frames.

Frames. Falt et al. give visual-motion and retinal-shift directions in the same anatomical frame:
0° = anterior (back-to-front motion; retina moving toward the antennae), 90° = dorsal, 180° =
posterior (front-to-back), 270° = ventral. The model's frame (right eye) has 0° = toward +azimuth
(front-to-back), 90° = upward. The two are mirror images: θ_model = 180° − θ_falt.

Oculomotor model: retinal shift = Σ_i w_i · unit(θ_i) over the muscles, with w_i the normalised,
baseline-subtracted activity of the motor neuron of muscle i and θ_i the muscle's pull direction.
Drosophila (optogenetic activation): MOS 51 ± 4°, MOT 320 ± 4° (anatomical frame), orthogonal.
A retinal shift in direction s produces visual motion in direction s (inverted sampling), so the
optokinetic reflex to motion in direction φ is a retinal shift in direction φ + 180° (Falt et al.
Fig. 3d–e: predicted inverted shift vs stimulus direction, R² = 0.994, slope 1.01, mean error 7.07°).
Hoverfly: MOS and MOT pulls by homology [verify by µCT], the MIO pull is a free parameter.
"""
from __future__ import annotations

import numpy as np

PULL_FALT = {"MOS": 51.0, "MOT": 320.0}   # anatomical frame, Drosophila


def falt_to_model(theta_deg, beta: float = 0.0):
    """Falt (holder) frame -> model frame. beta: rotation of the holder frame relative to the
    anatomical eye frame (head pitch in the holder; fitted in validate_falt)."""
    return (180.0 - (np.asarray(theta_deg, dtype=float) - beta)) % 360.0


def model_to_falt(theta_deg, beta: float = 0.0):
    return (180.0 - np.asarray(theta_deg, dtype=float) + beta) % 360.0


def pull_model(mio_pull_falt: float | None = None, beta: float = 0.0) -> dict:
    """Pull directions in the model frame; MIO pull given in the anatomical (Falt) frame."""
    d = {k: float(falt_to_model(v, beta)) for k, v in PULL_FALT.items()}
    if mio_pull_falt is not None:
        d["MIO"] = float(falt_to_model(mio_pull_falt, beta))
    return d


def unit(theta_deg):
    return np.array([np.cos(np.deg2rad(theta_deg)), np.sin(np.deg2rad(theta_deg))])


def shift_vector(weights: dict, pull: dict) -> np.ndarray:
    v = np.zeros(2)
    for nm, w in weights.items():
        if nm in pull:
            v = v + w * unit(pull[nm])
    return v


def direction(vec) -> float:
    return float(np.rad2deg(np.arctan2(vec[1], vec[0])) % 360)


def angle_between(a_deg, b_deg) -> float:
    return float(abs((np.asarray(a_deg) - np.asarray(b_deg) + 180) % 360 - 180))


def preferred_direction(dirs_deg, responses) -> tuple[float, float]:
    """Vector average of a tuning curve: (PD in deg, direction-selectivity length in [0, 1])."""
    r = np.asarray(responses, dtype=float)
    r = r - r.min() if r.min() < 0 else r
    v = np.sum(r[:, None] * np.stack([np.cos(np.deg2rad(dirs_deg)), np.sin(np.deg2rad(dirs_deg))], 1), 0)
    return direction(v), float(np.linalg.norm(v) / max(r.sum(), 1e-9))
