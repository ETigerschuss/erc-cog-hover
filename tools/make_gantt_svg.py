"""Draw the HOVER Gantt chart (Fig. B3) as SVG from the task list below.

Usage: python3 tools/make_gantt_svg.py  -> proposal/figures/fig_B3_gantt.svg
Then render to PNG with tools/render_figures.py. Keep this list in sync with proposal/gantt.md.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "proposal" / "figures" / "fig_B3_gantt.svg"

# (work package, label, start month, end month)  months are 1-based inclusive
TASKS = [
    ("WP1", "T1.1 Electrical synapses, both sexes (MESH, classifier)", 1, 18),
    ("WP1", "T1.2 Tier 1 biophysical", 1, 15),
    ("WP1", "T1.3 Tier 2 reduced (KAN reduction)", 7, 24),
    ("WP1", "T1.4 Tier 3 trainable SNN", 13, 36),
    ("WP1", "T1.5 Motor readout, efference copy", 10, 30),
    ("WP2", "T2.1 Model families by homology", 6, 24),
    ("WP2", "T2.2 Controversial stimuli in silico", 13, 24),
    ("WP2", "T2.3 Tethered Eristalis physiology (PD2, MPI-BI)", 19, 42),
    ("WP2", "T2.4 Free-flight pursuit (high risk)", 37, 48),
    ("WP2", "T2.5 Origin of the MIO (PhD 3, LMU)", 7, 48),
    ("WP3", "T3.1 Embodied simulator", 12, 27),
    ("WP3", "T3.2 Task optimisation", 25, 48),
    ("WP3", "T3.3 Analysis, motif catalogue", 37, 54),
    ("WP4", "T4.1 Active event-camera head", 13, 30),
    ("WP4", "T4.2 Motif SNNs on neuromorphic hardware", 25, 54),
    ("WP4", "T4.3 Benchmarks B-I, B-II, B-III (quadrotor)", 25, 58),
    ("WP4", "T4.4 Controversial stimuli for machines", 37, 54),
    ("WP5", "T5.1 Course modules (every semester)", 1, 60),
    ("WP5", "T5.2 Robot zoo", 19, 60),
    ("WP5", "T5.3 Community proofreading", 7, 36),
    ("WP5", "T5.4 Hoverfly watch", 13, 48),
    ("WP5", "T5.5 Releases, evaluation", 24, 60),
]
MILESTONES = [(12, "MS1"), (24, "MS2"), (30, "MS3"), (36, "MS4"), (48, "MS5"), (60, "MS6")]
COLORS = {"WP1": ("#2F5597", "#C9D8F0"), "WP2": ("#2E7D6B", "#CFE8DD"), "WP3": ("#6A4C93", "#DED3EE"),
          "WP4": ("#C55A11", "#FBD9BF"), "WP5": ("#7B2D8E", "#E8D3EE")}

LEFT, TOP, ROW, MONTH_W = 540, 70, 30, 18.5
W = int(LEFT + 60 * MONTH_W + 40)
H = int(TOP + ROW * len(TASKS) + 140)

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
     'font-family="Inter, Arial, Helvetica, sans-serif">', f'<rect width="{W}" height="{H}" fill="#fff"/>']
# year bands and month grid
for y in range(5):
    x0 = LEFT + y * 12 * MONTH_W
    fill = "#F7F7F7" if y % 2 == 0 else "#FFFFFF"
    s.append(f'<rect x="{x0:.1f}" y="{TOP - 30}" width="{12 * MONTH_W:.1f}" height="{ROW * len(TASKS) + 30}" fill="{fill}"/>')
    s.append(f'<text x="{x0 + 6 * MONTH_W:.1f}" y="{TOP - 40}" font-size="20" text-anchor="middle" fill="#333">Year {y + 1}</text>')
for m in range(0, 61, 6):
    x = LEFT + m * MONTH_W
    s.append(f'<line x1="{x:.1f}" y1="{TOP - 30}" x2="{x:.1f}" y2="{TOP + ROW * len(TASKS)}" stroke="#DDD" stroke-width="1"/>')
    s.append(f'<text x="{x:.1f}" y="{TOP - 10}" font-size="16" text-anchor="middle" fill="#666">M{m}</text>')
# rows
prev_wp = None
for i, (wp, label, a, b) in enumerate(TASKS):
    y = TOP + i * ROW
    stroke, fill = COLORS[wp]
    if wp != prev_wp:
        s.append(f'<text x="20" y="{y + 21}" font-size="20" font-weight="700" fill="{stroke}">{wp}</text>')
        if i:
            s.append(f'<line x1="20" y1="{y - 1}" x2="{W - 20}" y2="{y - 1}" stroke="#BBB" stroke-width="1"/>')
        prev_wp = wp
    s.append(f'<text x="80" y="{y + 21}" font-size="18" fill="#222">{label}</text>')
    x0 = LEFT + (a - 1) * MONTH_W
    w = (b - a + 1) * MONTH_W
    s.append(f'<rect x="{x0:.1f}" y="{y + 5}" width="{w:.1f}" height="{ROW - 10}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
# milestones
ybot = TOP + ROW * len(TASKS)
for m, name in MILESTONES:
    x = LEFT + m * MONTH_W
    s.append(f'<line x1="{x:.1f}" y1="{TOP - 30}" x2="{x:.1f}" y2="{ybot + 10}" stroke="#333" stroke-width="1.5" stroke-dasharray="6 5"/>')
    s.append(f'<polygon points="{x:.1f},{ybot + 12} {x - 9:.1f},{ybot + 24} {x:.1f},{ybot + 36} {x + 9:.1f},{ybot + 24}" fill="#333"/>')
    s.append(f'<text x="{x:.1f}" y="{ybot + 58}" font-size="18" font-weight="700" text-anchor="middle" fill="#333">{name}</text>')
s.append(f'<text x="20" y="{ybot + 96}" font-size="18" fill="#333">Milestones: MS1 (M12) electrical-synapse atlas v1 + Tier-2 model · MS2 (M24) model families + discriminating stimuli · MS3 (M30) active head, quadrotor and robot zoo running</text>')
s.append(f'<text x="20" y="{ybot + 124}" font-size="18" fill="#333">MS4 (M36) H1 decided, tethered Eristalis data complete · MS5 (M48) H2, H2b, H3 decided, motif catalogue · MS6 (M60) H4 decided, benchmark, dataset and kits released</text>')
s.append("</svg>")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(s))
print(OUT)
