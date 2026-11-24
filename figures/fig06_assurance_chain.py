"""Figure 6: workflow of an agent-mediated computation, the five assurance obligations and the release decision (schematic)."""
from figstyle import BLUE, G1, K, T_BLUE, T_GREEN, T_GREY, T_ORANGE, arrow, box, canvas, save, text

H = 86
fig, ax = canvas(H)
L, R = 1, 129

# ---- top: the workflow -------------------------------------------------------------------------------
text(ax, L, 82.5, "Agent-mediated computational workflow", size=8, weight="bold")
stages = [("Approved", "problem", T_GREY, "-"), ("Agent", "actions", T_BLUE, "-"), ("Executed", "model", T_BLUE, "-"),
          ("Numerical", "result", T_BLUE, "-"), ("Physical", "evidence", T_ORANGE, (0, (3, 1.5))),
          ("Released", "claim", T_GREEN, "-")]
n, g = len(stages), 3.6
w = (R - L - (n - 1) * g) / n
ys, hs = 64, 14
for i, (a, b, fc, ls) in enumerate(stages):
    x = L + i * (w + g)
    box(ax, x, ys, w, hs, fc=fc, ls=ls)
    text(ax, x + w / 2, ys + hs / 2, a + "\n" + b, size=7.5, weight="bold", ha="center", linespacing=1.1)
    if i < n - 1:
        arrow(ax, (x + w, ys + hs / 2), (x + w + g, ys + hs / 2))
text(ax, L + 4 * (w + g) + w / 2, ys - 2.6, "only if the claim is physical", size=6.2, ha="center", style="italic", color=G1)

# ---- middle: the five obligations ------------------------------------------------------------------------
text(ax, L, 54.5, "Assurance obligations assessed before release", size=8, weight="bold")
obl = [("S", "Specification", "fidelity", ["Does the executed", "model match the", "approved problem?"]),
       ("A", "Effect", "authorization", ["Was every action of", "the agent permitted", "and recorded?"]),
       ("N", "Numerical", "verification", ["Is the numerical", "error in the quantity", "of interest controlled?"]),
       ("V", "Physical", "validation", ["Physical claims only:", "does the result agree", "with matched data?"]),
       ("B", "Evidence", "binding", ["Does all evidence", "belong to this run", "and claim version?"])]
m, g2 = len(obl), 2.6
w2 = (R - L - (m - 1) * g2) / m
yo, ho, hh = 25, 26, 10
centres = []
for i, (k, t1, t2, q) in enumerate(obl):
    x = L + i * (w2 + g2)
    centres.append(x + w2 / 2)
    box(ax, x, yo, w2, ho, fc="white", ls=(0, (3, 1.5)) if k == "V" else "-")
    box(ax, x, yo + ho - hh, w2, hh, fc=BLUE, ec=K)
    text(ax, x + 2.0, yo + ho - hh / 2, k, size=11, weight="bold", color="white")
    text(ax, x + 7.4, yo + ho - hh / 2, t1 + "\n" + t2, size=6.6, weight="bold", color="white", linespacing=1.05)
    for j, s in enumerate(q):
        text(ax, x + w2 / 2, yo + ho - hh - 4.0 - 4.2 * j, s, size=6.5, ha="center")
    arrow(ax, (x + w2 / 2, yo), (x + w2 / 2, 17.6))

# ---- bottom: release decision ------------------------------------------------------------------------------
yd, hd = 1, 16.6
box(ax, L, yd, R - L, hd, fc=T_GREEN, lw=0.9)
text(ax, (L + R) / 2, yd + hd - 4.2, "Release decision (non-compensatory)", size=8, weight="bold", ha="center")
text(ax, (L + R) / 2, yd + hd - 9.0, "RELEASED only if every required obligation is SUPPORTED", size=7, ha="center")
text(ax, (L + R) / 2, yd + hd - 13.0, "otherwise WITHHELD, with the reason kept as REFUTED or UNRESOLVED", size=7, ha="center")
save(fig, "fig06_assurance_chain")
