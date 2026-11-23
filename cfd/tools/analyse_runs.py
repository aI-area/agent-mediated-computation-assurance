#!/usr/bin/env python3
"""Apply the PREREGISTRATION.md rules to the run matrix and write dispositions.

Usage: python analyse_runs.py runs --out results [--refs ../reference_values.csv]
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FINE3 = ["n0012_449-129", "n0012_897-257", "n0012_1793-513"]
COARSE = "n0012_225-65"
ALPHAS = [0.0, 2.15, 10.0, 15.0]
WINDOW = 2000
GCI_LIMIT = {"CL": 0.01, "CD": 0.03}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_coefficients(case):
    """Concatenate forceCoeffs coefficient.dat across restart directories."""
    files = sorted((case / "postProcessing" / "forceCoeffs").glob("*/coefficient*.dat"),
                   key=lambda p: float(p.parent.name))
    if not files:
        raise FileNotFoundError(f"no coefficient.dat in {case}")
    rows, header = {}, None
    for f in files:
        for line in f.read_text().splitlines():
            if line.startswith("#"):
                tokens = line[1:].split()
                if tokens and tokens[0] == "Time":
                    header = tokens
                continue
            vals = line.split()
            if vals:
                rows[float(vals[0])] = vals
    if header is None:
        raise ValueError(f"no column header in {files}")
    data = np.array([[float(v) for v in rows[t]] for t in sorted(rows)])
    col = {name: i for i, name in enumerate(header)}
    return data[:, col["Time"]], data[:, col["Cl"]], data[:, col["Cd"]], [str(f) for f in files]


def iterative(q):
    w = q[-WINDOW:]
    return float(w.mean()), float((w.max() - w.min()) / 2.0)


def celik(f1, f2, f3, r=2.0):
    """Celik et al. (2008) with constant ratio r; f1 finest. Returns dict."""
    e21, e32 = f2 - f1, f3 - f2
    out = {"f1": f1, "f2": f2, "f3": f3, "e21": e21, "e32": e32}
    if e21 == 0 or e32 == 0:
        out.update(R=None, p=None, gci_fine=None, status="UNRESOLVED", reason="zero grid difference")
        return out
    R = e21 / e32
    out["R"] = R
    if not 0 < R < 1:
        out.update(p=None, gci_fine=None, status="UNRESOLVED",
                   reason="oscillatory convergence" if R < 0 else "divergent or non-monotone")
        return out
    p = math.log(abs(e32 / e21)) / math.log(r)
    fs, flag = 1.25, None
    if not 0.5 <= p <= 3.0:
        fs, flag = 3.0, "observed order outside [0.5, 3]; Fs=3, p capped at 2"
        p = min(p, 2.0)
    ea21 = abs(e21 / f1)
    gci = fs * ea21 / (r**p - 1)
    f_ext = (r**p * f1 - f2) / (r**p - 1)
    asym = (fs * abs(e32 / f2) / (r**p - 1)) / (r**p * gci) if gci > 0 else None
    out.update(p=p, Fs=fs, gci_fine=gci, f_extrapolated=f_ext, asymptotic_ratio=asym,
               status="OK", reason=flag)
    return out


def load_refs(path):
    refs = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            refs.setdefault((float(row["alpha_deg"]), row["qoi"]), []).append(row)
    return refs


def numeric(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def assess(runs, refs, prereg_hash):
    results, evidence = [], {}
    for alpha in ALPHAS:
        series = {}
        for g in FINE3 + [COARSE]:
            case = runs / f"{g}_a{alpha:05.2f}"
            try:
                t, cl, cd, files = read_coefficients(case)
            except (FileNotFoundError, ValueError) as exc:
                series[g] = {"missing": str(exc)}
                continue
            evidence.update({f: sha256(f) for f in files})
            for extra in ["simpleFoam.log", "constant/polyMesh/owner"]:
                if (case / extra).exists():
                    evidence[str(case / extra)] = sha256(case / extra)
            series[g] = {"iterations": int(t[-1]), "CL": iterative(cl), "CD": iterative(cd)}
        for qoi in (["CD"] if alpha == 0 else ["CL", "CD"]):
            rec = {"alpha_deg": alpha, "qoi": qoi, "grids": {}}
            missing = [g for g in FINE3 if "missing" in series[g]]
            if missing:
                rec.update(N="UNRESOLVED", V="UNRESOLVED", reason=f"missing runs {missing}")
                results.append(rec)
                continue
            for g in FINE3 + [COARSE]:
                if "missing" not in series[g]:
                    rec["grids"][g] = {"mean": series[g][qoi][0], "e_it": series[g][qoi][1],
                                       "iterations": series[g]["iterations"]}
            f1, f2, f3 = (series[g][qoi][0] for g in reversed(FINE3))
            gci = celik(f1, f2, f3)
            rec["gci"] = gci
            e_it = series[FINE3[-1]][qoi][1]
            n_reasons = []
            if gci["status"] != "OK":
                n_reasons.append(gci["reason"])
                u_num = None
            else:
                u_num = gci["gci_fine"] / gci["Fs"] * abs(f1)
                if gci["gci_fine"] > GCI_LIMIT[qoi]:
                    n_reasons.append(f"GCI {gci['gci_fine']:.3%} above {GCI_LIMIT[qoi]:.0%}")
                if not (e_it <= 0.1 * u_num or e_it / abs(f1) <= 1e-5):
                    n_reasons.append("iterative error not small relative to discretization uncertainty")
            rec["U_num"] = u_num
            rec["N"] = "SUPPORTED" if not n_reasons else "UNRESOLVED"
            # code-to-code (TMR SST)
            tmr = [numeric(r["value"]) for r in refs.get((alpha, qoi), []) if r["source"].startswith("TMR")]
            tmr = [v for v in tmr if v is not None]
            if tmr and u_num is not None:
                m, s = float(np.mean(tmr)), (max(tmr) - min(tmr)) / 2
                tol = max(2 * s, u_num) + 0.01 * abs(m)
                rec["code_to_code"] = {"tmr_mean": m, "tmr_half_range": s, "diff": f1 - m, "tolerance": tol,
                                       "agrees": abs(f1 - m) <= tol}
                if rec["N"] == "SUPPORTED" and abs(f1 - m) > tol:
                    rec["N"] = "REFUTED"
                    n_reasons.append("verified disagreement with TMR SST code-to-code values")
            rec["N_reasons"] = n_reasons
            # validation (ASME V&V 20)
            lad = [r for r in refs.get((alpha, qoi), []) if r["source"].startswith("LADSON")]
            d = numeric(lad[0]["value"]) if lad else None
            u_d = numeric(lad[0]["uncertainty"]) if lad else None
            if rec["N"] != "SUPPORTED" or d is None or u_d is None:
                rec["V"] = "UNRESOLVED"
                rec["V_reason"] = "numerical prerequisite not supported" if rec["N"] != "SUPPORTED" \
                    else "Ladson value or uncertainty not entered"
            else:
                e = f1 - d
                u_val = math.hypot(u_num, u_d)
                rec["validation"] = {"S": f1, "D": d, "E": e, "u_num": u_num, "u_D": u_d, "u_val": u_val}
                rec["V"] = "SUPPORTED" if abs(e) <= 2 * u_val else "REFUTED"
            results.append(rec)
        if alpha == 0 and "missing" not in series[FINE3[-1]]:
            results.append({"alpha_deg": 0.0, "qoi": "CL_symmetry_check",
                            "value": series[FINE3[-1]]["CL"][0],
                            "pass": abs(series[FINE3[-1]]["CL"][0]) < 1e-4})
    return {"preregistration_sha256": prereg_hash, "results": results, "evidence_sha256": evidence}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", type=Path)
    ap.add_argument("--out", type=Path, default=Path("results"))
    ap.add_argument("--refs", type=Path, default=HERE.parent / "reference_values.csv")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    prereg = HERE.parent / "PREREGISTRATION.md"
    report = assess(a.runs, load_refs(a.refs), sha256(prereg))
    (a.out / "dispositions.json").write_text(json.dumps(report, indent=2))
    for r in report["results"]:
        if "N" in r:
            g = r.get("gci", {})
            print(f"alpha={r['alpha_deg']:>4} {r['qoi']}: N={r['N']:<10} V={r['V']:<10} "
                  f"GCI={g.get('gci_fine')!s:.8} p={g.get('p')!s:.6}")


if __name__ == "__main__":
    main()
