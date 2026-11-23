"""Self-test for p2d_cgrid_to_foam on a synthetic NACA 0012 C-grid."""
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import p2d_cgrid_to_foam as conv  # noqa: E402


def naca0012(xc):
    return 0.6 * (0.2969 * np.sqrt(xc) - 0.1260 * xc - 0.3516 * xc**2 + 0.2843 * xc**3 - 0.1036 * xc**4)


def synthetic_cgrid(n_air=65, n_wake=25, nj=33, r_far=20.0):
    beta = np.linspace(0, np.pi, (n_air + 1) // 2)
    xa = 0.5 * (1 + np.cos(beta))  # TE -> LE
    ya = naca0012(xa)
    ya[0] = 0.0
    lower = np.column_stack([xa, -ya])
    upper = np.column_stack([xa[::-1], ya[::-1]])
    air = np.vstack([lower, upper[1:]])  # TE(lower) .. LE .. TE(upper)
    xw = 1 + (r_far - 1) * np.linspace(0, 1, n_wake) ** 1.5
    wake_l = np.column_stack([xw[::-1], np.zeros(n_wake)])[:-1]
    wake_u = np.column_stack([xw, np.zeros(n_wake)])[1:]
    inner = np.vstack([wake_l, air, wake_u])
    phi = -np.pi / 2 - np.pi * np.linspace(0, 1, air.shape[0])  # lower TE -> upstream -> upper TE
    outer = np.vstack([
        np.column_stack([wake_l[:, 0], np.full(len(wake_l), -r_far)]),
        np.column_stack([1 + r_far * np.cos(phi), r_far * np.sin(phi)]),
        np.column_stack([wake_u[:, 0], np.full(len(wake_u), r_far)]),
    ])
    s = (np.linspace(0, 1, nj) ** 2)[None, :, None]
    g = inner[:, None, :] * (1 - s) + outer[:, None, :] * s
    return g[..., 0], g[..., 1]


def cell_volumes(points, faces, owner, neigh, ncells):
    pts = points[faces]
    sf = 0.5 * np.cross(pts[:, 2] - pts[:, 0], pts[:, 3] - pts[:, 1])
    fc = pts.mean(axis=1)
    contrib = np.einsum("ij,ij->i", sf, fc) / 3.0
    vol = np.zeros(ncells)
    np.add.at(vol, owner, contrib)
    np.add.at(vol, neigh, -contrib[: neigh.size])
    return vol


def test_roundtrip():
    x, y = synthetic_cgrid()
    with tempfile.TemporaryDirectory() as tmp:
        g = Path(tmp) / "g.p2dfmt"
        with open(g, "w") as fh:
            fh.write(f"1\n{x.shape[0]} {x.shape[1]}\n")
            fh.write(" ".join(f"{v:.16e}" for v in x.T.ravel()) + "\n")
            fh.write(" ".join(f"{v:.16e}" for v in y.T.ravel()) + "\n")
        xr, yr = conv.read_p2dfmt(g)
        assert np.allclose(xr, x) and np.allclose(yr, y)
        points, faces, owner, neigh, blocks, ncells, nw = conv.build_mesh(xr, yr, 1.0)
        assert nw == 25, nw
        assert conv.closure_check(points, faces, owner, neigh, ncells) < 1e-10
        vol = cell_volumes(points, faces, owner, neigh, ncells)
        assert vol.min() > 0, vol.min()
        assert np.all(owner[: neigh.size] < neigh)
        assert np.all(np.diff(owner[: neigh.size]) >= 0)
        b = {n: c for n, c, _ in blocks}
        nci, ncj = x.shape[0] - 1, x.shape[1] - 1
        assert b["airfoil"] == 64 and b["frontAndBack"] == 2 * nci * ncj
        assert b["farfield"] == nci + 2 * ncj
        assert len(set(map(tuple, np.sort(faces, axis=1)))) == len(faces)  # no duplicate faces
        conv.write_polymesh(Path(tmp) / "case", points, faces, owner, neigh, blocks, ncells)
        assert (Path(tmp) / "case/constant/polyMesh/boundary").exists()
    print("PASS", ncells, "cells", blocks)


if __name__ == "__main__":
    test_roundtrip()
