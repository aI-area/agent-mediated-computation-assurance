"""Figure 11: native residual and force histories of the under-resolved NACA 0012 realization (Section 7.4).

Usage: python fig11_native_residual_force.py [data_dir]   (default: ./data)"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from figstyle import BLUE, G1, G2, K, MM, VERM, W, panel, save

src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
a = np.genfromtxt(f"{src}/residual_force_history_20000_iterations.csv", delimiter=",", names=True)
d = np.genfromtxt(f"{src}/residual_force_history_5000_iterations.csv", delimiter=",", names=True)
assert all(np.array_equal(a[f][:5000], d[f]) for f in ("Cd", "Cl", "p"))  # D1 = first 5,000 iterations of A025
it = a["iteration"]
w1 = (it > 4000) & (it <= 5000)
w2 = it > 19000
fig, ax = plt.subplots(2, 2, figsize=(W * MM, 100 * MM), gridspec_kw={"hspace": 0.42, "wspace": 0.40})
# (a) residuals
A = ax[0, 0]
sty = {"p": (BLUE, "-"), "Ux": (K, (0, (4, 1.5))), "Uy": (K, "-."), "k": (G1, ":"), "omega": (G2, "-")}
lab = {"p": "$p$", "Ux": "$U_x$", "Uy": "$U_y$", "k": "$k$", "omega": r"$\omega$"}
for f, (c, ls) in sty.items():
    A.plot(it, a[f], color=c, ls=ls, lw=0.8, label=lab[f])
A.set_yscale("log")
A.set_ylim(1e-13, 3)
A.set_xlim(0, 20000)
A.axhline(1e-6, color=VERM, lw=0.8, label=r"$10^{-6}$")
A.axvline(5000, color=K, lw=0.5, ls=(0, (3, 2)))
A.set_xlabel(r"Iteration ($\times10^{3}$)")
A.set_ylabel("Initial residual")
A.legend(ncol=3, loc="lower left", handlelength=1.6, columnspacing=0.7, handletextpad=0.3, fontsize=6.5)
# (b), (c) forces from iteration 500
for P, key, lbl in ((ax[0, 1], "Cl", "$C_L$"), (ax[1, 0], "Cd", "$C_D$")):
    m = it >= 500
    P.plot(it[m], a[key][m], color=K, lw=0.9, label="A025")
    dm = d["iteration"] >= 500
    P.plot(d["iteration"][dm], d[key][dm], color=BLUE, lw=1.2, ls=(0, (3, 1.5)), label="D1")
    lo, hi = np.percentile(a[key][m], [0.5, 99.5])
    pad = (hi - lo) * 0.1
    P.set_ylim(lo - pad, hi + pad)
    P.set_xlim(0, 20000)
    P.axvline(5000, color=K, lw=0.5, ls=(0, (3, 2)))
    P.set_xlabel(r"Iteration ($\times10^{3}$)")
    P.set_ylabel(lbl)
ax[0, 1].legend(loc="lower right")
# (d) late windows
Dp = ax[1, 1]
x = np.arange(1, 1001)
for lab_, wm, c in (("D1", w1, BLUE), ("A025", w2, K)):
    Dp.plot(x, (a["Cl"][wm] - a["Cl"][wm].mean()) * 1e3, color=c, lw=0.9, label=f"{lab_} $C_L$")
    Dp.plot(x, (a["Cd"][wm] - a["Cd"][wm].mean()) * 1e3, color=c, lw=0.9, ls=(0, (2, 1.2)), label=f"{lab_} $C_D$")
Dp.set_xlabel("Sample in final 1,000 iterations")
Dp.set_ylabel(r"Deviation ($\times10^{-3}$)")
Dp.set_xlim(0, 1000)
Dp.legend(loc="lower right", ncol=2, columnspacing=0.8, handlelength=1.6)
for P in (ax[0, 0], ax[0, 1], ax[1, 0]):
    P.set_xticks([0, 5000, 10000, 15000, 20000])
    P.set_xticklabels(["0", "5", "10", "15", "20"])
for P, s in zip(ax.flat, "abcd"):
    panel(P, f"({s})", x=-0.20, y=1.0)
save(fig, "fig11_native_residual_force")
r1 = np.ptp(a["Cl"][w1])
m1, m2 = a["Cl"][w1].mean(), a["Cl"][w2].mean()
print(f"D1 C_L range {r1:.5f}; window means {m1:.4f} {m2:.4f}; p min {a['p'].min():.2e}")
