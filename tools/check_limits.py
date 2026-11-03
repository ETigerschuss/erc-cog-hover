"""Rough compliance checks: abstract length and approximate page counts (~550 words/page at 11 pt)."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parents[1]
ok = True
abs_txt = (root / "proposal/abstract.md").read_text()
m = re.search(r"<!-- ABSTRACT START -->\n(.*?)\n<!-- ABSTRACT END -->", abs_txt, re.S)
n = len(m.group(1)) if m else -1
print(f"Abstract: {n} characters (limit 2000)")
ok &= 0 < n <= 2000
for f, limit in [("B1a_extended_synopsis.md", 5), ("B1b_CV_track_record.md", 4), ("B2_scientific_proposal.md", 14)]:
    t = (root / "proposal" / f).read_text()
    body = re.split(r"\n## References", t)[0]
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    words = len(body.split())
    pages = words / 550
    print(f"{f}: {words} words ~ {pages:.1f} pages (limit {limit}; figures not counted)")
    ok &= pages <= limit
sys.exit(0 if ok else 1)
