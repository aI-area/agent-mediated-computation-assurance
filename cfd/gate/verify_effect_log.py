"""Verify the hash chain of the effect log (hash-chain equation, Section 7.2 of the article).

Usage: python verify_effect_log.py effects.jsonl [--restore placeholder=original ...]

In the public copy the host and user fields carry placeholders ("host", "user"). The links between records are checked
as published. Each record hash covers the original field values, so it can be recomputed only when those values are
supplied with --restore (for example --restore host=<host name> --restore user=<user name>)."""
import hashlib
import json
import sys

args = sys.argv[1:]
path = args[0] if args and not args[0].startswith("--") else "effects.jsonl"
restore = dict(x.split("=", 1) for i, x in enumerate(args) if i and args[i - 1] == "--restore")


def back(v):
    if isinstance(v, str):
        return restore.get(v, v)
    if isinstance(v, list):
        return [back(x) for x in v]
    if isinstance(v, dict):
        return {k: back(x) for k, x in v.items()}
    return v


records = [json.loads(line) for line in open(path, encoding="utf-8")]
links = all(records[i]["prev_sha256"] == (records[i - 1]["record_sha256"] if i else "0" * 64) for i in range(len(records)))
own = all(hashlib.sha256(json.dumps(back({k: v for k, v in r.items() if k != "record_sha256"}), sort_keys=True).encode()).hexdigest()
          == r["record_sha256"] for r in records)
print(f"{len(records)} records; chain links valid: {links}; record hashes valid: {own}"
      + ("" if own or restore else " (placeholders in this copy; supply --restore to check against the original values)"))
