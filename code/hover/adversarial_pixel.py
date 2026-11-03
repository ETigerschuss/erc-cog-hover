"""Pixel-level controversial stimulus by gradient descent (ALIstim ExperimentTwo, autograd backend).

Optimises a low-resolution movie (T_lr × H_lr × W_lr control points, bilinear in space, frame
repetition in time) through the differentiable front end of the male Eristalis model so that the
two MIO hypotheses predict maximally different retinal-shift directions, then verifies the movie
with the full Tier-1 network and computes the female model's prediction.
"""
from __future__ import annotations

import json
import pathlib
import time

import numpy as np
from autograd import value_and_grad

from .adversarial import MIO_HYPOTHESES, ONSET, SEED_PARAMS, Surrogate, clip_params, objective_from_rates, panel, render, tuning_runs
from .frontend_ad import DifferentiableFrontEnd, adam, make_objective
from .oculomotor import falt_to_model
from .species import Model


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=60)
    ap.add_argument("--lr", type=float, default=0.15)
    ap.add_argument("--T", type=int, default=20)
    ap.add_argument("--H", type=int, default=14)
    ap.add_argument("--W", type=int, default=18)
    ap.add_argument("--out", default=None)
    ap.add_argument("--fig", default=None)
    a = ap.parse_args(argv)
    t0 = time.time()
    male = Model("eristalis", "male", mio_from="HSN", mio_pull=0.0)
    female = Model("eristalis", "female")
    runs = tuning_runs(male)
    baseline = {nm: float(np.mean([r["baseline"][nm] for r in runs])) for nm in male.motor_neurons}
    sur = Surrogate(male); sur.fit(runs)
    print(f"models built, surrogate slopes {sur.slope} ({time.time() - t0:.0f} s)", flush=True)
    fe = DifferentiableFrontEnd(male, sur, T_lr=a.T, rep=4, H_lr=a.H, W_lr=a.W, fix_frames=24)
    # seed: the parametric seed stimulus, resampled to the control grid
    mov_seed = render(male, clip_params(SEED_PARAMS))
    el_c = np.linspace(-65, 65, a.H); az_c = np.linspace(-15, 150, a.W)
    ie = np.clip(np.round((el_c - male.el_grid[0])).astype(int), 0, len(male.el_grid) - 1)
    ia = np.clip(np.round((az_c - male.az_grid[0])).astype(int), 0, len(male.az_grid) - 1)
    t_idx = np.clip(int(ONSET / male.dt_frame) + np.arange(a.T) * 4, 0, mov_seed.shape[0] - 1)
    img = mov_seed[t_idx][:, ie][:, :, ia]
    z0 = np.arctanh(np.clip(2 * img - 1, -0.95, 0.95))
    th_a, th_b = (float(falt_to_model(v, male.arena_rotation)) for v in MIO_HYPOTHESES.values())
    loss, _ = make_objective(fe, baseline, th_a, th_b)
    vg = value_and_grad(loss)
    l0 = float(loss(z0)); print(f"seed loss {l0:+.4f} ({time.time() - t0:.0f} s)", flush=True)
    z, lbest = adam(vg, z0, steps=a.steps, lr=a.lr, log=lambda s: print(s, flush=True))
    print(f"optimised loss {lbest:+.4f} ({time.time() - t0:.0f} s)", flush=True)
    mov = np.asarray(fe.movie(z))
    r_m = male.run(mov, onset_s=24 * male.dt_frame)
    score, info = objective_from_rates(r_m["d_rate"], r_m["baseline"], male)
    print(f"Tier-1 verification: angle {info['angle']:.1f}°, MIO Δ {info['d_mio']:.1f} Hz, dirs {info['dirs']}, Δrates {r_m['d_rate']}", flush=True)
    r_f = female.run(mov, onset_s=24 * male.dt_frame)
    print(f"female prediction: {r_f['shift_dir']:.1f}° (mag {r_f['shift_mag']:.2f}); Δrates {r_f['d_rate']}", flush=True)
    res = dict(method="autograd pixel gradient descent", loss_seed=l0, loss_best=lbest, score_tier1=score,
               male=dict(dirs=info["dirs"], mags=info["mags"], d_rate=r_m["d_rate"], baseline=r_m["baseline"], lptc_dv=r_m["lptc_dv"]),
               female=dict(dir=r_f["shift_dir"], mag=r_f["shift_mag"], d_rate=r_f["d_rate"]),
               control_points=dict(T=a.T, H=a.H, W=a.W), seconds=time.time() - t0)
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(res, indent=1, default=float))
        np.save(str(pathlib.Path(a.out).with_suffix(".z.npy")), z)
    if a.fig:
        panel(male, female, mov, r_m, r_f, info, a.fig, title="pixel-optimised stimulus on the male eye")
    return res


if __name__ == "__main__":
    main()
