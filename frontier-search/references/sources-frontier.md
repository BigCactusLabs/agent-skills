# Frontier and experimental sources

For `hunt:` and experimental or pre-consensus work. Routes checked 2026-09-23–24 (the route, not every result). Use the relevant section, not every venue, and follow artifacts and authors beyond this list.

## Finding work before it is established

- Search the topic plus `lab notebook`, `work in progress`, `prototype`, `demo`, `ablation`, `negative result`, `replication`, `workshop`, `position paper`, `RFC`, or `open question`.
- Follow a useful artifact to its authors, related work, project logs, workshop program, and discussion. Feeds, archive pages, model and dataset cards, releases, and issue threads expose what general search misses.
- Keep promising early leads despite low citations or adoption. Check identity and what was actually built; state the mechanism, why it might matter, and the smallest test that would change confidence.
- Separate **idea**, **demonstrated prototype**, **author-measured result**, and **independently reproduced result**. A demo proves only what it shows; a benchmark gain keeps its setup and baseline; a roadmap is an intention.
- Seek failed replications, abandoned branches, negative data, and paused projects, not only launches. Classify the artifact, not the host: a lab's paper can be T1/T3, its development note T4, its discussion T5.

Lead entry: **what is new · artifact/date · evidence state · why it matters · unresolved test**. "Worth watching" and "worth a small experiment" are valid conclusions.

## AI models, agents, training, interpretability

| Source | Seek · check |
|---|---|
| [Transformer Circuits](https://www.transformer-circuits.pub/) | Interpretability papers, tools, [monthly updates](https://www.transformer-circuits.pub/2026/may-update/index.html) with preliminary experiments. Same origin as Anthropic Alignment Science. |
| [Anthropic Alignment Science](https://alignment.anthropic.com/) | Alignment experiments, evaluations, failure reports. First-party. |
| [Thinking Machines — Connectionism](https://thinkingmachines.ai/blog/) | Training, inference, adaptation research, named authors; separate research from company vision. |
| [Sakana AI](https://sakana.ai/blog/) | Experimental model methods; archive mixes research, products, and corporate news (English and Japanese). |
| [Answer.AI](https://www.answer.ai/) | Applied research, small tools, builder critiques. Check the byline; tutorials and launches differ in role. |
| [Prime Intellect](https://www.primeintellect.ai/blog) | Open training systems, RL environments, agent evals. Use the Research category; also a compute vendor. |
| [METR](https://metr.org/research/) | Agent capability and developer-productivity studies. Controlled measurements, surveys, and forecasts support different claims. |
| [ARC Prize](https://arcprize.org/blog) | Reasoning benchmarks, competition methods. Verified ≠ community submissions; keep benchmark version and compute budget. |
| [AI Alignment Forum](https://www.alignmentforum.org/) | Proposals, short investigations, critiques. Posts auto-cross-post to LessWrong ([FAQ](https://www.alignmentforum.org/posts/Yp2vYb4zHXEeoTkJc/welcome-and-faq)): one source. |
| [Ai2](https://allenai.org/research) / [Olmo](https://allenai.org/olmo) | Open-model research, training artifacts, data recipes. Open weights, open data, and a reproducible run are different claims. |
| [EleutherAI Pythia](https://github.com/EleutherAI/pythia) | Checkpoints for learning-dynamics experiments. Older suite; the README warns old evaluations may not reproduce on the current harness. |
| [Qwen on Hugging Face](https://huggingface.co/Qwen) | Model cards, technical reports, releases. The [old blog](https://qwenlm.github.io/blog/)'s new site returned no readable text; the [Qwen3 repo](https://github.com/QwenLM/Qwen3) is one version, not the family index. |
| [Nous Research](https://nousresearch.com/) → [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Agent memory and skill-learning code. Inspect code and traces; launch claims are not comparisons. |
| [Transluce](https://transluce.org/) | Model-behavior investigations, oversight tools. One observed failure does not establish its frequency. |
| [Goodfire](https://www.goodfire.com/research) | Interpretability and steering experiments. The index separates fundamental, applied, and link posts; joint work reported by a partner is the same study. |
| [BAIR blog](https://bair.berkeley.edu/blog/) | Author accounts of methods, systems, robotics. Follow to paper and code. |
| [Stanford CRFM](https://crfm.stanford.edu/blog.html) | HELM variants and evaluations; scores across variants are not interchangeable. |
| [FAR.AI](https://www.far.ai/research) ([publications](https://www.far.ai/publications)) | Adversarial robustness, deception tests. Keep attack conditions and model access with results. |
| [ML Collective](https://mlcollective.org/projects/) ([community](https://mlcollective.org/community/)) | Open collaborations and early projects, some in submission; preserve that state. |

Also OpenReview (venue, status, revisions, reviews) and Hugging Face (a paper's author-owned model, dataset, Space, discussion; trending rank is discovery only) from [sources.md](sources.md). Weights or a demo establish neither license, reproducibility, nor quality.

## Experimental software, interfaces, tools for thought

| Source | Seek · check |
|---|---|
| [Ink & Switch](https://www.inkandswitch.com/) | Local-first, malleable software, programmable ink. Notebooks such as [Livelymerge](https://www.inkandswitch.com/livelymerge/notebook/) show intermediate designs and failures. |
| [Folk Computer](https://folk.computer/) | Spatial and physical computing prototypes; the wiki links repo and newsletter. Check hardware needs. |
| [Dynamicland](https://dynamicland.org/) | Communal computing, physical programming. Much is older; record the artifact's year. |
| [Geoffrey Litt](https://www.geoffreylitt.com/) | Malleable software, AI-assisted interface prototypes. Ink & Switch coauthored work is one origin. |
| [Feeling of Computing](https://feelingof.com/) (formerly Future of Coding) | Builder demos, programming-medium experiments; the [history](https://history.futureofcoding.org/) needs JavaScript, dated [weekly archive](https://newsletter.futureofcoding.org/posts/future-of-coding-weekly-202508-week-3/) pages are readable. Attribute the builder, not the summary. |
| [LIVE workshop](https://liveprog.org/) | Live programming and new interfaces. A call for submissions is not a result. |
| [Programming Experience (PX)](https://2026.programming-conference.org/home/px-2026) | Exploratory programming, tangible toolkits; see the [program](https://2026.programming-conference.org/program/program-px-2026/). Verify the next edition rather than editing the URL's year. |
| [Lu Wilson / Todepond](https://www.todepond.com/portfolio/) | Spatial programming prototypes (Cellpond). Separate systems, art pieces, and satire. |
| [Josh Horowitz](https://joshuahhh.com/) → [Engraft](https://engraft.dev/) | Composable live interfaces; publications from 2023. Check repo state before adoption. |
| [Unison](https://www.unison-lang.org/) ([blog](https://www.unison-lang.org/blog/)) | Hash-addressed code, distributed programming. Separate language, tools, roadmap, commercial cloud. |
| [ICLC](https://iclc.toplap.org/) | Live coding; use a dated [catalogue](https://iclc.toplap.org/2025/catalogue/). Papers, demos, performances differ. |

## Hardware, GPU systems, robotics

| Source | Seek · check |
|---|---|
| [Colfax Research](https://research.colfax-intl.com/) | GPU kernel experiments, optimization diaries. Keep hardware, precision, shapes, software revision, and baseline with each number; a PR is not a release. |
| [Chips and Cheese](https://chipsandcheese.com/archive) | Microarchitecture measurements, interviews. Separate measurement from vendor briefing; check disclosed review samples. Access varies. |
| [lowRISC](https://lowrisc.org/articles/) | Open silicon design, verification. Proposal, simulation, formal result, measured chip are distinct stages. |
| [Tiny Tapeout](https://tinytapeout.com/) ([silicon-proven](https://tinytapeout.com/chips/silicon-proven/)) | Small public chip designs, bring-up notes. Submission, fabrication, demonstrated operation are distinct. |
| [Physical Intelligence](https://www.pi.website/blog) | Robot learning, VLA models. Separate simulation from physical trials; check task selection, interventions, trial counts. |

## Experimental science beyond software

| Source | Seek · check |
|---|---|
| [Arcadia Science](https://research.arcadiascience.com/) → [The Stacks](https://thestacks.org/organizations/arcadia-science) | Early biology methods, negative data; the [Icebox](https://research.arcadiascience.com/icebox) holds paused (not disproven) work. |
| [Speculative Technologies](https://spec.tech/) ([library](https://spec.tech/library)) | Industrial-research programs, roadmaps: hypotheses, not feasibility. |
| [Arc Institute](https://arcinstitute.org/news) | Biological methods, datasets, virtual-cell research. Follow researchers to papers and protocols. |
| [Convergent Research](https://www.convergentresearch.org/) | Focused research organizations; follow the portfolio to teams. Funding is not a finished tool. |
| [ARIA](https://aria.org.uk/) | Research programs, funded teams. Calls, awards, milestones, outcomes are distinct. |

## Maintainer discussions before release

Pitch, accepted proposal, implementation, and release are distinct states; read the whole thread and its outcome.

- [Swift Evolution](https://forums.swift.org/c/evolution/18) — pitches, reviews, decisions.
- [LLVM forums](https://discourse.llvm.org/) — compiler, IR, and MLIR proposals.
- [Scientific Python](https://discuss.scientific-python.org/) — SPECs and cross-package coordination.
- [Julia Discourse](https://discourse.julialang.org/) — new packages and performance experiments.
- [PostgreSQL mailing lists](https://www.postgresql.org/list/) — proposals, patch reviews, failure reports.
- [IETF mail archives](https://mailarchive.ietf.org/arch/) — protocol debate; check document status in [Datatracker](https://datatracker.ietf.org/).

Author social posts can surface an artifact first (fetchable routes: HN Algolia and Bluesky, [sources.md](sources.md#t5--pre-consensus)). Follow them to the paper, notebook, repo, or recording.
