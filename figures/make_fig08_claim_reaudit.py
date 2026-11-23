"""Figure 8: claim-level audit of the engineering-agent studies.

Usage: python make_fig08_claim_reaudit.py [summary.json]   (default: human_reaudit_summary.json, Online Resource 2)"""
import json
import os
import sys

import matplotlib.pyplot as plt
from figstyle import BLUE, G3, K, MM, VERM, W, panel, save

here = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "data", "human_reaudit_summary.json")
d = json.load(open(src))["all"]
fig = plt.figure(figsize=(W * MM, 92 * MM))
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.25], height_ratios=[1.0, 1.0], wspace=0.95, hspace=0.45,
                      left=0.10, right=0.97, top=0.95, bottom=0.10)
# (a) dispositions per obligation; V for the claims that require it
a = fig.add_subplot(gs[0, 0])
obl = ["S", "A", "N", "V", "B"]
col = {"SUP": BLUE, "REF": VERM, "UNR": G3}
name = {"SUP": "supported", "REF": "refuted", "UNR": "unresolved"}
seen = set()
for i, o in enumerate(obl):
    left = 0
    for k in ["SUP", "REF", "UNR"]:
        v = d[o].get(k, 0)
        if not v:
            continue
        a.barh(i, v, left=left, height=0.62, color=col[k], lw=0, label=None if k in seen else name[k])
        seen.add(k)
        if v >= 8:
            a.text(left + v / 2, i, str(v), ha="center", va="center", fontsize=6.5, color="white" if k == "SUP" else K)
        left += v
a.set_yticks(range(5))
a.set_yticklabels(["S", "A", "N", f"V ({d['Vreq']})", "B"])
a.invert_yaxis()
a.set_xlim(0, 135)
a.set_xlabel("Claims")
a.tick_params(axis="y", length=0)
a.legend(loc="lower right", bbox_to_anchor=(1.04, 0.13), ncol=1, handlelength=1.0, fontsize=6.5, labelspacing=0.3)
panel(a, "(a)", x=-0.12)
# (c) ETF types, primary or secondary
c = fig.add_subplot(gs[1, 0])
lab = {"E1": r"E1 completion$\to$S", "E2": r"E2 proxy$\to$N", "E3": r"E3 numerical$\to$V",
       "E4": r"E4 provenance$\to$validity", "E5": r"E5 benchmark$\to$context", "E6": r"E6 guard$\to$correctness"}
ks = sorted(d["etf_counts"], key=lambda k: -d["etf_counts"][k])
c.barh(range(len(ks)), [d["etf_counts"][k] for k in ks], height=0.62, color=G3, edgecolor=K, lw=0.4)
for i, k in enumerate(ks):
    c.text(d["etf_counts"][k] + 0.8, i, str(d["etf_counts"][k]), va="center", fontsize=6.5)
c.set_yticks(range(len(ks)))
c.set_yticklabels([lab[k] for k in ks], fontsize=6.5)
c.invert_yaxis()
c.set_xlim(0, 42)
c.set_xlabel("Claims")
c.tick_params(axis="y", length=0)
panel(c, "(c)", x=-0.12)
# (b) ARCS checklist
b = fig.add_subplot(gs[:, 1])
names = ["QoI and use stated", "Specification given", "Executed model vs spec", "Agent effects logged",
         "Approval gate", "Solver and schemes", "QoI iterative convergence", "Refinement study",
         "Discretization uncertainty", "y+ / element quality", "Validation data + uncertainty",
         "Validation regime matched", "Failed attempts reported", "Run identities", "Artifacts released",
         "Limitations stated"]
yn = [d["arcs"][str(i)] for i in range(1, 17)]
pct = [100 * y / n if n else 0 for y, n in yn]
b.barh(range(16), pct, height=0.62, color=G3, edgecolor=K, lw=0.4)
for i, (p, (y, n)) in enumerate(zip(pct, yn)):
    b.text(103, i, f"{y}/{n}", va="center", ha="left", fontsize=6.3)
b.set_yticks(range(16))
b.set_yticklabels([f"{i + 1:>2}  {s}" for i, s in enumerate(names)], fontsize=6.5)
b.set_ylim(15.6, -0.6)
b.set_xlim(0, 100)
b.set_xticks([0, 25, 50, 75, 100])
b.set_xlabel("Studies reporting the item (%)")
b.tick_params(axis="y", length=0)
panel(b, "(b)", x=-0.06, y=1.005)
save(fig, "fig08_claim_reaudit")
