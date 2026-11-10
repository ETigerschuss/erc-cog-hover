"""MIO pull direction as a free parameter on the full circle (12 hypotheses, 30° apart).

The MIO is a fan-shaped (radial) muscle, so its net pull direction cannot be read off a single
fibre orientation. With n hypotheses θ_k the predicted retinal shifts are v_k = c + w·u(θ_k), where
c is the common MOT/MOS term and w the MIO weight. The n predictions are distinguishable exactly
when the stimulus isolates the MIO: ρ = |c|/|w| < 1 makes the predicted directions wind once around
the circle, and ρ → 0 makes the measured shift direction equal the pull direction itself. The
design objective therefore changes from "largest angle between two hypotheses" to "smallest ρ at a
sufficient MIO drive": an MIO-isolating stimulus that reads out θ directly.

    python -m hover.mio_ring --out ring.json --fig fig_mio_ring.png
"""
from __future__ import annotations

import json
import pathlib
import time

import numpy as np

from .adversarial import (BOUNDS, DURATION, ONSET, SEED_PARAMS, Surrogate, clip_params, render, shift_vectors,
                          tuning_runs)
from .oculomotor import angle_between, direction, model_to_falt, unit
from .species import Model

HERE = pathlib.Path(__file__).resolve().parent


def ring(n=12):
    return {f"{int(round(k * 360 / n))}°": k * 360.0 / n for k in range(n)}


def isolation(d_rate, baseline, model: Model):
    """Common term c (model frame), MIO weight w, ρ = |c|/|w|."""
    c = np.zeros(2)
    for nm in ("MOT", "MOS"):
        if nm in d_rate:
            c = c + d_rate[nm] / max(baseline[nm], 1e-6) * unit(model.pull[nm])
    w = d_rate.get("MIO", 0.0) / max(baseline.get("MIO", 1.0), 1e-6)
    return c, float(w), float(np.linalg.norm(c) / max(abs(w), 1e-9))


def ring_report(d_rate, baseline, model: Model, n=12):
    """Predicted shift direction (anatomical frame) for each of n pull directions, and how well the
    hypotheses separate."""
    hyp = ring(n)
    vecs = shift_vectors(d_rate, baseline, model.pull, hyp, model.arena_rotation)
    th = np.array(list(hyp.values()))
    dirs = np.array([float(model_to_falt(direction(v), model.arena_rotation)) for v in vecs.values()])
    mags = np.array([float(np.linalg.norm(v)) for v in vecs.values()])
    sep = np.array([angle_between(dirs[i], dirs[(i + 1) % n]) for i in range(n)])
    err = np.array([(d - t + 180) % 360 - 180 for d, t in zip(dirs, th)])
    c, w, rho = isolation(d_rate, baseline, model)
    return dict(theta=th.tolist(), shift_dir=dirs.tolist(), shift_mag=mags.tolist(), adjacent_sep=sep.tolist(),
                min_sep=float(sep.min()), max_abs_error=float(np.abs(err).max()), rho=rho, w=w,
                c_dir=float(model_to_falt(direction(c), model.arena_rotation)), c_mag=float(np.linalg.norm(c)),
                d_rate={k: float(v) for k, v in d_rate.items()})


def score_isolation(d_rate, baseline, model: Model, min_mio_hz=10.0):
    _, _, rho = isolation(d_rate, baseline, model)
    return 1.0 / (1.0 + rho) * min(1.0, abs(d_rate.get("MIO", 0.0)) / min_mio_hz), rho


def _front_dv(model: Model, mov, onset_frames):
    _, _, g = model.front_end(mov)
    T = mov.shape[0]
    fb = slice(onset_frames - 10, onset_frames); fr = slice(onset_frames + 12, T)
    return {nm: float(v[fr].mean() - v[fb].mean()) for nm, (_, _, v) in g.items()}


def es_isolating(model: Model, sur: Surrogate, baseline, starts, generations=15, lam=5, seed=3, log=print):
    rng = np.random.default_rng(seed)
    scale = {}
    best_all = None
    for si, p0 in enumerate(starts):
        p = clip_params(p0)
        for key in p:
            base = key.rstrip("0123456789") if not key.startswith("bg") else key
            lo, hi = BOUNDS[base]; scale[key] = hi - lo
        d = sur.predict(_front_dv(model, render(model, p), int(ONSET / model.dt_frame)))
        best, rho = score_isolation(d, baseline, model)
        sigma = 0.2
        for gen in range(generations):
            improved = False
            for _ in range(lam):
                q = clip_params({k: v + sigma * scale[k] * rng.standard_normal() for k, v in p.items()})
                d = sur.predict(_front_dv(model, render(model, q), int(ONSET / model.dt_frame)))
                s, r = score_isolation(d, baseline, model)
                if s > best:
                    best, rho, p, improved = s, r, q, True
            sigma = min(0.4, sigma * 1.3) if improved else max(0.03, sigma * 0.8)
            if (gen + 1) % 5 == 0:
                log(f"  start {si} gen {gen + 1:2d}: score {best:.3f}  rho {rho:.2f}  σ {sigma:.2f}")
        if best_all is None or best > best_all[0]:
            best_all = (best, rho, p)
    return best_all[2], best_all[0], best_all[1]


def pixel_isolating(model: Model, sur: Surrogate, baseline, z0, steps=30, lr=0.1, min_mio_hz=10.0, log=print):
    """Gradient descent on the control-point movie: minimise ρ² at a sufficient MIO drive."""
    import autograd.numpy as anp
    from autograd import value_and_grad
    from .frontend_ad import DifferentiableFrontEnd, adam
    fe = DifferentiableFrontEnd(model, sur, T_lr=z0.shape[0], rep=4, H_lr=z0.shape[1], W_lr=z0.shape[2], fix_frames=24)
    pull = model.pull

    def loss(z):
        dv, mov = fe.responses(z)
        d = fe.motor(dv)
        c = anp.zeros(2)
        for nm in ("MOT", "MOS"):
            c = c + d[nm] / baseline[nm] * anp.array([np.cos(np.deg2rad(pull[nm])), np.sin(np.deg2rad(pull[nm]))])
        w = d["MIO"] / baseline["MIO"]
        rho2 = anp.dot(c, c) / (w * w + 1e-4)
        drive = anp.maximum(0.0, 1.0 - d["MIO"] / min_mio_hz)       # want a positive MIO modulation ≥ min_mio_hz
        return rho2 + 2.0 * drive + 0.02 * anp.mean(anp.abs(mov - 0.5)) * 2
    z, l = adam(value_and_grad(loss), z0, steps=steps, lr=lr, log=log)
    return np.asarray(fe.movie(z)), z, float(l)


def figure(model: Model, female: Model, best, reports, out_png):
    """Three panels: the MIO-isolating stimulus, the 12 predicted shifts, and predicted shift direction
    against pull direction for the stimuli compared."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d8d2"
    S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"       # categorical slots 1–3 (validated all-pairs)
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.5), dpi=300, gridspec_kw=dict(width_ratios=[1.2, 1.0, 1.15]))
    # (a) stimulus
    ax = axes[0]
    mov = best["movie"]
    frame = mov[min(int(best["onset_frames"] + 0.3 / model.dt_frame), mov.shape[0] - 1)]
    ax.imshow(frame, extent=[model.az_grid[0], model.az_grid[-1], model.el_grid[0], model.el_grid[-1]], origin="lower",
              cmap="gray", vmin=0, vmax=1, aspect="equal")
    A, E = np.meshgrid(model.az_grid, model.el_grid)
    hsn_m = next(s for s in model.front.specs if s.name == "HSN").rf(A, E)
    hsn_f = next(s for s in female.front.specs if s.name == "HSN").rf(A, E)
    ax.contour(A, E, hsn_m, levels=[0.5], colors=[S1], linewidths=1.6)
    ax.contour(A, E, hsn_f, levels=[0.5], colors=["white"], linewidths=1.0, linestyles="--")
    ax.text(12, 44, "HSN ♂", color="white", fontsize=7, ha="left", va="bottom",
            bbox=dict(boxstyle="round,pad=0.15", fc=S1, ec="none"))
    ax.text(-13, -6, "HSN ♀", color=INK, fontsize=7, ha="left", va="top",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    ax.set_xlim(-15, 150); ax.set_ylim(-70, 70)
    ax.set_xlabel("azimuth (°)"); ax.set_ylabel("elevation (°)")
    ax.set_title("a  MIO-isolating stimulus on the male eye", loc="left", fontsize=9, color=INK)
    for s in ("top", "right"):
        ax.spines[s].set_visible(True)
    # (b) twelve predicted shifts
    ax = axes[1]
    rep = reports[best["label"]]
    th = np.deg2rad(rep["theta"]); sd = np.deg2rad(rep["shift_dir"]); m = np.array(rep["shift_mag"])
    scale = 1.0 / max(m.max(), 1e-9)
    for t in np.deg2rad(np.arange(0, 360, 30)):          # ideal directions, recessive
        ax.plot([0, 1.18 * np.cos(t)], [0, 1.18 * np.sin(t)], color=GRID, lw=0.6, zorder=0)
    ax.add_patch(plt.Circle((0, 0), abs(rep["w"]) * scale, fill=False, ec=GRID, lw=0.8, ls="--", zorder=0))
    for k in range(len(th)):
        x, y = m[k] * scale * np.cos(sd[k]), m[k] * scale * np.sin(sd[k])
        ax.annotate("", xy=(x, y), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=S1, lw=1.4, mutation_scale=8))
        ax.text(1.13 * x + 0.02 * np.sign(x), 1.13 * y, f"{int(rep['theta'][k])}°", ha="center", va="center", fontsize=6.5, color=INK)
    cx, cy = rep["c_mag"] * scale * np.cos(np.deg2rad(rep["c_dir"])), rep["c_mag"] * scale * np.sin(np.deg2rad(rep["c_dir"]))
    ax.annotate("", xy=(cx, cy), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=S2, lw=2.0, mutation_scale=9))
    f = best["female"]
    fx, fy = f["mag"] * scale * np.cos(np.deg2rad(f["dir"])), f["mag"] * scale * np.sin(np.deg2rad(f["dir"]))
    ax.annotate("", xy=(fx, fy), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=S3, lw=2.0, mutation_scale=9))
    ax.set_xlim(-1.65, 1.65); ax.set_ylim(-1.55, 1.55); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.text(1.62, -0.14, "anterior\n(medial)", ha="right", va="top", fontsize=6.5, color=MUTED)
    ax.text(-1.62, -0.14, "posterior\n(lateral)", ha="left", va="top", fontsize=6.5, color=MUTED)
    ax.text(0.12, 1.5, "dorsal", ha="left", va="top", fontsize=6.5, color=MUTED)
    ax.text(0.12, -1.5, "ventral", ha="left", va="bottom", fontsize=6.5, color=MUTED)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color=S1, lw=1.6, label="male, MIO pull direction (label)"),
                       Line2D([], [], color=S2, lw=2.0, label="MOT + MOS term"),
                       Line2D([], [], color=S3, lw=2.0, label="female (no MIO)")],
              fontsize=6, loc="upper left", bbox_to_anchor=(-0.08, -0.02), frameon=False, ncol=1)
    ax.set_title("b  predicted retinal shift, 12 pull directions", loc="left", fontsize=9, color=INK)
    # (c) shift direction vs pull direction
    ax = axes[2]
    ax.plot([0, 330], [0, 330], color=MUTED, lw=1.0, ls=(0, (4, 3)), zorder=1, label="shift = pull (perfect isolation)")
    for (label, r), col, mk in zip(reports.items(), (S1, S2, S3), ("o", "s", "^")):
        t = np.array(r["theta"]); d = np.array(r["shift_dir"])
        y = t + ((d - t + 180) % 360 - 180)
        ax.plot(t, y, color=col, lw=2.0, marker=mk, ms=4.5, mec="white", mew=0.6, label=f"{label} (ρ = {r['rho']:.2f})")
    ax.set_xticks(range(0, 360, 60)); ax.set_yticks(range(0, 361, 60))
    ax.set_xlabel("MIO pull direction (°; 0° anterior, 90° dorsal)"); ax.set_ylabel("predicted retinal-shift direction (°)")
    ax.grid(color=GRID, lw=0.4); ax.set_axisbelow(True)
    ax.set_ylim(-40, 400)
    ax.legend(fontsize=6.5, loc="upper left", frameon=False)
    ax.set_title("c  how directly the shift reads out the pull", loc="left", fontsize=9, color=INK)
    fig.tight_layout()
    fig.savefig(out_png)
    print("figure:", out_png)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=15)
    ap.add_argument("--pixel-steps", type=int, default=30)
    ap.add_argument("--z0", default=None, help=".npy control-point movie to start the pixel search from")
    ap.add_argument("--out", default=str(HERE / "mio_ring_result.json"))
    ap.add_argument("--fig", default=None)
    ap.add_argument("--replot", action="store_true", help="redraw from the saved result (no search)")
    a = ap.parse_args(argv)
    t0 = time.time()
    male = Model("eristalis", "male", mio_from="HSN", mio_pull=0.0)
    female = Model("eristalis", "female")
    runs = tuning_runs(male)
    baseline = {nm: float(np.mean([r["baseline"][nm] for r in runs])) for nm in male.motor_neurons}
    sur = Surrogate(male); sur.fit(runs)
    print(f"models and surrogate ready ({time.time() - t0:.0f} s)", flush=True)
    reports, cands = {}, {}
    # the two pairwise-optimised stimuli of Fig. B1g / design doc §3b
    prev = json.loads((HERE / "adversarial_result.json").read_text())
    mov = render(male, clip_params(prev["stimulus"]))
    r = male.run(mov, onset_s=ONSET)
    reports["pairwise, parametric"] = ring_report(r["d_rate"], r["baseline"], male)
    cands["pairwise, parametric"] = dict(movie=mov, onset_frames=int(ONSET / male.dt_frame), run=r)
    z_prev = np.load(a.z0) if a.z0 else None
    if z_prev is not None:
        from .frontend_ad import DifferentiableFrontEnd
        fe = DifferentiableFrontEnd(male, sur, T_lr=z_prev.shape[0], rep=4, H_lr=z_prev.shape[1], W_lr=z_prev.shape[2], fix_frames=24)
        mov = np.asarray(fe.movie(z_prev))
        r = male.run(mov, onset_s=24 * male.dt_frame)
        reports["pairwise, pixel"] = ring_report(r["d_rate"], r["baseline"], male)
        cands["pairwise, pixel"] = dict(movie=mov, onset_frames=24, run=r)
    for k, v in reports.items():
        print(f"{k}: rho {v['rho']:.2f}, min adjacent separation {v['min_sep']:.1f}°, max |shift − pull| {v['max_abs_error']:.0f}°, Δrates {v['d_rate']}", flush=True)
    # MIO-isolating searches
    saved = json.loads(pathlib.Path(a.out).read_text()) if a.replot else None
    if saved:
        p = saved["params"]
    else:
        p, s, rho = es_isolating(male, sur, baseline, [SEED_PARAMS, prev["stimulus"]], generations=a.gens,
                                 log=lambda m: print(m, flush=True))
    mov = render(male, p)
    r = male.run(mov, onset_s=ONSET)
    iso = {"parametric": dict(movie=mov, onset_frames=int(ONSET / male.dt_frame), run=r, params=p)}
    print(f"isolating, parametric (Tier-1): {ring_report(r['d_rate'], r['baseline'], male)['rho']:.2f}, Δrates {r['d_rate']} ({time.time() - t0:.0f} s)", flush=True)
    z_saved = pathlib.Path(a.out).with_suffix(".z.npy")
    if saved and z_saved.exists():
        from .frontend_ad import DifferentiableFrontEnd
        z = np.load(z_saved)
        fe = DifferentiableFrontEnd(male, sur, T_lr=z.shape[0], rep=4, H_lr=z.shape[1], W_lr=z.shape[2], fix_frames=24)
        mov = np.asarray(fe.movie(z))
        r = male.run(mov, onset_s=24 * male.dt_frame)
        iso["pixel"] = dict(movie=mov, onset_frames=24, run=r, z=z)
    elif z_prev is not None and a.pixel_steps > 0:
        mov, z, l = pixel_isolating(male, sur, baseline, z_prev, steps=a.pixel_steps, log=lambda m: print(m, flush=True))
        r = male.run(mov, onset_s=24 * male.dt_frame)
        iso["pixel"] = dict(movie=mov, onset_frames=24, run=r, z=z)
        print(f"isolating, pixel (Tier-1): {ring_report(r['d_rate'], r['baseline'], male)['rho']:.2f}, Δrates {r['d_rate']} ({time.time() - t0:.0f} s)", flush=True)
    # choose the isolating stimulus with the smallest Tier-1 ρ among those with ΔMIO ≥ 8 Hz
    ok = {k: v for k, v in iso.items() if abs(v["run"]["d_rate"]["MIO"]) >= 8.0} or iso
    pick = min(ok, key=lambda k: ring_report(ok[k]["run"]["d_rate"], ok[k]["run"]["baseline"], male)["rho"])
    best = iso[pick]; label = f"MIO-isolating ({pick})"
    reports[label] = ring_report(best["run"]["d_rate"], best["run"]["baseline"], male)
    rf = female.run(best["movie"], onset_s=best["onset_frames"] * male.dt_frame)
    best.update(label=label, female=dict(dir=float(model_to_falt(rf["shift_dir"])), mag=rf["shift_mag"], d_rate=rf["d_rate"]))
    print(f"{label}: rho {reports[label]['rho']:.2f}, min adjacent separation {reports[label]['min_sep']:.1f}°, "
          f"max |shift − pull| {reports[label]['max_abs_error']:.0f}°; female {best['female']['dir']:.0f}° (mag {best['female']['mag']:.2f})", flush=True)
    res = dict(reports=reports, picked=pick, female=best["female"], params=iso["parametric"].get("params"),
               baseline=baseline, seconds=time.time() - t0)
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1, default=float))
    if "z" in best:
        np.save(str(pathlib.Path(a.out).with_suffix(".z.npy")), best["z"])
    if a.fig:
        figure(male, female, best, reports, a.fig)
    return res


if __name__ == "__main__":
    main()
