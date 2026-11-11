"""Render the proposal drafts to PDF in the ERC format and report real page counts.

Format (IfA p. 27, 36): A4, 11 pt serif, single spacing, 2 cm side margins, 1.5 cm bottom, header on
every page with "Serbe-Kamp | HOVER | Part B1/B2". Figures referenced as
`**Figure X (proposal/figures/name.png).**` are embedded at full text width above their caption.

Usage: python3 tools/render_pdf.py        -> build/*.pdf and a page-count table
Needs pandoc, Node + Playwright, and pypdf.
"""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "proposal"
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)

CSS = """
@page { size: A4; margin: 18mm 20mm 15mm 20mm; }
html { hyphens: auto; }
body { font-family: 'Times New Roman', 'Liberation Serif', 'DejaVu Serif', serif; font-size: 11pt; line-height: 1.15; color: #111; }
h1 { font-size: 15pt; line-height: 1.15; margin: 0 0 4pt 0; color: #14315c; }
h2 { font-size: 12pt; margin: 9pt 0 3.5pt 0; padding-bottom: 1pt; color: #14315c; border-bottom: 0.6pt solid #b9c4d6; break-after: avoid; }
h3 { font-size: 11pt; margin: 7pt 0 2.5pt 0; color: #14315c; break-after: avoid; }
p { margin: 0 0 4.5pt 0; text-align: justify; orphans: 2; widows: 2; }
ul, ol { margin: 0 0 4.5pt 0; padding-left: 16pt; }
li { margin-bottom: 1.5pt; text-align: justify; }
.key { background: #eef2f8; border-left: 2.4pt solid #14315c; padding: 4.5pt 8pt 0.5pt 8pt; margin: 3pt 0 6pt 0; break-inside: avoid; }
table { border-collapse: collapse; font-size: 9.5pt; line-height: 1.12; margin: 4pt 0 7pt 0; width: 100%; }
th { background: #e8edf5; text-align: left; border-top: 0.8pt solid #14315c; border-bottom: 0.8pt solid #14315c; padding: 2pt 4pt; vertical-align: bottom; }
td { border-bottom: 0.4pt solid #b5b5b5; padding: 2pt 4pt; vertical-align: top; }
tr { break-inside: avoid; }
img.fig { width: 100%; display: block; margin: 5pt 0 3pt 0; }
.caption { font-size: 9.5pt; line-height: 1.12; margin-bottom: 7pt; break-before: avoid; }
code { font-size: 9.5pt; }
"""


def md_to_html(md_text: str) -> str:
    md_text = re.sub(r"<!--.*?-->", "", md_text, flags=re.S)
    # embed figures above their caption
    def fig(m):
        path = (ROOT / m.group(2)).resolve()
        # the caption stays Markdown (so that italics render); its paragraph is classed after conversion
        return f'<img class="fig" src="file://{path}">\n\n**Figure {m.group(1)}.**'
    md_text = re.sub(r"\*\*Figure ([A-Z0-9]+) \(([^)]+)\)\.\*\*", fig, md_text)
    out = subprocess.run(["pandoc", "-f", "gfm+tex_math_dollars", "-t", "html5"], input=md_text,
                         capture_output=True, text=True, check=True)
    return re.sub(r"<p><strong>Figure ([A-Z0-9]+)\.</strong>", r'<p class="caption"><strong>Figure \1.</strong>', out.stdout)


def render(html_body: str, pdf_path: pathlib.Path, header: str) -> int:
    html = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    html_path = pdf_path.with_suffix(".html")
    html_path.write_text(html)
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://{html_path}');
  await page.pdf({{ path: '{pdf_path}', format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<div style="font-family:Times New Roman,serif;font-size:9pt;width:100%;text-align:left;padding-left:20mm;">{header}</div>',
    footerTemplate: '<div style="font-family:Times New Roman,serif;font-size:9pt;width:100%;text-align:center;"><span class="pageNumber"></span></div>',
    margin: {{ top: '18mm', bottom: '15mm', left: '20mm', right: '20mm' }} }});
  await browser.close();
}})().catch(e => {{ console.error(e); process.exit(1); }});
"""
    subprocess.run(["node", "-e", js], check=True)
    from pypdf import PdfReader
    return len(PdfReader(str(pdf_path)).pages)


def split(text: str, marker: str):
    i = text.find(marker)
    return (text, "") if i < 0 else (text[:i], text[i:])


parts = {}
cover = (P / "B1_cover_page.md").read_text()
part1_all = (P / "B1_PartI_synopsis.md").read_text()
part1, part1_refs = split(part1_all, "\n## References")
cv = (P / "B1_CV_track_record.md").read_text()
b2_all = (P / "B2_PartII.md").read_text()
b2, b2_tail = split(b2_all, "\n## Funding ID")
refs = (P / "references.md").read_text()

parts["B1_cover"] = (render(md_to_html(cover), BUILD / "B1_cover.pdf", "Serbe-Kamp | HOVER | Part B1"), None)
parts["B1_PartI (limit 5)"] = (render(md_to_html(part1), BUILD / "B1_PartI.pdf", "Serbe-Kamp | HOVER | Part B1"), 5)
parts["B1_CV (limit 4)"] = (render(md_to_html(cv), BUILD / "B1_CV.pdf", "Serbe-Kamp | HOVER | Part B1"), 4)
parts["B2_PartII (limit 7)"] = (render(md_to_html(b2), BUILD / "B2_PartII.pdf", "Serbe-Kamp | HOVER | Part B2"), 7)
# full documents for reading
render(md_to_html(cover + "\n\n<div style='page-break-before:always'></div>\n\n" + part1_all +
                  "\n\n<div style='page-break-before:always'></div>\n\n" + cv), BUILD / "B1_full.pdf", "Serbe-Kamp | HOVER | Part B1")
render(md_to_html(b2_all + "\n\n<div style='page-break-before:always'></div>\n\n" + refs), BUILD / "B2_full.pdf", "Serbe-Kamp | HOVER | Part B2")

ok = True
for name, (pages, limit) in parts.items():
    flag = "ok" if limit is None or pages <= limit else "FAIL"
    ok &= flag == "ok"
    print(f"[{flag}] {name}: {pages} page(s)")
print(json.dumps({k: v[0] for k, v in parts.items()}))
raise SystemExit(0 if ok else 1)
