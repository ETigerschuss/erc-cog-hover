"""Stage 7: controversial (adversarial) stimuli for the hoverfly models.

Two hypotheses about the male's third retinal muscle (MIO) differ only in its pull direction
θ_A and θ_B (anatomical frame; 0° = toward the antennae, 90° = dorsal). The predicted retinal-shift
vectors are v_X = v_MOT·u(θ_MOT) + v_MOS·u(θ_MOS) + v_MIO·u(θ_X), so they diverge most for stimuli
that drive the MIO strongly while leaving the common MOT/MOS term small. The search maximises the
angle between v_A and v_B subject to a minimum MIO modulation.

Search: parametric stimuli (K local grating patches on a grey or counter-moving background),
(1+λ) evolution strategy on a rate surrogate (motor-neuron Δrate = slope × Σ_j G_j ΔV_j from the
Ammer front end, slopes fitted to Tier-1 runs), then verification of the best stimulus with the
full Tier-1 Hodgkin–Huxley network, and the female model's prediction for the same stimulus.
A PyTorch pixel-level variant (gradient descent through the front end, as in ALIstim) plugs into
`objective_from_movie` once torch is available.
"""
from __future__ import annotations

import json
import pathlib
import time

import numpy as np

from .eye import grating_movie
from .oculomotor import angle_between, direction, falt_to_model, unit
from .species import Model

MIO_HYPOTHESES = {"MIO anterior (0°)": 0.0, "MIO dorsal (90°)": 90.0}
DURATION, ONSET = 1.0, 0.25

BOUNDS = {  # patch k: centre, radius, direction, speed, contrast; background grating
    "az": (-10.0, 120.0), "el": (-50.0, 60.0), "rad": (8.0, 40.0), "dir": (0.0, 360.0),
    "speed": (5.0, 80.0), "con": (0.0, 1.0), "bg_dir": (0.0, 360.0), "bg_speed": (5.0, 60.0), "bg_con": (0.0, 0.6),
}


def random_params(rng, k=2):
    p = {}
    for i in range(k):
        for key in ("az", "el", "rad", "dir", "speed", "con"):
            lo, hi = BOUNDS[key]
            p[f"{key}{i}"] = float(rng.uniform(lo, hi))
    for key in ("bg_dir", "bg_speed", "bg_con"):
        lo, hi = BOUNDS[key]
        p[key] = float(rng.uniform(lo, hi))
    return p


def clip_params(p):
    q = {}
    for k, v in p.items():
        base = k.rstrip("0123456789") if not k.startswith("bg") else k
        lo, hi = BOUNDS[base]
        q[k] = float(v % 360.0) if base in ("dir", "bg_dir") else float(np.clip(v, lo, hi))
    return q


def render(model: Model, p: dict, wavelength=20.0):
    """Movie (T, n_el, n_az): background grating plus K disc patches, each with its own grating."""
    A, E = np.meshgrid(model.az_grid, model.el_grid)
    mov = grating_movie(model.az_grid, model.el_grid, p["bg_dir"], p["bg_speed"], wavelength, DURATION,
                        model.dt_frame, contrast=p["bg_con"], onset=ONSET)
    k = 0
    while f"az{k}" in p:
        r = np.hypot(A - p[f"az{k}"], E - p[f"el{k}"])
        w = 1.0 / (1.0 + np.exp((r - p[f"rad{k}"]) / 2.0))
        patch = grating_movie(model.az_grid, model.el_grid, p[f"dir{k}"], p[f"speed{k}"], wavelength, DURATION,
                              model.dt_frame, contrast=p[f"con{k}"], onset=ONSET)
        mov = mov * (1 - w)[None] + patch * w[None]
        k += 1
    return mov


class Surrogate:
    """Δrate_MN ≈ s_MN · Σ_j G_{j,MN} ΔV_j, with ΔV_j the Ammer-membrane responses of the LPTCs."""

    def __init__(self, model: Model):
        self.model = model
        names, _, _, GJ = model.circuit
        self.W = {}
        for mn in model.motor_neurons:
            w = np.zeros(len(model.lptcs))
            for a, b, G, _ in GJ:
                a, b = int(a), int(b)
                for src, dst in ((a, b), (b, a)):
                    if names[dst] == mn and names[src] in model.lptcs:
                        w[model.lptcs.index(names[src])] += G
            self.W[mn] = w
        self.slope = {mn: 1.0 for mn in model.motor_neurons}

    def fit(self, runs):
        """runs: list of model.run() results (with ammer_dv and d_rate)."""
        for mn in self.model.motor_neurons:
            x = np.array([self.W[mn] @ np.array([r["ammer_dv"][n] for n in self.model.lptcs]) for r in runs])
            y = np.array([r["d_rate"][mn] for r in runs])
            self.slope[mn] = float((x @ y) / max(x @ x, 1e-9))
        return self.slope

    def predict(self, ammer_dv: dict) -> dict:
        v = np.array([ammer_dv[n] for n in self.model.lptcs])
        return {mn: self.slope[mn] * float(self.W[mn] @ v) for mn in self.model.motor_neurons}


def shift_vectors(d_rate: dict, baseline: dict, pull_common: dict, hyp: dict, beta=0.0) -> dict:
    """Retinal-shift vectors (model frame) for each MIO hypothesis."""
    base = np.zeros(2)
    for nm, th in pull_common.items():
        if nm in d_rate and nm != "MIO":
            base += d_rate[nm] / max(baseline[nm], 1e-6) * unit(th)
    out = {}
    for h, th in hyp.items():
        v = base.copy()
        if "MIO" in d_rate:
            v += d_rate["MIO"] / max(baseline["MIO"], 1e-6) * unit(float(falt_to_model(th, beta)))
        out[h] = v
    return out


def objective_from_rates(d_rate, baseline, model: Model, hyp=MIO_HYPOTHESES, min_mio_hz=10.0, min_mag=0.15):
    vecs = shift_vectors(d_rate, baseline, model.pull, hyp, model.arena_rotation)
    (ha, va), (hb, vb) = list(vecs.items())[:2]
    ang = angle_between(direction(va), direction(vb))
    mag = min(np.linalg.norm(va), np.linalg.norm(vb))
    d_mio = abs(d_rate.get("MIO", 0.0))
    score = ang * min(1.0, d_mio / min_mio_hz) * min(1.0, mag / min_mag)
    return score, dict(angle=ang, d_mio=d_mio, dirs={h: direction(v) for h, v in vecs.items()},
                       mags={h: float(np.linalg.norm(v)) for h, v in vecs.items()})


def evaluate_surrogate(model: Model, sur: Surrogate, p: dict, baseline: dict):
    mov = render(model, p)
    _, _, g = model.front_end(mov)
    T = mov.shape[0]
    fb = slice(int(ONSET / model.dt_frame) - 10, int(ONSET / model.dt_frame)); fr = slice(int(ONSET / model.dt_frame) + 12, T)
    ammer_dv = {nm: float(v[fr].mean() - v[fb].mean()) for nm, (_, _, v) in g.items()}
    d_rate = sur.predict(ammer_dv)
    score, info = objective_from_rates(d_rate, baseline, model)
    info["ammer_dv"] = ammer_dv; info["d_rate_pred"] = d_rate
    return score, info


SEED_PARAMS = {  # front-to-back motion on the male HSN field, counter-motion in the background
    "az0": 0.0, "el0": 25.0, "rad0": 15.0, "dir0": 0.0, "speed0": 30.0, "con0": 1.0,
    "az1": 60.0, "el1": -20.0, "rad1": 30.0, "dir1": 180.0, "speed1": 30.0, "con1": 0.3,
    "bg_dir": 180.0, "bg_speed": 20.0, "bg_con": 0.2,
}


def search(model: Model, sur: Surrogate, baseline: dict, generations=25, lam=6, k=2, seed=1, log=print, p0=None):
    rng = np.random.default_rng(seed)
    p = clip_params(p0) if p0 else (clip_params(SEED_PARAMS) if k == 2 else random_params(rng, k))
    best, info = evaluate_surrogate(model, sur, p, baseline)
    sigma = 0.25
    hist = [best]
    scale = {}
    for key in p:
        base = key.rstrip("0123456789") if not key.startswith("bg") else key
        lo, hi = BOUNDS[base]
        scale[key] = hi - lo
    for gen in range(generations):
        improved = False
        for _ in range(lam):
            q = {key: v + sigma * scale[key] * rng.standard_normal() for key, v in p.items()}
            q = clip_params(q)
            s, inf = evaluate_surrogate(model, sur, q, baseline)
            if s > best:
                best, p, info, improved = s, q, inf, True
        sigma = min(0.4, sigma * 1.3) if improved else max(0.03, sigma * 0.8)
        hist.append(best)
        log(f"  gen {gen + 1:2d}: score {best:6.1f}  angle {info['angle']:5.1f}°  MIO Δ {info['d_mio']:5.1f} Hz  σ {sigma:.2f}")
    return p, best, hist, info


def verify(model: Model, p: dict):
    mov = render(model, p)
    r = model.run(mov, onset_s=ONSET)
    score, info = objective_from_rates(r["d_rate"], r["baseline"], model)
    info.update(d_rate=r["d_rate"], baseline=r["baseline"], ammer_dv=r["ammer_dv"], lptc_dv=r["lptc_dv"])
    return score, info, r, mov


def tuning_runs(model: Model, dirs=range(0, 360, 60)):
    runs = []
    for d in dirs:
        mov = grating_movie(model.az_grid, model.el_grid, d, 30.0, 20.0, DURATION, model.dt_frame, onset=ONSET)
        runs.append(model.run(mov, onset_s=ONSET))
    return runs


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=25)
    ap.add_argument("--lam", type=int, default=6)
    ap.add_argument("--k", type=int, default=2)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--wvs", type=float, default=1.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--fig", default=None)
    ap.add_argument("--replot", default=None, help="JSON result of an earlier run: verify its stimulus and draw the panel only")
    a = ap.parse_args(argv)
    t0 = time.time()
    male = Model("eristalis", "male", mio_from="HSN", mio_pull=0.0, w_vs_mos=a.wvs)
    female = Model("eristalis", "female", w_vs_mos=a.wvs)
    if a.replot:
        prev = json.loads(pathlib.Path(a.replot).read_text())
        p = clip_params(prev["stimulus"])
        s_ver, info_v, r_m, mov = verify(male, p)
        r_f = female.run(mov, onset_s=ONSET)
        print(f"replot: angle {info_v['angle']:.1f}°, MIO Δ {info_v['d_mio']:.1f} Hz, dirs {info_v['dirs']}, female {r_f['shift_dir']:.1f}°")
        panel(male, female, mov, r_m, r_f, info_v, a.fig or "panel.png", params=p)
        return prev
    print(f"male: {male.eye.n} ommatidia, {male.eye.n_patch} circuits, cells {male.names}; female: {female.eye.n} ommatidia ({time.time() - t0:.0f} s)")
    runs = tuning_runs(male)
    baseline = {nm: float(np.mean([r["baseline"][nm] for r in runs])) for nm in male.motor_neurons}
    sur = Surrogate(male); print("surrogate slopes:", {k: round(v, 3) for k, v in sur.fit(runs).items()}, f"({time.time() - t0:.0f} s)")
    for r in runs[:3]:
        print("   check:", {k: round(v, 1) for k, v in r["d_rate"].items()}, "pred", {k: round(v, 1) for k, v in sur.predict(r["ammer_dv"]).items()})
    p, score, hist, info = search(male, sur, baseline, generations=a.gens, lam=a.lam, k=a.k, seed=a.seed)
    print("best (surrogate):", {k: round(v, 1) for k, v in p.items()}, f"angle {info['angle']:.1f}° ({time.time() - t0:.0f} s)")
    s_ver, info_v, r_m, mov = verify(male, p)
    print(f"seed-stimulus check: " + str({k: round(v, 1) for k, v in verify(male, clip_params(SEED_PARAMS))[1]["d_rate"].items()}))
    print(f"Tier-1 verification: angle {info_v['angle']:.1f}°, MIO Δ {info_v['d_mio']:.1f} Hz, dirs {info_v['dirs']}, Δrates {info_v['d_rate']}")
    r_f = female.run(mov, onset_s=ONSET)
    dir_f = r_f["shift_dir"]
    print(f"female prediction on the same stimulus: {dir_f:.1f}° (mag {r_f['shift_mag']:.2f}); Δrates {r_f['d_rate']}")
    res = dict(stimulus=p, score_surrogate=score, score_tier1=s_ver, history=hist, hypotheses=MIO_HYPOTHESES,
               male=dict(dirs=info_v["dirs"], mags=info_v["mags"], d_rate=info_v["d_rate"], baseline=info_v["baseline"],
                         lptc_dv=info_v["lptc_dv"], ammer_dv=info_v["ammer_dv"]),
               female=dict(dir=dir_f, mag=r_f["shift_mag"], d_rate=r_f["d_rate"], baseline=r_f["baseline"], lptc_dv=r_f["lptc_dv"]),
               surrogate_slopes=sur.slope, params=vars(a), seconds=time.time() - t0)
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(res, indent=1, default=float))
    if a.fig:
        panel(male, female, mov, r_m, r_f, info_v, a.fig, params=p)
    return res


def panel(male: Model, female: Model, mov, r_m, r_f, info, out_png, params=None, title="controversial stimulus on the male eye"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from .tier1_hh import DT
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), dpi=300, gridspec_kw=dict(width_ratios=[1.25, 1.2, 0.9]))
    # (1) stimulus snapshot on the eye with RF contours
    ax = axes[0]
    p = params or {}
    frame = mov[min(int((ONSET + 0.3) / male.dt_frame), mov.shape[0] - 1)]
    ax.imshow(frame, extent=[male.az_grid[0], male.az_grid[-1], male.el_grid[0], male.el_grid[-1]], origin="lower",
              cmap="gray", vmin=0, vmax=1, aspect="equal")
    A, E = np.meshgrid(male.az_grid, male.el_grid)
    for nm, col, ls in (("HSN", "#2F5597", "-"), ("HSNE", "#ad1457", "--"), ("HSE", "#c2185b", ":")):
        spec = next(s for s in male.front.specs if s.name == nm)
        ax.contour(A, E, spec.rf(A, E), levels=[0.5], colors=[col], linewidths=1.2, linestyles=ls)
    w_f = next(s for s in female.front.specs if s.name == "HSN").rf(A, E)
    ax.contour(A, E, w_f, levels=[0.5], colors=["#2F5597"], linewidths=1.0, linestyles="-.")
    k = 0
    while f"az{k}" in p:
        ax.annotate("", xy=(p[f"az{k}"] + 8 * np.cos(np.deg2rad(p[f"dir{k}"])), p[f"el{k}"] + 8 * np.sin(np.deg2rad(p[f"dir{k}"]))),
                    xytext=(p[f"az{k}"], p[f"el{k}"]), arrowprops=dict(arrowstyle="->", color="#ff9800", lw=1.8))
        k += 1
    if p.get("bg_con", 0.0) > 0.02:
        ax.annotate("", xy=(120 + 10 * np.cos(np.deg2rad(p["bg_dir"])), -60 + 10 * np.sin(np.deg2rad(p["bg_dir"]))),
                    xytext=(120, -60), arrowprops=dict(arrowstyle="->", color="#ff9800", lw=1.2))
    ax.set_xlim(-15, 150); ax.set_ylim(-70, 70)
    ax.set_xlabel("azimuth (°)", fontsize=8); ax.set_ylabel("elevation (°)", fontsize=8); ax.tick_params(labelsize=7)
    ax.set_title(title, fontsize=9)
    ax.legend(handles=[Line2D([], [], color="#2F5597", ls="-", label="HSN ♂"), Line2D([], [], color="#2F5597", ls="-.", label="HSN ♀"),
                       Line2D([], [], color="#ad1457", ls="--", label="HSNE"), Line2D([], [], color="#c2185b", ls=":", label="HSE")],
              fontsize=6, loc="lower right", frameon=True)
    # (2) LPTC responses and motor-neuron rates
    ax = axes[1]
    t = r_m["t"] / 1000.0
    k = np.ones(int(10.0 / DT)) / int(10.0 / DT)  # 10 ms boxcar for display (removes the spikelets)
    for nm, col in (("HSN", "#2F5597"), ("HSNE", "#ad1457"), ("HSE", "#c2185b"), ("VS2", "#2e7d32")):
        i = male.names.index(nm)
        v = np.convolve(r_m["V"][:, i] - r_m["V"][r_m["base"], i].mean(), k, mode="same")
        ax.plot(t, v, color=col, lw=0.9, label=nm)
    ax.set_ylabel("LPTC ΔV (mV, 10 ms smoothed)", fontsize=8); ax.set_xlabel("time (s)", fontsize=8); ax.tick_params(labelsize=7)
    ax.axvspan((male.pre_ms / 1000 + ONSET), (male.pre_ms / 1000 + DURATION), color="0.9", zorder=0)
    ax2 = ax.twinx()
    for nm, col in (("MOT", "#e65100"), ("MOS", "#6a1b9a"), ("MIO", "#000000")):
        ax2.plot(t, r_m["rates"][nm], color=col, lw=1.0, label=nm)
    ax2.set_ylabel("motor neuron rate (Hz)", fontsize=8); ax2.tick_params(labelsize=7)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=6, ncol=2, loc="upper left", frameon=False)
    ax.set_title("male circuit (Tier-1 HH network)", fontsize=9)
    # (3) predicted retinal shift directions
    ax = axes[2]
    vecs = shift_vectors(r_m["d_rate"], r_m["baseline"], male.pull, MIO_HYPOTHESES, male.arena_rotation)
    vecs["female (no MIO)"] = r_f["shift_vec"]
    cols = {"MIO anterior (0°)": "#1565c0", "MIO dorsal (90°)": "#c62828", "female (no MIO)": "#2e7d32"}
    m = max(np.linalg.norm(v) for v in vecs.values()) or 1.0
    for h, v in vecs.items():
        ax.annotate("", xy=(v[0] / m, v[1] / m), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=cols[h], lw=2.0))
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15); ax.set_aspect("equal")
    ax.axhline(0, color="0.8", lw=0.5); ax.axvline(0, color="0.8", lw=0.5)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(1.05, 0.03, "post.", fontsize=6, ha="right"); ax.text(-1.1, 0.03, "ant.", fontsize=6)
    ax.text(0.03, 1.0, "dorsal", fontsize=6); ax.text(-1.1, -1.08, "ventral", fontsize=6)
    ax.legend(handles=[Line2D([], [], color=c, lw=2, label=f"{h}: {direction(v):.0f}°") for h, v in vecs.items() for c in [cols[h]]],
              fontsize=6, loc="lower right", frameon=True)
    ax.set_title(f"predicted retinal shift ({info['angle']:.0f}° apart)", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_png)
    print("panel:", out_png)


if __name__ == "__main__":
    main()
