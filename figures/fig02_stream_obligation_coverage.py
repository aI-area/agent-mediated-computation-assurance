"""Figure 2: obligation relevance by literature stream (counts from the extraction matrix, Online Resource 2)."""
import matplotlib.pyplot as plt
import numpy as np
from figstyle import MM, W, K, save

streams = [("S1", "Engineering agents", 40), ("S2", "Agent security", 134), ("S3", "Computational assurance", 63)]
obls = [("S", "Specification\nfidelity"), ("A", "Effect\nauthorization"), ("N", "Numerical\nverification"),
        ("V", "Physical\nvalidation"), ("B", "Evidence\nbinding")]
data = {"S1": {"S": (40, 0), "A": (10, 25), "N": (33, 7), "V": (2, 3), "B": (12, 15)},
        "S2": {"S": (0, 0), "A": (123, 11), "N": (0, 0), "V": (0, 0), "B": (50, 79)},
        "S3": {"S": (19, 44), "A": (0, 0), "N": (60, 1), "V": (22, 0), "B": (5, 14)}}
n = {s: N for s, _, N in streams}
E = np.array([[data[s][o][0] / n[s] * 100 for o, _ in obls] for s, _, _ in streams])
cmap = plt.get_cmap("Blues")
fig = plt.figure(figsize=(W * MM, 52 * MM))
ax = fig.add_axes([0.30, 0.04, 0.58, 0.68])
shade = np.where(E > 0, 0.05 + 0.80 * E / 100, np.nan)
ax.imshow(shade, cmap=cmap, vmin=0, vmax=1, aspect="auto")
for r, (s, _, _) in enumerate(streams):
    for c, (o, _) in enumerate(obls):
        e, i = data[s][o]
        if e + i == 0:
            continue
        col = "white" if shade[r, c] > 0.55 else K
        ax.text(c, r - 0.14, f"{e}/{i}", ha="center", va="center", fontsize=7.5, color=col)
        ax.text(c, r + 0.22, f"{round((e + i) / n[s] * 100)}%", ha="center", va="center", fontsize=6.5, color=col)
ax.set_xticks(range(5))
ax.set_xticklabels([f"{o}\n{l}" for o, l in obls], fontsize=7, linespacing=1.1)
ax.xaxis.tick_top()
ax.set_yticks(range(3))
ax.set_yticklabels([f"{s} {lab} ({N})" for s, lab, N in streams], fontsize=7)
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(True)
    sp.set_linewidth(0.6)
ax.set_xticks(np.arange(-.5, 5), minor=True)
ax.set_yticks(np.arange(-.5, 3), minor=True)
ax.grid(which="minor", color="white", lw=1.2)
ax.tick_params(which="minor", length=0)
cax = fig.add_axes([0.90, 0.04, 0.018, 0.68])
sm = plt.cm.ScalarMappable(cmap=plt.matplotlib.colors.ListedColormap(cmap(np.linspace(0.05, 0.85, 256))),
                           norm=plt.Normalize(0, 100))
cb = fig.colorbar(sm, cax=cax)
cb.set_label("Explicit share (%)", fontsize=7)
cb.ax.tick_params(labelsize=6.5, width=0.6, length=2)
cb.outline.set_linewidth(0.6)
save(fig, "fig02_stream_obligation_coverage")
