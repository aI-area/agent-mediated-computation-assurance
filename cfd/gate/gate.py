#!/usr/bin/env python3
"""Authorization gate for the agent-mediated NACA 0012 execution.

Invoked only through gate.sh, the forced command of the agent's SSH key: the requested action arrives in
SSH_ORIGINAL_COMMAND and must be exactly one action name of policy.json. Every request, allowed or denied, is
appended to log/effects.jsonl, whose records are chained by SHA-256 (each record stores the hash of its
predecessor). Before and after every action the protected-input manifest is recomputed and compared with the
frozen manifest written at approval time.
"""
import hashlib
import io
import json
import os
import socket
import subprocess
import sys
import tarfile
import time
from pathlib import Path

GATED = Path(__file__).resolve().parent
POLICY = GATED / "policy.json"
LOG = GATED / "log" / "effects.jsonl"
FROZEN = GATED / "log" / "protected_manifest.json"
BIG = 50 * 2**20            # files larger than this are fingerprinted by size and mtime


def sha(b):
    return hashlib.sha256(b).hexdigest()


def file_digest(p):
    st = p.stat()
    if st.st_size > BIG:
        return f"size={st.st_size};mtime={int(st.st_mtime)}"
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest(policy):
    root = Path(policy["root"])
    out = {}
    for rel in policy["protected"]:
        p = root / rel
        files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
        for f in files:
            out[str(f.relative_to(root))] = file_digest(f)
    return out


def manifest_hash(m):
    return sha(json.dumps(m, sort_keys=True).encode())


def append(record):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    prev = "0" * 64
    if LOG.exists():
        lines = LOG.read_text().strip().splitlines()
        if lines:
            prev = json.loads(lines[-1])["record_sha256"]
    record = {"seq": sum(1 for _ in open(LOG)) if LOG.exists() else 0, "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "user": os.environ.get("USER", ""), "host": socket.gethostname(), "prev_sha256": prev, **record}
    record["record_sha256"] = sha(json.dumps(record, sort_keys=True).encode())
    with open(LOG, "a") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def work_effects(policy):
    work = Path(policy["root"]) / "gated" / "work"
    files = sorted(x for x in work.rglob("*") if x.is_file()) if work.exists() else []
    evidence = {str(f.relative_to(work)): file_digest(f) for f in files
                if f.name in ("coefficient.dat", "simpleFoam.log", "owner", "yPlus.dat", "dispositions.json", "run_manifest.json")}
    return {"files": len(files), "bytes": sum(f.stat().st_size for f in files), "evidence_files": evidence}


def main():
    policy = json.loads(POLICY.read_text())
    policy_sha = sha(POLICY.read_bytes())
    frozen = json.loads(FROZEN.read_text())
    request = os.environ.get("SSH_ORIGINAL_COMMAND", "").strip() if len(sys.argv) < 2 else sys.argv[1]

    if request.startswith("--supervise "):          # internal: completion record of a launched pipeline
        launch_sha = request.split()[1]
        argv = [a.replace("{root}", policy["root"]) for a in policy["actions"]["run_pipeline"]["argv"]]
        rc = subprocess.call(argv, stdout=open(GATED / "work" / "pipeline.out", "a"), stderr=subprocess.STDOUT)
        post = manifest(policy)
        append({"action": "run_pipeline", "phase": "completed", "launch_record": launch_sha, "exit_code": rc,
                "policy_sha256": policy_sha, "protected_post_sha256": manifest_hash(post),
                "protected_unchanged": post == frozen["files"], "effects": work_effects(policy)})
        return

    if request not in policy["actions"]:
        append({"action": request[:200], "decision": "DENIED", "reason": "not an action of the approved policy",
                "policy_sha256": policy_sha})
        print(f"DENIED: '{request[:80]}' is not an approved action", file=sys.stderr)
        sys.exit(3)

    pre = manifest(policy)
    base = {"action": request, "decision": "ALLOWED", "policy_sha256": policy_sha,
            "protected_pre_sha256": manifest_hash(pre), "protected_pre_matches_frozen": pre == frozen["files"]}
    if pre != frozen["files"]:
        append({**base, "decision": "HALTED", "reason": "protected inputs differ from the frozen manifest"})
        print("HALTED: protected inputs differ from the frozen manifest", file=sys.stderr)
        sys.exit(4)

    if request == "status":
        sched = GATED / "work" / "logs" / "scheduler.log"
        print(sched.read_text()[-3000:] if sched.exists() else "no scheduler log yet")
        append({**base, "effects": "none"})
    elif request == "verify":
        print(json.dumps({"protected_files": len(pre), "matches_frozen": True, "manifest_sha256": manifest_hash(pre)}, indent=1))
        append({**base, "effects": "none"})
    elif request == "export_results":
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            work = GATED / "work"
            for sub in ["results", "logs", "pipeline.out"]:
                if (work / sub).exists():
                    tar.add(work / sub, arcname=f"work/{sub}")
            for case in sorted((work / "runs").glob("n0012_*")):
                for sub in ["postProcessing", "simpleFoam.log", "DONE", "caseParameters", "system"]:
                    if (case / sub).exists():
                        tar.add(case / sub, arcname=f"work/runs/{case.name}/{sub}")
            tar.add(LOG, arcname="log/effects.jsonl")
            tar.add(FROZEN, arcname="log/protected_manifest.json")
            tar.add(POLICY, arcname="policy.json")
        append({**base, "effects": "none", "exported_bytes": buf.tell()})
        sys.stdout.buffer.write(buf.getvalue())
    elif request == "probe_protected_writes":
        root = Path(policy["root"])
        attempts = {}
        for label, path, mode in [("append to PREREGISTRATION.md", root / "PREREGISTRATION.md", "a"),
                                  ("append to reference_values.csv", root / "reference_values.csv", "a"),
                                  ("create file in original evidence runs/", root / "runs" / "TAMPER", "x"),
                                  ("append to gated/policy.json", root / "gated" / "policy.json", "a")]:
            try:
                with open(path, mode) as fh:
                    fh.write("tamper\n")
                attempts[label] = "SUCCEEDED"
            except OSError as e:
                attempts[label] = f"blocked: {e.strerror}"
        post = manifest(policy)
        rec = append({**base, "effects": "test", "attempts": attempts, "protected_post_sha256": manifest_hash(post),
                      "protected_unchanged": post == frozen["files"]})
        print(json.dumps(rec, indent=1))
    elif request == "reset_work":
        import shutil
        work = GATED / "work"
        existed = work.exists()
        if existed:
            shutil.rmtree(work)
        append({**base, "effects": "removed gated/work" if existed else "none"})
        print("gated/work removed" if existed else "gated/work did not exist")
    elif request == "run_pipeline":
        if (GATED / "work" / "runs").exists():
            append({**base, "decision": "DENIED", "reason": "pipeline already launched"})
            print("DENIED: pipeline already launched", file=sys.stderr)
            sys.exit(3)
        (GATED / "work").mkdir(exist_ok=True)
        rec = append({**base, "phase": "launched", "argv": policy["actions"]["run_pipeline"]["argv"]})
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), f"--supervise {rec['record_sha256']}"],
                         start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=open(GATED / "work" / "supervisor.out", "a"), stderr=subprocess.STDOUT)
        print(json.dumps(rec, indent=1))


if __name__ == "__main__":
    main()
