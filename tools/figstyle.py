"""Shared style of the proposal figures: one type family, one palette, sizes in millimetres.

All figures are drawn at their printed size (text width 170 mm), so the font sizes below are the
sizes on paper: 7 pt is the smallest text used anywhere. Output is vector (SVG with text as paths,
PDF) plus a 600 dpi PNG for the Word export.
"""
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIG = ROOT / "proposal" / "figures"
SRC = FIG / "src"
sys.path.insert(0, str(ROOT / "code"))

TEXT_W = 170.0                     # mm, text width of the proposal
INK, INK2, INK3 = "#0b0b0b", "#52514e", "#8a8983"
GRID = "#d9d8d2"
PAPER = "#ffffff"
TILE = "#f5f4f0"
MALE, FEMALE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"     # categorical slots 1-3
MALE_L, FEMALE_L = "#a9c9ee", "#f6c1ab"
MUSCLE = "#d92d20"                 # the third muscle (same red as in the tomography renderings)
F_SMALL, F_BASE, F_TITLE, F_PANEL = 7.0, 7.5, 8.5, 10.0


def setup():
    fam = "Inter" if any(f.name == "Inter" for f in font_manager.fontManager.ttflist) else "DejaVu Sans"
    plt.rcParams.update({
        "font.family": [fam, "DejaVu Sans"], "font.size": F_BASE, "text.color": INK,
        "axes.labelsize": F_BASE, "axes.titlesize": F_TITLE, "axes.labelcolor": INK, "axes.edgecolor": INK2,
        "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
        "xtick.labelsize": F_SMALL, "ytick.labelsize": F_SMALL, "xtick.color": INK2, "ytick.color": INK2,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "legend.fontsize": F_SMALL, "legend.frameon": False, "lines.linewidth": 1.4,
        "svg.fonttype": "path", "pdf.fonttype": 42, "figure.dpi": 150, "savefig.dpi": 600,
        "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
        "mathtext.default": "regular",
    })


def mm(x):
    return x / 25.4


def figure(height_mm, width_mm=TEXT_W):
    return plt.figure(figsize=(mm(width_mm), mm(height_mm)))


def axes_mm(fig, left, top, width, height, **kw):
    """Axes placed in millimetres from the top-left corner of the figure."""
    W, H = fig.get_size_inches() * 25.4
    return fig.add_axes([left / W, 1 - (top + height) / H, width / W, height / H], **kw)


def label(fig, x_mm, y_mm, s, **kw):
    """Text placed in millimetres from the top-left corner of the figure."""
    W, H = fig.get_size_inches() * 25.4
    kw.setdefault("va", "top"); kw.setdefault("ha", "left")
    return fig.text(x_mm / W, 1 - y_mm / H, s, **kw)


def panel(fig, x_mm, y_mm, letter, title=None):
    label(fig, x_mm, y_mm, letter, fontsize=F_PANEL, fontweight="bold")
    if title:
        label(fig, x_mm + 4.5, y_mm + 0.45, title, fontsize=F_TITLE, fontweight="semibold")


def save(fig, name):
    for ext in ("svg", "pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}")
    plt.close(fig)
    print("wrote", FIG / f"{name}.svg/.pdf/.png")
