# Reproduction package: Assurance of Agent-Mediated Computational-Engineering Claims

This repository contains the data, code and computational records behind the article

> M. Hussain, J. Hussain, J. Abbas, Y. A. Bangash, Z. Ma, H. Wu, *Assurance of Agent-Mediated Computational-Engineering Claims: A Critical Review of Specification, Authorization, Verification, Validation, and Evidence Binding*, Archives of Computational Methods in Engineering (submitted).

It reproduces every number reported for the literature review, the recall audit and the claim-level audit; it verifies the preregistration and the authorization record of the NACA 0012 case; it replays the frozen analysis of that case from its native force histories; and it regenerates all figures.

## Quick start

```bash
python -m pip install -r requirements.txt
python reproduce.py
```

`reproduce.py` runs five checks and writes its outputs to `out/`:

| Step | What it does | Article |
|---|---|---|
| 1 | Recomputes the screening agreement, recall estimates, release counts with Clopper–Pearson intervals, obligation dispositions, ETF and tier counts, release-rule sensitivity and the comparison with the automated coding | Sections 2 and 6, Tables 15–17 |
| 2 | Checks the SHA-256 hashes of the frozen preregistration, reference values and data, analysis and set-up scripts and case template | Section 7.1 |
| 3 | Verifies the links of the hash-chained authorization effect log (27 records) | Section 7.2, Equation (15) |
| 4 | Applies the frozen acceptance rules to the force histories of the gated execution and compares the dispositions and uncertainties with the recorded ones and with the first execution | Section 7.3, Tables 20–21 |
| 5 | Regenerates Figures 1–10 and Supplementary Figure S1 | — |

Python 3.9 or later. Step 5 uses Arial or Liberation Sans; with another font, line breaks in the schematic figures may shift.

## Contents

```
review/
  search/          frozen eligibility rules, exclusion codes, search strings and strategy
  literature/      screening decisions for the 15,728 discovery records, selection lineage, full-text decisions,
                   the 237 included studies with bibliography, extraction matrix, codebook and S1 study matrix
  recall_audit/    the 816 audit records, the two authors' independent screening, disagreements with consensus,
                   recall estimates, seed recall and the preprint search (with the update check of 14 Nov 2026)
  claim_audit/     coding guide; primary coding, verification coding and the 242 verification queries with
                   consensus decisions; joint coding of the 30 records added at full text; the final claim-level
                   dataset (199 records, 131 included); consensus change log; the automated comparison coding
  analysis/        reproduce_reported_numbers.py
cfd/
  PREREGISTRATION.md, reference_values.csv, reference_data/, tools/, case_template/, Allrun.sh
                   the frozen case (hashes and freeze time in logs/preregistration.sha256)
  gate/            authorization gate: program, forced-command wrapper, approved policy, pipeline, key scripts,
                   protected-input manifest, hash-chained effect log and its verifier
  gated_execution/ dispositions with evidence hashes; per case the force and wall-resolution histories,
                   parameters and dictionaries; pipeline logs (13 Nov 2026)
  first_execution/ dispositions, runners, scheduler log and solver-setting benchmark of the first execution
                   of the frozen procedure, without the gate (3 Nov 2026)
  exhibit/         native logs and force histories of the under-resolved realization of Section 7.4
figures/           figure programs (shared style in figstyle.py) and their input data
supplement/        Online Resource 1 of the article (supplementary text, tables and figures, PDF)
```

## Online Resources of the article

The electronic supplementary material submitted with the article corresponds to this repository as follows.

| Online Resource | Content | Location in this repository |
|---|---|---|
| 1 | Supplementary text, tables and figures | `supplement/Online_Resource_1_supplement.pdf` |
| 2 | Data of the literature review, the recall audit and the claim-level audit | `review/` |
| 3 | Code and records of the NACA 0012 case, and the figure programs | `cfd/`, `figures/` |

The supplementary PDF is the version submitted for peer review and may be revised during review.

## Running the CFD case

The NASA Turbulence Modeling Resource grids and the Ladson data are public; their archive hashes are recorded in `cfd/logs/preregistration.sha256` and `cfd/PREREGISTRATION.md`. With OpenFOAM v2312, `cfd/tools/setup_cases.py` converts the PLOT3D grids (`p2d_cgrid_to_foam.py`, tested by `test_p2d_cgrid_to_foam.py`) and generates the 16 cases from `case_template/`; `cfd/gate/pipeline.sh` runs the matrix and `cfd/tools/analyse_runs.py` applies the frozen rules:

```bash
python cfd/tools/analyse_runs.py <runs directory> --out results
```

The gated execution used 6–16 cores for about eleven hours. Field directories, solver logs and residual histories of the full matrix are not in this repository because of their size; they are in the archived deposit (see below).

The files under `cfd/` that are covered by `logs/preregistration.sha256` and by `gate/protected_manifest.json` are kept byte for byte as frozen, and the execution records (runners, solver and pipeline logs, dispositions with evidence hashes, effect log) as they were produced.

## Data not redistributed

Licensed database exports (Scopus, Web of Science, IEEE Xplore, ACM Digital Library) and publication full texts are not included. Records are identified by DOI or database identifier, and coding decisions cite page-located evidence.

## Archive and citation

Archived release with the full CFD records: [https://doi.org/10.5281/zenodo.24461521](https://doi.org/10.5281/zenodo.24461521). Please cite the article and the archived release (`CITATION.cff`).

## Licence

Code: MIT (`LICENSE`). Data and documentation: CC BY 4.0 (`LICENSE-DATA`).
