"""Verify the hash chain of the authorization effect log (Section 7.2 of the article).

Usage: python verify_effect_log.py effects.jsonl"""
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "effects.jsonl"
records = [json.loads(line) for line in open(path, encoding="utf-8")]
links = all(records[i]["prev_sha256"] == (records[i - 1]["record_sha256"] if i else "0" * 64) for i in range(len(records)))
print(f"{len(records)} records; chain links valid: {links}")
sys.exit(0 if links else 1)
