"""Figure 1 of Part B1: the project as a storyboard of six tiles (the question and the five work packages).

Usage: python3 tools/fig_concept.py
"""
import json

import numpy as np
from matplotlib import patheffects as pe
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, PathPatch, Polygon, Rectangle, RegularPolygon
from matplotlib.path import Path
from PIL import Image

import figstyle as fs
from figstyle import FEMALE, GRID, INK, INK2, INK3, MALE, MUSCLE, TILE

W = 170.0
TW, GAP = 54.0, 4.0
ROW_H = (45.5, 36.5)                 # heights of the two rows of tiles [mm]
H = sum(ROW_H) + GAP
YELLOW = "#ffcf33"


def tile(fig, col, row, number, title, tag, sub=None):
    """Tile background, number badge, title, work-package tag and one-line subtitle. Returns an
    axes in millimetres (origin top-left of the tile, y downward) and the tile height."""
    th = ROW_H[row]
    x0, y0 = col * (TW + GAP), sum(ROW_H[:row]) + row * GAP
    ax = fs.axes_mm(fig, x0, y0, TW, th)
    ax.set_xlim(0, TW); ax.set_ylim(th, 0); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.3, 0.3), TW - 0.6, th - 0.6, boxstyle="round,pad=0,rounding_size=2.2", fc=TILE, ec="none"))
    ax.add_patch(Circle((4.6, 4.7), 2.5, fc=INK, ec="none"))
    ax.text(4.6, 4.75, str(number), ha="center", va="center", fontsize=8, fontweight="bold", color="white")
    ax.text(8.6, 4.75, title, ha="left", va="center", fontsize=fs.F_TITLE, fontweight="bold", color=INK)
    if tag:
        ax.text(TW - 2.4, 4.75, tag, ha="right", va="center", fontsize=fs.F_SMALL, color=INK3, fontweight="semibold")
    if sub:
        ax.text(2.4, 10.4, sub, ha="left", va="center", fontsize=fs.F_BASE, color=INK2)
    return ax, th


def foot(ax, th, s, **kw):
    kw.setdefault("fontsize", fs.F_BASE); kw.setdefault("color", INK); kw.setdefault("fontweight", "semibold")
    ax.text(TW / 2, th - 3.4, s, ha="center", va="center", **kw)


def arrow(ax, p, q, color=INK2, lw=0.9, head=2.6, style="-|>", **kw):
    a = FancyArrowPatch(p, q, arrowstyle=f"{style},head_length={head},head_width={head * 0.6}", lw=lw, color=color,
                        shrinkA=0, shrinkB=0, **kw)
    ax.add_patch(a)
    return a


def zigzag(ax, p, q, n=4, amp=0.7, color=INK2, lw=0.8, ls="-"):
    """Electrical-synapse (resistor) symbol between two points."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    d = q - p; L = np.hypot(*d); u = d / L; v = np.array([-u[1], u[0]])
    a, b = p + u * L * 0.28, p + u * L * 0.72
    pts = [p, a]
    for k in range(1, 2 * n):
        pts.append(a + (b - a) * k / (2 * n) + v * amp * (1 if k % 2 else -1))
    pts += [b, q]
    pts = np.array(pts)
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, ls=ls, solid_joinstyle="miter", solid_capstyle="round")


def cell(ax, xy, r, text, ec=INK2, fc="white", tc=INK, lw=0.9, ls="-", fs_=fs.F_SMALL, weight="semibold"):
    ax.add_patch(Circle(xy, r, fc=fc, ec=ec, lw=lw, ls=ls, zorder=3))
    ax.text(xy[0], xy[1] + 0.05, text, ha="center", va="center", fontsize=fs_, color=tc, fontweight=weight, zorder=4)


# ----------------------------------------------------------------------------- tile 1: the question
def tile_question(fig):
    ax, th = tile(fig, 0, 0, 1, "A third eye muscle, in males only", None)
    im = Image.open(fs.SRC / "ct_eristalis_m_crop.jpg")
    w = TW - 4.0; h = w * im.size[1] / im.size[0]
    x0, y0 = 2.0, 8.4
    img = ax.imshow(np.asarray(im), extent=(x0, x0 + w, y0 + h, y0), aspect="auto", interpolation="lanczos", zorder=2)
    img.set_clip_path(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=1.2", transform=ax.transData))
    sx, sy = w / 1400.0, h / 846.0                      # preview-pixel coordinates of the crop -> mm
    P = lambda px, py: (x0 + px * sx, y0 + py * sy)
    halo = [pe.withStroke(linewidth=1.8, foreground="black")]
    red = "#ff6b5e"
    ax.text(*P(40, 70), "third muscle", ha="left", va="center", fontsize=fs.F_BASE, fontweight="bold", color=red, zorder=5, path_effects=halo)
    ax.plot(*zip(P(345, 82), P(642, 188)), color=red, lw=0.8, zorder=5)
    ax.text(*P(1362, 70), "muscles of both sexes", ha="right", va="center", fontsize=fs.F_SMALL, color="white", zorder=5, path_effects=halo)
    for tgt in ((800, 312), (1052, 742)):
        ax.plot(*zip(P(1150, 102), P(*tgt)), color="white", lw=0.6, zorder=5, alpha=0.9)
    ax.text(*P(40, 800), "male hoverfly head, micro-CT", ha="left", va="center", fontsize=fs.F_SMALL, color="white", zorder=5, path_effects=halo)
    ax.text(TW / 2, (y0 + h + th) / 2 - 0.1, "What is it for?", ha="center", va="center", fontsize=9.5, fontweight="bold", color=MUSCLE)
    ax.set_xlim(0, TW); ax.set_ylim(th, 0)


# ----------------------------------------------------------------------------- tile 2: model
def hex_patch(ax, cx, cy, r=1.25, color=INK2):
    for q, s in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)):
        x = cx + r * 1.732 * (q + s / 2.0); y = cy + r * 1.5 * s
        ax.add_patch(RegularPolygon((x, y), 6, radius=r, orientation=0, fc="white", ec=color, lw=0.6))


def tile_model(fig):
    ax, th = tile(fig, 1, 0, 2, "Model", "WP1 · H1", "connectome + electrical synapses")
    ym = 24.2
    hex_patch(ax, 6.2, ym)
    ax.add_patch(FancyBboxPatch((12.6, ym - 3.3), 7.4, 6.6, boxstyle="round,pad=0,rounding_size=0.8", fc="white", ec=INK2, lw=0.8))
    ax.text(16.3, ym, "T4\nT5", ha="center", va="center", fontsize=fs.F_SMALL, color=INK, fontweight="semibold", linespacing=0.95)
    arrow(ax, (9.9, ym), (12.2, ym), head=2.0)
    hs, vs = (28.4, ym - 4.6), (28.4, ym + 4.6)
    arrow(ax, (20.3, ym - 0.9), (25.2, hs[1] + 0.7), head=2.0)
    arrow(ax, (20.3, ym + 0.9), (25.2, vs[1] - 0.7), head=2.0)
    cell(ax, hs, 3.0, "HS"); cell(ax, vs, 3.0, "VS")
    xm = 42.6
    mot, mos, mio = (xm, ym - 8.4), (xm, ym), (xm, ym + 8.4)
    zigzag(ax, (hs[0] + 3.0, hs[1] - 0.7), (mot[0] - 3.1, mot[1] + 0.3))
    zigzag(ax, (hs[0] + 3.0, hs[1] + 0.9), (mos[0] - 3.1, mos[1] - 0.9))
    zigzag(ax, (vs[0] + 3.0, vs[1] - 0.9), (mos[0] - 3.1, mos[1] + 0.9))
    for src in ((hs[0] + 2.2, hs[1] + 2.1), (vs[0] + 3.0, vs[1] + 0.8)):          # which cells drive the third muscle?
        ax.plot([src[0], mio[0] - 3.2], [src[1], mio[1] - (0.6 if src[1] < ym else -0.4)], color=MUSCLE, lw=0.8, ls=(0, (2.2, 1.6)), zorder=1)
    cell(ax, mot, 3.2, "MOT", fs_=6.5); cell(ax, mos, 3.2, "MOS", fs_=6.5)
    cell(ax, mio, 3.2, "?", ec=MUSCLE, tc=MUSCLE, lw=1.1, fs_=9, weight="bold")
    yl = 37.6
    for x, s in ((6.2, "eye"), (16.3, "motion\ndetectors"), (28.4, "wide-field\ncells"), (xm + 1.2, "eye-muscle\nmotor neurons")):
        ax.text(x, yl, s, ha="center", va="top", fontsize=fs.F_SMALL, color=INK2, linespacing=0.98)
    ax.text(xm + 3.7, mio[1], "third", ha="left", va="center", fontsize=fs.F_SMALL, color=MUSCLE, fontweight="bold")


# ----------------------------------------------------------------------------- tile 3: test
def thumb(ax, x0, y0, w, kind, tag):
    from fig_results import stimulus_frame
    psi, el, frame, bowl = stimulus_frame(kind)
    i0, i1 = np.searchsorted(psi, -95), np.searchsorted(psi, 95)
    j0, j1 = np.searchsorted(el, -57), np.searchsorted(el, 78)
    sub = frame[j0:j1, i0:i1][::-1]
    h = w * sub.shape[0] / sub.shape[1]
    im = ax.imshow(sub, cmap="gray", vmin=0, vmax=1, extent=(x0, x0 + w, y0 + h, y0), aspect="auto", interpolation="bilinear", zorder=2)
    im.set_clip_path(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=1.0", transform=ax.transData))
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=1.0", fc="none", ec=INK2, lw=0.6, zorder=3))
    s = w / 190.0
    cx, cy, r = x0 + (bowl.LOVE_SPOT[0] + 95) * s, y0 + (78 - bowl.LOVE_SPOT[1]) * s, bowl.LOVE_SPOT[2] * s
    c = Circle((cx, cy), r, fc="none", ec=YELLOW, lw=0.9, ls=(0, (2.5, 1.4)), zorder=4)
    c.set_path_effects([pe.withStroke(linewidth=1.7, foreground=INK)])
    ax.add_patch(c)
    ax.text(x0 + w / 2, y0 + h + 1.9, tag, ha="center", va="center", fontsize=fs.F_SMALL, color=INK, fontweight="semibold")
    return h


def fly_head(ax, cx, cy, s=1.0):
    """Front view of a fly head: two large eyes that meet at the top, the third muscle between them."""
    ax.add_patch(Ellipse((cx, cy), 9.6 * s, 6.8 * s, fc="#e9e7e1", ec=INK2, lw=0.8, zorder=3))
    for sign in (-1, 1):
        ax.add_patch(Ellipse((cx + sign * 2.45 * s, cy - 0.3 * s), 4.5 * s, 5.6 * s, angle=sign * 14, fc="#b9856a", ec=INK2, lw=0.7, zorder=4))
    ax.add_patch(Circle((cx, cy - 2.3 * s), 0.6 * s, fc=MUSCLE, ec="none", zorder=5))


def tile_test(fig):
    ax, th = tile(fig, 2, 0, 3, "Test", "WP2 · H2", "two stimuli, then the animal in the loop")
    w = 15.8
    xa, xb, yt = 2.6, 20.4, 14.2
    h = thumb(ax, xa, yt, w, "matched", "matched")
    thumb(ax, xb, yt, w, "love_spot", "love spot")
    # the loop: display -> eyes -> tracker -> next stimulus -> display
    yl = 36.2
    hx, hy = 45.6, 19.8
    fly_head(ax, hx, hy, 0.95)
    ax.text(hx, hy - 4.9, "tethered fly", ha="center", va="center", fontsize=fs.F_SMALL, color=INK2)
    arrow(ax, (xb + w + 0.5, hy), (hx - 5.1, hy), head=2.0)
    arrow(ax, (hx, hy + 3.7), (hx, hy + 8.2), head=2.0)
    ax.text(hx, hy + 10.5, "retinal\ntracking", ha="center", va="center", fontsize=fs.F_SMALL, color=INK, fontweight="semibold", linespacing=0.98)
    ax.plot([hx, hx, xa + w / 2], [hy + 13.0, yl, yl], color=INK2, lw=0.9, zorder=1)
    arrow(ax, (xa + w / 2, yl), (xa + w / 2, yt + h + 3.6), head=2.0)
    arrow(ax, (xb + w / 2, yl), (xb + w / 2, yt + h + 3.6), head=2.0)
    ax.text(TW / 2, yl + 3.2, "measured movement → next stimulus", ha="center", va="center", fontsize=fs.F_SMALL, color=INK2)


# ----------------------------------------------------------------------------- tile 4: explain
def dots(ax, x, y, n, third=False, r=1.25, gap=3.4):
    for k in range(n):
        last = third and k == n - 1
        ax.add_patch(Circle((x + k * gap, y), r, fc=MUSCLE if last else INK2, ec="none"))


def pill(ax, x, y, w, text, color):
    ax.add_patch(FancyBboxPatch((x, y - 2.8), w, 5.6, boxstyle="round,pad=0,rounding_size=2.8", fc="white", ec=color, lw=1.0))
    ax.text(x + w / 2, y + 0.05, text, ha="center", va="center", fontsize=fs.F_SMALL, color=INK, fontweight="semibold")


def tile_explain(fig):
    ax, th = tile(fig, 0, 1, 4, "Explain", "WP3 · H3", "one network, trained either to")
    for y, text, col, n, third in ((17.0, "hold position", FEMALE, 2, False), (24.6, "catch a target", MALE, 3, True)):
        pill(ax, 2.6, y, 21.0, text, col)
        arrow(ax, (24.6, y), (28.8, y), head=2.2)
        dots(ax, 31.4, y, n, third)
        ax.text(31.4 + n * 3.4 - 0.6, y, "muscles" if not third else "muscles?", ha="left", va="center", fontsize=fs.F_SMALL,
                color=MUSCLE if third else INK2, fontweight="bold" if third else "normal")
    foot(ax, th, "Does a third muscle emerge?")


# ----------------------------------------------------------------------------- tile 5: transfer
def camera(ax, cx, cy):
    ax.add_patch(FancyBboxPatch((cx - 4.2, cy - 2.8), 8.4, 5.6, boxstyle="round,pad=0,rounding_size=0.8", fc="white", ec=INK2, lw=0.9, zorder=3))
    ax.add_patch(Circle((cx, cy), 1.9, fc="#dfe9f7", ec=INK2, lw=0.9, zorder=4))
    ax.add_patch(Circle((cx, cy), 0.8, fc=MALE, ec="none", zorder=5))
    for sgn in (-1, 1):
        arrow(ax, (cx + sgn * 5.0, cy), (cx + sgn * 8.0, cy), color=MUSCLE, head=2.0, lw=1.0)
    arrow(ax, (cx, cy - 3.5), (cx, cy - 6.2), color=MUSCLE, head=2.0, lw=1.0)


def chip(ax, cx, cy, s=3.2):
    ax.add_patch(FancyBboxPatch((cx - s, cy - s), 2 * s, 2 * s, boxstyle="round,pad=0,rounding_size=0.6", fc="white", ec=INK2, lw=0.9, zorder=3))
    for k in (-2, 0, 2):
        for sgn in (-1, 1):
            ax.plot([cx + k * 0.9, cx + k * 0.9], [cy + sgn * s, cy + sgn * (s + 1.1)], color=INK2, lw=0.8)
            ax.plot([cx + sgn * s, cx + sgn * (s + 1.1)], [cy + k * 0.9, cy + k * 0.9], color=INK2, lw=0.8)
    for k, hgt in enumerate((1.6, 0.9, 2.0, 1.2, 1.7)):                 # spikes
        x = cx - 2.0 + k * 1.0
        ax.plot([x, x], [cy + 1.3, cy + 1.3 - hgt * 1.2], color=MALE, lw=1.0, zorder=4)
    ax.plot([cx - 2.5, cx + 2.5], [cy + 1.3, cy + 1.3], color=MALE, lw=0.6, zorder=4)


def quadrotor(ax, cx, cy, s=0.92):
    for a in (45, 135, 225, 315):
        x, y = cx + 4.2 * s * np.cos(np.deg2rad(a)), cy + 4.2 * s * np.sin(np.deg2rad(a))
        ax.plot([cx, x], [cy, y], color=INK2, lw=1.2, zorder=3)
        ax.add_patch(Circle((x, y), 2.1 * s, fc="white", ec=INK2, lw=0.9, zorder=4))
    ax.add_patch(FancyBboxPatch((cx - 1.5 * s, cy - 1.5 * s), 3.0 * s, 3.0 * s, boxstyle="round,pad=0,rounding_size=0.5", fc=INK2, ec="none", zorder=5))


def tile_transfer(fig):
    ax, th = tile(fig, 1, 1, 5, "Transfer", "WP4 · H4", "event cameras that move their sensor")
    y = 19.4
    camera(ax, 11.4, y + 0.6)
    chip(ax, 29.0, y)
    quadrotor(ax, 45.2, y)
    arrow(ax, (21.0, y), (23.6, y), head=2.0)
    arrow(ax, (34.6, y), (38.0, y), head=2.0)
    for x, s in ((11.4, "moving sensor"), (29.0, "spiking chip"), (45.2, "flying robot")):
        ax.text(x, y + 7.6, s, ha="center", va="center", fontsize=fs.F_SMALL, color=INK2)
    foot(ax, th, "small targets · ego-motion · flight")


# ----------------------------------------------------------------------------- tile 6: validate
def robot(ax, cx, cy, color=INK2):
    ax.add_patch(FancyBboxPatch((cx - 3.0, cy - 2.0), 6.0, 4.0, boxstyle="round,pad=0,rounding_size=0.9", fc="white", ec=color, lw=0.9, zorder=3))
    for sgn in (-1, 1):
        ax.add_patch(Circle((cx + sgn * 2.3, cy + 2.3), 1.15, fc=color, ec="none", zorder=4))
    ax.add_patch(Circle((cx, cy - 0.3), 0.95, fc="#dfe9f7", ec=color, lw=0.7, zorder=4))


def tile_validate(fig):
    ax, th = tile(fig, 2, 1, 6, "Validate at scale", "WP5", "students and citizens run every model")
    y = 18.4
    for k, x in enumerate((9.0, 18.0, 27.0, 36.0, 45.0)):
        robot(ax, x, y + (0.8 if k % 2 else -0.8))
    ax.text(TW / 2, 26.6, "low-cost spiking robots", ha="center", va="center", fontsize=fs.F_SMALL, color=INK2)
    foot(ax, th, "courses · robot zoo · proofreading")


def connectors(fig):
    """Small arrows between the tiles (reading order 1 → 6)."""
    ax = fs.axes_mm(fig, 0, 0, W, H)
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off"); ax.patch.set_alpha(0)
    for row in (0, 1):
        y = sum(ROW_H[:row]) + row * GAP + ROW_H[row] / 2
        for col in (0, 1):
            x = (col + 1) * TW + col * GAP
            arrow(ax, (x + 0.4, y), (x + GAP - 0.4, y), color=INK3, head=2.6, lw=1.1)
    ax.set_zorder(10)


def main():
    fs.setup()
    fig = fs.figure(H, W)
    tile_question(fig); tile_model(fig); tile_test(fig)
    tile_explain(fig); tile_transfer(fig); tile_validate(fig)
    connectors(fig)
    fs.save(fig, "fig_1_concept")


if __name__ == "__main__":
    main()
