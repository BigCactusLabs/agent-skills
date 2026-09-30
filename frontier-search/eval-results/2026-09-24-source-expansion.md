# Source expansion — 2026-09-24

## Scope and outcome

Expanded the source guides after live web research on September 23–24, with the user's clarified emphasis on cutting-edge, frontier, and experimental work. Added 24 frontier entries and 13 supporting research/verification entries. The entrypoint routes directly to the relevant guide. Existing venue examples remain, with carried dates distinguished from fresh checks.

This is a **source-route and static validation record**, not an independent behavioral evaluation. E18 was added; fresh-agent E18, E7, E8, and E13 runs were not performed. Prior full-suite failures and partial results are not resolved by this check. No authenticated API or prototype code was run.

## Live source checks

| Check | Evidence and observed outcome | Limit |
|---|---|---|
| Public work in progress | [Livelymerge notebook](https://www.inkandswitch.com/livelymerge/notebook/) exposes dated internal notes, sketches, and design work. | Index verified; no claim that the prototype was installed or reproduced. Search and page retrieval showed different newest entries, so no exact latest-entry claim was retained. |
| Preliminary findings stay preliminary | [Transformer Circuits May update](https://www.transformer-circuits.pub/2026/may-update/index.html) explicitly describes preliminary experiments rather than mature papers. | The source guide preserves that qualification; it does not endorse the experimental result. |
| Negative and paused work is discoverable | [Arcadia on The Stacks](https://thestacks.org/organizations/arcadia-science) labels negative data, methods, resources, and open questions; [Icebox](https://research.arcadiascience.com/icebox) describes paused work. | Deposit type and paused status are not peer review or a finding that a hypothesis is false. |
| Original artifacts beyond news | [Folk Computer](https://folk.computer/) links example programs, hardware/software notes, a repository, and dated updates. [LIVE](https://liveprog.org/) and [PX](https://2026.programming-conference.org/home/px-2026) expose experimental-programming venues. | A program or call is only a discovery route; implementation and publication status require artifact-level checks. |
| Correlated domains | [Alignment Forum FAQ](https://www.alignmentforum.org/posts/Yp2vYb4zHXEeoTkJc/welcome-and-faq) describes automatic cross-posting to LessWrong. | Added an explicit shared-origin example; this is not a full E13 run. |
| Rebranded community | [futureofcoding.org](https://futureofcoding.org/) redirected to [Feeling of Computing](https://feelingof.com/). Its history landing page returned a JavaScript shell; indexed dated history pages and newsletter pages were readable. | Guide names both the current venue and the access/date limits of the old archive. |
| Historical archive | [USENIX ;login: Online](https://www.usenix.org/publications/loginonline) states that publication concluded in 2025. | Added as historical context, not a new active feed. |
| Access varies by runtime | [Federal Register API documentation](https://www.federalregister.gov/developers/documentation/api/v1) loaded; [SEC filing search](https://www.sec.gov/search-filings) loaded; [CourtListener API help](https://www.courtlistener.com/help/api/) redirected to Free Law Project documentation. | Removed blanket “API-only” claims. A loaded landing page does not establish access to all records or API endpoints. |
| Literature routes | OpenAlex, Semantic Scholar, Crossref, PubMed, ACL Anthology, PMLR, USENIX proceedings, Zenodo, and IDEAS owner pages/indexes were retrieved. | No claim of complete search coverage, API availability, or full-text access. URLs and route-specific caveats are in sources-research.md. |

## Selection and counter-checks

- Prioritized lab notebooks, public experiments, workshop programs, and maintainer discussions after the user clarified their interest. General data and legal directories explored earlier were not added merely to increase the count.
- Practitioner identity checks included [Hamel Husain's O'Reilly article](https://www.oreilly.com/radar/a-field-guide-to-rapidly-improving-ai-products/), [Jepsen citations in USENIX research](https://www.usenix.org/system/files/nsdi25-ding.pdf), and [Geoffrey Litt's credited Ink & Switch appearances](https://www.inkandswitch.com/appearances/). These support identity/context, not independent replication of a technical claim.
- Sites whose contents could not be adequately inspected were not promoted into the new verified route tables: the attempted EleutherAI and Nous research paths, the CVF portal, and Chips and Cheese. These remain possible future leads, not a blacklist or a claim that the sites are inactive.
- Removed prior instructions to verify unread articles through snippets, volatile corpus counts, employer claims, and categorical judgments about a whole venue. Kept the existing budgets, tier requirements, and source-grounding invariants.

## Validation

- Skill Creator's `quick_validate.py`: passed.
- Local Markdown targets in the changed source guides and entrypoint: resolved.
- New source entries have explicit owner/index links, intended uses, and evidence limits.
- Only the Sources routing paragraph changed in SKILL.md; the research budgets and other workflow rules were preserved.

E18 remains available for a later independent behavior run. The checks above establish that the source routes and distinctions have concrete examples; they do not establish model compliance on arbitrary future questions.
