# Verified venue appendix

*Every entry verified active 2026-09-02 by fetching the venue's own archive/feed, unless flagged otherwise. This list is disposable calibration data, not an allowlist: a stale entry gets re-verified, not trusted, and the tier table's recognition patterns always outrank it. Loaded on demand from SKILL.md's Source tiers section.*

Flags: **[gated]** paywall or login; **[api-only]** blocks naive page fetches, use its API; **[fetch-blocked]** 403s naive fetches and has no public API — cite from search snippets or a mirror, never from memory; **[stale]** archive has not moved in >12 months; **[unverified]** could not be confirmed this pass.

## T4 — Practitioner, by domain

| Venue | Domain | Note |
|-------|--------|------|
| Simon Willison — simonwillison.net | AI/software | Multiple posts per day; the current reference cadence |
| Marc Brooker — brooker.co.za/blog | Distributed systems | AWS Sr. Principal; now also agentic-AI safety |
| Julia Evans — jvns.ca | Tools/debugging ground truth | Lower cadence than her peak, still current |
| Sebastian Raschka — magazine.sebastianraschka.com | ML architecture | From-scratch implementations = strong anti-slop signal |
| Lilian Weng — lilianweng.github.io | ML surveys | Low cadence, cited like papers |
| Eugene Yan — eugeneyan.com | ML systems | Now at Anthropic — read eval/safety posts with that in mind |
| Zvi Mowshowitz — thezvi.substack.com | AI discourse | Use as link-harvesting layer, not as conclusions |
| SemiAnalysis — semianalysis.com | Chips/AI economics | **[gated]** research tier; free posts are T4 |
| Google Project Zero — projectzero.google | Security | Each post is a primary artifact |
| Trail of Bits — blog.trailofbits.com | Security | Every post bylined; consultancy with skin in the game |
| Krebs on Security — krebsonsecurity.com | Security/cybercrime | Breaks stories, doesn't aggregate |
| tl;dr sec — tldrsec.com | Security | Weekly curated-with-commentary; T4/T5 bridge |
| Construction Physics — construction-physics.com | Physical economy | Construction, batteries, grid, fabs |
| Volts — volts.wtf | Energy/grid | Incl. data-center energy demand |
| Asianometry — asianometry.com | Semiconductors | **[stale]** newsletter archive last dated 2025-01; the work continues video-first, so treat as T4 only via a transcript you fetched |
| Money Stuff (Matt Levine) — Bloomberg | Finance mechanics | **[gated]**; free email tier exists |
| Noahpinion — noahpinion.blog | Macro/industrial policy | Framing and data pointers, not a primary |
| In the Pipeline (Derek Lowe) — science.org/blogs/pipeline | Pharma/chemistry | **[fetch-blocked]** since 2026-09 (403 on page fetch); still the cleanest science-T4 pattern — reach posts via search snippets |
| Ground Truths (Eric Topol) — erictopol.substack.com | Medicine/medical AI | Cites primary literature inline |
| Your Local Epidemiologist — yourlocalepidemiologist.substack.com | Public health | Now multi-author masthead; check per-post byline |
| Transformer — transformernews.ai | AI policy | Named staff; reporting, not aggregation |
| Quanta Magazine — quantamagazine.org | Science | The rare science-media outlet that passes the filter |
| fly.io blog — fly.io/blog | Infra | Now ~monthly — authoritative but not a heartbeat source |
| Oxide and Friends — oxide-and-friends.transistor.fm | Hardware/OS | Podcast with recordings; Cantrill/Leventhal |

## T5 — Pre-consensus

| Venue | Note |
|-------|------|
| Lobsters — lobste.rs | Invite-gated; density holds |
| LessWrong — lesswrong.com | AI alignment dominant; persistent pseudonyms with karma history |
| r/LocalLLaMA | Best for open-weights/quant/hardware reports; weak on "which model is best" threads. `WebFetch` refuses reddit.com outright — read threads through search-result snippets |
| discuss.python.org / internals.rust-lang.org | Official Discourse — where decisions pre-date the changelog; maintainers in-thread |
| infosec.exchange | Mastodon; the credible X-replacement for security |
| Hugging Face papers — huggingface.co/papers | The paper-discussion layer Papers with Code used to be |
| Dwarkesh Podcast — dwarkesh.com | Transcripts published, so quotable |

## T2 — Authority artifacts beyond GitHub

| Artifact | Kind | Note |
|----------|------|------|
| CISA KEV catalog | Correction ledger (security) | "Actually exploited" beats raw CVSS; catalog page and alert pages both fetch fine (2026-09) |
| OSV.dev | Correction ledger (deps) | 40+ ecosystems, machine-readable |
| endoflife.date | Lifecycle record | 464 products, has an API |
| Retraction Watch — retractionwatch.com | Correction ledger (science) | 66k+ retractions, open data via Crossref |
| PubPeer | Correction ledger (science) | **[unverified]** this pass (403) |
| ClinicalTrials.gov | Pre-claim registry (medicine) | Registered vs published endpoints detects outcome-switching |
| CourtListener / RECAP | Registry + ledger (law) | Docket alerts are a real monitoring primitive; **[api-only]** in practice |
| Federal Register | Registry (US regulation) | **[api-only]** — blocks page fetches outright |
| SEC EDGAR | Pre-claim registry (vendors) | **[api-only]** for filings and full-text search; the landing page itself loads |

## T3 — Beyond arxiv

| Venue | Note |
|-------|------|
| OpenReview — openreview.net | Public reviews/rebuttals often more informative than the paper |
| alphaXiv — alphaxiv.org | Citation-grounded discovery |
| Epoch AI — epoch.ai | Structured AI-trend data; straddles T3/T4 |
| bioRxiv / medRxiv | Now run by nonprofit openRxiv |
| SSRN | Econ/law/finance; Elsevier-owned, "preprint" means less here than on arxiv. **[fetch-blocked]** since 2026-09 (403) |
| Arena — arena.ai | Human-vote leaderboards at arena.ai/leaderboard; **moved from lmarena.ai** (old links 301). The homepage now sells a general AI-tools product — go straight to the leaderboard path |

## Known dead / moved (do not cite as live)

- **Papers with Code — dead** (Meta sunset it July 2025 without notice). paperswithcode.com now 302-redirects to huggingface.co/papers/trending; snapshot at the Hugging Face `pwc-archive` org. Cite the Hugging Face page, not the old URL.
- **lmarena.ai → arena.ai** (operator rebranded to Arena Intelligence, 2026).
