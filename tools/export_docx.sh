#!/usr/bin/env bash
# Export the proposal drafts to .docx so the text can be pasted into the OFFICIAL ERC B1/B2 templates
# (download them from the submission system; the ERC requires its templates, IfA p. 27).
# Figures referenced as "**Figure X (path.svg).**" are embedded from their 600 dpi PNG twins.
# Usage: tools/export_docx.sh   -> writes build/*.docx
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
for f in proposal/B1_cover_page.md proposal/B1_PartI_synopsis.md proposal/B1_CV_track_record.md \
         proposal/B2_PartII.md proposal/references.md; do
  python3 - "$f" <<'PY' | pandoc -f gfm -o "build/$(basename "$f" .md).docx" --resource-path=.
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
t = re.sub(r"</?div[^>]*>", "", t)
t = re.sub(r"\*\*Figure ([A-Z0-9]+) \(([^)]+?)\.(?:svg|png)\)\.\*\*", r"![](\2.png){width=17cm}\n\n**Figure \1.**", t)
sys.stdout.write(t)
PY
  echo "build/$(basename "$f" .md).docx"
done
