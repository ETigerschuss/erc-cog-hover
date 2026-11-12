"""Compliance checks against the ERC-2027-CoG rules (IfA v11.0).

- Abstract: <= 2000 characters (form field) and identical on the B1 cover page.
- Acronym: <= 20 characters.
- Page counts of the rendered PDFs in build/ (run tools/render_pdf.py first):
  B1 Part I <= 5, CV <= 4, B2 Part II <= 7 (references and Funding ID excluded).
- Resources text <= 8000 characters.
- Budget: sums the budget-csv block per beneficiary; indirect = 25 % of (A + C); total <= EUR 2,000,000.

Exit code 1 if any check fails.
"""
import csv
import io
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "proposal"
ok = True


def check(label, passed, detail):
    global ok
    ok &= passed
    print(f"[{'ok' if passed else 'FAIL'}] {label}: {detail}")


def block(text, name):
    m = re.search(rf"<!-- {name} START -->\n(.*?)\n<!-- {name} END -->", text, re.S)
    return m.group(1) if m else None


abstract = block((P / "abstract.md").read_text(), "ABSTRACT")
check("Abstract length", abstract is not None and len(abstract) <= 2000, f"{len(abstract or '')} / 2000 characters")
cover = (P / "B1_cover_page.md").read_text()
check("Abstract identical on B1 cover page", block(cover, "ABSTRACT") == abstract, "cover page vs abstract.md")
acr = re.search(r"\*\*Acronym:\*\*\s*(\S+)", cover)
check("Acronym", bool(acr) and len(acr.group(1)) <= 20, f"{acr.group(1) if acr else '?'} (max 20 characters)")

# Page limits: the rendered PDFs are authoritative (tools/render_pdf.py). A word count is printed
# for orientation only, because figures and tables make words per page meaningless.
try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None
for fname, limit, cut, pdf in [
    ("B1_PartI_synopsis.md", 5, r"\n## References", "B1_PartI.pdf"),
    ("B1_CV_track_record.md", 4, None, "B1_CV.pdf"),
    ("B2_PartII.md", 7, r"\n## Funding ID", "B2_PartII.pdf"),
]:
    src = P / fname
    t = src.read_text()
    body = re.split(cut, t)[0] if cut else t
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    words = len(body.split())
    f = ROOT / "build" / pdf
    if PdfReader is None or not f.exists():
        check(f"{fname} pages", False, f"no rendered PDF; run tools/render_pdf.py ({words} words)")
        continue
    pages = len(PdfReader(str(f)).pages)
    stale = f.stat().st_mtime < src.stat().st_mtime
    check(f"{fname} pages", pages <= limit and not stale,
          f"{pages} / {limit} pages in build/{pdf}" + (" (PDF older than the text: re-run tools/render_pdf.py)" if stale else "")
          + f"; {words} words")

ptxt = (P / "PartA_budget_resources.md").read_text()
res = block(ptxt, "RESOURCES")
check("Resources text", res is not None and len(res) <= 8000, f"{len(res or '')} / 8000 characters")

m = re.search(r"```budget-csv\n(.*?)```", ptxt, re.S)
rows = list(csv.DictReader(io.StringIO(m.group(1)))) if m else []
per = {}
for r in rows:
    b = r.get("beneficiary", "ALL")
    cat = r["category"].split(".")[0]
    per.setdefault(b, {}).setdefault(cat, 0)
    per[b][cat] += int(r["amount"])
grand = 0
for b, sums in per.items():
    base = sums.get("A", 0) + sums.get("C", 0)
    indirect = round(0.25 * base)
    total = base + sums.get("B", 0) + sums.get("D", 0) + indirect
    grand += total
    print(f"       {b}: " + ", ".join(f"{k}={v:,}" for k, v in sorted(sums.items()))
          + f", E={indirect:,} -> total {total:,}")
check("Budget cap", grand <= 2_000_000, f"total EUR {grand:,} (cap 2,000,000 without additional funding)")

sys.exit(0 if ok else 1)
