#!/usr/bin/env python3
"""Convert a 2-D PLOT3D C-grid (NASA TMR NACA 0012 family) to an OpenFOAM polyMesh.

The C-grid wraps from the lower downstream far field, around the airfoil, to the
upper downstream far field; the j=0 line coincides with itself along the wake.
Wake points are merged so the wake cut becomes a set of internal faces.

Patches: airfoil (wall), farfield (j=jmax line and both i ends), frontAndBack (empty).
The grid is extruded one cell in z with span `--span` (default 1, so Aref = span).
"""
import argparse
import gzip
from pathlib import Path

import numpy as np


def read_p2dfmt(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as fh:
        tokens = fh.read().split()
    vals = iter(tokens)
    nbl = int(next(vals))
    if nbl != 1:
        raise SystemExit(f"expected one block, found {nbl}")
    ni, nj = int(next(vals)), int(next(vals))
    data = np.array([float(t.replace("D", "E").replace("d", "e")) for t in vals])
    if data.size != 2 * ni * nj:
        raise SystemExit(f"expected {2 * ni * nj} coordinates, found {data.size}")
    x = data[: ni * nj].reshape(nj, ni).T  # Fortran order: i fastest
    y = data[ni * nj :].reshape(nj, ni).T
    return x, y


def wake_point_count(x, y, tol=1e-10):
    """Number of j=0 points (from each end) that coincide across the wake cut."""
    ni = x.shape[0]
    n = 0
    while n < ni // 2 and abs(x[n, 0] - x[ni - 1 - n, 0]) < tol and abs(y[n, 0] - y[ni - 1 - n, 0]) < tol:
        n += 1
    if n == 0:
        raise SystemExit("no coincident wake points found; not a C-grid?")
    return n  # includes the trailing-edge point


def build_mesh(x, y, span):
    ni, nj = x.shape
    nw = wake_point_count(x, y)

    # 2-D point numbering with merged wake points
    raw = np.arange(ni * nj).reshape(nj, ni).T  # raw[i, j]
    for i in range(nw):
        raw[i, 0] = raw[ni - 1 - i, 0]
    uniq, inv = np.unique(raw.ravel(), return_inverse=True)
    pid2d = inv.reshape(raw.shape)
    np2d = uniq.size
    flat_idx = uniq  # raw index -> coordinates
    xs = x.T.ravel()[flat_idx]
    ys = y.T.ravel()[flat_idx]
    points = np.vstack(
        [np.column_stack([xs, ys, np.zeros(np2d)]), np.column_stack([xs, ys, np.full(np2d, span)])]
    )

    def p(i, j, k):
        return pid2d[i, j] + k * np2d

    nci, ncj = ni - 1, nj - 1
    cid = lambda i, j: j * nci + i  # noqa: E731
    ncells = nci * ncj

    faces, owner, neigh, patch = [], [], [], []

    def edge_face(a, b):
        return [a, b, b + np2d, a + np2d]

    # i-direction faces (lines of constant i)
    for j in range(ncj):
        for i in range(ni):
            f = edge_face(pid2d[i, j], pid2d[i, j + 1])
            if i == 0:
                faces.append(f); owner.append(cid(0, j)); neigh.append(-1); patch.append("farfield")
            elif i == ni - 1:
                faces.append(f); owner.append(cid(nci - 1, j)); neigh.append(-1); patch.append("farfield")
            else:
                faces.append(f); owner.append(cid(i - 1, j)); neigh.append(cid(i, j)); patch.append(None)

    # j-direction faces (lines of constant j)
    for i in range(nci):
        for j in range(nj):
            f = edge_face(pid2d[i, j], pid2d[i + 1, j])
            if j == nj - 1:
                faces.append(f); owner.append(cid(i, ncj - 1)); neigh.append(-1); patch.append("farfield")
            elif j == 0:
                if i < nw - 1:  # lower wake cell; pair with upper wake cell
                    partner = nci - 1 - i
                    faces.append(f); owner.append(cid(i, 0)); neigh.append(cid(partner, 0)); patch.append(None)
                elif i >= nci - (nw - 1):
                    continue  # upper wake: already added from the lower side
                else:
                    faces.append(f); owner.append(cid(i, 0)); neigh.append(-1); patch.append("airfoil")
            else:
                faces.append(f); owner.append(cid(i, j - 1)); neigh.append(cid(i, j)); patch.append(None)

    # front and back
    for j in range(ncj):
        for i in range(nci):
            q = [pid2d[i, j], pid2d[i + 1, j], pid2d[i + 1, j + 1], pid2d[i, j + 1]]
            faces.append(q); owner.append(cid(i, j)); neigh.append(-1); patch.append("frontAndBack")
            faces.append([v + np2d for v in q]); owner.append(cid(i, j)); neigh.append(-1); patch.append("frontAndBack")

    faces = np.array(faces, dtype=np.int64)
    owner = np.array(owner, dtype=np.int64)
    neigh = np.array(neigh, dtype=np.int64)

    # owner must be the lower cell index for internal faces
    internal = neigh >= 0
    swap = internal & (owner > neigh)
    owner[swap], neigh[swap] = neigh[swap], owner[swap].copy()

    # cell centres (mean of the 8 hex vertices)
    cc = np.zeros((ncells, 3))
    for j in range(ncj):
        for i in range(nci):
            v = [p(i, j, 0), p(i + 1, j, 0), p(i + 1, j + 1, 0), p(i, j + 1, 0)]
            cc[cid(i, j)] = points[v + [w + np2d for w in v]].mean(axis=0)

    # orient: normal from owner to neighbour (internal) or outward (boundary)
    pts = points[faces]
    n = np.cross(pts[:, 1] - pts[:, 0], pts[:, 3] - pts[:, 0])
    fc = pts.mean(axis=1)
    flip = np.einsum("ij,ij->i", n, fc - cc[owner]) < 0
    faces[flip] = faces[flip][:, ::-1]

    # ordering: internal (owner, neighbour) upper-triangular, then patches
    order_patches = ["airfoil", "farfield", "frontAndBack"]
    patch = np.array([p_ if p_ else "" for p_ in patch])
    idx_int = np.where(internal)[0]
    idx_int = idx_int[np.lexsort((neigh[idx_int], owner[idx_int]))]
    blocks, start = [], idx_int.size
    order = [idx_int]
    for name in order_patches:
        ids = np.where(patch == name)[0]
        order.append(ids)
        blocks.append((name, ids.size, start))
        start += ids.size
    order = np.concatenate(order)
    return points, faces[order], owner[order], neigh[order][: idx_int.size], blocks, ncells, nw


HEADER = """FoamFile
{{
    version     2.0;
    format      ascii;
    arch        "LSB;label=32;scalar=64";
    class       {cls};
    location    "constant/polyMesh";
    object      {obj};
}}
"""


def write_list(path, cls, obj, rows, fmt, note=""):
    with open(path, "w", newline="\n") as fh:
        fh.write(HEADER.format(cls=cls, obj=obj))
        if note:
            fh.write(f"// {note}\n")
        fh.write(f"\n{len(rows)}\n(\n")
        fh.writelines(fmt(r) + "\n" for r in rows)
        fh.write(")\n")


def write_polymesh(outdir, points, faces, owner, neigh, blocks, ncells):
    d = Path(outdir) / "constant" / "polyMesh"
    d.mkdir(parents=True, exist_ok=True)
    note = f"nPoints:{len(points)} nCells:{ncells} nFaces:{len(faces)} nInternalFaces:{len(neigh)}"
    write_list(d / "points", "vectorField", "points", points, lambda r: f"({r[0]:.15g} {r[1]:.15g} {r[2]:.15g})")
    write_list(d / "faces", "faceList", "faces", faces, lambda r: "4(" + " ".join(map(str, r)) + ")")
    write_list(d / "owner", "labelList", "owner", owner, str, note)
    write_list(d / "neighbour", "labelList", "neighbour", neigh, str, note)
    types = {"airfoil": "wall", "farfield": "patch", "frontAndBack": "empty"}
    with open(d / "boundary", "w", newline="\n") as fh:
        fh.write(HEADER.format(cls="polyBoundaryMesh", obj="boundary"))
        fh.write(f"\n{len(blocks)}\n(\n")
        for name, n, start in blocks:
            fh.write(f"    {name}\n    {{\n        type            {types[name]};\n")
            if types[name] == "wall":
                fh.write("        inGroups        1(wall);\n")
            fh.write(f"        nFaces          {n};\n        startFace       {start};\n    }}\n")
        fh.write(")\n")


def closure_check(points, faces, owner, neigh, ncells):
    """Sum of outward face-area vectors per cell must vanish for a closed mesh."""
    pts = points[faces]
    sf = 0.5 * np.cross(pts[:, 2] - pts[:, 0], pts[:, 3] - pts[:, 1])
    acc = np.zeros((ncells, 3))
    np.add.at(acc, owner, sf)
    np.add.at(acc, neigh, -sf[: neigh.size])
    scale = np.abs(sf).max()
    return float(np.abs(acc).max() / scale)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("grid", type=Path)
    ap.add_argument("case", type=Path)
    ap.add_argument("--span", type=float, default=1.0)
    a = ap.parse_args()
    x, y = read_p2dfmt(a.grid)
    points, faces, owner, neigh, blocks, ncells, nw = build_mesh(x, y, a.span)
    err = closure_check(points, faces, owner, neigh, ncells)
    if err > 1e-8:
        raise SystemExit(f"mesh not closed: max relative face-sum {err:.3e}")
    write_polymesh(a.case, points, faces, owner, neigh, blocks, ncells)
    print(f"{a.grid.name}: {x.shape[0]}x{x.shape[1]} points, {ncells} cells, "
          f"{nw} merged wake points, patches {[(b[0], b[1]) for b in blocks]}, closure {err:.1e}")


if __name__ == "__main__":
    main()
