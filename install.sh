#!/usr/bin/env bash
# Sync this checkout into a tool's skills directory.
#   ./install.sh                  -> ~/.config/opencode/skills/bytesmith
#   ./install.sh /path/to/skills  -> /path/to/skills/bytesmith
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_ROOT="${1:-$HOME/.config/opencode/skills}"
DEST="$DEST_ROOT/bytesmith"

# The payload is the skill itself; dev tooling rides along so the test suites
# travel with the install.
PAYLOAD=(
  SKILL.md
  checklist.md
  countermeasures.md
  report-template.html
  report-styles.css
  examples
  fixture
)

mkdir -p "$DEST"
for item in "${PAYLOAD[@]}"; do
  rm -rf "${DEST:?}/$item"
  cp -r "$SRC/$item" "$DEST/$item"
done

echo "installed -> $DEST"
for item in "${PAYLOAD[@]}"; do
  printf '  %s\n' "$item"
done

# Fail loudly if the payload is broken, rather than leaving a dead skill behind.
python3 - "$DEST" <<'PY'
import sys, pathlib, re
d = pathlib.Path(sys.argv[1])
skill = (d / "SKILL.md").read_text()
m = re.search(r"^---\n(.*?)\n---", skill, re.S)
if not m:
    raise SystemExit("FAIL: SKILL.md has no YAML frontmatter")
if "name: bytesmith" not in m.group(1):
    raise SystemExit("FAIL: frontmatter is missing name: bytesmith")
cl = (d / "checklist.md").read_text()
pts = re.findall(r"^\*\*(\d+)\. .+?\*\* — \*w ([\d.]+)\*", cl, re.M)
if len(pts) != 36:
    raise SystemExit(f"FAIL: expected 36 checklist points, found {len(pts)}")
if round(sum(float(w) for _, w in pts), 2) != 37.5:
    raise SystemExit("FAIL: checklist weights do not sum to 37.5")
print("  payload verified: frontmatter ok, 36 points, Σw 37.5")
PY
