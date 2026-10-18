# stale-verdict-guard

**Bind a pass/fail verdict to a fingerprint of the source it judged, so an edit after review makes the verdict stale.**

[![test](https://github.com/Kein-chronicle/stale-verdict-guard/actions/workflows/test.yml/badge.svg)](https://github.com/Kein-chronicle/stale-verdict-guard/actions/workflows/test.yml) ![license](https://img.shields.io/badge/license-MIT-blue.svg) ![dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)

## Why

A verdict file that is not tied to the exact source is a claim, not evidence. Stamp it once; any later change to the files under the root (build output such as `node_modules`, `dist` and `build` is ignored by default) voids the pass, and so does a different `--pipeline-version` on `check`.

## Install

**As a Claude Code skill** (Claude uses it when the task matches the skill description):

```sh
git clone https://github.com/Kein-chronicle/stale-verdict-guard.git ~/.claude/skills/verdict-stamp
```

For a single project, clone into `<project>/.claude/skills/verdict-stamp` instead, then start a new Claude Code session.

**As plain scripts:**

```sh
git clone https://github.com/Kein-chronicle/stale-verdict-guard.git
cd stale-verdict-guard
```

**Requires:** Python 3.10+.

## Quick start

Stamp, edit, check:

```console
$ bash examples/demo.sh
# A bare verdict file is not evidence
$ python3 scripts/stamp.py check .demo-tmp/verdict.json --root .demo-tmp/src
UNSTAMPED: a verdict that is not bound to a source fingerprint is a claim, not evidence
[exit 1]

# Stamp it against the source it judged
$ python3 scripts/stamp.py stamp .demo-tmp/verdict.json --root .demo-tmp/src --pipeline-version 3
stamped 1 files
[exit 0]

$ python3 scripts/stamp.py check .demo-tmp/verdict.json --root .demo-tmp/src --pipeline-version 3
fresh
[exit 0]

# The source changes after the verdict: the pass is void
$ python3 scripts/stamp.py check .demo-tmp/verdict.json --root .demo-tmp/src --pipeline-version 3
STALE: source changed after this verdict - the judgement no longer applies
[exit 1]

# Revert the change: fresh again. Bump the pipeline version: void again
$ python3 scripts/stamp.py check .demo-tmp/verdict.json --root .demo-tmp/src --pipeline-version 3
fresh
[exit 0]

$ python3 scripts/stamp.py check .demo-tmp/verdict.json --root .demo-tmp/src --pipeline-version 4
STALE: verdict was made under pipeline 3, now 4 - past verdicts are void
[exit 1]
```

The output above is real: it is produced by the files in `examples/`.

## Use it on your own files

```sh
python3 scripts/stamp.py stamp verdict.json --root src/ --pipeline-version 1
python3 scripts/stamp.py check verdict.json --root src/ --pipeline-version 1
```

Sample inputs for every file format are in `examples/` and `tests/`; the details are in [SKILL.md](SKILL.md).

## What it checks

- `stamp` writes a content fingerprint and a pipeline version into the verdict JSON.
- `check` recomputes it: `fresh`, `STALE` or `UNSTAMPED`. `check` only compares the pipeline version if you pass `--pipeline-version`; a verdict file inside `--root` is left out of the hash; an unreadable file is exit `2`.
- Reverting an edit makes the verdict fresh again.
- An empty tree cannot be stamped.

## Limits

- A local fingerprint, not a cryptographic signature: anyone who can edit the verdict file can restamp it.

## Related projects

These solve neighbouring problems; use them when they fit better.

- **in-toto / Sigstore cosign attestations**: signed supply-chain attestations; heavier and cryptographic

## More from the same collection

Small, tested tools that grew out of running AI agents and game/app pipelines for months:

- [**llm-verdict-gate**](https://github.com/Kein-chronicle/llm-verdict-gate): Make AI and human review gates impossible to pass by silence: machine-parsed PASS/FAIL, missing verdict = FAIL.
- [**ci-gate-forgery-test**](https://github.com/Kein-chronicle/ci-gate-forgery-test): Prove your CI gates can actually fail: feed each gate forged-bad, empty and missing input and flag the ones that stay green.
- [**agent-definition-of-done-gate**](https://github.com/Kein-chronicle/agent-definition-of-done-gate): A completion rule for AI agents: a human can't close a gate that has an automated measurement, and parking work needs evidence.

## Development

```sh
python3 tests/run.py
```

The tests include inputs that are supposed to be rejected, so a green run also shows the checks can fail. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

If this saved you a debugging session, a star helps other people find it. Bug reports and failing test cases are even better.

<sub>Keywords: quality-gates, ci, attestation, claude-code, claude-skills, agent-skills, provenance</sub>
