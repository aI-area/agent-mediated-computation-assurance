"""Figure 5: representative computational-assurance workflows (Section 3.3, schematic)."""
from figstyle import K, T_BLUE, T_GREEN, T_GREY, W, arrow, box, canvas, save, text

H = 66
fig, ax = canvas(H)
X0, R, GAP = 8, W - 1, 4.5                 # content start, right edge, gap between boxes
CW = (R - X0 - 3 * GAP) / 4                 # four columns of equal width
BH = 9.5                                    # box height
cols = [X0 + i * (CW + GAP) for i in range(4)]


def node(i, y, s, fc=T_GREY):
    box(ax, cols[i], y - BH / 2, CW, BH, fc=fc)
    text(ax, cols[i] + CW / 2, y, s, ha="center", linespacing=1.2)


def chain(y, labels, fills):
    for i, (s, fc) in enumerate(zip(labels, fills)):
        node(i, y, s, fc)
    for i in range(3):
        arrow(ax, (cols[i] + CW, y), (cols[i + 1], y))


def tag(s, y):
    text(ax, 0.5, y, s, size=8, weight="bold", ha="left")


# (a) code verification: the manufactured field is also the exact reference
ya = 57
tag("(a)", ya)
chain(ya, ["Prescribed field $u^{*}$", "Derived forcing and\nboundary data", "Run implementation\non test grids",
           "Compare $u_h$ with $u^{*}$;\nobserved order"], [T_GREY, T_GREY, T_GREY, T_BLUE])
yb_line = ya - BH / 2 - 4.2
xa, xd = cols[0] + CW / 2, cols[3] + CW / 2
ax.plot([xa, xa, xd], [ya - BH / 2, yb_line, yb_line], color=K, lw=0.6, ls="--")
arrow(ax, (xd, yb_line), (xd, ya - BH / 2), ls="--")
text(ax, (xa + xd) / 2, yb_line + 1.6, "exact reference field", ha="center", style="italic")

# (b) solution verification for a fixed quantity of interest
yb = 36
tag("(b)", yb)
chain(yb, ["Fixed problem and\nquantity $q$", "Refined grids\n$h_1, h_2, h_3, \\ldots$", "Check iterative error\nof each $q(h)$",
           "Assess grid trend;\nestimate $U_{\\mathrm{num}}$"], [T_GREY, T_GREY, T_GREY, T_BLUE])

# (c) physical validation at matched conditions
yc = 13
tag("(c)", yc)
off = 6.2
node(0, yc, "Matched operating\nconditions")
node(1, yc + off, "Experiment $D$ with\nuncertainty $u_D$")
node(1, yc - off, "Qualified prediction $S$\nwith $U_{\\mathrm{num}}$")
node(2, yc, "Compare $E = S - D$\nwith uncertainty", fc=T_BLUE)
node(3, yc, "Assess adequacy\nfor intended use", fc=T_GREEN)
for s in (1, -1):
    arrow(ax, (cols[0] + CW, yc + s * 1.8), (cols[1], yc + s * off))
    arrow(ax, (cols[1] + CW, yc + s * off), (cols[2], yc + s * 1.8))
arrow(ax, (cols[2] + CW, yc), (cols[3], yc))

save(fig, "fig05_assurance_workflows")
