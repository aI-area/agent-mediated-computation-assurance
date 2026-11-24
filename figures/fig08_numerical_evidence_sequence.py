"""Figure 8: evidence sequence for numerical verification of a quantity of interest (schematic)."""
from figstyle import G1, K, T_BLUE, T_GREEN, T_GREY, T_ORANGE, arrow, box, canvas, save, text

H = 113
fig, ax = canvas(H)
X, DW = 1, 78          # decision column
PX, PW = 90, 39        # outcome column
NH, STEP = 10, 16.5
ytop = 103
box(ax, X, ytop, DW, 9, fc=T_GREY)
text(ax, X + DW / 2, ytop + 4.5, r"Numerical result for the quantity of interest $q$ of claim $c_v$", size=7.5, weight="bold", ha="center")
nodes = [("Q1", "Code verified for the solver version and options invoked?", ""),
         ("Q2", "Predeclared iterative criterion met at the reported iterations?", "Eq. (10)"),
         ("Q3", "Three or more systematically refined grids of the problem?", ""),
         ("Q4", r"Monotone convergence with $p_{\rm obs}$ near the formal order?", "Eq. (11)"),
         ("Q5", r"Numerical uncertainty within the acceptance rule $\varepsilon$?", "Eq. (11)")]
outs = [("UNRESOLVED", "not bound to this run"), ("UNRESOLVED$^{\\dagger}$", "iterative error unknown"),
        ("UNRESOLVED", r"$\delta_{\rm disc}$ not estimated"), ("conservative estimate", "larger $F_s$ or more grids"),
        ("UNRESOLVED", "bound exceeds $\\varepsilon$")]
prev = ytop
for k, ((tag, q, eq), (o1, o2)) in enumerate(zip(nodes, outs)):
    y = ytop - (k + 1) * STEP
    box(ax, X, y, DW, NH, fc=T_BLUE)
    text(ax, X + 2, y + NH / 2, tag, size=7.5, weight="bold")
    text(ax, X + 9, y + NH / 2, q, size=7)
    if eq:
        text(ax, X + DW - 2, y + NH / 2 - 3.2, eq, size=6.5, ha="right", color=G1)
    arrow(ax, (X + DW / 2, prev), (X + DW / 2, y + NH))
    if k:
        text(ax, X + DW / 2 - 1.5, (prev + y + NH) / 2, "yes", size=6.5, ha="right")
    dashed = k == 3
    box(ax, PX, y, PW, NH, ls=(0, (3, 1.5)) if dashed else "-", fc=T_GREY if dashed else T_ORANGE)
    text(ax, PX + PW / 2, y + NH - 3.2, o1, size=7, ha="center", weight="normal" if dashed else "bold")
    text(ax, PX + PW / 2, y + 3.0, o2, size=6.5, ha="center")
    arrow(ax, (X + DW, y + NH / 2), (PX, y + NH / 2))
    text(ax, (X + DW + PX) / 2, y + NH / 2 + 1.6, "no", size=6.5, ha="center")
    prev = y
    if dashed:
        yr = y - (STEP - NH) / 2
        ax.plot([PX + PW / 2, PX + PW / 2, X + DW / 2 + 6], [y, yr, yr], color=K, lw=0.6, ls=(0, (3, 1.5)))
        arrow(ax, (X + DW / 2 + 6.01, yr), (X + DW / 2 + 0.3, yr), ls=(0, (3, 1.5)))
yS = prev - STEP
arrow(ax, (X + DW / 2, prev), (X + DW / 2, yS + NH))
text(ax, X + DW / 2 - 1.5, (prev + yS + NH) / 2, "yes", size=6.5, ha="right")
box(ax, X + DW / 2 - 18, yS, 36, NH, lw=1.0, fc=T_GREEN)
text(ax, X + DW / 2, yS + NH / 2, "N SUPPORTED", size=7.5, weight="bold", ha="center")
save(fig, "fig08_numerical_evidence_sequence")
