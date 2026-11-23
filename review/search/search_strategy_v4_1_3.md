# Database specific search strategy and eligibility rules

Protocol version: 4.1.3  
Frozen: 2026-09-15  
Action: A01-01  
Review type: reproducible state-of-the-art critical review  
Initial-search coverage end: 2026-09-15  

## Decision

The corpus will be built from three independently searchable literature streams and joined only during claim-level synthesis. A paper does not need to address agentic systems, security, and numerical verification simultaneously. This prevents the integrative research question from becoming an over-restrictive retrieval requirement.

This document is the governing strategy after the prospective S3V precision amendment. It supersedes v4.1.2 for subsequent retrieval while preserving every earlier registry, export, screenshot, and decision record. SCP-S1 and SCP-S2 were validly executed under v4.1.2 and remain unchanged. SCP-S3V v4.1.2 was stopped before export after its result-count and precision diagnostic; subsequent S3V retrieval uses v4.1.3 only.

The three streams are:

1. **Agent-mediated computational engineering**: systems that formulate, alter, execute, inspect, or report PDE, FEM, CFD, multiphysics, or related numerical-simulation workflows.
2. **Agent security, authorization, provenance, and assurance**: attacks, controls, evidence and execution lineage, capabilities, information flow, identity, delegation, runtime governance, and trace assurance for tool-using LLM agents.
3. **Numerical V&V and computational credibility**: code and solution verification, discretization and iterative error, validation, uncertainty quantification, model discrepancy, simulation credibility, assurance cases, assumption management, and workflow provenance.

## Review questions served

The searches support identification of artifacts and decisions agents can change; assumptions required by S/A/N/V/B; complementary and non-overlapping guarantees; documented Evidence-Transfer Failures; assurance-versus-utility and cost evidence; and gaps involving native solver artifacts, adaptive attacks, and provenance.

## Coverage boundaries

- Streams 1 and 2 cover 2017-01-01 through 2026-09-15. The start date follows the modern large-language-model era while allowing early tool-using and scientific-agent work.
- Stream 3 has no lower date limit. Foundational verification, validation, uncertainty, assurance-case, and provenance sources are eligible.
- The final update extends all upper dates to the actual pre-submission search date and preserves the initial exports.
- Retrieval applies no language, geography, citation-count, open-access, or positive-result filter.
- English full text is required for final claim-level extraction unless an auditable translation is available. Language decisions occur during screening, not retrieval.
- Journal articles, conference papers, reviews, book chapters, and preprints are retrieved. Standards, authoritative guidance, foundational books, and technical reports are additionally eligible in Stream 3 and, when directly relevant, Stream 2.
- Retractions are excluded from positive evidence but retained as linked status records when relevant to the review history. Corrections and errata are linked to the study family.
- Preprints and later publications are one study family. Publication status and version remain visible.

## Canonical concept blocks

### Stream 1 blocks

**Agent block**

`LLM OR "large language model" OR "large language models" OR "agentic AI" OR "AI agent" OR "AI agents" OR "scientific agent" OR "scientific agents" OR "engineering agent" OR "engineering agents"`

**Agency block**

`agent OR agents OR autonomous OR autonomy OR "tool use" OR "tool using" OR "tool-using" OR orchestration`

**Computational engineering block**

`"finite element" OR "finite elements" OR FEM OR FEniCS OR FEniCSx OR DOLFINx OR "computational fluid dynamics" OR CFD OR OpenFOAM OR PDE OR "partial differential equation" OR "partial differential equations" OR "numerical simulation" OR "numerical simulations" OR multiphysics OR "scientific computing"`

### Stream 2 blocks

**Agent block**

`"LLM agent" OR "LLM agents" OR "language model agent" OR "language model agents" OR "tool using agent" OR "tool-using agent" OR "agentic AI"`

**Security and assurance block**

`"prompt injection" OR "indirect prompt injection" OR "memory poisoning" OR "tool security" OR sandbox OR sandboxing OR capability OR capabilities OR "least privilege" OR authorization OR authorisation OR provenance OR "information flow" OR identity OR delegation OR "runtime monitoring" OR "runtime enforcement" OR "execution trace" OR "trace contract" OR assurance OR attestation OR MCP OR "Model Context Protocol" OR A2A`

### Stream 3 blocks

**Computational-model block**

`"finite element" OR "finite elements" OR FEM OR FEniCS OR FEniCSx OR DOLFINx OR "computational fluid dynamics" OR CFD OR OpenFOAM OR PDE OR "partial differential equation" OR "partial differential equations" OR "numerical simulation" OR "numerical simulations" OR multiphysics OR "scientific computing"`

**Credibility block**

The credibility concepts are executed as three separate substreams. S3V uses the numerical-verification block below; S3P retains physical validation, uncertainty, and model-discrepancy concepts; S3A retains assurance, provenance, evidence, and assumption-management concepts.

**S3V numerical-verification block**

`"code verification" OR "solution verification" OR "discretization error" OR "discretisation error" OR "iterative error" OR "grid convergence" OR "mesh convergence" OR "grid convergence index" OR "Richardson extrapolation" OR "order of accuracy" OR "observed order of accuracy" OR "method of manufactured solutions" OR "manufactured solution" OR "manufactured solutions"`

No topical `NOT` block is permitted in the initial search. Exclusions are applied transparently during screening.

## Database plan and exact query families

The machine-readable forms are frozen in `search_strings_v4_1_3.csv`. Each row is executed and exported separately so source and stream counts remain reconstructable. Stream 3 is executed as three separately archived and later deduplicated substreams: S3V (numerical verification), S3P (physical validation and uncertainty), and S3A (assurance and evidence).

### Multidisciplinary index

Scopus is attempted first. If institutional Scopus access is unavailable before any results are inspected, Web of Science Core Collection is the prespecified substitute. The access choice and reason are logged. Both may be run if both are available, but neither may be silently substituted after result inspection.

**Scopus field and filters**: `TITLE-ABS-KEY`; Streams 1-2 use `PUBYEAR > 2016 AND PUBYEAR < 2027`; Stream 3 has no year clause. Eligible Scopus document types are article, conference paper, review, and book chapter. Search results are exported with full citation, abstract, author keywords, DOI, source, year, cited references when permitted, EID, and funding fields.

**Web of Science field and filters**: `TS=` Topic; Streams 1-2 use `PY=2017-2026`; Stream 3 has no year clause. Document types are Article, Proceedings Paper, Review Article, and Book Chapter. Export Full Record and Cited References with UT and DOI.

### Engineering and computer science sources

IEEE Xplore uses Command Search over All Metadata with uppercase Boolean operators and exact phrases in quotation marks. Results are filtered to the frozen date range and exported with citations, abstracts, index terms, DOI, publication title, year, and document identifier.

ACM Digital Library uses Advanced Search with the frozen expression entered in Abstract, Title, and Author Keyword/Index Term fields, combined as `Match Any` within a concept block and `Match All` between concept blocks. The ACM Full-Text Collection and The ACM Guide to Computing Literature are both searched and exported separately because their coverage differs. The interface-generated query URL or serialized query is archived with the export.

### Publisher platforms

SpringerLink and ScienceDirect searches use the corresponding stream expression in title, abstract, and keyword fields where the interface permits. Results are filtered by the frozen date boundaries, content types, and English only at screening. Springer Nature content and ScienceDirect content are exported or captured as complete result lists with stable article URLs and DOIs.

Publisher searches are retained because records can appear online before complete indexing in multidisciplinary databases. They are deduplicated later and are not treated as independent studies.

### Preprints and open bibliographic index

arXiv API searches use the frozen `all:` expressions and date limits. Raw Atom/XML responses, request URLs, retrieval timestamps, arXiv identifiers, versions, categories, DOIs, and journal references are archived.

OpenAlex provides an openly reproducible cross-disciplinary sensitivity search. Each canonical stream string is passed through the `search` parameter with `from_publication_date` and `to_publication_date` filters as applicable. The cursor-paginated JSON responses and API URL are archived. OpenAlex does not replace the selected multidisciplinary subscription index.

### Standards and authoritative guidance

Stream 3 additionally searches the ASME Digital Collection and standards catalog, AIAA publications/catalog, NASA Technical Reports Server, NIST publications, and SISO publications. Searches combine `verification validation uncertainty` or `simulation credibility assurance` with `computational modeling`, `CFD`, or `finite element`. Known standards found through references are verified at the issuing body and recorded even when only metadata or an official summary is accessible. Access restrictions are logged; inaccessible standards are not paraphrased beyond available official text.

### Gap filling and semantic sensitivity searches

Google Scholar is used only for exact-title checks, cited-by/related-record discovery, and gap filling. Because rankings and result counts are unstable, it is not a core denominator source. Query, date, browser state, result pages inspected, and records retained are logged.

Consensus and SciSpace are supplementary semantic sensitivity sources. Their frozen natural-language questions appear in `search_strings_v4_1_3.csv`. Results may identify candidates but do not enter the evidence table until verified against a primary bibliographic or publisher record and the source text.

## Search execution and archive rules

For every query, A01-02 must record database/source, query ID, exact submitted string, searchable fields, interface/API version when visible, filters, date and timezone, exported count, pagination/completeness, export format, access limitation, file path, and SHA-256 hash.

Raw exports are immutable. If syntax fails or a query is too long for an interface, retain the failed attempt, record the error, split only at prespecified OR-block boundaries, and union the split results. Any substantive term change requires a dated amendment before re-execution; both original and amended exports remain archived.

Before bulk export, the ten positive controls in `seed_recall_v4_1_1.csv` must pass through at least one prespecified core or authoritative source for their expected stream. Supplementary semantic retrieval alone does not pass. A miss is diagnosed before bulk searching and may prompt a prospective amendment only when it demonstrates a construct-level recall defect.

Where an interface supports only year-level filtering, retrieve the complete eligible year, preserve the raw export, and post-filter by the frozen date precedence: official electronic publication date, issue date, original repository submission date for preprints, then year-only metadata. Unresolved year-only or conflicting dates remain `UNCERTAIN_DATE`. arXiv eligibility uses the original submitted timestamp while retaining the analyzed version; OpenAlex uses exact API bounds.

No query may be stopped because preliminary results look sufficient or unfavorable. Database rate limits and export caps are handled by deterministic pagination. Search results are not removed before raw archival.

## Eligibility rules

The complete machine-readable rules and reason codes are in `eligibility_rules_v4_1_1.yaml` and `screening_reason_codes_v4_1_1.csv`.

### General inclusion

A record is eligible when it has a public bibliographic identity; falls within the applicable date boundary; is an allowed evidence type; and directly satisfies at least one stream-specific rule. A work may enter through only one stream and still support cross-stream synthesis later.

### Stream-specific inclusion

- **Stream 1**: the work describes or evaluates an LLM/agentic system that can formulate, alter, execute, inspect, verify, postprocess, or release artifacts or claims in a computational-engineering or numerical-simulation workflow.
- **Stream 2**: the work describes, evaluates, surveys, or formalizes an attack, control, trust mechanism, authorization model, provenance or trace mechanism, or assurance method materially applicable to tool-using LLM agents.
- **Stream 3**: the work defines, evaluates, applies, standardizes, or critically reviews methods needed to determine whether a computational model, numerical result, workflow artifact, or simulation-supported claim is credible for an intended use.

### General exclusion

Exclude static predictive ML with no control of simulation artifacts; social agent-based simulation; generic robotics actuation; broad AI ethics without a direct S/A/N/V/B contribution; generic cybersecurity with no material agent relevance; purely symbolic/classical agents outside the date/scope rationale; non-scholarly promotional material; records lacking enough source text for the claimed use after reasonable retrieval; non-English works without an auditable English translation; duplicates; retracted works as positive evidence; and records outside the applicable date boundary.

Static surrogate or physics-informed ML studies are excluded from Stream 1 unless an agent controls or audits the simulation workflow. They may enter Stream 3 only when they make a directly relevant V&V, validation, uncertainty, discrepancy, credibility, or provenance contribution.

### Evidence roles

- `R1_PEER_REVIEWED_PRIMARY`: empirical, methodological, or formal primary study.
- `R2_PEER_REVIEWED_REVIEW`: review or survey used for synthesis and citation tracing.
- `R3_PREPRINT`: current but not peer-reviewed; version and later publication checked.
- `R4_STANDARD_GUIDANCE_BOOK_REPORT`: authoritative foundation or normative/practice context.
- `R5_SOFTWARE_OFFICIAL_DOCUMENTATION`: architecture, interface, or reproducibility evidence only; not sole support for performance or novelty.
- `R6_GENERAL_WEB`: discovery or temporal context only; excluded from the scholarly evidence table unless reclassified after source verification.

Evidence roles are not interchangeable. A preprint or software page cannot silently be represented as peer-reviewed evidence, and a standard does not establish empirical agent performance.

## Screening decision rules

Allowed decisions are `INCLUDE`, `EXCLUDE`, and `UNCERTAIN`. Uncertainty is retained through the union of two automated consistency passes. Final inclusion or exclusion must cite the source text and an eligibility rule or exclusion code. Automated passes are not independent human review. Actual human involvement is reported exactly as performed; no reviewer identity, expertise, independence, or adjudication is invented.

One of the two actual manuscript authors confirms every final eligibility decision and substantive claim code from source text. The other author additionally checks every novelty-critical study, full-text exclusion, and unresolved disagreement. The audit log records the person who actually performed each confirmation; if these checks are not performed, the manuscript must describe the narrower process.

Title-only exclusion is permitted only for unmistakable scope failures. Otherwise the abstract is inspected. Full-text exclusions use one primary reason code. Multi-stream eligibility is recorded without duplicating the study family.

## Study-family and citation-chaining rules

DOI is the primary duplicate key; normalized title, authors, year, arXiv ID, and explicit version-of relations are fallbacks. Preprint and publication versions remain linked. The most complete peer-reviewed version is the primary extraction target, while materially different preprint claims or experiments are retained at version level.

Backward references and forward citations are traced from included reviews, seminal V&V sources, closest-work records, and high-relevance primary studies. Citation chaining supplements but never replaces the database searches. Every chained record is screened under the same frozen rules and tagged with its discovery path.

## Quality and stopping rules

Citation count, venue prestige, and author reputation may guide reading order but never eligibility. Quality is assessed with design-appropriate criteria during extraction; unsuitable biomedical risk-of-bias tools will not be mechanically applied to software, security, simulation, standards, or formal-method studies.

All frozen database queries must be executed. Citation chaining continues until one complete backward/forward round from newly included high-relevance records yields no new eligible conceptual or empirical mechanism family. This saturation rule affects chaining only, not core database execution.

## Final update

Immediately before submission, rerun every core query with the upper date advanced to the update date, rerun closest-work exact-title and concept searches, link new versions and publications, rescreen new records, and document whether the novelty hierarchy or manuscript claims changed.

## Syntax references used for freezing

- Scopus Support Center, Advanced Search and `TITLE-ABS-KEY`: https://service.elsevier.com/app/answers/detail/a_id/11365/supporthub/scopus/~/how-can-i-best-use-the-advanced-search%3F/
- Web of Science Core Collection field tags: https://webofscience.help.clarivate.com/en-us/Content/wos-core-collection/woscc-search-field-tags.htm
- IEEE Xplore search guide: https://ieeexplore.ieee.org/Xplorehelp/downloads/user-guides/IEEE_Xplore_Searching_and_Saving_Searches.pdf
- ACM Digital Library user guide: https://libraries.acm.org/binaries/content/assets/libraries/new_acm-digital-library-user-guide.pdf
- PRISMA-S reporting extension: https://doi.org/10.1186/s13643-020-01542-z

## Freeze rule

This strategy is frozen before A01-02. Changes require a prospective dated decision-log amendment identifying the affected query IDs, reason, exact old and new strings, and whether all affected sources were rerun. Results already observed may not be used to silently tune eligibility or search terms.

