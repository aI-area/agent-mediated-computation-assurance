"""Figure 9: grid convergence and comparison with Ladson's data for the gated NACA 0012 execution.

Usage: python make_fig09_naca0012_tmr.py [dispositions.json] [CLCD_Ladson_expdata.dat]
Defaults: the gated-execution dispositions and the Ladson file of the CFD artifacts (Online Resource 3)."""
import json
import os
import sys

import matplotlib.pyplot as plt
from figstyle import BLUE, G1, K, MM, VERM, W, panel, save

here = os.path.dirname(os.path.abspath(__file__))
disp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "data", "dispositions_gated.json")
lad_f = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "data", "CLCD_Ladson_expdata.dat")
CELLS = {"n0012_225-65": 224 * 64, "n0012_449-129": 448 * 128, "n0012_897-257": 896 * 256, "n0012_1793-513": 1792 * 512}
EXHIBIT = {"alpha": 2.15, "CL": 0.211161, "CD": 0.005011}  # under-resolved realization, final iteration (Section 7.4)

rows, zone = [], None
for line in open(lad_f):
    s = line.strip()
    if s.startswith("zone"):
        zone = s.split('"')[1]
    elif zone == "120 grit" and s and s[0] in "-.0123456789":
        rows.append(tuple(map(float, s.split())))
lad = [r for r in rows if r[0] < 17.5]
res = [r for r in json.load(open(disp))["results"] if "grids" in r]

fig, ax = plt.subplots(1, 3, figsize=(W * MM, 46 * MM), gridspec_kw={"wspace": 0.52})
mk = {0.0: ("o", K), 2.15: ("s", K), 10.0: ("^", G1), 15.0: ("D", G1)}
for r in res:
    if r["qoi"] != "CD":
        continue
    gs = sorted(r["grids"], key=lambda g: CELLS[g])
    h = [1e3 * CELLS[g] ** -0.5 for g in gs]
    f = [r["grids"][g]["mean"] / r["grids"][gs[-1]]["mean"] for g in gs]
    m, c = mk[r["alpha_deg"]]
    ax[0].plot(h, f, marker=m, ms=3.2, color=c, mfc="white", lw=0.8, label=f"{r['alpha_deg']:g}°")
ax[0].set_xlabel(r"$h=N_{\rm cells}^{-1/2}$ ($\times10^{-3}$)")
ax[0].set_ylabel(r"$C_D/C_{D,\rm fine}$")
ax[0].set_xlim(0, 9)
ax[0].legend(title=r"$\alpha$", loc="lower left", handlelength=1.6, fontsize=6.5, title_fontsize=6.5)
fine = {(r["alpha_deg"], r["qoi"]): r["grids"]["n0012_1793-513"]["mean"] for r in res}
unum = {(r["alpha_deg"], r["qoi"]): (r.get("U_num") or 0.0) for r in res}
for k, (q, lab) in enumerate([("CL", r"$C_L$"), ("CD", r"$C_D$")]):
    A = ax[k + 1]
    A.plot([x[0] for x in lad], [x[1 + k] for x in lad], "s", ms=3, mfc="white", mec=K, mew=0.6, ls="none",
           label="Ladson, 120 grit")
    pts = sorted((al, v) for (al, qq), v in fine.items() if qq == q)
    A.errorbar([p[0] for p in pts], [p[1] for p in pts], yerr=[unum[(p[0], q)] for p in pts], fmt="o", ms=3.5,
               color=BLUE, capsize=1.8, elinewidth=0.6, label="SST, finest grid")
    A.plot(EXHIBIT["alpha"], EXHIBIT[q], "x", ms=5, mew=1.2, color=VERM, ls="none", label="under-resolved run")
    A.set_xlabel(r"$\alpha$ (deg)")
    A.set_ylabel(lab)
    A.set_xticks([-5, 0, 5, 10, 15])
h_, l_ = ax[1].get_legend_handles_labels()
fig.legend(h_, l_, loc="upper center", bbox_to_anchor=(0.66, -0.10), ncol=3, fontsize=6.5, handletextpad=0.3, columnspacing=1.2)
for P, s in zip(ax, "abc"):
    panel(P, f"({s})", x=-0.30, y=1.0)
save(fig, "fig09_naca0012_tmr")
