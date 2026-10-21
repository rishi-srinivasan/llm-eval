#!/usr/bin/env python3
"""Minimal Luna-vs-GLM Click bug-fix runner.

  eval.py validate                      # base fails / reference passes, per task
  eval.py run RUN [--smoke] [--models luna,glm] [--tasks echo-empty-bytes,..] [--reps 3] [--timeout 900]
  eval.py report RUN                    # results/RUN/results.jsonl -> report.md
Attempts already present on disk are skipped (no silent retries; delete to redo).
"""
import argparse, json, os, shutil, statistics as st, subprocess as sp, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
REPO = ROOT / ".cache/click.git"
IMAGE = "click-eval"
CODEX_HOME = Path.home() / ".codex"
SMOKE = {"id": "smoke", "base": "a5f5aa6d4012d256ccca24638f2642fc371e9f77", "dir": "smoke"}
HOST = "http://host.docker.internal:11434/v1"
MODELS = {  # codex `-c` overrides; Luna low reasoning, GLM provider-default reasoning (max)
    "luna": ["-m", "gpt-5.6-luna", "-c", 'model_reasoning_effort="low"'],
    "glm": ["-m", os.environ.get("GLM_MODEL", "glm-5.3-flash:cloud"),  # GLM_MODEL only for unscored smoke
             "-c", 'model_provider="ollama_host"',
            "-c", f'model_providers.ollama_host={{name="Ollama Cloud via host",base_url="{HOST}",wire_api="responses"}}',
            "-c", 'model_catalog_json="/home/eval/.codex/models.json"'],
}


def sh(cmd, **kw):
    return sp.run(cmd, capture_output=True, text=True, **kw)


def tasks():
    return json.loads((ROOT / "tasks.json").read_text())


def task_dir(t):
    return ROOT / (t.get("dir") or f"tasks/{t['id']}")


def snapshot(base, dest):
    if not REPO.exists():  # bare clone: cheap `git archive` of pinned commits, no checkout
        sp.run(["git", "clone", "--bare", "https://github.com/pallets/click", str(REPO)], check=True)
    dest.mkdir(parents=True)
    arch = sp.run(["git", "--git-dir", str(REPO), "archive", base], capture_output=True, check=True).stdout
    sp.run(["tar", "-x", "-C", str(dest)], input=arch, check=True)


def pytest(ws, args, timeout):
    """Run pytest in a throwaway network-less container."""
    t0, name = time.time(), f"grade-{time.time_ns()}"
    try:
        r = sh(["docker", "run", "--rm", "--name", name, "--network", "none", "-v", f"{ws}:/workspace", IMAGE,
                "python", "-m", "pytest", "-q", "-p", "no:cacheprovider", *args], timeout=timeout)
        return r.returncode == 0, (r.stdout + r.stderr)[-3000:], time.time() - t0
    except sp.TimeoutExpired:
        sh(["docker", "rm", "-f", name])
        return False, "grading timeout", time.time() - t0


def grade(t, patch, timeout=900):
    """Clean base snapshot + model's src patch; original tests and withheld regression tests."""
    with tempfile.TemporaryDirectory(dir=ROOT / ".cache") as d:
        ws = Path(d) / "ws"
        snapshot(t["base"], ws)
        if patch.strip():
            ap = sh(["patch", "-p1", "-s", "--no-backup-if-mismatch"], input=patch, cwd=ws)
            if ap.returncode:
                return dict(original=False, regression=False, grade_error="patch does not apply: " + (ap.stdout + ap.stderr)[-300:], grade_time=0)
        shutil.copy(task_dir(t) / "test_regression.py", ws / "tests/test_regression.py")
        ok1, o1, s1 = pytest(ws, ["tests", "--ignore=tests/test_regression.py", *[f"--deselect={x}" for x in t.get("deselect", [])]], timeout)
        ok2, o2, s2 = pytest(ws, ["tests/test_regression.py"], timeout)
    return dict(original=ok1, regression=ok2, grade_time=s1 + s2, grade_log=o1[-600:] + "\n" + o2[-1200:])


def validate():
    bad = 0
    for t in tasks():
        ref = (task_dir(t) / "reference.patch").read_text()
        b, r = grade(t, ""), grade(t, ref)
        good = b["original"] and not b["regression"] and r["original"] and r["regression"]
        bad += not good
        print(f"{t['id']}: base(orig={b['original']} regr={b['regression']}) ref(orig={r['original']} regr={r['regression']}) -> {'OK' if good else 'FAIL'}")
    sys.exit(bad)


def attempt(run, t, model, rep, timeout):
    aid = f"{t['id']}-{model}-r{rep}"
    out = run / "attempts" / aid
    if out.exists():
        return None
    out.mkdir(parents=True)
    ws, home = run / "workspaces" / aid, run / "auth" / aid
    snapshot(t["base"], ws)
    for c in (["init", "-q"], ["add", "-A"], ["-c", "user.name=e", "-c", "user.email=e@e", "commit", "-qm", "base"]):
        sh(["git", *c], cwd=ws)
    home.mkdir(parents=True)
    shutil.copy(ROOT / "config.toml", home / "config.toml")
    if model == "luna":
        shutil.copy(CODEX_HOME / "auth.json", home / "auth.json")
    else:
        shutil.copy(CODEX_HOME / "ollama-launch-models.json", home / "models.json")
    prompt = (task_dir(t) / "prompt.md").read_text()
    cname = f"eval-{aid}"
    sh(["docker", "rm", "-f", cname])
    sp.run(["docker", "run", "-d", "--name", cname, "--add-host", "host.docker.internal:host-gateway", "--security-opt", "seccomp=unconfined",  # lets codex's bwrap sandbox run
            
            "-v", f"{ws}:/workspace", "-v", f"{home}:/home/eval/.codex", IMAGE], check=True, capture_output=True)
    cmd = ["docker", "exec", cname, "codex", "exec", "--json", "--skip-git-repo-check", "-C", "/workspace", *MODELS[model], prompt]
    t0, status = time.time(), "ok"
    with open(out / "events.jsonl", "w") as ev, open(out / "stderr.txt", "w") as er:
        try:
            rc = sp.run(cmd, stdout=ev, stderr=er, timeout=timeout).returncode
        except sp.TimeoutExpired:
            rc, status = None, "timeout"
    wall = time.time() - t0
    sh(["docker", "rm", "-f", cname])
    (home / "auth.json").unlink(missing_ok=True)
    sh(["git", "add", "-A"], cwd=ws)
    patch = sh(["git", "diff", "--cached", "HEAD", "--", "src"], cwd=ws).stdout
    (out / "patch.diff").write_text(patch)
    events, usage = [], dict(input=0, cached_input=0, output=0, reasoning=0)
    turns = 0
    for line in (out / "events.jsonl").read_text().splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        events.append(e)
        if e.get("type") == "turn.completed" and e.get("usage"):
            turns += 1
            u = e["usage"]  # cumulative per turn.completed in `exec`; one turn per run
            usage = dict(input=u.get("input_tokens"), cached_input=u.get("cached_input_tokens"),
                         output=u.get("output_tokens"), reasoning=u.get("reasoning_output_tokens"))
    errors = [e for e in events if e.get("type") in ("error", "turn.failed")]
    if status == "ok" and (rc != 0 or not turns):
        status = "infra_or_model_error"  # inspect events.jsonl/stderr.txt; not retried
    res = dict(id=aid, task=t["id"], model=model, rep=rep, status=status, exit_code=rc, wall_time=wall,
               usage=usage if turns else None, error_events=len(errors), patch_bytes=len(patch),
               codex_args=MODELS[model])
    res.update(grade(t, patch, timeout))
    res["pass"] = status == "ok" and res["original"] and res["regression"]
    (out / "meta.json").write_text(json.dumps(res, indent=1))
    with open(run / "results.jsonl", "a") as f:
        f.write(json.dumps(res) + "\n")
    print(aid, status, "PASS" if res["pass"] else "fail", f"{wall:.0f}s", flush=True)
    return res


def run(a):
    root = ROOT / "results" / a.run
    ts = [SMOKE] if a.smoke else [t for t in tasks() if not a.tasks or t["id"] in a.tasks.split(",")]
    models = a.models.split(",")
    pair = 0
    for rep in range(1, (1 if a.smoke else a.reps) + 1):
        for t in ts:
            order = ["luna", "glm"] if pair % 2 == 0 else ["glm", "luna"]  # alternate first model
            pair += 1
            for m in order:
                if m in models:
                    attempt(root, t, m, rep, a.timeout)


def dist(xs):
    xs = [x for x in xs if x is not None]
    return f"{st.median(xs):,.0f} ({min(xs):,.0f}-{max(xs):,.0f})" if xs else "n/a"


def report(a):
    root = ROOT / "results" / a.run
    rs = [json.loads(l) for l in (root / "results.jsonl").read_text().splitlines()]
    models = sorted({r["model"] for r in rs})
    L = [f"# Report: {a.run}", "", "Median (min-max). Tokens are provider-reported (different tokenizers); n/a = not reported.", "",
         "## Passes by task", "", "| task | " + " | ".join(models) + " |", "|---|" + "---|" * len(models)]
    for t in sorted({r["task"] for r in rs}):
        L.append(f"| {t} | " + " | ".join(
            f"{sum(r['pass'] for r in rs if r['task'] == t and r['model'] == m)}/{sum(r['task'] == t and r['model'] == m for r in rs)}" for m in models) + " |")
    L += ["", "## Overall, time, tokens (all attempts incl. failures)", "",
          "| model | passes | status counts | wall s | input | cached | output | reasoning | total out+in |", "|---|---|---|---|---|---|---|---|---|"]
    def u(r, k): return (r["usage"] or {}).get(k) if r["usage"] else None
    for m in models:
        x = [r for r in rs if r["model"] == m]
        sc = {s: sum(r["status"] == s for r in x) for s in {r["status"] for r in x}}
        tot = [(u(r, "input") or 0) + (u(r, "output") or 0) if r["usage"] else None for r in x]
        L.append(f"| {m} | {sum(r['pass'] for r in x)}/{len(x)} | {sc} | {dist([r['wall_time'] for r in x])} | "
                 + " | ".join(dist([u(r, k) for r in x]) for k in ("input", "cached_input", "output", "reasoning")) + f" | {dist(tot)} |")
    both = [t for t in {r["task"] for r in rs} if all(any(r["pass"] and r["task"] == t and r["model"] == m for r in rs) for m in models)]
    L += ["", f"## Tasks solved at least once by every model: {sorted(both) or 'none'}", ""]
    if both:
        L += ["| model | wall s | output tokens |", "|---|---|---|"]
        for m in models:
            x = [r for r in rs if r["model"] == m and r["task"] in both and r["pass"]]
            L.append(f"| {m} | {dist([r['wall_time'] for r in x])} | {dist([u(r, 'output') for r in x])} |")
    L += ["", "## Failed attempts: resource use", "", "| model | failed | wall s total | input+output total |", "|---|---|---|---|"]
    for m in models:
        x = [r for r in rs if r["model"] == m and not r["pass"]]
        L.append(f"| {m} | {len(x)} | {sum(r['wall_time'] for r in x):,.0f} | {sum((u(r, 'input') or 0) + (u(r, 'output') or 0) for r in x):,} |")
    L += ["", "Effective settings: luna = low reasoning; glm = provider default (ollama reports default `max`). Budgets are not equivalent.",
          "GLM runs on Ollama Cloud (not local inference). Six tasks, historical bugs possibly in training data; not a general capability claim."]
    (root / "report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("validate")
    r = s.add_parser("run")
    r.add_argument("run"); r.add_argument("--smoke", action="store_true")
    r.add_argument("--models", default="luna,glm"); r.add_argument("--tasks")
    r.add_argument("--reps", type=int, default=3); r.add_argument("--timeout", type=int, default=900)
    s.add_parser("report").add_argument("run")
    a = p.parse_args()
    {"validate": lambda: validate(), "run": lambda: run(a), "report": lambda: report(a)}[a.cmd]()
