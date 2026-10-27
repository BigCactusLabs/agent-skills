# Research discovery and verification

For a lead's underlying paper, related work, data, correction record, or a stronger comparison. Owner docs checked 2026-09-23–24 (open-access rows 2026-09-30); authenticated APIs untested. Recheck access, quotas, and terms when used; a searchable record is not accessible full text.

## Find the original work and adjacent research

| Source | Route · limit |
|---|---|
| [OpenAlex](https://help.openalex.org/api/) | Works, authors, citations. Discovery index; citation counts don't validate. |
| [Semantic Scholar](https://webflow.semanticscholar.org/product/api) | References, citing papers, recommendations; some endpoints need a key. |
| [Crossref](https://www.crossref.org/services/metadata-retrieval/) | DOI metadata, [updates](https://www.crossref.org/documentation/principles-practices/best-practices/versioning), [Retraction Watch data](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/). No correction is not proof of soundness. |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov/about/) | Biomedical citations and abstracts, linking full text; not a full-text collection. |
| [ACL Anthology](https://aclanthology.org/) | NLP papers; main, workshop, and demo tracks differ. |
| [PMLR](https://proceedings.mlr.press/) | ML conference and workshop volumes; workshop ≠ main-conference acceptance. |
| [USENIX proceedings](https://www.usenix.org/publications/proceedings) | Systems and security papers; artifacts and talks on event pages. |
| [Zenodo](https://zenodo.org/) | Code and datasets linked from papers. A DOI is not peer review. |
| [IDEAS / RePEc](https://ideas.repec.org/) | Economics working papers; working and journal versions are one study. |
| [Unpaywall](https://unpaywall.org/products/api) | Legal open-access copy: `api.unpaywall.org/v2/<doi>?email=<real address>`; placeholder addresses get HTTP 422; rate limits unread (docs need JavaScript). The copy may be a preprint. |
| [CORE](https://core.ac.uk/services/api) | Open-access full-text search. Keyless limit "one batch request or five single requests per 10 seconds" (hit 429 on 2026-09-30). |
| [Europe PMC REST](https://www.ebi.ac.uk/europepmc/webservices/rest/search) | Biomedical search with open-access and PMC flags; keyless (docs returned 403). `isOpenAccess` ≠ `inPMC`. |
| [arXiv API](https://info.arxiv.org/help/api/index.html) | Metadata and versions. [Terms](https://info.arxiv.org/help/api/tou.html): one request per three seconds, one connection; rate-limited ("Rate exceeded", 503) on 2026-10-17 while `curl` of `arxiv.org/abs/<id>` worked. Check the abs page's submission history before citing: a later version can be a withdrawal (2610.05195 v2). No personal identifiers in the User-Agent. |

For a paywalled paper, seek a legal open copy (Unpaywall, CORE, Europe PMC, the author's page) before `Access-limited:`, and record the version read. Google Scholar is manual-only (robots.txt disallows `/scholar`).

Expansion path: **one useful paper → cited predecessors → newer citing work → competing methods or replications**. When independence matters, use at least one route outside the original lab's citation cluster.

## Check what was planned and what was measured

| Source | Route · limit |
|---|---|
| [OSF Registries](https://help.osf.io/article/330-welcome-to-registrations) | Study plans, registration dates, amendments; compare timing with reported outcomes. The [Projects transition](https://help.osf.io/article/759-details-of-osf-projects-transition) doesn't affect Registrations or Preprints. |
| [MLCommons / MLPerf](https://mlcommons.org/benchmarks/) | Benchmark rules and results. Keep version, workload, hardware, software, division; reviewed, provisional, unverified results differ. |
| [Exa ATLAS](https://exa.ai/blog/atlas-benchmark) | Agentic web-search benchmark, preview 2026-10-08, built and ranked by the vendor. Tasks, gold tables and grader unreleased as of 2026-10-26 (none in [exa-labs/benchmarks](https://github.com/exa-labs/benchmarks)): figures are vendor-reported until they ship. |
| [Jepsen](https://jepsen.io/analyses) | Distributed-system failure tests, valid for the tested version and fault model; "no bug found" is not correctness. See [methods](https://jepsen.io/services/analysis) and [funding context](https://jepsen.io/analyses/ethics). |
| [Hamel Husain](https://hamel.dev/) | Applied-AI evaluation, error analysis; practitioner with consulting and teaching interests. |

Keep preprints, public reviews, registered reports, benchmark results, and firsthand reports distinct; combine them where they answer different parts of the question.
