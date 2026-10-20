# Practitioner venues, authority records, and access notes

Discovery examples, not an allowlist or a rating of a venue's every post; classify each artifact by its role in the answer.

**Dates.** ✓ = checked live 2026-09-30 (a post within the month unless a latest date is given; endpoints responded as noted); (09-23) = rechecked 2026-09-23; unmarked = 2026-09-02 snapshot. Recheck activity and the artifact before relying on an entry; carry no employer, cadence, or corpus-size claims into an answer.

**Flags.** **[gated]** payment or login for some content. **[fetch-blocked]** a prior fetch failed in that runtime (not permanent). **[stale]** no archive update in >12 months at the snapshot. APIs are alternate routes, not necessarily keyless.

## T4 — Practitioner, by domain

| Venue | Domain | Note |
|---|---|---|
| Simon Willison — simonwillison.net | AI/software | Experiments linking original artifacts |
| Marc Brooker — brooker.co.za/blog | Distributed systems | Check the post's scope |
| Julia Evans — jvns.ca | Tools/debugging | Worked explanations |
| Sebastian Raschka — magazine.sebastianraschka.com | ML architecture | Inspect code and evaluation setup |
| Lilian Weng — lilianweng.github.io | ML surveys | Check the date; follow cited papers |
| Eugene Yan — eugeneyan.com | ML systems | Applied ML and evaluation |
| Zvi Mowshowitz — thezvi.substack.com | AI discourse | Link harvesting, not conclusions |
| SemiAnalysis — semianalysis.com | Chips/AI economics | **[gated]** research tier; free posts T4 |
| Google Project Zero — projectzero.google | Security | Original vulnerability research |
| Trail of Bits — blog.trailofbits.com | Security | Check byline, artifacts, consultancy |
| Krebs on Security — krebsonsecurity.com | Security/cybercrime | Reporting, not experiment |
| tl;dr sec — tldrsec.com | Security | Weekly curation; T4/T5 bridge |
| Construction Physics — construction-physics.com | Physical economy | Construction, batteries, grid, fabs |
| Volts — volts.wtf | Energy/grid | Includes data-center demand |
| Asianometry — asianometry.com | Semiconductors | ✓ Newsletter **[stale]** (2025-01-21); YouTube active via `youtube.com/feeds/videos.xml?channel_id=UC1LpsuAUaKoMzzJSEt5WImw`. Cite the recording or transcript |
| Money Stuff (Matt Levine) — Bloomberg | Finance mechanics | **[gated]**; free email tier |
| Noahpinion — noahpinion.blog | Macro/industrial policy | Framing and data pointers |
| In the Pipeline (Derek Lowe) — science.org/blogs/pipeline | Pharma/chemistry | **[fetch-blocked]**; snippets are leads |
| Ground Truths (Eric Topol) — erictopol.substack.com | Medical AI | Cites primary literature inline |
| Your Local Epidemiologist — yourlocalepidemiologist.substack.com | Public health | Multi-author; check each byline |
| Transformer — transformernews.ai | AI policy | Named staff reporting |
| Quanta Magazine — quantamagazine.org | Science | Follow to named researchers and papers |
| fly.io blog — fly.io/blog | Infra | Operating reports; vendor |
| Oxide and Friends — oxide-and-friends.transistor.fm | Hardware/OS | Podcast with recordings |
| Phil Eaton — notes.eatonphil.com | Databases | ✓ Internals; check employer per post |
| Andy Pavlo — cs.cmu.edu/~pavlo/blog | Databases | ✓ Annual review (latest 2026-01-04); cite the year |
| Alex Russell — infrequently.org | Web performance | ✓ Advocacy vs measurement; check affiliation |
| Jake Archibald — jakearchibald.com | Web platform/CSS | ✓ Browser-behavior write-ups |
| Michael Tsai — mjtsai.com/blog | Apple development | ✓ Quote-links; cite the original |
| Jake Wharton — jakewharton.com | Android/Kotlin | ✓ About monthly |
| Lorin Hochstein — surfingcomplexity.blog | Incident analysis | ✓ The operator's postmortem is primary |
| Charity Majors — charity.wtf | Observability | ✓ Covers honeycomb.io too; vendor interest |
| Corey Quinn — lastweekinaws.com | AWS cost | ✓ Satire mixed in; employer sells cost advisory |
| matklad — matklad.github.io | Languages/systems | ✓ |
| Ralf Jung — ralfj.de/blog | Rust semantics | ✓ Latest 2026-03-13 |
| Max Bernstein — bernsteinbear.com | Compilers/JITs | ✓ Feed pins an old item; sort by date |
| Nathan Lambert — interconnects.ai | AI post-training | ✓ Check for paywall |
| Lawfare — lawfaremedia.org | Security law/policy | ✓ Feed omits bylines; cite the filing or statute |
| Eric Goldman — blog.ericgoldman.org | Internet/IP law | ✓ Guest posts appear; check byline |
| Apricitas Economics — apricitas.io | Macro/labor data | ✓ Cite the official series |
| Calculated Risk — calculatedrisk.substack.com | Housing/macro data | ✓ From calculatedriskblog.com 2026-01; paywall unchecked |
| The Climate Brink — theclimatebrink.com | Climate science | ✓ |
| Carbon Brief — carbonbrief.org | Climate/energy | ✓ Feed byline "Staff"; read the author |
| Owl Posting — owlposting.com | Biotech | ✓ |
| Century of Bio — centuryofbio.com | Biotech | ✓ Latest 2026-06-21; investor context |
| Asimov Press — asimov.press | Biology | ✓ Feed byline is the publication; read the author |

## T5 — Pre-consensus

| Venue | Note |
|---|---|
| Lobsters — lobste.rs | Verify participants and the artifact |
| LessWrong — lesswrong.com | AI alignment; persistent pseudonyms with karma history |
| r/LocalLLaMA | Open weights, quantization, hardware. Fetch access varies by runtime; verify the author's setup |
| discuss.python.org / internals.rust-lang.org | Official Discourse; decisions precede the changelog |
| infosec.exchange | Security practitioners on Mastodon |
| Hugging Face papers — huggingface.co/papers | Discussion; popularity is not validation |
| Dwarkesh Podcast — dwarkesh.com | Transcripts, so quotable |
| Hacker News via Algolia — hn.algolia.com/api/v1 | ✓ Keyless. `search_by_date?tags=story` or `tags=comment` with `numericFilters=created_at_i>…` (URL-encode `>`); `/items/<id>` returns a thread |
| Bluesky AppView — api.bsky.app/xrpc | ✓ Logged out: `app.bsky.feed.searchPosts` on `api.bsky.app` (403 on `public.api.bsky.app`); `getAuthorFeed` on `public.api.bsky.app`. Best for known experts |
| GitHub Discussions — github.com/<org>/<repo>/discussions | ✓ Readable logged out, timestamped. Check whether participants are maintainers |
| Mastodon tags — e.g. hachyderm.io/api/v1/timelines/tag/<tag> | ✓ Keyless, mixes federated posts; unauthenticated `/api/v2/search` returns no statuses. Follow known accounts |

## T2 — Authority records

| Record | Kind | Note |
|---|---|---|
| CISA KEV catalog | Exploitation (security) | Absence is not proof of safety |
| OSV.dev | Vulnerabilities (deps) | Match ecosystem and affected versions |
| [GitHub Advisory Database](https://github.com/advisories) | Vulnerabilities (deps) | ✓ [REST API](https://docs.github.com/en/rest/security-advisories/global-advisories) keyless, 60 req/h. Reviewed ≠ unreviewed |
| [NVD](https://nvd.nist.gov/developers/start-here) | Vulnerability enrichment | ✓ CVE API 2.0 keyless at a lower rate. Since [2026-04-15](https://www.nist.gov/news-events/news/2026/04/nist-updates-nvd-operations-address-record-cve-growth) NIST fully enriches only prioritized CVEs; **a missing CVSS/CPE is not evidence of low severity** |
| [CVE.org](https://www.cve.org/) | Vulnerability IDs | ✓ `cveawg.mitre.org/api/cve/<id>` keyless. CNA description, not a severity finding |
| [deps.dev](https://docs.deps.dev/api/v3/) | Package lifecycle | ✓ Keyless v3 (`publishedAt`, `isDeprecated`). Derived; confirm at the registry |
| [OpenSSF Scorecard](https://scorecard.dev/) | Repo security practices | ✓ `api.scorecard.dev` keyless. The [README](https://github.com/ossf/scorecard) says the aggregate "tells you nothing about what individual behaviors a repository is or is not doing"; read the checks |
| Registry JSON: [PyPI](https://docs.pypi.org/api/json/), [npm](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md), crates.io `/api/v1/crates/<name>` | Releases (deps) | ✓ Keyless. PyPI `downloads` is always -1. Release dates show publishing, not maintenance quality |
| endoflife.date | Lifecycle | Confirm consequential dates with the owner |
| Statuspage (e.g. [githubstatus.com/api](https://www.githubstatus.com/api)) | Incidents (vendors) | ✓ `/api/v2/incidents.json`. Vendor self-report |
| SEC EDGAR — [filing search](https://www.sec.gov/search-filings) | Filings (vendors) | (09-23) Disclosures, not proof of claims |
| Retraction Watch | Corrections (science) | (09-23) Via [Crossref](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/); read the notice |
| PubPeer | Corrections (science) | ✓ Homepage reachable; `/search` bot-challenged: **[fetch-blocked]** |
| ClinicalTrials.gov | Registry (medicine) | Compare dated registrations and amendments with reported endpoints |
| [openFDA](https://open.fda.gov/apis/authentication/) | Drugs/devices | ✓ Keyless, 1,000 req/day per IP. Unvalidated; confirm at Drugs@FDA or the label |
| CourtListener / RECAP — [API](https://wiki.free.law/c/courtlistener/help/api) | Law | (09-23) Access depends on account; coverage incomplete |
| Federal Register — [API](https://www.federalregister.gov/developers/documentation/api/v1) | US regulation | (09-23) Verify document status and effective date |
| [Congress.gov API](https://api.congress.gov/) | US legislation | ✓ Key required; `DEMO_KEY` works. Bill status is not enactment |
| [legislation.gov.uk](https://www.legislation.gov.uk/developer) | UK law | ✓ Keyless. "Changes to Legislation" lists unapplied amendments |
| EU law — [CELLAR SPARQL](https://publications.europa.eu/webapi/rdf/sparql) | EU law | ✓ Keyless. EUR-Lex **[fetch-blocked]** (WAF). Consolidated vs original text |
| Web standards — [W3C API](https://api.w3.org/specifications/html?format=json), [WHATWG](https://whatwg.org/faq) | Standards | ✓ For HTML/DOM/Fetch the WHATWG Living Standard is current; W3C `/TR` may be a dated snapshot |
| [Wayback Machine](https://archive.org/help/wayback_api.php) ([CDX](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server)) | Page provenance | ✓ Keyless. Dead links, past states, silent edits (compare CDX digests). No capture proves nothing |

## T3 — Beyond arXiv

| Venue | Note |
|---|---|
| OpenReview — openreview.net | Public reviews and rebuttals often beat the paper |
| alphaXiv — alphaxiv.org | Discussion; verify in the paper |
| Epoch AI — epoch.ai | Structured AI-trend data; T3/T4 |
| bioRxiv / medRxiv | Check review status and later versions |
| SSRN | Working papers; **[fetch-blocked]** |
| Arena — arena.ai (was lmarena.ai) | Preference leaderboards; check method, date |
| NBER — nber.org/papers | ✓ Not peer-reviewed; the journal version is the same study |

## Moved sources

- [Papers with Code](https://paperswithcode.com/) → [Hugging Face Trending Papers](https://huggingface.co/papers/trending) (2026-09-23); the old benchmark database may be gone.
- **archive.today is not a provenance route:** it served DDoS code in January 2026, Wikimedia reports altered archives, and English Wikipedia deprecated it on 2026-02-20 ([record](https://meta.wikimedia.org/wiki/Archive.today_incident), checked 2026-09-30). Use the Wayback Machine; an archive.today copy is an unverified lead.
