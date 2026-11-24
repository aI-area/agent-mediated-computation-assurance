"""Reproduce the reported results: review and claim-level audit numbers, preregistration hashes, authorization log,
CFD dispositions, figures. Usage: python reproduce.py [--skip-figures]"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
ok = []


def step(title):
    print(f"\n=== {title}")


def run(args, cwd=ROOT, env=None):
    r = subprocess.run([sys.executable, *args], cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout, r.stderr)
        raise SystemExit(f"failed: {' '.join(map(str, args))}")
    return r.stdout


def check(name, cond):
    ok.append((name, bool(cond)))
    print(f"  [{'ok' if cond else 'FAIL'}] {name}")


step("1  Review, recall audit and claim-level audit")
txt = run(["analysis/reproduce_reported_numbers.py"], cwd=ROOT / "review")
(OUT / "review_numbers.txt").write_text(txt, encoding="utf-8")
print(txt)
check("4 of 131 claims releasable", "all: n=131 releasable=4" in txt)
check("44 S dispositions supported, 43 by direct comparison", "S supported: 44 | with direct comparison (ARCS item 3): 43" in txt)

step("2  Preregistration hashes")
manifest = (ROOT / "cfd" / "logs" / "preregistration.sha256").read_text().splitlines()
print("  frozen " + manifest[0].split()[1])
bad = []
for line in manifest[1:]:
    h, name = line.split(maxsplit=1)
    p = ROOT / "cfd" / name.lstrip("*")
    if hashlib.sha256(p.read_bytes()).hexdigest() != h:
        bad.append(name)
check(f"{len(manifest) - 1} frozen files match their recorded SHA-256", not bad)

step("3  Authorization effect log")
txt = run(["cfd/gate/verify_effect_log.py", "cfd/gate/effects.jsonl"])
print("  " + txt.strip())
check("hash-chain links valid (record hashes need the original host and user values; see README)", "chain links valid: True" in txt)

step("4  CFD dispositions from the native force histories")
run(["cfd/tools/analyse_runs.py", "cfd/gated_execution/runs", "--out", str(OUT / "cfd"), "--refs", "cfd/reference_values.csv"])
key = lambda r: (r["alpha_deg"], r["qoi"])
new = {key(r): r for r in json.load(open(OUT / "cfd" / "dispositions.json"))["results"] if "grids" in r}
rec = {key(r): r for r in json.load(open(ROOT / "cfd" / "gated_execution" / "results" / "dispositions.json"))["results"] if "grids" in r}
first = {key(r): r for r in json.load(open(ROOT / "cfd" / "first_execution" / "dispositions.json"))["results"] if "grids" in r}
for k in sorted(rec):
    print(f"  alpha={k[0]:>5} {k[1]}: N={new[k]['N']:<11} V={new[k]['V']:<11} U_num={new[k]['U_num']:.3e}")
check("dispositions identical to the recorded ones", all(new[k]["N"] == rec[k]["N"] and new[k]["V"] == rec[k]["V"] for k in rec))
check("numerical uncertainties identical to the recorded ones",
      all(abs(new[k]["U_num"] - rec[k]["U_num"]) <= 1e-12 * max(1, abs(rec[k]["U_num"])) for k in rec))
check("dispositions identical to the first execution", all(first[k]["N"] == rec[k]["N"] and first[k]["V"] == rec[k]["V"] for k in rec))

if "--skip-figures" not in sys.argv:
    step("5  Figures")
    env = dict(os.environ, FIG_OUT=str(OUT / "figures"))
    for f in sorted((ROOT / "figures").glob("fig*_*.py")):
        run([f.name], cwd=ROOT / "figures", env=env)
    n = len(list((OUT / "figures").glob("*.pdf")))
    check(f"{n} figures written to out/figures", n == 11)

print("\nSummary: " + ("all checks passed" if all(c for _, c in ok) else "FAILED: " + ", ".join(n for n, c in ok if not c)))
sys.exit(0 if all(c for _, c in ok) else 1)
