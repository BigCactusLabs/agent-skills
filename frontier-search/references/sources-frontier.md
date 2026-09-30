# Frontier and experimental sources

Use for `hunt:` and for cutting-edge, experimental, or pre-consensus work. Routes were checked 2026-09-23–24; that verifies the route, not every result on it. Pick the relevant section; do not search every venue, and follow artifacts and authors beyond this list.

## Finding work before it is established

- Search for the artifact combined with the topic: `lab notebook`, `work in progress`, `prototype`, `demo`, `ablation`, `negative result`, `replication`, `workshop`, `position paper`, `RFC`, `open question`.
- Follow a useful artifact to its authors, related work, project logs, workshop program, and discussion. RSS feeds, archive pages, model and dataset cards, repository releases, and issue threads expose work general search misses.
- Keep promising early leads despite low citations or adoption. Check identity and what the author actually built; state the mechanism, why it might matter, and the smallest test that would change confidence.
- Separate **idea**, **demonstrated prototype**, **author-measured result**, and **independently reproduced result**. A demo proves only the behavior shown; a benchmark gain keeps its setup and baseline; a roadmap is an intention.
- Look for failed replications, abandoned branches, negative data, and paused projects as well as launches. Classify the artifact, not the host: a lab's paper can be T1/T3, its development note T4, its discussion T5. Do not count one artifact several times to fill tiers.

A compact entry for a lead: **what is new · artifact/date · evidence state · why it matters · unresolved test**. "Worth watching" and "worth a small experiment" are valid conclusions.

## AI models, agents, training, interpretability

| Source | Seek · check |
|---|---|
| [Transformer Circuits](https://www.transformer-circuits.pub/) | Interpretability papers, tools, and [monthly updates](https://www.transformer-circuits.pub/2026/may-update/index.html) that include preliminary experiments. Same origin as Anthropic Alignment Science. |
| [Anthropic Alignment Science](https://alignment.anthropic.com/) | Alignment experiments, evaluations, failure reports. First-party. |
| [Thinking Machines — Connectionism](https://thinkingmachines.ai/blog/) | Training, inference, and adaptation research with named authors; separate research from company vision. |
| [Sakana AI](https://sakana.ai/blog/) | Experimental model methods. Archive mixes research, products, and corporate news, in English and Japanese. |
| [Answer.AI](https://www.answer.ai/) | Applied research, small tools, builder critiques. Check the byline; tutorials and launches play different roles. |
| [Prime Intellect](https://www.primeintellect.ai/blog) | Open training systems, RL environments, agent evaluations. Use the Research category; also a compute vendor. |
| [METR](https://metr.org/research/) | Agent capability measurement, developer-productivity studies. Controlled measurements, surveys, and forecasts support different claims. |
| [ARC Prize](https://arcprize.org/blog) | Reasoning benchmarks and competition methods. Separate verified from community submissions; keep benchmark version and compute budget. |
| [AI Alignment Forum](https://www.alignmentforum.org/) | Proposals, short investigations, critiques. Posts auto-cross-post to LessWrong ([FAQ](https://www.alignmentforum.org/posts/Yp2vYb4zHXEeoTkJc/welcome-and-faq)); the copies are one source. |
| [Ai2](https://allenai.org/research) / [Olmo](https://allenai.org/olmo) | Open-model research, training artifacts, data recipes. Open weights, open data, and a reproducible run are different claims. |
| [EleutherAI Pythia](https://github.com/EleutherAI/pythia) | Checkpoints for learning-dynamics experiments. Older suite; the README warns older evaluations may not reproduce with the current harness. |
| [Qwen on Hugging Face](https://huggingface.co/Qwen) | Model cards, technical reports, release artifacts. The [old blog](https://qwenlm.github.io/blog/) points to a new site that returned no readable text; the [Qwen3 repository](https://github.com/QwenLM/Qwen3) is a versioned example, not the latest-family index. |
| [Nous Research](https://nousresearch.com/) → [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Agent memory and skill-learning implementations. Inspect code and traces; launch-page claims are not comparisons. |
| [Transluce](https://transluce.org/) | Model-behavior investigations and oversight tools. One observed failure does not establish its frequency. |
| [Goodfire](https://www.goodfire.com/research) | Interpretability and steering experiments. The index separates fundamental research, applied research, and link posts; joint work reported by a partner is the same study. |
| [BAIR blog](https://bair.berkeley.edu/blog/) | Author-written accounts of methods, systems, robotics. Follow to the paper and code. |
| [Stanford CRFM](https://crfm.stanford.edu/blog.html) | HELM variants and model evaluations. Scores from different HELM variants are not interchangeable. |
| [FAR.AI](https://www.far.ai/research) ([publications](https://www.far.ai/publications)) | Adversarial robustness, deception tests. Keep attack conditions and model access with each result. |
| [ML Collective](https://mlcollective.org/projects/) ([community](https://mlcollective.org/community/)) | Open collaborations and early projects, including work in submission; preserve that state. |

Also use OpenReview (venue, status, revisions, visible reviews) and Hugging Face (follow a paper to its author-owned model, dataset, Space, and discussion; trending rank is a discovery signal) from [sources.md](sources.md). Available weights or a demo do not establish license terms, reproducibility, or quality.

## Experimental software, interfaces, tools for thought

| Source | Seek · check |
|---|---|
| [Ink & Switch](https://www.inkandswitch.com/) | Local-first, malleable software, programmable ink. Project notebooks such as [Livelymerge](https://www.inkandswitch.com/livelymerge/notebook/) show intermediate designs and failed approaches. |
| [Folk Computer](https://folk.computer/) | Spatial and physical computing prototypes; the public wiki links repository and newsletter. Check what hardware it needs. |
| [Dynamicland](https://dynamicland.org/) | Communal computing and physical programming. Much of the front shelf is older; record the artifact's year. |
| [Geoffrey Litt](https://www.geoffreylitt.com/) | Malleable software and AI-assisted interface prototypes. Ink & Switch coauthored work shares that origin. |
| [Feeling of Computing](https://feelingof.com/) (the old Future of Coding domain redirects here) | Builder demos and programming-medium experiments; the [history](https://history.futureofcoding.org/) needs JavaScript, but dated [weekly archive](https://newsletter.futureofcoding.org/posts/future-of-coding-weekly-202508-week-3/) pages are readable. Attribute the builder, not the summary. |
| [LIVE workshop](https://liveprog.org/) | Live programming and new programming interfaces. A call for submissions is not an accepted result. |
| [Programming Experience (PX)](https://2026.programming-conference.org/home/px-2026) | Exploratory programming and tangible toolkits; follow the [program](https://2026.programming-conference.org/program/program-px-2026/). Verify the next edition rather than changing the URL's year. |
| [Lu Wilson / Todepond](https://www.todepond.com/portfolio/) | Spatial programming prototypes such as Cellpond. Separate implemented systems, art pieces, and satire. |
| [Josh Horowitz](https://joshuahhh.com/) → [Engraft](https://engraft.dev/) | Composable live interfaces; publications are from 2023. Check repository state before adoption. |
| [Unison](https://www.unison-lang.org/) ([blog](https://www.unison-lang.org/blog/)) | Hash-addressed code and distributed programming. Separate language, tools, roadmap, and commercial cloud. |
| [ICLC](https://iclc.toplap.org/) | Live coding; use a dated [catalogue](https://iclc.toplap.org/2025/catalogue/). Papers, demos, and performances are different artifacts. |

## Hardware, GPU systems, robotics

| Source | Seek · check |
|---|---|
| [Colfax Research](https://research.colfax-intl.com/) | GPU kernel experiments and optimization diaries. Keep hardware, precision, shapes, software revision, and baseline with each number; a pull request is not a release. |
| [Chips and Cheese](https://chipsandcheese.com/archive) | Microarchitecture measurements and interviews. Separate measurement from vendor briefing; check disclosed review samples. Article access varies. |
| [lowRISC](https://lowrisc.org/articles/) | Open silicon design and verification. Proposal, simulation, formal result, and measured chip are different stages. |
| [Tiny Tapeout](https://tinytapeout.com/) ([silicon-proven](https://tinytapeout.com/chips/silicon-proven/)) | Small public chip designs and bring-up notes. Submission, fabrication, and demonstrated operation are separate. |
| [Physical Intelligence](https://www.pi.website/blog) | Robot learning and VLA models. Separate simulation from physical trials; check task selection, interventions, and trial counts. |

## Experimental science beyond software

| Source | Seek · check |
|---|---|
| [Arcadia Science](https://research.arcadiascience.com/) → [The Stacks](https://thestacks.org/organizations/arcadia-science) | Early biology methods and negative data; the [Icebox](https://research.arcadiascience.com/icebox) records paused work (paused is not disproven). |
| [Speculative Technologies](https://spec.tech/) ([library](https://spec.tech/library)) | Industrial-research programs and roadmaps; a source of hypotheses, not feasibility. |
| [Arc Institute](https://arcinstitute.org/news) | Biological methods, datasets, virtual-cell research. Follow named researchers to papers and protocols. |
| [Convergent Research](https://www.convergentresearch.org/) | Focused research organizations; follow the portfolio to individual teams. Funding is not a finished tool. |
| [ARIA](https://aria.org.uk/) | Research programs and funded teams across fields. Calls, awards, milestones, and outcomes are distinct. |

This is a selective seed set; use the authors, references, and collaborators in these artifacts to reach adjacent fields.

## Maintainer discussions before release

Pitch, accepted proposal, implementation, and shipped release are distinct states; read the whole thread and its outcome.

- [Swift Evolution](https://forums.swift.org/c/evolution/18) — pitches, reviews, decisions.
- [LLVM forums](https://discourse.llvm.org/) — compiler, IR, and MLIR proposals.
- [Scientific Python](https://discuss.scientific-python.org/) — SPECs and cross-package coordination.
- [Julia Discourse](https://discourse.julialang.org/) — new packages and performance experiments.
- [PostgreSQL mailing lists](https://www.postgresql.org/list/) — proposals, patch reviews, failure reports.
- [IETF mail archives](https://mailarchive.ietf.org/arch/) — protocol debate; check document status in [Datatracker](https://datatracker.ietf.org/).

Author posts on social networks can surface an artifact before these indexes. Fetchable routes: the [Hacker News Algolia API](https://hn.algolia.com/api) and Bluesky's `app.bsky.feed.getAuthorFeed` ([access details](sources.md#t5--pre-consensus)). Follow them to the paper, notebook, repository, or recording; private chats, repost counts, and repeated launch summaries are not independent evidence.
