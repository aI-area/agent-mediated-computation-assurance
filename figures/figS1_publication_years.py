"""Supplementary Figure S1: publication years of the 237 included studies.

Usage: python figS1_publication_years.py [extraction_matrix_237.csv]"""
import csv
import os
import sys
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
from figstyle import BLUE, G2, K, MM, W, panel, save

here = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "data", "extraction_matrix_237.csv")
r = list(csv.DictReader(open(src, encoding="utf-8-sig")))
assert len(r) == 237
counts = Counter((x["stream"], int(float(x["year"]))) for x in r)
fig, (a, b) = plt.subplots(1, 2, figsize=(W * MM, 58 * MM), gridspec_kw={"width_ratios": [1.8, 1], "wspace": 0.32})
years = np.arange(1998, 2024)
a.bar(years, [counts["S3", y] for y in years], color=K, width=0.7)
a.set(xlim=(1997, 2024), ylim=(0, 8), xticks=[1998, 2006, 2014, 2023], yticks=[0, 2, 4, 6, 8],
      xlabel="Publication year", ylabel="Included studies")
x = np.arange(4)
base = np.zeros(4)
for stream, col in (("S1", BLUE), ("S2", G2), ("S3", K)):
    v = np.array([counts[stream, y] for y in range(2024, 2028)])
    b.bar(x, v, bottom=base, width=0.62, color=col, lw=0, label=stream)
    base += v
for i, n in enumerate(base):
    b.text(i, n + 2, str(int(n)), ha="center", va="bottom", fontsize=6.5)
b.set(xticks=x, xticklabels=["2024", "2025", "2026*", "2027†"], ylim=(0, 150), yticks=[0, 50, 100, 150],
      xlabel="Publication year")
b.legend(loc="upper left", handlelength=1.0, fontsize=6.5)
for ax_, p in ((a, "(a)"), (b, "(b)")):
    panel(ax_, p, x=-0.06, y=1.02)
save(fig, "figS1_publication_years")
