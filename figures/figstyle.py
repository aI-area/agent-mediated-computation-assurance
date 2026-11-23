"""Shared figure style: 130 mm text width, Arial, black text, square boxes with light colour-blind-safe fills."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

OUT = os.environ.get("FIG_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"))
os.makedirs(OUT, exist_ok=True)
MM = 1 / 25.4
W = 130
K, G1, G2, G3 = "#000000", "#595959", "#A6A6A6", "#D9D9D9"
BLUE, VERM, GREEN = "#0072B2", "#D55E00", "#009E73"
T_BLUE, T_ORANGE, T_GREEN, T_GREY = "#DCEBF7", "#FBE3D2", "#DCF0E4", "#EEEEEE"
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "mathtext.fontset": "stixsans", "font.size": 7, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "legend.frameon": False, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "lines.linewidth": 1.0, "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "text.color": K,
    "axes.labelcolor": K, "xtick.color": K, "ytick.color": K, "axes.edgecolor": K,
})


def canvas(h):
    fig = plt.figure(figsize=(W * MM, h * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, ls="-", lw=0.6, fc="white", ec=K):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls))


def text(ax, x, y, s, size=7, **k):
    k.setdefault("va", "center")
    k.setdefault("color", K)
    return ax.text(x, y, s, fontsize=size, **k)


def arrow(ax, p, q, ls="-", color=K, lw=0.6):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=8, lw=lw, color=color,
                                 shrinkA=0, shrinkB=0, linestyle=ls))


def panel(ax, s, x=-0.02, y=1.02):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=8, weight="bold", ha="right", va="bottom")


def save(fig, name):
    fig.savefig(f"{OUT}/{name}.pdf")
    fig.savefig(f"{OUT}/{name}.png", dpi=300)
    plt.close(fig)
