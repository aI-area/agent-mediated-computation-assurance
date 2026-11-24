"""Figure 1: structure of the review, from the literature base to the framework and its two empirical tests (schematic)."""
from figstyle import BLUE, K, T_BLUE, T_GREEN, T_GREY, T_ORANGE, arrow, box, canvas, save, text

H = 128
fig, ax = canvas(H)
RAIL, X0, R = 15, 18, 129          # rail width, content start, right edge
W = R - X0


def rail(y, h, label):
    box(ax, 1, y, RAIL, h, fc=BLUE, ec=K)
    text(ax, 1 + RAIL / 2, y + h / 2, label, size=7, weight="bold", color="white", ha="center", linespacing=1.1)


def card(x, y, w, h, title, lines, fc, size=6.6):
    box(ax, x, y, w, h, fc=fc)
    text(ax, x + w / 2, y + h - 3.6, title, size=7.4, weight="bold", ha="center")
    for k, s in enumerate(lines):
        text(ax, x + w / 2, y + h - 8.4 - 3.8 * k, s, size=size, ha="center")


gap = 3
# row 1: review protocol
y1, h1 = 113, 14
rail(y1, h1, "Section 2\nMethod")
card(X0, y1, W, h1, "Literature search and selection",
     ["Scopus, Web of Science, IEEE Xplore, ACM DL  →  15,728 records  →  237 included studies;",
      "recall audit and preregistered preprint search add 100 engineering-agent studies"], T_GREY)
# row 2: three literature streams
y2, h2 = 87, 21
rail(y2, h2, "Section 3\nLiterature")
w3 = (W - 2 * gap) / 3
streams = [("S1  Engineering agents", ["40 studies (131 after", "recall audit): model building,", "solver control, CFD, and FEM"]),
           ("S2  Agent security", ["134 studies: prompt", "injection, tool control,", "authorization, provenance"]),
           ("S3  Assurance foundations", ["63 studies: verification,", "validation, uncertainty,", "credibility, assurance cases"])]
for i, (t, ls) in enumerate(streams):
    card(X0 + i * (w3 + gap), y2, w3, h2, t, ls, T_BLUE)
arrow(ax, (X0 + W / 2, y1), (X0 + W / 2, y2 + h2))
# row 3: synthesis
y3, h3 = 61, 21
rail(y3, h3, "Section 4\nSynthesis")
w2 = (W - gap) / 2
card(X0, y3, w2, h3, "Five assurance obligations",
     ["specification fidelity (S), effect authorization (A),", "numerical verification (N), physical", "validation (V), evidence binding (B)"], T_ORANGE)
card(X0 + w2 + gap, y3, w2, h3, "Six evidence-transfer failures (E1–E6)",
     ["evidence for one obligation used", "in place of another, e.g. a completed", "run taken as numerical verification"], T_ORANGE)
# the three streams merge into one connector that feeds both synthesis boxes
ym = (y2 + y3 + h3) / 2
centres = [X0 + i * (w3 + gap) + w3 / 2 for i in range(3)]
for xs in centres:
    ax.plot([xs, xs], [y2, ym], color=K, lw=0.6, solid_capstyle="butt")
ax.plot([centres[0], centres[2]], [ym, ym], color=K, lw=0.6, solid_capstyle="butt")
for xs in (X0 + w2 / 2, X0 + w2 + gap + w2 / 2):
    arrow(ax, (xs, ym), (xs, y3 + h3))
# row 4: method
y4, h4 = 39, 17
rail(y4, h4, "Section 5\nFramework")
card(X0, y4, W, h4, "Claim-to-Computation Audit (C2CA) and ARCS reporting checklist",
     ["claim version  →  admissible evidence  →  obligation dispositions  →  release rule",
      "an assurance-case pattern, an eight-step audit procedure, and 16 reporting items"], T_GREY)
arrow(ax, (X0 + w2 / 2, y3), (X0 + w2 / 2, y4 + h4))
arrow(ax, (X0 + w2 + gap + w2 / 2, y3), (X0 + w2 + gap + w2 / 2, y4 + h4))
# row 5: two empirical tests
y5, h5 = 16, 18
rail(y5, h5, "Sections\n6–7\nTests")
card(X0, y5, w2, h5, "Claim-level audit (Section 6)",
     ["131 engineering-agent studies coded", "from full texts: 4 claims releasable"], T_GREEN)
card(X0 + w2 + gap, y5, w2, h5, "Preregistered CFD case (Section 7)",
     ["NACA 0012 on the NASA TMR grids, run", "by an agent under an authorization gate"], T_GREEN)
arrow(ax, (X0 + w2 / 2, y4), (X0 + w2 / 2, y5 + h5))
arrow(ax, (X0 + w2 + gap + w2 / 2, y4), (X0 + w2 + gap + w2 / 2, y5 + h5))
# row 6: discussion
y6, h6 = 1, 10
rail(y6, h6, "Sections\n8–9")
box(ax, X0, y6, W, h6, fc="white")
text(ax, X0 + W / 2, y6 + h6 / 2,
     "Comparison with assurance approaches, limitations, research roadmap, and conclusions", size=7.2, weight="bold", ha="center")
for xs in (X0 + w2 / 2, X0 + w2 + gap + w2 / 2):
    arrow(ax, (xs, y5), (xs, y6 + h6))
save(fig, "fig01_review_structure")
