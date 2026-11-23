#!/usr/bin/env python3
"""Create the grid x angle run matrix from case_template and the TMR PLOT3D grids.

Usage: python setup_cases.py --grids DIR --out runs [--nprocs 32] [--iters 60000]
"""
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

from p2d_cgrid_to_foam import build_mesh, closure_check, read_p2dfmt, write_polymesh

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "case_template"
GRIDS = ["n0012_225-65", "n0012_449-129", "n0012_897-257", "n0012_1793-513"]
ALPHAS = [0.0, 2.15, 10.0, 15.0]

# NASA TMR NACA 0012 SST freestream: Tu = 0.052 %, nu_t/nu = 0.009, U = 1, Re = 6e6
NU = 1.0 / 6.0e6
K_INF = 1.5 * (0.00052 * 1.0) ** 2
NUT_INF = 0.009 * NU
OMEGA_INF = K_INF / NUT_INF


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_grid(grid_dir, stem):
    for suffix in (".p2dfmt.gz", ".p2dfmt"):
        p = grid_dir / (stem + suffix)
        if p.exists():
            return p
    raise SystemExit(f"grid {stem} not found in {grid_dir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grids", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--nprocs", type=int, default=32)
    ap.add_argument("--iters", type=int, default=60000)
    a = ap.parse_args()
    manifest = []
    for stem in GRIDS:
        gpath = find_grid(a.grids, stem)
        x, y = read_p2dfmt(gpath)
        points, faces, owner, neigh, blocks, ncells, nw = build_mesh(x, y, 1.0)
        closure = closure_check(points, faces, owner, neigh, ncells)
        for alpha in ALPHAS:
            case = a.out / f"{stem}_a{alpha:05.2f}"
            if case.exists():
                shutil.rmtree(case)
            shutil.copytree(TEMPLATE, case)
            write_polymesh(case, points, faces, owner, neigh, blocks, ncells)
            ar = math.radians(alpha)
            (case / "caseParameters").write_text(
                f"Ux {math.cos(ar):.15g};\nUy {math.sin(ar):.15g};\n"
                f"liftX {-math.sin(ar):.15g};\nliftY {math.cos(ar):.15g};\n"
                f"kInf {K_INF:.10e};\nomegaInf {OMEGA_INF:.10e};\nnIter {a.iters};\n"
            )
            dp = case / "system" / "decomposeParDict"
            dp.write_text(dp.read_text().replace("NPROCS", str(a.nprocs)))
            manifest.append({"case": case.name, "grid": stem, "grid_sha256": sha256(gpath),
                             "cells": ncells, "alpha_deg": alpha, "wake_points": nw,
                             "closure": closure, "nu": NU, "kInf": K_INF, "omegaInf": OMEGA_INF})
            print(case.name, ncells, "cells")
    (a.out / "run_manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
