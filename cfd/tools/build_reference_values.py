#!/usr/bin/env python3
"""Build reference_values.csv prospectively (before any run) from TMR SST values and Ladson TM-4074.

Ladson rule (preregistered): 120-grit set is D. At alpha 0 the two rows at -0.01/0.01 are averaged.
Otherwise D is linearly interpolated in alpha between the bracketing 120-grit points.
u_D = max(half-range across the 80/120/180-grit sets interpolated to alpha, floor), with floors of
1 % of |CL| (minimum 0.002) and 3 % of CD, a prospective allowance for tunnel and trip effects.
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ALPHAS = [0.0, 2.15, 10.0, 15.0]
TMR = {  # SST on the 897x257 grid, M = 0.15
    (0.0, "CD"): {"CFL3D": 0.00809, "FUN3D": 0.00808, "NTS": 0.00809},
    (10.0, "CL"): {"CFL3D": 1.0778, "FUN3D": 1.0840, "NTS": 1.0765},
    (10.0, "CD"): {"CFL3D": 0.01236, "FUN3D": 0.01253, "NTS": 0.01251},
    (15.0, "CL"): {"CFL3D": 1.5068, "FUN3D": 1.5109, "NTS": 1.5100},
    (15.0, "CD"): {"CFL3D": 0.02219, "FUN3D": 0.02275, "NTS": 0.02187},
}


def read_ladson(path):
    sets, cur = {}, None
    for line in open(path):
        line = line.strip()
        if line.startswith("zone"):
            cur = line.split('"')[1]
            sets[cur] = []
        elif cur and line and not line.startswith(("#", "variables")):
            a, cl, cd = map(float, line.split())
            if a < 17.5:  # pre-stall branch only
                sets[cur].append((a, cl, cd))
    return {k: sorted(v) for k, v in sets.items()}


def at_alpha(rows, alpha):
    if alpha == 0.0:
        near = [r for r in rows if abs(r[0]) < 0.06]
        return sum(r[1] for r in near) / len(near), sum(r[2] for r in near) / len(near)
    for (a0, l0, d0), (a1, l1, d1) in zip(rows, rows[1:]):
        if a0 <= alpha <= a1:
            w = (alpha - a0) / (a1 - a0)
            return l0 + w * (l1 - l0), d0 + w * (d1 - d0)
    raise ValueError(alpha)


def main():
    lad = read_ladson(HERE / "reference_data" / "CLCD_Ladson_expdata.dat")
    rows = []
    for (alpha, q), vals in TMR.items():
        for code, v in vals.items():
            rows.append([f"TMR_{code}_SST", alpha, q, v, "", "tmbwg.github.io/turbmodels/naca0012_val_sst.html 897x257"])
    for alpha in ALPHAS:
        per = {g: at_alpha(r, alpha) for g, r in lad.items()}
        for i, q in enumerate(["CL", "CD"]):
            if alpha == 0.0 and q == "CL":
                continue
            d = per["120 grit"][i]
            spread = (max(p[i] for p in per.values()) - min(p[i] for p in per.values())) / 2
            floor = max(0.01 * abs(d), 0.002) if q == "CL" else 0.03 * d
            rows.append(["LADSON_120GRIT", alpha, q, round(d, 6), round(max(spread, floor), 6),
                         f"TM-4074 tripped Re=6e6 M=0.15; grit half-range {spread:.6f}; floor {floor:.6f}"])
    with open(HERE / "reference_values.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "alpha_deg", "qoi", "value", "uncertainty", "note"])
        w.writerows(rows)
    for r in rows:
        if r[0].startswith("LADSON"):
            print(r[:5])


if __name__ == "__main__":
    main()
