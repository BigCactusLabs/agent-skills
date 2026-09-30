# Research discovery and verification

Use when a lead needs its underlying paper, related work, data, correction record, or a stronger comparison. Owner documentation was checked 2026-09-23–24 (open-access rows 2026-09-30); authenticated APIs were not tested. Recheck access, quotas, and terms when used. A searchable record does not mean accessible full text.

## Find the original work and adjacent research

| Source | Route · limit |
|---|---|
| [OpenAlex](https://help.openalex.org/api/) | Works, authors, citations. Discovery index; citation counts are not validation. |
| [Semantic Scholar](https://webflow.semanticscholar.org/product/api) | References, citing papers, recommendations. Some endpoints need a key. |
| [Crossref](https://www.crossref.org/services/metadata-retrieval/) | DOI metadata, [updates](https://www.crossref.org/documentation/principles-practices/best-practices/versioning), [Retraction Watch data](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/). No correction found does not prove soundness. |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov/about/) | Biomedical citations and abstracts with links to full text; not a full-text collection. |
| [ACL Anthology](https://aclanthology.org/) | NLP papers; main-conference, workshop, and demo papers differ. |
| [PMLR](https://proceedings.mlr.press/) | ML conference and workshop volumes; workshop is not main-conference acceptance. |
| [USENIX proceedings](https://www.usenix.org/publications/proceedings) | Systems and security papers, with artifacts and talks on event pages. |
| [Zenodo](https://zenodo.org/) | Code and datasets linked from papers. A DOI is not peer review. |
| [IDEAS / RePEc](https://ideas.repec.org/) | Economics working papers; a working paper and its journal version are one study. |
| [Unpaywall](https://unpaywall.org/products/api) | Legal open-access copy: `api.unpaywall.org/v2/<doi>?email=<real address>`; placeholder addresses get HTTP 422; rate limits unread (docs need JavaScript). Copy may be a preprint. |
| [CORE](https://core.ac.uk/services/api) | Open-access full-text search. Keyless limit "one batch request or five single requests per 10 seconds" (hit 429 on 2026-09-30). |
| [Europe PMC REST](https://www.ebi.ac.uk/europepmc/webservices/rest/search) | Biomedical search with open-access and PMC flags; keyless (docs page returned 403). `isOpenAccess` differs from `inPMC`. |
| [arXiv API](https://info.arxiv.org/help/api/index.html) | Metadata and versions. [Terms](https://info.arxiv.org/help/api/tou.html): one request every three seconds, one connection. |

For a paywalled paper, look for a legal open copy (Unpaywall, CORE, Europe PMC, the author's page) before reporting `Access-limited:`, and record which version you read. Google Scholar is manual-only (robots.txt disallows `/scholar`).

Expansion path: **one useful paper → cited predecessors → newer citing work → competing methods or replications**. When the decision depends on independence, use at least one route outside the original lab's citation cluster; several indexes returning the same paper are one channel.

## Check what was planned and what was measured

| Source | Route · limit |
|---|---|
| [OSF Registries](https://help.osf.io/article/330-welcome-to-registrations) | Study plans, registration dates, amendments. Compare timing with reported outcomes. The [Projects transition](https://help.osf.io/article/759-details-of-osf-projects-transition) is separate from Registrations and Preprints. |
| [MLCommons / MLPerf](https://mlcommons.org/benchmarks/) | Benchmark rules and results. Keep version, workload, hardware, software, and division; reviewed, provisional, and unverified results differ. |
| [Jepsen](https://jepsen.io/analyses) | Distributed-system failure tests; findings apply to the tested version and fault model; "no bug found" is not proof of correctness. See [methods](https://jepsen.io/services/analysis) and [funding context](https://jepsen.io/analyses/ethics). |
| [Hamel Husain](https://hamel.dev/) | Applied-AI evaluation and error analysis; practitioner evidence with consulting and teaching interests. |

Keep preprints, public reviews, registered reports, benchmark results, and firsthand reports distinct; combine them when they answer different parts of the question.
