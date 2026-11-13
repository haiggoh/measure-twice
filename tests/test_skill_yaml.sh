#!/usr/bin/env bash
# Strict-YAML frontmatter tests for every skills/*/SKILL.md in the repo.
#
# Why: Claude Code's own loader is lenient, but strict YAML parsers (PyYAML,
# claude.ai upload validation, Cowork) reject a plain scalar whose value contains
# a ": " sequence — the whole file fails to parse, not just one field.
#
# Requires a python3 with PyYAML (test-only): the system python3, else the pipx
# pytest venv; exits 2 (same convention as test_hook.sh's jq requirement) when
# neither exists.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

pass=0; fail=0
check() { if [ "$1" -eq 0 ]; then echo "  PASS: $2"; pass=$((pass+1)); else echo "  FAIL: $2"; fail=$((fail+1)); fi; }

PY="$(command -v python3)"
"$PY" -c "import yaml" >/dev/null 2>&1 || PY="$HOME/.local/pipx/venvs/pytest/bin/python"
"$PY" -c "import yaml" >/dev/null 2>&1 || { echo "pyyaml required for tests (try: pipx install pytest)"; exit 2; }

echo "== Strict YAML parse of every skills/*/SKILL.md frontmatter =="
OUT="$("$PY" - "$HERE/.." <<'PYEOF'
import glob, os, re, sys
import yaml

root = sys.argv[1]
files = sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md")))
if not files:
    print("NOFILES")
    sys.exit(2)

bad = 0
for f in files:
    rel = os.path.relpath(f, root)
    try:
        with open(f, encoding="utf-8") as fh:
            txt = fh.read()
        m = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", txt, re.S)
        if not m:
            print(f"FAIL {rel}: no frontmatter block")
            bad += 1
            continue
        fm = m.group(1)
        # Duplicate top-level keys: PyYAML silently keeps the last, but js-yaml (the
        # parser class behind several loaders) rejects them. Column-0 key lines only,
        # so a colon inside a quoted scalar value cannot false-positive.
        for key in ("name", "description"):
            hits = len(re.findall(r"^%s:" % key, fm, re.M))
            if hits != 1:
                print(f"FAIL {rel}: '{key}' appears {hits}x in frontmatter (strict parsers reject duplicates)")
                bad += 1
        d = yaml.safe_load(fm)
    except Exception as e:
        first = str(e).splitlines()[0][:160] if str(e) else ""
        print(f"FAIL {rel}: {type(e).__name__}: {first}")
        bad += 1
        continue
    if not isinstance(d, dict):
        print(f"FAIL {rel}: frontmatter parsed as {type(d).__name__}, expected a mapping")
        bad += 1
        continue
    for key in ("name", "description"):
        v = d.get(key)
        if not isinstance(v, str) or not v.strip():
            print(f"FAIL {rel}: '{key}' missing or empty after strict parse")
            bad += 1

if bad == 0:
    print(f"OK {len(files)} file(s) strict-parsed")
sys.exit(1 if bad else 0)
PYEOF
)"
status=$?
printf '%s\n' "$OUT"
if [ "$status" -eq 2 ]; then
  echo "  FAIL: no SKILL.md files found under skills/"
  fail=$((fail+1))
else
  check "$status" "every skills/*/SKILL.md frontmatter strict-parses with non-empty name+description"
fi

echo
echo "PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ]
