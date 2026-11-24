"""Figure 4: reporting profiles of the 40 engineering-agent studies.

(a) How each item is reported; (b) which items the studies report together (explicit or implicit content).
The per-study codes are tabulated in Supplementary Table S9.3 (supp_tables/tab_S9.3.tex, written by this script).

Usage: python fig04_study_evidence_profiles.py [study_matrix.csv] [reference_numbers.csv] [table_out.tex]"""
import csv
import os
import sys
from collections import Counter

import matplotlib.pyplot as plt
from figstyle import BLUE, G1, G2, G3, K, MM, W, panel, save

here = os.path.dirname(os.path.abspath(__file__))
mat = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "data", "engineering_agent_study_matrix_S1_40.csv")
refs = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "data", "reference_numbers.csv")
tab = sys.argv[3] if len(sys.argv) > 3 else os.path.join(here, "output", "tab_S9.3.tex")
rs = sorted(csv.DictReader(open(mat, encoding="utf-8-sig")), key=lambda r: r["canonical_candidate_id"])
assert len(rs) == 40
num = {r["included_study_id"]: r["reference_number"] for r in csv.DictReader(open(refs, encoding="utf-8"))}
items = [("numerical_verification_check", "Numerical check"), ("physical_validation_check", "Physical check"),
         ("provenance_binding", "Trace binding"), ("artifact_or_code_available", "Artifacts released")]


def code(v):
    if v.startswith(("YES", "EXPLICIT")):
        return "Y"
    if v.startswith("IMPLICIT"):
        return "I"
    if v == "NONE":
        return "0"
    assert v in ("NR", "NA"), v
    return "NR"


fig = plt.figure(figsize=(W * MM, 62 * MM))
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.05], height_ratios=[1.6, 1.0], wspace=0.55, hspace=0.06,
                      left=0.17, right=0.99, top=0.93, bottom=0.08)
# (a) reporting level of each item
a = fig.add_subplot(gs[:, 0])
spec = Counter(r["specification_evidence_level"] for r in rs)
rows = [("Specification", [(spec["F"], K, "F"), (spec["C"], G1, "C"), (spec["D"], G3, "D")])]
lev = [("Y", BLUE, "explicit"), ("I", "#9CC5E3", "implicit"), ("0", G2, "none"), ("NR", "white", "not reported")]
for f, lab in items:
    c = Counter(code(r[f]) for r in rs)
    rows.append((lab, [(c[k], col, k) for k, col, _ in lev]))
for i, (lab, segs) in enumerate(rows):
    left = 0
    for v, col, k in segs:
        if v:
            a.barh(i, v, left=left, height=0.6, color=col, edgecolor=K, lw=0.4)
            if v >= 3:
                tc = "white" if col in (K, G1, BLUE) else K
                a.text(left + v / 2, i, (f"{k} {v}" if i == 0 else str(v)), ha="center", va="center", fontsize=6.3, color=tc)
            left += v
a.set_yticks(range(len(rows)))
a.set_yticklabels([r[0] for r in rows])
a.set_ylim(len(rows) - 0.4, -0.6)
a.set_xlim(0, 40)
a.set_xticks([0, 10, 20, 30, 40])
a.set_xlabel("Studies")
a.tick_params(axis="y", length=0)
from matplotlib.patches import Patch
a.legend(handles=[Patch(fc=col, ec=K, lw=0.4, label=l) for _, col, l in lev], loc="upper center",
         bbox_to_anchor=(0.45, -0.17), ncol=4, fontsize=6.3, handlelength=1.0, columnspacing=0.8, handletextpad=0.4)
panel(a, "(a)", x=-0.02, y=1.02)
# (b) co-reporting combinations, items counted when explicit or implicit
combo = Counter(tuple(int(code(r[f]) in "YI") for f, _ in items) for r in rs)
order = sorted(combo, key=lambda k: (-combo[k], -sum(k)))
b = fig.add_subplot(gs[0, 1])
b.bar(range(len(order)), [combo[k] for k in order], width=0.6, color=K)
for j, k in enumerate(order):
    b.text(j, combo[k] + 0.4, str(combo[k]), ha="center", va="bottom", fontsize=6.3)
b.set_xlim(-0.6, len(order) - 0.4)
b.set_ylim(0, 18)
b.set_xticks([])
b.set_ylabel("Studies")
b.spines["bottom"].set_visible(False)
panel(b, "(b)", x=-0.02, y=1.02)
m = fig.add_subplot(gs[1, 1], sharex=b)
for j, k in enumerate(order):
    on = [i for i, v in enumerate(k) if v]
    for i in range(len(items)):
        m.plot(j, i, "o", ms=3.6, color=K if i in on else G3, mec=K if i in on else G3)
    if len(on) > 1:
        m.plot([j, j], [min(on), max(on)], color=K, lw=1.0)
m.set_ylim(len(items) - 0.5, -0.5)
m.set_yticks(range(len(items)))
m.set_yticklabels(["Numerical", "Physical", "Binding", "Artifacts"], fontsize=6.5)
m.tick_params(length=0)
m.set_xticks([])
for s in m.spines.values():
    s.set_visible(False)
save(fig, "fig04_study_evidence_profiles")

# Supplementary table: per-study codes
sym = {"Y": "Y", "I": "I", "0": "0", "NR": "--"}
lines = [r"\begin{longtable}{@{}llccccc@{}}",
         r"\caption{Reporting profiles of the 40 engineering-agent studies (Fig.~4 of the article). Spec.: specification evidence as a declaration (D), a comparison procedure (C) or a fidelity observation (F). Y explicit report; I implicit content; 0 reported absence; -- not reported.}\label{tab:S9.3}\\",
         r"\toprule", r"Study & Ref. & Spec. & Numerical & Physical & Binding & Artifacts \\", r"\midrule", r"\endfirsthead",
         r"\toprule", r"Study & Ref. & Spec. & Numerical & Physical & Binding & Artifacts \\", r"\midrule", r"\endhead",
         r"\bottomrule", r"\endlastfoot"]
for r in rs:
    fid = r["canonical_candidate_id"]
    ref = f"[{num[fid]}]" if fid in num else ""
    lines.append(" & ".join([fid, ref, r["specification_evidence_level"]] + [sym[code(r[f])] for f, _ in items]) + r" \\")
lines.append(r"\end{longtable}")
os.makedirs(os.path.dirname(tab), exist_ok=True)
open(tab, "w", encoding="utf-8").write("\n".join(lines) + "\n")
