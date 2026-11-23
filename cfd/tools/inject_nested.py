#!/usr/bin/env python3
"""Initialise a fine TMR C-grid case from the converged next-coarser case by injection.

The TMR family is nested (coarse grid = every other fine point), and p2d_cgrid_to_foam numbers cells as
cid = j*(ni-1) + i, so fine cell (I, J) lies inside coarse cell (I//2, J//2). The coarse latest-time fields
must be ASCII (run foamFormatConvert first). Only internal fields are written; boundary entries are kept.
Usage: python inject_nested.py COARSE_CASE FINE_CASE NI_COARSE NJ_COARSE
"""
import re
import sys
from pathlib import Path

import numpy as np

FIELDS = ["U", "p", "k", "omega", "nut"]


def latest_time(case):
    times = [d for d in Path(case).iterdir() if d.is_dir() and re.fullmatch(r"\d+(\.\d+)?", d.name) and d.name != "0"]
    return max(times, key=lambda d: float(d.name))


def read_internal(path):
    txt = Path(path).read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<(scalar|vector)>\s*(\d+)\s*\((.*?)\n\)\s*;", txt, re.S)
    if not m:
        raise SystemExit(f"{path}: no nonuniform ASCII internalField (convert to ASCII first)")
    kind, n, body = m.group(1), int(m.group(2)), m.group(3)
    vals = np.array(body.replace("(", " ").replace(")", " ").split(), dtype=float)
    return kind, vals.reshape(n, 3) if kind == "vector" else vals


def write_internal(path, kind, arr):
    txt = Path(path).read_text()
    if kind == "vector":
        body = "\n".join(f"({a:.10g} {b:.10g} {c:.10g})" for a, b, c in arr)
    else:
        body = "\n".join(f"{a:.10g}" for a in arr)
    new = f"internalField   nonuniform List<{kind}>\n{len(arr)}\n(\n{body}\n)\n;"
    txt = re.sub(r"internalField\s+[^;]*;", lambda _: new, txt, count=1)
    Path(path).write_text(txt)


def main():
    coarse, fine, ni, nj = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    nci, ncj = ni - 1, nj - 1
    fci, fcj = 2 * nci, 2 * ncj
    I, J = np.meshgrid(np.arange(fci), np.arange(fcj))      # J rows, I columns
    parent = ((J // 2) * nci + (I // 2)).ravel()              # fine cid order = J*fci + I
    src = latest_time(coarse)
    for f in FIELDS:
        kind, vals = read_internal(src / f)
        assert len(vals) == nci * ncj, (f, len(vals), nci * ncj)
        write_internal(Path(fine) / "0" / f, kind, vals[parent])
    print(f"injected {FIELDS} from {src} into {fine}/0 ({fci * fcj} cells)")


if __name__ == "__main__":
    main()
