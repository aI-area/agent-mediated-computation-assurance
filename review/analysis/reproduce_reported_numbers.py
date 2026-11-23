"""Recompute the numbers reported for the recall audit and the claim-level audit from the released data.

Run from the Online Resource 2 folder: python analysis/reproduce_reported_numbers.py"""
import collections
import csv
import itertools
import json
from pathlib import Path

from scipy.stats import beta

B = Path(__file__).resolve().parent.parent


def rows(p):
    return list(csv.DictReader(open(B / p, encoding="utf-8")))


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return round(po, 3), round((po - pe) / (1 - pe), 3)


def cp(x, n):
    return (0.0 if x == 0 else beta.ppf(0.025, x, n - x + 1), 1.0 if x == n else beta.ppf(0.975, x + 1, n - x))


# recall audit: screening agreement and pool estimates
a = {r["record_id"]: r["decision"] for r in rows("recall_audit/screening_author1.csv")}
b = {r["record_id"]: r["decision"] for r in rows("recall_audit/screening_author2.csv")}
print("screening kappa (3 categories):", kappa([(a[k], b[k]) for k in a]))
print("screening kappa (include vs not):", kappa([(a[k] == "INCLUDE", b[k] == "INCLUDE") for k in a]))
for src, (target, pool) in {"S2 random sample": ("S2", 6796), "S3 random sample": ("S3", 7568)}.items():
    S = [r for r in rows("recall_audit/screening_consensus_final.csv") if r["source_set"] == src]
    x = sum(r["decision"] == "INCLUDE" and target in r["streams"] for r in S)
    lo, hi = cp(x, len(S))
    print(f"{src}: {x}/{len(S)} = {100 * x / len(S):.1f}% [{100 * lo:.1f}, {100 * hi:.1f}]; pool {round(pool * x / len(S))} [{round(pool * lo)}, {round(pool * hi)}]")

# claim-level audit
H = [r for r in rows("claim_audit/claim_audit_final_dataset.csv") if r["eligibility"] == "INCLUDE"]
peer = lambda r: "arXiv" not in r["stream"]


def req(r, drop=()):
    return [o for o in "SANB" if o not in drop] + (["V"] if r["V_required"] == "Y" and "V" not in drop else [])


def rel(r, drop=()):
    return all(r[o] == "SUP" for o in req(r, drop))


for name, Q in [("all", H), ("peer-reviewed", [r for r in H if peer(r)]), ("preprints", [r for r in H if not peer(r)])]:
    x = sum(rel(r) for r in Q)
    lo, hi = cp(x, len(Q))
    print(f"{name}: n={len(Q)} releasable={x} ({100 * x / len(Q):.1f}% [{100 * lo:.1f}, {100 * hi:.1f}])",
          {o: sum(r[o] == "SUP" for r in Q) for o in "SANB"}, "V", sum(r["V"] == "SUP" for r in Q), "/", sum(r["V_required"] == "Y" for r in Q))
print("ETF any:", sum(bool(r["primary_ETF"] or r["secondary_ETF"]) for r in H),
      dict(collections.Counter(x for r in H for x in (r["primary_ETF"], r["secondary_ETF"]) if x)))
print("tiers:", dict(collections.Counter(r["evidence_tier"] for r in H)))
print("unsupported required obligations per claim:", dict(sorted(collections.Counter(sum(r[o] != "SUP" for o in req(r)) for r in H).items())))
print("release-rule sensitivity:")
for k in range(4):
    for drop in itertools.combinations("SANBV", k):
        n = sum(rel(r, drop) for r in H)
        if k < 2 or n >= 10:
            print("  remove", drop or "none", "->", n)

direct = [r for r in H if r["S"] == "SUP" and r["ARCS03"] == "Y"]
print("S supported:", sum(r["S"] == "SUP" for r in H), "| with direct comparison (ARCS item 3):", len(direct),
      "| releasable if S requires direct comparison:", sum(all((r[o] == "SUP" and (o != "S" or r["ARCS03"] == "Y")) for o in req(r)) for r in H))

# authors' consensus vs automated comparison coding
A = {r["id"]: r for r in rows("claim_audit/automated_comparison_coding.csv")}
Hall = {r["id"]: r for r in rows("claim_audit/claim_audit_final_dataset.csv")}
ids = [k for k in Hall if k in A]
print("eligibility kappa (authors vs automated):", kappa([(Hall[k]["eligibility"], A[k]["eligibility"]) for k in ids]), len(ids))
both = [k for k in ids if Hall[k]["eligibility"] == A[k]["eligibility"] == "INCLUDE"]
norm = lambda f, v: v or ("NR" if f == "V" else "none" if f == "primary_ETF" else "")
for f in ["V_required", "S", "A", "N", "V", "B", "primary_ETF", "evidence_tier"]:
    print(f"  {f}:", kappa([(norm(f, Hall[k][f]), norm(f, A[k][f])) for k in both]), len(both))
print("releasable among jointly included: authors", sum(rel(Hall[k]) for k in both), "automated", sum(rel(A[k]) for k in both),
      "either", sum(rel(Hall[k]) or rel(A[k]) for k in both))
etf = lambda r: bool(r["primary_ETF"] or r["secondary_ETF"])
print("shared set: S supported authors", sum(Hall[k]["S"] == "SUP" for k in both), "automated", sum(A[k]["S"] == "SUP" for k in both),
      "| B supported authors", sum(Hall[k]["B"] == "SUP" for k in both), "automated", sum(A[k]["B"] == "SUP" for k in both),
      "| any ETF authors %.0f%% automated %.0f%%" % (100 * sum(etf(Hall[k]) for k in both) / len(both), 100 * sum(etf(A[k]) for k in both) / len(both)))
