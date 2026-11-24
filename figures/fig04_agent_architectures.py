"""Figure 4: representative engineering-agent architectures, the object each agent changes, and its feedback (Section 3.1, schematic)."""
from figstyle import BLUE, K, T_BLUE, T_GREY, T_ORANGE, W, arrow, box, canvas, save, text

H = 84
fig, ax = canvas(H)
GAP = 5
PW = (W - 1 - 2 * GAP) / 3            # panel width
BW = PW - 9                           # box width (room on the right for the feedback loop)
BH = 9.0                              # box height
ROWS = [62, 48, 34, 20]               # box centres, top to bottom


def panel(i, title, labels, fills, feedback, blind):
    x0 = 0.5 + i * (PW + GAP)
    text(ax, x0, 79.5, title, size=7.4, weight="bold", ha="left")
    for y, s, fc in zip(ROWS, labels, fills):
        box(ax, x0, y - BH / 2, BW, BH, fc=fc)
        text(ax, x0 + BW / 2, y, s, ha="center", linespacing=1.15)
    for y1, y2 in zip(ROWS, ROWS[1:]):
        arrow(ax, (x0 + BW / 2, y1 - BH / 2), (x0 + BW / 2, y2 + BH / 2))
    # feedback loop: from the last box back to the agent
    xr = x0 + BW + 4.5
    ax.plot([x0 + BW, xr, xr], [ROWS[3], ROWS[3], ROWS[1]], color=BLUE, lw=0.9)
    arrow(ax, (xr, ROWS[1]), (x0 + BW, ROWS[1]), color=BLUE, lw=0.9)
    text(ax, xr + 0.8, (ROWS[1] + ROWS[3]) / 2, feedback, size=6.3, color=BLUE, rotation=90, ha="left")
    # what the feedback does not test
    box(ax, x0, 1, BW, 10.5, fc="white", ls="--")
    text(ax, x0 + BW / 2, 6.25, blind, size=6.6, ha="center", linespacing=1.15)


panel(0, "(a) Generate and test a solver",
      ["PDE specification", "LLM agent", "Generated solver code", "Run on benchmark\nproblems"],
      [T_GREY, T_GREY, T_ORANGE, T_GREY],
      "error against reference solution",
      "Not tested: equations,\nterms, and regimes\noutside the benchmark")
panel(1, "(b) Control an existing solver",
      ["Engineering request", "LLM agent", "Model settings via\ntool calls", "Solve in persistent\nsolver session"],
      [T_GREY, T_GREY, T_ORANGE, T_GREY],
      "tool status and convergence",
      "Not tested: whether a\nboundary condition is on\nthe intended surface")
panel(2, "(c) Coordinate workflow agents",
      ["Case description", "Planning and writing\nagents", "Case files in\ndependency order", "Run case"],
      [T_GREY, T_GREY, T_ORANGE, T_GREY],
      "execution errors to reviewer",
      "Not tested: a case that\nruns but gives an\ninaccurate field")

# legend
box(ax, 0.5, 71.2, 4, 3, fc=T_ORANGE)
text(ax, 5.6, 72.7, "object the agent changes", size=6.4, ha="left")
ax.plot([42, 47], [72.7, 72.7], color=BLUE, lw=0.9)
text(ax, 48, 72.7, "feedback that guides the next action", size=6.4, ha="left", color=K)
box(ax, 91, 71.2, 4, 3, fc="white", ls="--")
text(ax, 96.1, 72.7, "not tested by that feedback", size=6.4, ha="left")

save(fig, "fig04_agent_architectures")
