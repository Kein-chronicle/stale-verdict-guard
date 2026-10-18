#!/usr/bin/env python3
"""verdict-stamp: bind a verdict to the exact source it judged.
usage: stamp.py stamp verdict.json --root DIR [--ignore NAME ...] [--pipeline-version V]
       stamp.py check verdict.json --root DIR [--ignore NAME ...] [--pipeline-version V]
exit 0 fresh | 1 stale/unstamped | 2 bad input"""
import argparse, hashlib, json, os, sys, time
DEFAULT_IGNORE = {".git", "node_modules", "__pycache__", ".DS_Store", "dist", "build", "DerivedData"}

def tree_hash(root, ignore, skip=None):
    """skip: a file to leave out of the hash (the verdict file itself, when it lives inside the tree)."""
    h = hashlib.sha256(); n = 0
    def unreadable(error):
        print("cannot traverse source tree"); sys.exit(2)
    for d, dirs, files in os.walk(root, onerror=unreadable):
        dirs[:] = sorted(x for x in dirs if x not in ignore)
        if any(os.path.islink(os.path.join(d, x)) for x in dirs):
            print("source contains a linked directory: cannot fingerprint its contents"); sys.exit(2)
        for f in sorted(files):
            if f in ignore: continue
            p = os.path.join(d, f); rel = os.path.relpath(p, root)
            if os.path.islink(p):
                print("source contains a linked file: materialize it before stamping"); sys.exit(2)
            if skip and os.path.realpath(p) == skip: continue
            try: digest = hashlib.sha256(open(p, "rb").read()).digest()
            except OSError as e: print(f"cannot read {rel}: {e.strerror}"); sys.exit(2)       # dangling symlink, permissions: never silently skipped
            h.update(rel.encode()); h.update(b"\0"); h.update(digest); n += 1
    return h.hexdigest(), n

ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["stamp", "check"]); ap.add_argument("verdict")
ap.add_argument("--root", required=True); ap.add_argument("--ignore", nargs="*", default=[]); ap.add_argument("--pipeline-version")
a = ap.parse_args()
if not os.path.isdir(a.root): print("bad root"); sys.exit(2)
ign = DEFAULT_IGNORE | set(a.ignore); fp, n = tree_hash(a.root, ign, os.path.realpath(a.verdict))
if n == 0: print("root has no files: an empty tree cannot be stamped"); sys.exit(2)
try: v = json.load(open(a.verdict))
except Exception as e: print(f"bad verdict file: {e}"); sys.exit(2)
if not isinstance(v, dict): print("verdict must be an object"); sys.exit(2)
if a.cmd == "stamp":
    v["stamp"] = {"fingerprint": fp, "files": n, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "pipeline_version": a.pipeline_version}
    json.dump(v, open(a.verdict, "w"), indent=1); print(f"stamped {n} files"); sys.exit(0)
s = v.get("stamp")
if not s: print("UNSTAMPED: a verdict that is not bound to a source fingerprint is a claim, not evidence"); sys.exit(1)
if not isinstance(s, dict) or not isinstance(s.get("fingerprint"), str): print("bad stamp"); sys.exit(2)
if s["fingerprint"] != fp: print("STALE: source changed after this verdict - the judgement no longer applies"); sys.exit(1)
if a.pipeline_version and s.get("pipeline_version") != a.pipeline_version:
    print(f"STALE: verdict was made under pipeline {s.get('pipeline_version')}, now {a.pipeline_version} - past verdicts are void"); sys.exit(1)
print("fresh"); sys.exit(0)
