#!/bin/bash
# Download the 4K originals listed in footage/manifest.json into footage/ (git-ignored).
# The Drive files must be shared "anyone with the link"; otherwise download them by hand into footage/.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY' | while read -r name id; do
import json
for f in json.load(open("footage/manifest.json"))["files"]:
    print(f["name"], f["drive_id"])
PY
  out="footage/$name.MP4"
  [ -s "$out" ] && continue
  echo "fetch $name"
  curl -sS -L --retry 4 -o "$out.part" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
  mv "$out.part" "$out"
done
