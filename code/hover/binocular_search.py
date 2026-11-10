"""Controversial stimulus between the male and the female hoverfly, both eyes.

Both sexes see the same binocular stimulus; the search maximises the difference between their
predicted retinal movements (four numbers per animal: anterior/medial and dorsal shift of the right
and of the left retina). The male model carries hypothesis H2: a median M. interocularis that pulls
both retinae toward the midline and is driven by HSN of both sides through the electrically coupled
HS network.

Stimulus family: two half-field background gratings (left and right of the midline) and K patches.
Each patch grating has a conjugate drift (same in both eyes) and, optionally, a disparity drift
(opposite in the two eyes: positive = front-to-back in both eyes, as for a surface that recedes).
`--single-screen` removes the disparity drift (one display, same image for both eyes).

    python -m hover.binocular_search --out r.json --fig panel.png [--single-screen]
"""
from __future__ import annotations

import json
import pathlib
import time

import numpy as np

from .binocular import PSI, BinocularModel, split_eyes
from .eye import grating_movie

HERE = pathlib.Path(__file__).resolve().parent
DURATION, ONSET = 1.0, 0.25
BOUNDS = {"psi": (-120.0, 120.0), "el": (-50.0, 60.0), "rad": (8.0, 40.0), "dir": (0.0, 360.0), "speed": (0.0, 60.0),
          "dspeed": (-40.0, 40.0), "con": (0.0, 1.0),
          "bgL_dir": (0.0, 360.0), "bgL_speed": (0.0, 60.0), "bgR_dir": (0.0, 360.0), "bgR_speed": (0.0, 60.0), "bg_con": (0.0, 0.6)}
SEED_DICHOPTIC = {  # a frontal patch whose disparity changes (front-to-back in both eyes), contracting surround
    "psi0": 0.0, "el0": 25.0, "rad0": 18.0, "dir0": 0.0, "speed0": 0.0, "dspeed0": 30.0, "con0": 1.0,
    "psi1": 70.0, "el1": -10.0, "rad1": 30.0, "dir1": 180.0, "speed1": 20.0, "dspeed1": 0.0, "con1": 0.3,
    "bgL_dir": 0.0, "bgL_speed": 20.0, "bgR_dir": 180.0, "bgR_speed": 20.0, "bg_con": 0.2}
SEED_SCREEN = {     # local expansion over the two HSN fields, contracting surround
    "psi0": 12.0, "el0": 25.0, "rad0": 12.0, "dir0": 0.0, "speed0": 30.0, "dspeed0": 0.0, "con0": 1.0,
    "psi1": -12.0, "el1": 25.0, "rad1": 12.0, "dir1": 180.0, "speed1": 30.0, "dspeed1": 0.0, "con1": 1.0,
    "bgL_dir": 0.0, "bgL_speed": 20.0, "bgR_dir": 180.0, "bgR_speed": 20.0, "bg_con": 0.2}


def _base(key):
    return key if key.startswith("bg") else key.rstrip("0123456789")


def clip(p, single_screen=False):
    q = {}
    for k, v in p.items():
        b = _base(k); lo, hi = BOUNDS[b]
        q[k] = float(v % 360.0) if b in ("dir", "bgL_dir", "bgR_dir") else float(np.clip(v, lo, hi))
        if single_screen and b == "dspeed":
            q[k] = 0.0
    return q


def render(bm: BinocularModel, p: dict, wavelength=20.0):
    """Returns (right-eye movie, left-eye movie, head-centred movies for display)."""
    el = bm.el_grid
    A, E = np.meshgrid(PSI, el)
    g = lambda d, s, c: grating_movie(PSI, el, d, s, wavelength, DURATION, bm.dt_frame, contrast=c, onset=ONSET)
    wR = (1.0 / (1.0 + np.exp(-PSI / 3.0)))[None, None, :]
    bg = g(p["bgL_dir"], p["bgL_speed"], p["bg_con"]) * (1 - wR) + g(p["bgR_dir"], p["bgR_speed"], p["bg_con"]) * wR
    HR, HL = bg.copy(), bg.copy()
    k = 0
    while f"psi{k}" in p:
        r = np.hypot(A - p[f"psi{k}"], E - p[f"el{k}"])
        w = (1.0 / (1.0 + np.exp((r - p[f"rad{k}"]) / 2.0)))[None]
        dv = p[f"dspeed{k}"] * np.cos(np.deg2rad(p[f"dir{k}"]))      # disparity drift along the grating normal
        HR = HR * (1 - w) + g(p[f"dir{k}"], p[f"speed{k}"] + dv, p[f"con{k}"]) * w
        HL = HL * (1 - w) + g(p[f"dir{k}"], p[f"speed{k}"] - dv, p[f"con{k}"]) * w
        k += 1
    mR, mL = split_eyes(HR, HL)
    return mR, mL, (HR, HL)


def evaluate(male: BinocularModel, female: BinocularModel, p: dict, female_weight=0.5):
    mR, mL, _ = render(male, p)
    rm = male.run(mR, mL, onset_s=ONSET)
    rf = female.run(mR, mL, onset_s=ONSET)
    diff = float(np.linalg.norm(rm["vec4"] - rf["vec4"]))
    score = diff - female_weight * float(np.linalg.norm(rf["vec4"]))
    return score, dict(diff=diff, male=rm, female=rf)


def search(male, female, p0, generations=18, lam=5, seed=1, single_screen=False, log=print, checkpoint=None):
    rng = np.random.default_rng(seed)
    p = clip(p0, single_screen)
    best, info = evaluate(male, female, p)
    scale = {k: BOUNDS[_base(k)][1] - BOUNDS[_base(k)][0] for k in p}
    sigma = 0.2
    hist = [best]
    for gen in range(generations):
        improved = False
        for _ in range(lam):
            q = clip({k: v + sigma * scale[k] * rng.standard_normal() for k, v in p.items()}, single_screen)
            s, inf = evaluate(male, female, q)
            if s > best:
                best, p, info, improved = s, q, inf, True
        sigma = min(0.4, sigma * 1.3) if improved else max(0.03, sigma * 0.8)
        hist.append(best)
        if checkpoint:   # the run can be finished from here with --replot or --resume
            pathlib.Path(checkpoint).write_text(json.dumps(dict(stimulus=p, history=hist, generation=gen + 1), indent=1))
        m, f = info["male"], info["female"]
        log(f"  gen {gen + 1:2d}: score {best:.3f}  diff {info['diff']:.3f}  male medial {m['medial']:+.3f} version {m['version']:+.3f} "
            f"| female medial {f['medial']:+.3f} version {f['version']:+.3f} | MIO {m['d_rate'].get('MIO', 0):+.1f} Hz  σ {sigma:.2f}")
    return p, best, hist, info


def summary(r):
    return dict(d_rate={k: float(v) for k, v in r["d_rate"].items()}, baseline={k: float(v) for k, v in r["baseline"].items()},
                shift_R=[float(x) for x in r["shift"]["R"]], shift_L=[float(x) for x in r["shift"]["L"]],
                medial=r["medial"], version=r["version"], dorsal=r["dorsal"],
                lptc_dv={k: float(v) for k, v in r["lptc_dv"].items()})


def panel(male, female, p, info, extra, out_png, title="controversial stimulus, male vs female"):
    """Three sub-panels: what each eye sees; motor-neuron modulation in both sexes; predicted retinal
    shifts of both eyes."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle, Patch
    INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d8d2"
    S1, S2, NEUT = "#2a78d6", "#eb6834", "#8a8983"     # male, female, male with the MIO cut
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
    fig = plt.figure(figsize=(10.5, 3.2), dpi=300)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.15, 1.0, 1.25], hspace=0.12, wspace=0.28,
                          left=0.05, right=0.985, top=0.9, bottom=0.14)
    # (1) what each eye sees: frontal field in head coordinates
    _, _, (HR, HL) = render(male, p)
    fi = min(int((ONSET + 0.3) / male.dt_frame), HR.shape[0] - 1)
    A, E = np.meshgrid(PSI, male.el_grid)
    spec_m = next(s for s in male.eye_model.front.specs if s.name == "HSN")
    spec_f = next(s for s in female.eye_model.front.specs if s.name == "HSN")
    for row, (eye, H, sgn) in enumerate((("left eye", HL, -1.0), ("right eye", HR, +1.0))):
        ax = fig.add_subplot(gs[row, 0])
        ax.imshow(H[fi], extent=[PSI[0], PSI[-1], male.el_grid[0], male.el_grid[-1]], origin="lower", cmap="gray",
                  vmin=0, vmax=1, aspect="auto")
        ax.contour(A, E, spec_m.rf(sgn * A, E), levels=[0.5], colors=[S1], linewidths=1.4)
        ax.contour(A, E, spec_f.rf(sgn * A, E), levels=[0.5], colors=[S2], linewidths=1.0, linestyles="--")
        k = 0
        while f"psi{k}" in p:
            dv = p[f"dspeed{k}"] * np.cos(np.deg2rad(p[f"dir{k}"]))
            v = p[f"speed{k}"] + sgn * dv
            if abs(v) > 1.0 and p[f"con{k}"] > 0.05:
                d = np.deg2rad(p[f"dir{k}"]) + (np.pi if v < 0 else 0.0)
                ax.annotate("", xy=(p[f"psi{k}"] + 11 * np.cos(d), p[f"el{k}"] + 11 * np.sin(d)), xytext=(p[f"psi{k}"], p[f"el{k}"]),
                            arrowprops=dict(arrowstyle="-|>", color="#ffd400", lw=1.6, mutation_scale=9))
            k += 1
        ax.axvline(0, color="white", lw=0.5, ls=":")
        ax.set_xlim(-75, 75); ax.set_ylim(-45, 70)
        ax.text(-72, 62, eye, color=INK, fontsize=7, va="top", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
        ax.set_ylabel("elevation (°)", fontsize=7); ax.tick_params(labelsize=6.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(True)
        if row == 0:
            ax.set_xticklabels([]); ax.set_title(title, loc="left", fontsize=9, color=INK)
            ax.legend(handles=[Line2D([], [], color=S1, lw=1.4, label="HSN field ♂"), Line2D([], [], color=S2, lw=1.0, ls="--", label="HSN field ♀")],
                      fontsize=5.5, loc="lower right", frameon=True, framealpha=0.85, borderpad=0.3, handlelength=1.6)
        else:
            ax.set_xlabel("azimuth in head coordinates (°)", fontsize=7)
    # (2) motor-neuron modulation
    ax = fig.add_subplot(gs[:, 1])
    m, f = info["male"], info["female"]
    labels = ["MOT\nleft", "MOT\nright", "MOS\nleft", "MOS\nright", "MIO"]
    keys = ["MOT_L", "MOT_R", "MOS_L", "MOS_R", "MIO"]
    x = np.arange(len(keys)); wbar = 0.36
    mv = [m["d_rate"].get(k, 0.0) for k in keys]; fv = [f["d_rate"].get(k, np.nan) for k in keys]
    ax.bar(x - wbar / 2, mv, wbar, color=S1, edgecolor="white", linewidth=1.0, label="male")
    ax.bar(x + wbar / 2, np.nan_to_num(fv), wbar, color=S2, edgecolor="white", linewidth=1.0, label="female")
    ax.text(x[-1] + wbar / 2, 0.6, "no\nmuscle", ha="center", va="bottom", fontsize=5.5, color=MUTED)
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=6.5)
    ax.set_ylabel("motor-neuron rate change (Hz)", fontsize=7); ax.tick_params(axis="y", labelsize=6.5)
    ax.grid(axis="y", color=GRID, lw=0.4); ax.set_axisbelow(True)
    ax.legend(fontsize=6.5, frameon=False, loc="upper left")
    ax.set_title("retinal motor neurons (Tier-1 network)", loc="left", fontsize=9, color=INK)
    # (3) predicted retinal shifts of both eyes, seen from behind the animal
    ax = fig.add_subplot(gs[:, 2])
    cx = {"L": -1.25, "R": 1.25}
    sets = [("male", m["shift"], S1, "-"), ("female", f["shift"], S2, "-"), ("male, MIO cut", extra["male_cut"], NEUT, (0, (3, 2)))]
    mx = max(max(np.linalg.norm(v[s]) for s in ("R", "L")) for _, v, _, _ in sets) or 1.0
    for side in ("L", "R"):
        ax.add_patch(Circle((cx[side], 0), 1.0, fill=False, ec=GRID, lw=1.0))
        ax.plot([cx[side] - 1, cx[side] + 1], [0, 0], color=GRID, lw=0.5); ax.plot([cx[side], cx[side]], [-1, 1], color=GRID, lw=0.5)
        ax.text(cx[side], -1.22, "left eye" if side == "L" else "right eye", ha="center", va="top", fontsize=7, color=INK)
        sx = 1.0 if side == "L" else -1.0                       # medial is toward the midline between the eyes
        for name, vec, col, ls in sets:
            a, d = vec[side]
            ax.annotate("", xy=(cx[side] + sx * a / mx * 0.95, d / mx * 0.95), xytext=(cx[side], 0),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=2.0, mutation_scale=9, ls=ls))
    ax.plot([0, 0], [-1.05, 1.05], color=MUTED, lw=0.6, ls=":")
    ax.text(0, 1.1, "midline", ha="center", va="bottom", fontsize=6.5, color=MUTED)
    ax.text(cx["L"] - 1.02, 0.05, "lateral", ha="left", va="bottom", fontsize=5.5, color=MUTED)
    ax.text(cx["R"] + 1.02, 0.05, "lateral", ha="right", va="bottom", fontsize=5.5, color=MUTED)
    ax.text(cx["L"] + 0.04, 0.98, "dorsal", ha="left", va="top", fontsize=5.5, color=MUTED)
    ax.set_xlim(-2.35, 2.35); ax.set_ylim(-1.75, 1.3); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.legend(handles=[Line2D([], [], color=c, lw=2, ls=ls, label=n) for n, _, c, ls in sets], fontsize=6.5, frameon=False,
              loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.04), handlelength=2.2, columnspacing=1.2)
    ax.set_title("predicted retinal shift of each eye", loc="left", fontsize=9, color=INK)
    fig.savefig(out_png)
    print("panel:", out_png)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=18)
    ap.add_argument("--lam", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--single-screen", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--fig", default=None)
    ap.add_argument("--replot", default=None, help="JSON of an earlier run: re-evaluate its stimulus and draw the panel")
    ap.add_argument("--resume", default=None, help="checkpoint JSON to continue the search from")
    a = ap.parse_args(argv)
    t0 = time.time()
    male = BinocularModel("eristalis", "male", mio="median")
    female = BinocularModel("eristalis", "female")
    print(f"models ready ({time.time() - t0:.0f} s)", flush=True)
    if a.replot:
        prev = json.loads(pathlib.Path(a.replot).read_text())
        p = clip(prev["stimulus"]); score, info = evaluate(male, female, p); hist = prev.get("history", [])
    else:
        p0 = json.loads(pathlib.Path(a.resume).read_text())["stimulus"] if a.resume else (SEED_SCREEN if a.single_screen else SEED_DICHOPTIC)
        p, score, hist, info = search(male, female, p0, generations=a.gens, lam=a.lam, seed=a.seed, single_screen=a.single_screen,
                                      log=lambda s: print(s, flush=True),
                                      checkpoint=(str(pathlib.Path(a.out).with_suffix(".ckpt.json")) if a.out else None))
    mR, mL, _ = render(male, p)
    m = info["male"]
    w = m["d_rate"]["MIO"] / m["baseline"]["MIO"]
    cut = {s: m["shift"][s] - w * np.array([np.cos(np.deg2rad(male.mio_pull)), np.sin(np.deg2rad(male.mio_pull))]) for s in ("R", "L")}
    cut4 = np.array([cut["R"][0], cut["R"][1], cut["L"][0], cut["L"][1]])
    indep = BinocularModel("eristalis", "male", mio="independent").run(mR, mL, onset_s=ONSET)
    res = dict(stimulus=p, single_screen=bool(a.single_screen), score=score, diff=info["diff"], history=hist,
               male=summary(info["male"]), female=summary(info["female"]), male_independent=summary(indep),
               male_mio_cut=dict(shift_R=cut["R"].tolist(), shift_L=cut["L"].tolist(),
                                 diff_to_female=float(np.linalg.norm(cut4 - info["female"]["vec4"]))),
               fraction_of_difference_due_to_mio=float(1.0 - np.linalg.norm(cut4 - info["female"]["vec4"]) / max(info["diff"], 1e-9)),
               seconds=time.time() - t0)
    print(json.dumps({k: v for k, v in res.items() if k not in ("history", "male", "female", "male_independent")}, indent=1, default=float), flush=True)
    for lab in ("male", "female", "male_independent"):
        r = res[lab]
        print(f"{lab:17s}: medial {r['medial']:+.3f} version {r['version']:+.3f} dorsal {r['dorsal']:+.3f} | Δrates "
              + " ".join(f"{k}:{v:+.1f}" for k, v in r["d_rate"].items()), flush=True)
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(res, indent=1, default=float))
    if a.fig:
        panel(male, female, p, info, dict(male_cut=cut), a.fig)
    return res


if __name__ == "__main__":
    main()
