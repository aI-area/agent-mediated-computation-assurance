"""Map included-study identifiers to the reference numbers printed in the compiled article (from its .aux file).

Usage: python build_reference_numbers.py <manuscript.aux> <cited_reference_identity_map.csv> <out.csv>"""
import csv
import re
import sys

aux, idmap, out = sys.argv[1:4]
num = dict(re.findall(r"bibcite\{(\w+)\}\{\{(\d+)\}", open(aux, encoding="utf-8").read()))
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["included_study_id", "bibtex_key", "reference_number"])
    n = 0
    for r in csv.DictReader(open(idmap, encoding="utf-8-sig")):
        if r["included_study_id"] and r["bibtex_key"] in num:
            w.writerow([r["included_study_id"], r["bibtex_key"], num[r["bibtex_key"]]])
            n += 1
            if num[r["bibtex_key"]] != r["printed_reference"]:
                print("renumbered", r["included_study_id"], r["printed_reference"], "->", num[r["bibtex_key"]])
print(n, "studies mapped")
