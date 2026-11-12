"""Figure B1 of Part B2: the evidence behind the preliminary results (not repeated from Part I).

a  MESH: the gaze circuit as neuron meshes with contact sites, and a validated membrane apposition
b  the model against the Drosophila measurements of Falt et al. 2026
c  direction tuning of the predicted retinal movement for the two apertures, male and female
d  what the two stimuli say under each idea of what drives the third muscle
e  closed-loop stimulus search in silico
f  what an event sensor sees for three sizes of the sensor movement

Data: code/hover/bowl_result.json, eventcam_result.json, results_raw/validate_falt.json.
Usage: python3 tools/fig_support.py
"""
import json

import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch
from PIL import Image

import figstyle as fs
from fig_results import BLUES
from figstyle import FEMALE, GRID, INK, INK2, INK3, MALE, MALE_L, MUSCLE

CODE = fs.ROOT / "code" / "hover"
H = 95.5


def img_axes(fig, x, y, w, path):
    im = Image.open(path)
    h = w * im.size[1] / im.size[0]
    ax = fs.axes_mm(fig, x, y, w, h)
    ax.imshow(np.asarray(im), interpolation="lanczos")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(GRID); s.set_linewidth(0.5)
    return ax, h


# ----------------------------------------------------------------------------- a
def panel_mesh(fig, x0, y0):
    ax, h = img_axes(fig, x0, y0, 27.0, fs.SRC / "mesh_gaze_circuit.jpg")
    fs.label(fig, x0, y0 + h + 0.9, "gaze circuit as meshes;\ncontact sites in red", fontsize=fs.F_SMALL, color=INK2, linespacing=1.05)
    ax2, h2 = img_axes(fig, x0 + 29.0, y0, 23.8, fs.SRC / "em_apposition.jpg")
    fs.label(fig, x0 + 29.0, y0 + h2 + 0.9, "validated apposition,\nmotor neuron and VS2", fontsize=fs.F_SMALL, color=INK2, linespacing=1.05)


# ----------------------------------------------------------------------------- b
def panel_validation(fig, x0, y0):
    v = json.loads((CODE / "results_raw" / "validate_falt.json").read_text())["summary"]
    from hover.oculomotor import model_to_falt
    ax = fs.axes_mm(fig, x0, y0 + 0.5, 21.0, 21.0, projection="polar")
    ax.set_theta_zero_location("E"); ax.set_ylim(0, 1); ax.set_yticks([])
    ax.set_xticks(np.deg2rad([0, 90, 180, 270])); ax.set_xticklabels([])
    ax.spines["polar"].set_color(GRID); ax.grid(color=GRID, lw=0.5)
    for nm, meas in (("MOS", 212.0), ("MOT", 141.0)):
        mod = v["pd"][nm]["pd_falt"]
        ax.annotate("", xy=(np.deg2rad(meas), 0.93), xytext=(0, 0), arrowprops=dict(arrowstyle="-", lw=4.0, color="#c9c8c2", shrinkA=0, shrinkB=0))
        ax.annotate("", xy=(np.deg2rad(mod), 0.93), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>,head_length=0.5,head_width=0.25", lw=1.0, color=INK, shrinkA=0, shrinkB=0))
        ax.text(np.deg2rad(meas + (30 if nm == "MOS" else -30)), 0.62, nm, ha="center", va="center", fontsize=fs.F_SMALL, fontweight="semibold", color=INK)
    fs.label(fig, x0, y0 + 23.2, "preferred directions of\nthe two motor neurons:\nmeasured (grey), model", fontsize=fs.F_SMALL, color=INK2, linespacing=1.05)
    # optokinetic reflex: direction of the compensatory movement against stimulus direction
    stim = np.array(model_to_falt(np.array(v["dirs_model"]), v["beta"]))
    comp = np.array(model_to_falt(np.array(v["okr"]["inverted_shift_dir"]), v["beta"]))
    comp = stim + ((comp - stim + 180) % 360 - 180)             # unwrap around the identity line
    ax2 = fs.axes_mm(fig, x0 + 34.5, y0 + 4.6, 17.0, 17.0)
    ax2.plot([0, 360], [0, 360], color=INK3, lw=0.7, ls=(0, (3, 2)))
    ax2.plot(stim, comp, ls="none", marker="o", ms=2.4, color=INK, clip_on=False)
    ax2.set_xlim(0, 360); ax2.set_ylim(-20, 380); ax2.set_xticks([0, 180, 360]); ax2.set_yticks([0, 180, 360])
    ax2.set_xlabel("stimulus (°)", fontsize=fs.F_SMALL, labelpad=1)
    ax2.set_ylabel("model (°)", fontsize=fs.F_SMALL, labelpad=0.5)
    ax2.set_title("reflex direction", fontsize=fs.F_SMALL, color=INK, pad=2.5, fontweight="semibold")
    ax2.text(0.04, 0.97, f"mean\nerror {v['okr']['mean_abs_error']:.0f}°", transform=ax2.transAxes, ha="left", va="top", fontsize=fs.F_SMALL, color=INK2, linespacing=1.0)


# ----------------------------------------------------------------------------- c
def panel_tuning(fig, x0, y0, res):
    from hover import bowl
    for k, (cond, title) in enumerate(((bowl.MATCHED[0], "grating outside"), (bowl.LOVE[0], "grating inside"))):
        rows = res["scan"][cond]
        d = np.array([r["dir"] for r in rows] + [360.0])
        f = np.array([r["amp_female"] for r in rows]); f = np.r_[f, f[0]]
        m = np.array([r["amp_male"] for r in rows]); m = np.r_[m, m[0]]
        ax = fs.axes_mm(fig, x0 + k * 22.0, y0 + 5.2, 18.6, 21.0)
        ax.plot(d, f, color=FEMALE, lw=1.3); ax.plot(d, m, color=MALE, lw=1.3)
        ax.set_xlim(0, 360); ax.set_ylim(0, 0.36); ax.set_xticks([0, 90, 180, 270, 360]); ax.set_xticklabels(["→", "↑", "←", "↓", "→"], fontsize=8)
        ax.set_yticks([0, 0.1, 0.2, 0.3])
        ax.yaxis.grid(True, color=GRID, lw=0.5); ax.set_axisbelow(True)
        ax.set_xlabel("drift direction", fontsize=fs.F_SMALL, labelpad=1)
        ax.set_title(title, fontsize=fs.F_SMALL, color=INK, pad=2.5, fontweight="semibold")
        if k == 0:
            ax.set_ylabel("retinal movement\n(model, rel. units)", fontsize=fs.F_SMALL, labelpad=1, linespacing=1.0)
            pick = bowl.MATCHED[1]
            ax.text(118, 0.305, "male", color=MALE, fontsize=fs.F_SMALL, fontweight="semibold", ha="center")
            ax.text(150, 0.065, "female", color=FEMALE, fontsize=fs.F_SMALL, fontweight="semibold", ha="center")
        else:
            ax.set_yticklabels([])
            pick = bowl.LOVE[1]
        ax.axvline(pick, color=INK3, lw=0.7, ls=(0, (2, 1.6)), zorder=0)


# ----------------------------------------------------------------------------- d
def panel_answers(fig, x0, y0, res):
    alt = res["alternatives"]
    rows = (("HSN", "love-spot cell (H2)"), ("HSNE", "its neighbour HSNE"), ("HS", "all horizontal cells"),
            ("VS", "vertical cells"), ("none", "no visual drive"))
    ax = fs.axes_mm(fig, x0 + 28.5, y0 + 5.2, 22.0, 25.0)
    yy = np.arange(len(rows))[::-1].astype(float)
    for y, (key, name) in zip(yy, rows):
        a, b = alt[key]["matched"]["ratio"], alt[key]["love_spot"]["ratio"]
        ax.plot([a, b], [y, y], color=GRID, lw=1.6, zorder=1, solid_capstyle="round")
        ax.plot(a, y, marker="o", ms=4.6, mfc="white", mec=INK, mew=1.1, zorder=3)
        ax.plot(b, y, marker="o", ms=4.6, mfc=INK, mec=INK, mew=1.1, zorder=3)
        ax.text(-0.08, y, name, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=fs.F_SMALL, color=INK,
                fontweight="semibold" if key == "HSN" else "normal")
    ax.axvline(1.0, color=INK3, lw=0.7, ls=(0, (2, 1.6)), zorder=0)
    ax.set_xlim(0.8, 3.15); ax.set_ylim(-0.6, len(rows) - 0.4); ax.set_yticks([])
    ax.set_xticks([1, 2, 3]); ax.spines["left"].set_visible(False)
    ax.set_xlabel("retinal movement,\nmale ÷ female", fontsize=fs.F_SMALL, labelpad=1, linespacing=1.0)
    fs.label(fig, x0, y0 + 0.6, "third muscle driven by", fontsize=fs.F_SMALL, color=INK2)
    # legend for the two markers
    lx, ly = x0 + 27.0, y0 + 0.4
    W, Hh = fig.get_size_inches() * 25.4
    for dx, filled, txt in ((0.0, False, "matched"), (14.6, True, "love spot")):
        fig.add_artist(Circle(((lx + dx + 1.0) / W, 1 - (ly + 1.25) / Hh), 0.8 / W, transform=fig.transFigure,
                              fc=INK if filled else "white", ec=INK, lw=1.0))
        fs.label(fig, lx + dx + 2.8, ly, txt, fontsize=fs.F_SMALL, color=INK)


# ----------------------------------------------------------------------------- e
def panel_loop(fig, x0, y0, res):
    cl = res["closed_loop"]
    ax = fs.axes_mm(fig, x0 + 9.5, y0 + 2.0, 37.0, 28.0)
    ref, has_naive = None, False
    for key, r in sorted(cl.items()):
        h = r["history"]
        t = [x["trials"] for x in h]; j = [x["true"] for x in h]
        if r["scenario"] == "displaced":
            ref = r["designed_stimulus_true"]
            strong = r["noise"] <= 0.02
            ax.plot(t, j, color=MALE if strong else MALE_L, lw=1.4 if strong else 1.0, zorder=3 if strong else 2)
        elif r["scenario"] == "naive":
            ax.plot(t, j, color=INK3, lw=1.1, zorder=2); has_naive = True
    if ref is not None:
        ax.axhline(ref, color=INK, lw=0.7, ls=(0, (3, 2)), zorder=1)
        ax.text(183, ref - 0.008, "stimulus designed\nwith the model", ha="right", va="top", fontsize=fs.F_SMALL, color=INK, linespacing=1.0)
    ax.text(4, 0.222, "search steered by\nthe tracked retina", ha="left", va="top", fontsize=fs.F_SMALL, color=MALE, fontweight="semibold", linespacing=1.0)
    if has_naive:
        ax.text(183, 0.05, "arbitrary start", ha="right", va="bottom", fontsize=fs.F_SMALL, color=INK2)
    ax.set_xlim(0, 185); ax.set_ylim(0, 0.225); ax.set_xticks([0, 50, 100, 150]); ax.set_yticks([0, 0.1, 0.2])
    ax.yaxis.grid(True, color=GRID, lw=0.5); ax.set_axisbelow(True)
    ax.set_xlabel("stimulus presentations", fontsize=fs.F_SMALL, labelpad=1)
    ax.set_ylabel("movement due to the\nthird muscle (rel. units)", fontsize=fs.F_SMALL, labelpad=1, linespacing=1.0)


# ----------------------------------------------------------------------------- f
def panel_events(fig, x0, y0):
    from hover import eventcam as ec
    amps = (0.0, 0.5, 4.0)
    ex = ec.example(seed=3, amps=amps)
    px, py = ex["pos"]
    half = 24
    for k, (c, a) in enumerate(zip(ex["counts"], amps)):
        ax = fs.axes_mm(fig, x0 + k * 18.2, y0 + 5.0, 16.6, 16.6)
        sub = c[int(py) - half:int(py) + half, int(px) - half:int(px) + half]
        ax.imshow(sub, cmap=BLUES, vmin=0, vmax=4, interpolation="nearest")
        ax.add_patch(Circle((half + 1.0 - a * 0.25, half - a * 0.43), 5.0, fc="none", ec=MUSCLE, lw=0.9))
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(True); s.set_color(GRID); s.set_linewidth(0.6)
        ax.set_title(("sensor still", "½ pixel", "4 pixels")[k], fontsize=fs.F_SMALL, color=INK, pad=2.5, fontweight="semibold")
    fs.label(fig, x0, y0 + 23.2, "events of one glance, 48 × 48 pixels;\ncircle: the small moving target",
             fontsize=fs.F_SMALL, color=INK2, linespacing=1.05)


def main():
    fs.setup()
    res = json.loads((CODE / "bowl_result.json").read_text())
    fig = fs.figure(H)
    r1, r2 = 0.0, 47.5
    fs.panel(fig, 0.0, r1, "a", "Electrical synapses found by MESH")
    panel_mesh(fig, 1.0, r1 + 6.2)
    fs.panel(fig, 57.5, r1, "b", "The model against the fly")
    panel_validation(fig, 59.5, r1 + 6.2)
    fs.panel(fig, 115.0, r1, "c", "Direction tuning, both stimuli")
    panel_tuning(fig, 127.0, r1 + 4.4, res)
    fs.panel(fig, 0.0, r2, "d", "Two stimuli, three answers")
    panel_answers(fig, 1.0, r2 + 6.2, res)
    fs.panel(fig, 57.5, r2, "e", "The animal corrects the model")
    panel_loop(fig, 58.5, r2 + 6.2, res)
    fs.panel(fig, 115.0, r2, "f", "What an event sensor sees")
    panel_events(fig, 116.0, r2 + 6.2)
    fs.save(fig, "fig_B1_support")


if __name__ == "__main__":
    main()
