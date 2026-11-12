"""Figures B2 (work packages and their dependencies) and B3 (Gantt chart) of Part B2.

Both are drawn at print size with the same type and colours as the other figures; no text is
smaller than 7 pt. Keep the task list in sync with proposal/gantt.md and section 2 of B2_PartII.md.

Usage: python3 tools/fig_workplan.py
"""
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

import figstyle as fs
from figstyle import GRID, INK, INK2, INK3, MALE, MALE_L, MUSCLE, TILE

W = 170.0

WPS = [
    dict(n=1, name="Model", sub="connectome → spiking circuit", meta="M1–36 · H1",
         tasks=["T1.1 electrical synapses", "T1.2 Tier 1: biophysical", "T1.3 Tier 2: reduced",
                "T1.4 Tier 3: trainable", "T1.5 muscles, efference copy"],
         out=["D1.1 synapse atlas (M18)", "D1.2 reduced model (M24)"]),
    dict(n=2, name="Test", sub="what is the third muscle for?", meta="M6–48 · H2, H2b",
         tasks=["T2.1 male and female models", "T2.2 two stimuli, closed loop", "T2.3 tethered experiments",
                "T2.4 free flight (high risk)", "T2.5 origin of the muscle"],
         out=["D2.1 stimuli, software (M24)"]),
    dict(n=3, name="Explain", sub="why a third muscle?", meta="M12–54 · H3",
         tasks=["T3.1 embodied simulator", "T3.2 pursuit vs stabilisation", "T3.3 ablation and theory"],
         out=["D3.2 motif catalogue (M48)"]),
    dict(n=4, name="Transfer", sub="active event-based vision", meta="M13–60 · H4",
         tasks=["T4.1 active camera head", "T4.2 neuromorphic chips", "T4.3 benchmarks, quadrotor",
                "T4.4 closed loop for machines"],
         out=["D4.3 benchmark, data (M54)"]),
]
WP5 = dict(n=5, name="Validate at scale", sub="teaching and open science", meta="M1–60",
           tasks=["T5.1 IU courses", "T5.2 robot zoo", "T5.3 community proofreading", "T5.4 hoverfly watch", "T5.5 open releases"])

# (work package, label, first month, last month), months 1-based inclusive
TASKS = [
    (1, "T1.1 Electrical synapses, both sexes", 1, 18), (1, "T1.2 Tier 1, biophysical", 1, 15),
    (1, "T1.3 Tier 2, reduced", 7, 24), (1, "T1.4 Tier 3, trainable", 13, 36), (1, "T1.5 Motor readout, efference copy", 10, 30),
    (2, "T2.1 Male and female model family", 6, 24), (2, "T2.2 Two stimuli, closed loop (in silico)", 13, 24),
    (2, "T2.3 Tethered experiments (PD2, MPI-BI)", 19, 42), (2, "T2.4 Free-flight tracking (high risk)", 37, 48),
    (2, "T2.5 Origin of the third muscle (PhD 3, LMU)", 7, 48),
    (3, "T3.1 Embodied simulator", 12, 27), (3, "T3.2 Task optimisation", 25, 48), (3, "T3.3 Analysis, motif catalogue", 37, 54),
    (4, "T4.1 Active event-camera head", 13, 30), (4, "T4.2 Motif networks on neuromorphic chips", 25, 54),
    (4, "T4.3 Benchmarks B-I, B-II, B-III", 25, 58), (4, "T4.4 Closed loop for machines", 37, 54),
    (5, "T5.1 Course modules, every semester", 1, 60), (5, "T5.2 Robot zoo", 19, 60), (5, "T5.3 Community proofreading", 7, 36),
    (5, "T5.4 Hoverfly watch", 13, 48), (5, "T5.5 Releases and evaluation", 24, 60),
]
MILESTONES = [(12, "MS1"), (24, "MS2"), (30, "MS3"), (36, "MS4"), (48, "MS5"), (60, "MS6")]


def arrow(ax, p, q, color=INK2, lw=0.9, head=2.4, ls="-", **kw):
    a = FancyArrowPatch(p, q, arrowstyle=f"-|>,head_length={head},head_width={head * 0.6}", lw=lw, color=color,
                        shrinkA=0, shrinkB=0, linestyle=ls, **kw)
    ax.add_patch(a)


def badge(ax, x, y, n):
    ax.add_patch(Circle((x, y), 2.4, fc=INK, ec="none", zorder=3))
    ax.text(x, y + 0.05, str(n), ha="center", va="center", fontsize=7.5, fontweight="bold", color="white", zorder=4)


def workplan():
    bw, gap, bh = 39.5, 4.0, 40.4
    H = bh + 7.0 + 13.6
    fig = fs.figure(H, W)
    ax = fs.axes_mm(fig, 0, 0, W, H)
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    for k, wp in enumerate(WPS):
        x0 = k * (bw + gap)
        ax.add_patch(FancyBboxPatch((x0 + 0.3, 0.3), bw - 0.6, bh - 0.6, boxstyle="round,pad=0,rounding_size=2.0", fc=TILE, ec="none"))
        badge(ax, x0 + 4.3, 4.5, wp["n"])
        ax.text(x0 + 8.2, 4.5, f"WP{wp['n']}  {wp['name']}", ha="left", va="center", fontsize=fs.F_TITLE, fontweight="bold")
        ax.text(x0 + 2.2, 9.8, wp["sub"], ha="left", va="center", fontsize=fs.F_SMALL, color=INK2)
        ax.text(x0 + 2.2, 13.0, wp["meta"], ha="left", va="center", fontsize=fs.F_SMALL, color=INK3, fontweight="semibold")
        y = 17.4
        for line in wp["tasks"]:
            ax.text(x0 + 2.2, y, line, ha="left", va="center", fontsize=fs.F_SMALL, color=INK)
            y += 3.2
        yo = bh - 2.6 - 3.2 * (len(wp["out"]) - 1)
        for line in wp["out"]:
            ax.text(x0 + 2.2, yo, line, ha="left", va="center", fontsize=fs.F_SMALL, color=INK, fontweight="semibold")
            yo += 3.2
        if k < 3:
            arrow(ax, (x0 + bw + 0.4, 9.8), (x0 + bw + gap - 0.4, 9.8), color=INK, head=2.6, lw=1.1)
    # data flow back from WP2 to WP1 (dashed)
    arrow(ax, (bw + gap - 0.4, 13.0), (bw + 0.4, 13.0), color=INK3, head=2.4, lw=1.0, ls=(0, (2.5, 1.6)))
    # WP5 strip
    y5 = bh + 7.0
    ax.add_patch(FancyBboxPatch((0.3, y5 + 0.3), W - 0.6, 13.0, boxstyle="round,pad=0,rounding_size=2.0", fc=TILE, ec="none"))
    badge(ax, 4.3, y5 + 4.5, 5)
    ax.text(8.2, y5 + 4.5, f"WP5  {WP5['name']}", ha="left", va="center", fontsize=fs.F_TITLE, fontweight="bold")
    ax.text(49.0, y5 + 4.6, f"{WP5['sub']}", ha="left", va="center", fontsize=fs.F_SMALL, color=INK2)
    ax.text(W - 2.2, y5 + 4.6, WP5["meta"], ha="right", va="center", fontsize=fs.F_SMALL, color=INK3, fontweight="semibold")
    ax.text(2.2, y5 + 9.9, "   ·   ".join(WP5["tasks"]), ha="left", va="center", fontsize=fs.F_SMALL, color=INK)
    # links between WP5 and the others
    for xc, label, up in ((bw / 2, "labels", True), (2 * (bw + gap) + bw / 2, "task statistics", True), (3 * (bw + gap) + bw / 2, "models on robots", False)):
        if up:
            arrow(ax, (xc, y5 - 0.2), (xc, bh + 0.4), color=INK3, head=2.4, lw=1.0, ls=(0, (2.5, 1.6)))
        else:
            arrow(ax, (xc, bh + 0.4), (xc, y5 - 0.2), color=INK, head=2.6, lw=1.1)
        ax.text(xc + (1.6 if up else -1.6), bh + 3.5, label, ha="left" if up else "right", va="center", fontsize=fs.F_SMALL, color=INK2)
    fs.save(fig, "fig_B2_workplan")


def gantt():
    row, top = 2.72, 9.0
    n = len(TASKS)
    H = top + n * row + 8.0
    fig = fs.figure(H, W)
    ax = fs.axes_mm(fig, 0, 0, W, H)
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    left, right = 67.0, W - 2.5
    mw = (right - left) / 60.0
    X = lambda m: left + m * mw                       # x of the END of month m (m = 0: project start)
    # year bands and month ticks
    for yr in range(5):
        if yr % 2 == 0:
            ax.add_patch(Rectangle((X(12 * yr), top - 1.0), 12 * mw, n * row + 2.0, fc="#f5f4f0", ec="none", zorder=0))
        ax.text(X(12 * yr + 6), 2.6, f"Year {yr + 1}", ha="center", va="center", fontsize=fs.F_BASE, fontweight="semibold", color=INK)
    for m in range(0, 61, 12):
        ax.text(X(m), 6.6, f"M{m}" if m else "M1", ha="center", va="center", fontsize=fs.F_SMALL, color=INK2)
    names = {1: "WP1", 2: "WP2", 3: "WP3", 4: "WP4", 5: "WP5"}
    prev = None
    for i, (wp, label, a, b) in enumerate(TASKS):
        y = top + i * row + row / 2
        if wp != prev:
            ax.text(0.5, y, names[wp], ha="left", va="center", fontsize=fs.F_SMALL, fontweight="bold", color=INK)
            if prev is not None:
                ax.plot([0, right], [y - row / 2, y - row / 2], color=GRID, lw=0.6, zorder=1)
            prev = wp
        ax.text(8.6, y, label, ha="left", va="center", fontsize=fs.F_SMALL, color=INK)
        risky = "high risk" in label
        ax.add_patch(FancyBboxPatch((X(a - 1), y - row * 0.31), (b - a + 1) * mw, row * 0.62, boxstyle="round,pad=0,rounding_size=0.5",
                                    fc="white" if risky else MALE_L, ec=MALE, lw=0.7, hatch="////" if risky else None, zorder=2))
    ybot = top + n * row
    for m, name in MILESTONES:
        ax.plot([X(m), X(m)], [top - 1.0, ybot + 1.6], color=INK, lw=0.7, ls=(0, (2.5, 1.8)), zorder=3)
        ax.add_patch(Polygon([(X(m), ybot + 1.4), (X(m) + 1.2, ybot + 2.9), (X(m), ybot + 4.4), (X(m) - 1.2, ybot + 2.9)], fc=INK, ec="none", zorder=4))
        ax.text(X(m), ybot + 6.6, name, ha="center" if m < 60 else "right", va="center", fontsize=fs.F_SMALL, fontweight="bold", color=INK)
    fs.save(fig, "fig_B3_gantt")


if __name__ == "__main__":
    fs.setup()
    workplan()
    gantt()
