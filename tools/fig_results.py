"""Figure 2 of Part B1: the three results that say what the project is about.

a  two stimuli for one bowl display: matched (same predicted retinal movement in both sexes) and
   love spot (different), with the male model after cutting the third muscle
b  where on the display the sexes differ (a small grating patch at every position)
c  event camera: how far the sensor should move depends on the task

Data: code/hover/bowl_result.json (python -m hover.bowl), code/hover/eventcam_result.json
(python -m hover.eventcam).   Usage: python3 tools/fig_results.py
"""
import json

import numpy as np
from matplotlib import patheffects as pe
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

import figstyle as fs
from figstyle import FEMALE, GRID, INK, INK2, INK3, MALE, MALE_L

CODE = fs.ROOT / "code" / "hover"
HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
YELLOW = "#ffcf33"


def stimulus_frame(kind):
    from hover import bowl
    from hover.binocular import PSI
    from hover.eye import grid
    el = grid()[1]
    if kind == "matched":
        mv = bowl.bowl_stimulus(el, 270.0)
    else:
        mv = bowl.bowl_stimulus(el, 90.0, aperture=bowl.LOVE_SPOT)
    return PSI, el, mv[45], bowl


def draw_stimulus(ax, kind):
    psi, el, frame, bowl = stimulus_frame(kind)
    ax.imshow(frame, cmap="gray", vmin=0, vmax=1, origin="lower", extent=(psi[0], psi[-1], el[0], el[-1]),
              interpolation="bilinear", aspect="equal")
    ax.set_xlim(-100, 100); ax.set_ylim(-60, 80)
    x0, x1 = bowl.BOWL_AZ; y0, y1 = bowl.BOWL_EL
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=14", fc="none", ec=INK2, lw=0.6))
    c = Circle(bowl.LOVE_SPOT[:2], bowl.LOVE_SPOT[2], fc="none", ec=YELLOW, lw=1.1, ls=(0, (3, 1.6)))
    c.set_path_effects([pe.withStroke(linewidth=2.0, foreground=INK)])
    ax.add_patch(c)
    up = kind != "matched"
    xa = -66 if not up else 44
    ya = (30, -22) if not up else (4, 50)
    arr = FancyArrowPatch((xa, ya[0]), (xa, ya[1]), arrowstyle="-|>,head_length=3.2,head_width=2.0", lw=1.6, color=YELLOW, shrinkA=0, shrinkB=0)
    arr.set_path_effects([pe.withStroke(linewidth=3.0, foreground=INK)])
    ax.add_patch(arr)
    ax.set_xticks([-90, 0, 90]); ax.set_yticks([-50, 0, 50])
    ax.tick_params(length=2, pad=1.5)
    for s in ax.spines.values():
        s.set_visible(False)


def draw_bars(ax, d, ymax=0.32, ylabel=True, note=None):
    vals = [d["amp_female"], d["amp_male"], d["amp_male_cut"]]
    x = [0, 1, 2.15]
    ax.bar(x[0], vals[0], width=0.72, color=FEMALE, lw=0)
    ax.bar(x[1], vals[1], width=0.72, color=MALE, lw=0)
    ax.bar(x[2], vals[2], width=0.72, color="white", ec=MALE, lw=1.0, hatch="////")
    ax.set_xticks(x); ax.set_xticklabels(["female", "male", "male, third\nmuscle cut"], fontsize=fs.F_SMALL, linespacing=0.95)
    ax.tick_params(axis="x", length=0, pad=2)
    ax.set_ylim(0, ymax); ax.set_yticks([0, 0.1, 0.2, 0.3]); ax.set_xlim(-0.6, 2.75)
    ax.yaxis.grid(True, color=GRID, lw=0.5); ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    if ylabel:
        ax.set_ylabel("retinal movement\n(model, rel. units)", fontsize=fs.F_SMALL, labelpad=2)
    else:
        ax.set_yticklabels([])
    if note:
        ax.text(0.5, max(vals[:2]) + 0.022, note, ha="center", va="bottom", fontsize=fs.F_BASE, fontweight="semibold", color=INK)


def panel_two_stimuli(fig, x0, y0, res, w=31.0, gap=6.5):
    """Two thumbnails with bars below. x0, y0 in mm (top-left of the panel content)."""
    ts = res["two_stimuli"]
    h_im = w * 140.0 / 200.0
    for k, (key, title, dx) in enumerate((("matched", "Matched stimulus", 0.0), ("love_spot", "Love-spot stimulus", w + gap))):
        fs.label(fig, x0 + dx, y0, title, fontsize=fs.F_BASE, fontweight="semibold")
        sub = "full-field square-wave grating" if key == "matched" else "the grating only in the love spot"
        fs.label(fig, x0 + dx, y0 + 3.4, sub, fontsize=fs.F_SMALL, color=INK2)
        ax = fs.axes_mm(fig, x0 + dx, y0 + 7.4, w, h_im)
        draw_stimulus(ax, key)
        if k == 0:
            ax.set_ylabel("elevation (°)", fontsize=fs.F_SMALL, labelpad=1)
        else:
            ax.set_yticklabels([])
        ax.set_xlabel("azimuth on the display (°)", fontsize=fs.F_SMALL, labelpad=1)
        axb = fs.axes_mm(fig, x0 + dx, y0 + 7.4 + h_im + 10.5, w, 16.0)
        d = ts[key]
        note = "same" if key == "matched" else f"{d['ratio']:.1f}×"
        draw_bars(axb, d, ylabel=(k == 0), note=note)


def panel_map(fig, x0, y0, res, w=37.0):
    m = res["map"]
    az, el, D = np.array(m["az"]), np.array(m["el"]), np.array(m["diff"])
    from hover import bowl
    h = w * (el[-1] - el[0] + 10) / (az[-1] - az[0] + 10)
    ax = fs.axes_mm(fig, x0, y0, w, h)
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("blue_seq", ["#f3f6fb", "#c6dbf3", "#7fb0e6", MALE, "#123f7a"])
    im = ax.imshow(D, origin="lower", cmap=cmap, vmin=0, vmax=D.max(), aspect="equal",
                   extent=(az[0] - 5, az[-1] + 5, el[0] - 5, el[-1] + 5), interpolation="nearest")
    c = Circle(bowl.LOVE_SPOT[:2], bowl.LOVE_SPOT[2], fc="none", ec=INK, lw=0.9, ls=(0, (3, 1.6)))
    ax.add_patch(c)
    ax.annotate("love spot", xy=(bowl.LOVE_SPOT[0] + 13, bowl.LOVE_SPOT[1] + 12), xytext=(34, 58), fontsize=fs.F_SMALL, color=INK,
                arrowprops=dict(arrowstyle="-", lw=0.6, color=INK, shrinkA=1, shrinkB=0), va="center")
    ax.set_xticks([-80, -40, 0, 40, 80]); ax.set_yticks([-40, 0, 40])
    ax.set_xlabel("azimuth of the patch (°)", fontsize=fs.F_SMALL, labelpad=1); ax.set_ylabel("elevation (°)", fontsize=fs.F_SMALL, labelpad=1)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=2, pad=1.5)
    cax = fs.axes_mm(fig, x0, y0 + h + 9.0, w * 0.62, 1.6)
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False); cb.set_ticks([0, D.max()]); cb.set_ticklabels(["0", f"{D.max():.2f}"])
    cb.ax.tick_params(length=0, pad=1.5, labelsize=fs.F_SMALL)
    fs.label(fig, x0, y0 + h + 13.8, "male − female difference in\nretinal movement (rel. units)", fontsize=fs.F_SMALL, color=INK2, linespacing=1.05)


def panel_eventcam(fig, x0, y0, ev, w=35.0, h=27.0, key="default", labels=True):
    r = ev[key]
    a = np.array(r["amps"]); x = np.where(a == 0, 0.125, a)
    ax = fs.axes_mm(fig, x0, y0, w, h)
    ax.set_xscale("log")
    ax.plot(x, 100 * np.array(r["reg_ok"]), color=FEMALE, marker="o", ms=2.4, lw=1.4, clip_on=False)
    ax.plot(x, 100 * np.array(r["target_top1"]), color=MALE, marker="o", ms=2.4, lw=1.4, clip_on=False)
    ax.set_ylim(0, 100); ax.set_xlim(0.11, 13)
    ax.set_xticks([0.125, 0.5, 1, 2, 4, 8]); ax.set_xticklabels(["0", "½", "1", "2", "4", "8"])
    ax.minorticks_off()
    ax.set_yticks([0, 50, 100])
    ax.yaxis.grid(True, color=GRID, lw=0.5); ax.set_axisbelow(True)
    ax.set_xlabel("sensor movement\nper glance (pixels)", fontsize=fs.F_SMALL, labelpad=1.5, linespacing=1.0)
    ax.set_ylabel("success (%)", fontsize=fs.F_SMALL, labelpad=0.5)
    return ax, r


def main():
    fs.setup()
    res = json.loads((CODE / "bowl_result.json").read_text())
    ev = json.loads((CODE / "eventcam_result.json").read_text())
    fig = fs.figure(72.0)
    fs.panel(fig, 0.0, 0.0, "a", "Model prediction: two stimuli single out the third muscle")
    panel_two_stimuli(fig, 11.5, 6.6, res)
    fs.panel(fig, 87.5, 0.0, "b", "The sexes differ only here")
    panel_map(fig, 97.0, 14.0, res, w=29.0)
    fs.panel(fig, 132.0, 0.0, "c", "Event camera: two tasks,\nopposite needs")
    ax, r = panel_eventcam(fig, 142.0, 14.0, ev, w=26.5, h=33.0)
    # direct labels, in the colour of their line, in the free corners
    ax.text(1.0, 1.035, "static scene registered", transform=ax.transAxes, ha="right", va="bottom", fontsize=fs.F_SMALL, color=FEMALE, fontweight="semibold")
    ax.text(0.0, -0.44, "moving target found", transform=ax.transAxes, ha="left", va="top", fontsize=fs.F_SMALL, color=MALE, fontweight="semibold")
    fs.save(fig, "fig_2_results")


if __name__ == "__main__":
    main()
