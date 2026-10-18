import json, os, subprocess, sys, tempfile
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "stamp.py"); ok = True
def run(*a): return subprocess.run([sys.executable, S, *a], capture_output=True, text=True).returncode
def expect(n, g, w):
    global ok; k = g == w; ok &= k; print(("ok   " if k else "FAIL ") + f"{n}: exit {g} (want {w})")
d = tempfile.mkdtemp(); src = os.path.join(d, "src"); os.makedirs(src)
open(os.path.join(src, "a.txt"), "w").write("one"); os.makedirs(os.path.join(src, "node_modules")); open(os.path.join(src, "node_modules", "x"), "w").write("junk")
v = os.path.join(d, "v.json"); json.dump({"verdict": "PASS"}, open(v, "w"))
expect("unstamped verdict is not evidence", run("check", v, "--root", src), 1)
expect("stamp", run("stamp", v, "--root", src, "--pipeline-version", "50"), 0)
expect("fresh right after stamp", run("check", v, "--root", src, "--pipeline-version", "50"), 0)
open(os.path.join(src, "node_modules", "x"), "w").write("changed junk")
expect("ignored directories do not invalidate", run("check", v, "--root", src), 0)
open(os.path.join(src, "a.txt"), "w").write("two")
expect("source edit makes the verdict stale", run("check", v, "--root", src), 1)
open(os.path.join(src, "a.txt"), "w").write("one")
expect("reverting the edit makes it fresh again", run("check", v, "--root", src, "--pipeline-version", "50"), 0)
expect("pipeline version bump voids old verdicts", run("check", v, "--root", src, "--pipeline-version", "51"), 1)
inside = os.path.join(src, "verdict.json"); json.dump({"verdict": "PASS"}, open(inside, "w"))
expect("verdict stored inside the root can be stamped", run("stamp", inside, "--root", src), 0)
expect("...and is still fresh afterwards (its own file is not hashed)", run("check", inside, "--root", src), 0)
os.remove(inside)
os.symlink(os.path.join(d, "nowhere"), os.path.join(src, "dangling"))
expect("an unreadable file (dangling symlink) is exit 2, not a traceback", run("check", v, "--root", src), 2)
os.remove(os.path.join(src, "dangling"))
empty = os.path.join(d, "empty"); os.makedirs(empty)
expect("empty tree cannot be stamped", run("stamp", v, "--root", empty), 2)
ok &= subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_release_regressions.py")]).returncode == 0
sys.exit(0 if ok else 1)
