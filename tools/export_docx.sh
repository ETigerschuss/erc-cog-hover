#!/usr/bin/env bash
# Export the proposal drafts to .docx so the text can be pasted into the OFFICIAL ERC B1/B2 templates
# (download them from the submission system; the ERC requires its templates, IfA p. 27).
# Usage: tools/export_docx.sh   -> writes build/*.docx
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
for f in proposal/B1_cover_page.md proposal/B1_PartI_synopsis.md proposal/B1_CV_track_record.md \
         proposal/B2_PartII.md proposal/references.md; do
  pandoc "$f" -o "build/$(basename "$f" .md).docx"
  echo "build/$(basename "$f" .md).docx"
done
