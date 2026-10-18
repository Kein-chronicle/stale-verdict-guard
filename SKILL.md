---
name: verdict-stamp
description: Bind every review verdict, QA pass or sign-off to the fingerprint of the exact source it judged, so a pass cannot outlive the code (or the rules) it judged. Use when pipelines show "PASS" for builds that changed afterwards, when you bump a pipeline/rubric version and must void past verdicts, or when agents might reuse a stale approval.
---

# verdict-stamp

A verdict without a source fingerprint is a claim, not evidence. A verdict made under rubric version 49 says nothing
under version 50 ("when the pipeline version rises, every past judgement becomes void").

- `stamp` writes `{fingerprint, files, at, pipeline_version}` into the verdict file (hash of relative paths + file hashes;
  ignores `.git`, `node_modules`, build outputs - extend with `--ignore`).
- `check` recomputes. Exit 1 when: no stamp (UNSTAMPED), source changed (STALE), or pipeline version differs (STALE).
- An empty tree cannot be stamped (hashing nothing would "freshly" match forever).
- Order that works: change -> (re)run measurements -> write verdict -> **stamp** -> check. Never stamp before the verdict exists.
- Related: re-judging should happen on the *measuring* step, not by editing the stamp; and `freeze`-style archiving of an
  already-shipped artifact should not re-run checks (nothing to revert) - make that an explicit flag, not an accident.

```bash
python3 scripts/stamp.py stamp verdict.json --root ./src --pipeline-version 50
python3 scripts/stamp.py check verdict.json --root ./src --pipeline-version 50
python3 tests/run.py
```

Source symlinks are rejected (exit 2), including linked directories that a normal directory walk would skip. Materialize a stable source snapshot first. Fingerprints detect changes; they are not signatures, and someone who can edit both source and verdict can forge a new stamp.
