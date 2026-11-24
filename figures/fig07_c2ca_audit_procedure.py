"""Figure 7: Claim-to-Computation Audit procedure (schematic)."""
from figstyle import G1, K, T_BLUE, T_GREEN, T_GREY, T_ORANGE, arrow, box, canvas, save, text

H = 92
fig, ax = canvas(H)
L, R, GAP = 1, 129, 4
HW = (R - L - GAP) / 2


def step(x, y, w, h, title, lines, size=7, fc="white"):
    box(ax, x, y, w, h, fc=fc)
    text(ax, x + 2, y + h - 3.6, title, size=8, weight="bold", va="center")
    for k, s in enumerate(lines):
        text(ax, x + 2, y + h - 9.0 - 4.3 * k, s, size=size)


# row 1
y1, h1 = 70, 21
step(L, y1, HW, h1, "1. Define the claim version",
     [r"$c_v=(q,\ \theta,\ u,\ \varepsilon)_v$", "quantity of interest, model and conditions,", "intended use, acceptance rule"], fc=T_GREY)
step(L + HW + GAP, y1, HW, h1, r"2. Approve the required set $R(c_v)$",
     ["S, A, N, B always", "V if $c_v$ asserts physical adequacy", r"$R(c_v)\neq\emptyset$; fixed by the release authority"], fc=T_GREY)
arrow(ax, (L + HW, y1 + h1 / 2), (L + HW + GAP, y1 + h1 / 2))
# divider
yd = 66.5
ax.plot([L, R], [yd, yd], color=K, lw=0.5, ls=(0, (4, 2)))
text(ax, R, yd + 1.6, "fixed before outcome evidence is interpreted", size=6.5, style="italic", ha="right")
# row 2: admissibility
y2, h2 = 49, 13
step(L, y2, R - L, h2, "3. Admissibility gate, for each evidence item and obligation",
     [r"identity verified $\wedge$ bound to $c_v$ and the exact run $\wedge$ context applicable $\wedge$ complete and finite $\wedge$ rule approved in advance"],
     size=6.8, fc=T_ORANGE)
arrow(ax, (L + HW / 2, y1), (L + HW / 2, y2 + h2))
# row 3: dispositions
y3, h3 = 28, 17
step(L, y3, R - L, h3, r"4. Obligation dispositions $d_i(c_v)$, $i\in R(c_v)$",
     [r"$d_i\in\{$SUPPORTED, REFUTED, UNRESOLVED$\}$ for $i\in\{$S, A, N, V, B$\}$",
      "V is NOT_REQUIRED when excluded by the approved claim; never counted as support"], fc=T_BLUE)
arrow(ax, ((L + R) / 2, y2), ((L + R) / 2, y3 + h3))
text(ax, (L + R) / 2 + 2, (y2 + y3 + h3) / 2, "admissible evidence only", size=6.5, ha="left", color=G1)
# row 4
y4, h4 = 1, 21
step(L, y4, HW, h4, r"5. Epistemic disposition $E(c_v)$", [], fc=T_GREEN)
step(L + HW + GAP, y4, HW, h4, r"6. Release status $L(c_v)$", [], fc=T_GREEN)
rows5 = [("REFUTED", r"if any $d_i$ = REFUTED"), ("SUPPORTED", r"if all $d_i$ = SUPPORTED"), ("UNRESOLVED", "otherwise")]
rows6 = [("RELEASED", r"only if all $d_i$ = SUPPORTED"), ("WITHHELD", "otherwise, reason retained:"), ("", "REFUTED or UNRESOLVED")]
for x0, rows in ((L, rows5), (L + HW + GAP, rows6)):
    for k, (a, b) in enumerate(rows):
        yy = y4 + h4 - 9.0 - 4.3 * k
        text(ax, x0 + 2, yy, a)
        text(ax, x0 + 21, yy, b)
for x in (L + HW / 2, L + HW + GAP + HW / 2):
    arrow(ax, (x, y3), (x, y4 + h4))
save(fig, "fig07_c2ca_audit_procedure")
