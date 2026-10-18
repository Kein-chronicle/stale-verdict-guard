#!/usr/bin/env bash
cd "$(dirname "$0")/.."
run() { printf '$ %s\n' "$*"; "$@"; printf '[exit %s]\n\n' "$?"; }
tmp=.demo-tmp; rm -rf "$tmp"; mkdir -p "$tmp/src"; trap 'rm -rf "$tmp"' EXIT
echo "export const price = 10;" > "$tmp/src/app.js"; echo '{"verdict": "PASS"}' > "$tmp/verdict.json"
echo "# A bare verdict file is not evidence"
run python3 scripts/stamp.py check "$tmp/verdict.json" --root "$tmp/src"
echo "# Stamp it against the source it judged"
run python3 scripts/stamp.py stamp "$tmp/verdict.json" --root "$tmp/src" --pipeline-version 3
run python3 scripts/stamp.py check "$tmp/verdict.json" --root "$tmp/src" --pipeline-version 3
echo "# The source changes after the verdict: the pass is void"
echo "export const price = 11;" > "$tmp/src/app.js"
run python3 scripts/stamp.py check "$tmp/verdict.json" --root "$tmp/src" --pipeline-version 3
echo "# Revert the change: fresh again. Bump the pipeline version: void again"
echo "export const price = 10;" > "$tmp/src/app.js"
run python3 scripts/stamp.py check "$tmp/verdict.json" --root "$tmp/src" --pipeline-version 3
run python3 scripts/stamp.py check "$tmp/verdict.json" --root "$tmp/src" --pipeline-version 4
