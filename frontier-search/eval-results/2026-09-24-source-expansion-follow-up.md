# Source expansion follow-up — 2026-09-24

## Scope and outcome

Continued after the user requested more depth, with a broad mix led by AI and experimental software. Added 22 entries to the frontier guide: 10 AI, 4 experimental-software, 5 hardware/robotics, and 3 other science entries. The two new source guides now contain 59 table entries in total: 46 frontier entries and 13 research/verification entries. These are discovery entries, not 59 independent evidence channels.

Added section navigation and kept SKILL.md, research budgets, tier rules, and the existing evaluation scenarios unchanged in this pass. This is a source-route and static validation record. No fresh-agent evaluation, model training, prototype installation, hardware test, or independent replication was performed. Earlier suite failures remain unresolved.

## Evidence that changed source selection

| Finding | Checked evidence | Consequence |
|---|---|---|
| Open training artifacts have useful version history | [Pythia's repository](https://github.com/EleutherAI/pythia) README and metadata retrieved through `gh api`; it contains checkpoints, research links, errata, and an evaluation-version warning. [Ai2](https://allenai.org/research) links its open-model research. | Added concrete routes to inspect training and learning dynamics, without claiming the models are the newest or reproductions were run. |
| Previously inaccessible sites can have usable alternate routes | [Nous's home page](https://nousresearch.com/) and [Hermes repository](https://github.com/NousResearch/hermes-agent) were readable. [Chips and Cheese's archive](https://chipsandcheese.com/archive) exposed bylines and a current correction notice. | Added these routes; the earlier failed retrievals remain accurately recorded in the first-pass report. |
| A blog move can leave an old archive readable and the destination empty in extraction | [Qwen's old blog](https://qwenlm.github.io/blog/) points to [the new research site](https://qwen.ai/research), which returned no readable text. The [official Hugging Face organization](https://huggingface.co/Qwen) and [Qwen3 README](https://github.com/QwenLM/Qwen3) were readable. | Prefer the owner artifact hub. Label the repository as a versioned example rather than the newest release. |
| Experimental programming has identifiable builders and concrete publication trails | [Todepond's portfolio](https://www.todepond.com/portfolio/), [Lu Wilson's ICLC contribution record](https://iclc.toplap.org/2025/catalogue/person/wilson-lu.html), [Josh Horowitz's page](https://joshuahhh.com/), and [Engraft](https://engraft.dev/) expose named work and artifacts. | Added builder and event routes; retained older publication dates and distinguished prototypes, artistic work, and satire. This is source inspection relevant to E18, not an E18 behavioral pass. |
| Performance reports expose conditions and provenance | [Colfax's optimization diary](https://research.colfax-intl.com/optimization-diaries-s-p-ping-pong-for-flashattention-4-decode/) links a code change and scopes its experiment. [Chester Lam's Adreno article](https://chipsandcheese.com/p/qualcomms-adreno-x2-gpu) identifies test hardware and a supplied review sample. [Hot Chips](https://hotchips.org/in-the-news/) links the venue's conference coverage. | Added hardware sources with setup, correction, and measurement-versus-briefing checks. The Hot Chips link supports venue context, not independent validation of measured results. |
| Robotics research offers more than demonstration videos | [Physical Intelligence's online-RL report](https://www.pi.website/research/rlt) names authors and links its paper. | Added the research index with checks for physical trials, task selection, interventions, and trial counts; no performance figure was copied into the guide. |
| Research programs widen discovery without establishing results | [Arc Institute](https://arcinstitute.org/news), [Convergent Research](https://www.convergentresearch.org/), and [ARIA](https://aria.org.uk/) expose investigators, research resources, or programs. | Added routes into biology and unusual research agendas. Funding and roadmaps remain leads to follow, not proof of feasibility. |

Other added owner indexes retrieved: Transluce, Goodfire, BAIR, Stanford CRFM, FAR.AI, ML Collective, Unison, lowRISC, and Tiny Tapeout. The frontier guide links each route and records its purpose and limits. Goodfire's old `.ai` research URL redirected to `.com`; Ai2's old blog redirected to its research index.

## Access and freshness limits

- EleutherAI's attempted website routes remained inaccessible through the web tool; its Pythia repository was readable through GitHub's API. This is not evidence that the website is inactive.
- Qwen's new research site and the attempted Smol Training Playbook Space did not expose sufficient readable content. The Qwen owner model hub supplied an alternative; the Space was not added as a verified source.
- Other attempted software sites that could not be inspected were omitted without claims that they are dead or low quality. Distill's retrieved index is historical and was not added as an active frontier feed.
- Repository metadata showed Pythia, Qwen3, and Hermes were not archived at this check. Their last pushes differed substantially. This was route verification, not an adoption recommendation or a complete maintenance audit.
- Pages, paper links, and code links were inspected as evidence. No retrieved setup command was executed; no community was joined or feed subscribed to.

## Validation

- Skill Creator's `quick_validate.py`: passed.
- Local Markdown targets, section anchors, table structure, and whitespace: passed.
- All 32 external URLs added to the frontier guide matched this pass's retrieved sources. Three repository routes were checked through GitHub's API, including README and archived-state inspection; the others used web search/retrieval. This checks source routes, not every linked artifact.
- SKILL.md and the existing research/verification guide, broader source guide, and eval scenarios were byte-identical to the snapshot at the start of this pass.
- Draft checks retained the supported limits: Pythia's README contains its evaluation-version warning; Engraft identifies its 2023 publications and limited documentation; Qwen's model hub supplies a readable alternative to the empty new-site extraction. No benchmark or reproduction claim was inferred from those routes.

Full behavioral evaluation remains unrun. Route checks and static checks do not establish that future searches will consistently follow the skill.
