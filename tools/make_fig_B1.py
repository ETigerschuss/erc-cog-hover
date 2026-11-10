"""Assemble Fig. B1 (B2 preliminary results) from the source panels.

Sources (copied into proposal/figures/src/ by this script when run with --import <dfg_repo_path>):
  mesh_em.png        MESH: 3D meshes + EM cut-out of a putative gap junction (MOS_L <-> VS2_L)
  gj_motif.png       electrical wiring motif VS1-4 -> MOS MN, HS -> MOS and MOT MN (Falt et al. 2026)
  pd_pred.png        measured vs predicted preferred directions of MOS and MOT RMNs (Falt et al. 2026)
  tier1_traces.png   Tier-1 model output in MESH: LPTC Vm, MN spikes, pseudopupil, polar
  ct_eristalis_m.png micro-CT, male Eristalis, three retinal muscles in red (Kviatko et al.)
  ct_melanostoma.png micro-CT, male Melanostoma, the MIO in red (Kviatko et al.)
  fig_B1e_mio_controversial.png   panel g from code/hover/binocular_search.py (male vs female, both eyes)

Usage:  python3 tools/make_fig_B1.py [--import /home/user/dfg-eristalis]
Output: proposal/figures/fig_B1_preliminary.png (3400 px wide, 17 cm at 500 dpi)
"""
import pathlib
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIG = ROOT / "proposal" / "figures"
SRC = FIG / "src"
SRC.mkdir(parents=True, exist_ok=True)

IMPORT = {
    "mesh_em.png": "mesh and overlaps and em picture.png",
    "gj_motif.png": "circuit motif drosophila.png",
    "pd_pred.png": "preferred direction MOS and MOT and prediction.png",
    "tier1_traces.png": "4 rows tier1 simulation right eye.png",
    "ct_eristalis_m.png": "eristalis_60286_ET_M_ALL_01.png",
    "ct_melanostoma.png": "melanostoma zoom mio.png",
}

if "--import" in sys.argv:
    dfg = pathlib.Path(sys.argv[sys.argv.index("--import") + 1])
    for dst, src in IMPORT.items():
        im = Image.open(dfg / src)
        im.load()
        if max(im.size) > 1600:  # keep the repository small
            s = 1600 / max(im.size)
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        big = max(im.size) > 900
        im.convert("RGB").save((SRC / dst).with_suffix(".jpg" if big else ".png"), quality=90)
        print("imported", dst, im.size)

W = 3420
ROW1_H = 720
PAD = 24
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
FONT_S = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)


def fit(im: Image.Image, w: int, h: int, crop=None) -> Image.Image:
    if crop:
        im = im.crop(crop)
    s = min(w / im.width, h / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), "white")
    canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas


def load(name):
    p = SRC / name
    if not p.exists():
        p = p.with_suffix(".jpg")
    return Image.open(p).convert("RGB")


# ---- row 1: a MESH EM, b motif, c measured vs predicted, d Tier-1 traces, e CT
mesh = load("mesh_em.png")
mw, mh = mesh.size
# left pane = 3D meshes (x < 0.50 w, y < 0.85 h); right pane = EM (x > 0.56 w, y < 0.84 h)
em = fit(mesh, 540, ROW1_H, crop=(int(0.565 * mw), 0, mw, int(0.84 * mh)))
mesh3d = fit(mesh, 400, ROW1_H, crop=(0, 0, int(0.42 * mw), int(0.80 * mh)))
motif = fit(load("gj_motif.png"), 470, ROW1_H)
pd = fit(load("pd_pred.png"), 400, ROW1_H)
traces = fit(load("tier1_traces.png"), 820, ROW1_H)
ct = fit(load("ct_eristalis_m.png"), 650, ROW1_H, crop=None)
row1 = [("a", mesh3d), ("", em), ("b", motif), ("c", pd), ("d", traces), ("e", ct)]
widths = [p[1].width for p in row1]
assert sum(widths) + PAD * (len(row1) - 1) <= W, (sum(widths), W)

# ---- row 2: f MIO controversial stimulus (full width) with the Melanostoma MIO inset on the left
panel_f = Image.open(FIG / "fig_B1e_mio_controversial.png").convert("RGB")
mel = load("ct_melanostoma.png")
mel_w = 600
mel = fit(mel, mel_w, int(mel_w * mel.height / mel.width))
f_w = W - mel_w - PAD
s = f_w / panel_f.width
panel_f = panel_f.resize((f_w, int(panel_f.height * s)), Image.LANCZOS)
ROW2_H = max(panel_f.height, mel.height) + 70

H = ROW1_H + 70 + PAD + ROW2_H + 10
out = Image.new("RGB", (W, H), "white")
draw = ImageDraw.Draw(out)
x = 0
y0 = 70
for lab, im in row1:
    out.paste(im, (x, y0))
    if lab:
        draw.text((x + 6, 2), lab, fill="black", font=FONT)
    x += im.width + PAD
# small sub-labels
draw.text((8, y0 + ROW1_H - 44), "MESH meshes", fill="#333", font=FONT_S)
draw.text((mesh3d.width + PAD + 8, y0 + ROW1_H - 44), "EM: MOS↔VS2 apposition", fill="#333", font=FONT_S)
draw.text((x - ct.width + 8, y0 + ROW1_H - 44), "♂ Eristalis: 3 retinal muscles", fill="#333", font=FONT_S)

y1 = y0 + ROW1_H + PAD + 60
draw.text((6, y1 - 64), "f", fill="black", font=FONT)
out.paste(mel, (0, y1 + (ROW2_H - 70 - mel.height) // 2))
draw.text((8, y1 + ROW2_H - 110), "♂ Melanostoma: MIO (red)", fill="#333", font=FONT_S)
draw.text((mel_w + PAD + 6, y1 - 64), "g", fill="black", font=FONT)
out.paste(panel_f, (mel_w + PAD, y1 + (ROW2_H - 70 - panel_f.height) // 2))

out.save(FIG / "fig_B1_preliminary.png", dpi=(500, 500))
print("wrote", FIG / "fig_B1_preliminary.png", out.size)
