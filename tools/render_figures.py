"""Render the SVG figures in proposal/figures/ to PNG (and PDF) with the bundled Chromium.

Usage: python3 tools/render_figures.py [--scale 3]
Requires Node + Playwright (pre-installed in the cloud environment; locally: `npm i playwright`).
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIG = ROOT / "proposal" / "figures"
scale = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 3

JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [svgPath, pngPath, pdfPath, scale] = process.argv.slice(2);
  const svg = fs.readFileSync(svgPath, 'utf8');
  const m = svg.match(/width="(\d+)"\s+height="(\d+)"/);
  const w = parseInt(m[1]), h = parseInt(m[2]);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: parseInt(scale) });
  await page.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
  await page.waitForTimeout(300);
  await page.screenshot({ path: pngPath, clip: { x: 0, y: 0, width: w, height: h } });
  await page.pdf({ path: pdfPath, width: `${w}px`, height: `${h}px`, printBackground: true, pageRanges: '1' });
  await browser.close();
  console.log(pngPath);
})().catch(e => { console.error(e); process.exit(1); });
"""
js_file = ROOT / "tools" / "_render_svg.js"
js_file.write_text(JS)
for svg in sorted(FIG.glob("*.svg")):
    png = svg.with_suffix(".png")
    pdf = svg.with_suffix(".pdf")
    subprocess.run(["node", str(js_file), str(svg), str(png), str(pdf), str(scale)], check=True)
js_file.unlink()
