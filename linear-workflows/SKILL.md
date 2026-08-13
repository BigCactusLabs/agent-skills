---
name: linear-workflows
description: Use when working with the Linear connector, Linear MCP tools, Linear issues, projects, teams, labels, comments, documents, customers, customer requests, initiatives, releases, diffs and code review, coding sessions, status updates, delegation, agent sessions, Linear Agent, or Linear-backed planning workflows.
---

# Linear Workflows

Linear's MCP server and agent platform change monthly. Two facts drive every rule:

- **The tool surface is per-connector and per-session.** Hosts expose different subsets under different prefixes. A tool that exists upstream can be absent here.
- **Linear separates `assignee` from `delegate`.** Humans are assigned; agents are delegated. Never collapse the two.

Verify, then act. Do not trust a memorised tool list — including this one.

## 1. Discover the surface first

1. Run the host's tool discovery (`tool_search`, `ToolSearch`, or equivalent) before any Linear call.
2. Read the returned **schemas**, not just names. Parameters carry the real contract (§5).
3. Treat discovery as advertised capability, not proof. Smoke-test an unfamiliar read with a low-limit call first.
4. A tool that is not surfaced does not exist in this session. Do not guess a name; find another path or say the capability is unavailable.

Prefixes vary by host — `mcp__claude_ai_Linear__<tool>` and `mcp__codex_apps__linear_<tool>` are two seen in the wild. The `<tool>` half is stable; the prefix is not. Expect 50-60 tools per host — enough that wrong-tool selection and schema cost are real risks, so discover progressively instead of loading the whole surface.

`https://mcp.linear.app/mcp/readonly` exposes read tools only; `/mcp` is read-write. A `read`-scoped token gives the same guarantee on the standard endpoint.

## 2. Read cheaply

Oversized reads are the main failure mode. Claude Code warns above 10k tokens of MCP output and truncates at 25k, and Linear bills query complexity, not just requests.

- Pass an explicit `limit`. Default 50, max 250 — both usually too many.
- Use the `fields` selector where offered (`list_issues` has one). `id` always returns.
- Filter server-side: `team`, `project`, `state`, `assignee`, `delegate`, `label`, `cycle`, `release`, `query`, `updatedAt`/`createdAt` (ISO-8601 durations such as `-P7D`).
- `orderBy: updatedAt` puts the freshest rows first; then stop. Page with `cursor` only when the answer needs it.
- Use a getter (`get_issue`, `get_project`) for one entity instead of listing and filtering. Getters accept issue identifiers such as `TEAM-123`, not only UUIDs.
- Use `search_documentation` for "how does feature X work", not workspace reads.

Complexity caps: 3M points/hour on an API key, 2M on OAuth, 10,000 per query. The requests-per-hour figure is **contested** — Linear's rate-limit page says 5,000 in prose and 2,500 for API keys in its table — so trust the `X-RateLimit-*` headers at runtime. Never poll; use webhooks.

A GraphQL `200` is not success: Linear returns partial data alongside an `errors` array, so inspect both. Rate-limit failures carry code `RATELIMITED`, usually with HTTP 400.

## 3. What exists (2026-08)

| Area | Tools | Notes |
|---|---|---|
| Workspace | `get_workspace`, `list_teams`, `get_team`, `list_users`, `get_user`, `list_cycles` | Start here to resolve names to IDs. |
| Issues | `list_issues`, `get_issue`, `save_issue`, `list_comments`, `save_comment`, `list_issue_statuses`, `list_issue_labels` | `get_issue` takes opt-in `includeRelations`, `includeCustomerNeeds`, `includeReleases`. |
| Projects | `list_projects`, `get_project`, `save_project`, `list_milestones`, `save_milestone`, `list_project_labels` | |
| Initiatives † | `list_initiatives`, `get_initiative`, `save_initiative`, `list_initiative_labels`, `create_initiative_label` | Proposed/Canceled statuses, priority and labels since 2026-07; teams can lead initiatives since 2026-08. |
| Status updates | `get_status_updates`, `save_status_update`, `delete_status_update` | Covers projects and initiatives via `type`. `health` is `onTrack`/`atRisk`/`offTrack`. Structured reports, not comments. |
| Documents | `list_documents`, `get_document`, `save_document` | Parentable to a team, initiative or cycle. |
| Releases | `list_release_pipelines`, `list_releases`, `get_release`, `save_release`, `list_release_notes`, `get_release_note`, `save_release_note` | Shipped 2026-04, on MCP since 2026-06. `list_issues` takes a `release` filter. |
| Diffs / code review † | `list_diffs`, `get_diff`, `get_diff_threads`; `save_diff_comment`, `resolve_diff_thread`, `submit_diff_review`, `merge_diff` | Native review since 2026-05, synced to GitHub. Reads are widespread, writes host-dependent. |
| Agent skills | `list_agent_skills`, `get_agent_skill` | Read-only, 2026-07. An empty list means none are defined, not a broken tool. |
| Attachments | `create_attachment`, `get_attachment`, `prepare_attachment_upload`, `extract_images` | |
| Customers † | `list_customers`, `save_customer`, `delete_customer`, `save_customer_need`, `delete_customer_need` | A customer request is a **`CustomerNeed`**. No `get_customer` or `list_customer_needs` — reach needs through `get_issue` with `includeCustomerNeeds`. |
| Generic search † | `search`, `fetch` | Broad keyword and URL entry points. |

† Host-dependent — see §6.

`research` / `linear_research` exists on no connector observed. Prefer structured reads over natural-language research anyway. When a native read is missing, use the closest list tool plus a getter and say which capability is unavailable rather than inferring an answer.

## 4. Agents, delegation and sessions

Developer Preview; the API may change. Agents are OAuth app users needing `app:assignable` to receive delegated work and `app:mentionable` to appear in mentions; an `actor=app` install cannot hold `admin`. Customers and initiatives need `customer:*` / `initiative:*`.

**Delegate is not assignee.** Assigning an issue to an app sets `delegate`. The human assignee stays accountable; the agent acts. Set `delegate` only on explicit request, and never silently move a human assignee.

When acting *as* a Linear agent:

- Sessions open automatically on @mention, delegation, or a re-prompt; an integration can open one with `agentSessionCreateOnIssue` / `agentSessionCreateOnComment`. States (`pending`, `active`, `error`, `awaitingInput`, `complete`, `stale`) are derived from your activities — do not manage them.
- Emit a `thought` within **10 seconds** of `created` or the session reads as unresponsive. Webhook handlers return within 5 seconds. Silence past 30 minutes goes stale; a later activity revives it.
- Emit `thought`, `action`, `elicitation`, `response` or `error`. `prompt` is user-generated. Finish with `response`; use `elicitation` when blocked, `error` for failures.
- **Read `AgentActivity`, not comments,** to reconstruct a conversation. Comments are editable; activities are frozen snapshots.
- A plan is replaced whole — no per-item update.
- Starting an unstarted issue: move it to the lowest-position status of type `started` on that team.
- If a human delegated the work, leave assignment alone. If no delegate is set and you are implementing, delegate to yourself.
- Deprecated: `actor=application` → `actor=app`; `AgentSession.externalLink` → `externalUrls`.

Adjacent surfaces: **coding sessions** (agent writes code via Claude Code or Codex, 2026-06), **Loops** (recurring scheduled or event-triggered agent workflows, 2026-07), **Code Intelligence** (repositories as shared agent context, 2026-05).

A **Linear Agent skill** is a workspace resource — reusable instructions saved from a good agent conversation, shareable per team, read-only over MCP. Not a repository skill file, and not this file.

## 5. Mutation rules

Never call `save_*`, `create_*`, `delete_*`, `merge_*`, `submit_*` or `resolve_*` unless the user asks for that change.

Before mutating:

1. Read the target and confirm the entity. Tools accept names, slugs, URLs or IDs; names are ambiguous, so resolve once and carry the ID. Skip an ambiguous match rather than guess.
2. State the change in plain language. Linear's own guidance: show the proposed object, the matched entity and the exact comment text before writing.
3. Use the narrowest tool and preserve unrelated fields.

**Field semantics are not uniform — read the schema.** Three kinds sit on the same tool:

- **Replace-the-set.** `save_issue.labels` replaces the whole label set; omitted labels are deleted. Read current labels first and send the full intended list. `setReleases` is the same.
- **Append-only.** `links`, `blocks`, `blockedBy`, `relatedTo`, `addReleases` — these never remove, so do not imply they do.
- **Explicit removal.** `removeBlocks`, `removeBlockedBy`, `removeRelatedTo`, `removeReleases`, and `null` on nullable scalars (`assignee`, `delegate`, `cycle`, `project`, `dueDate`, `parentId`, `estimate`). Use only on request.

For descriptions and documents use `patch` (`replace`, `insert_before`, `insert_after`, `prepend`, `append`, `replace_range`) instead of rewriting the body. Patches are atomic and each anchor must match exactly once, so a stale read fails loudly instead of clobbering someone's text.

Send Markdown as literal text with real newlines — no escape sequences.

**Confirm separately, every time** for `merge_diff`, `submit_diff_review`, any `delete_*`, publishing a status update or release note, and setting a delegate. A prior approval covers that instance only.

## 6. Connectors expose different subsets

Two hosts enumerated on 2026-08-13 advertised 59 and 53 Linear tools. Neither list was a subset of the other — each carried tools the other lacked:

| Present on one host, absent on the other | |
|---|---|
| `search`, `fetch` | `get_workspace` |
| `list_customers`, `save_customer`, `delete_customer`, `save_customer_need`, `delete_customer_need` | `save_diff_comment`, `delete_diff_comment`, `resolve_diff_thread` |
| `list_initiatives`, `get_initiative`, `save_initiative`, `list_initiative_labels`, `create_initiative_label` | `submit_diff_review`, `merge_diff` |

So customer and initiative work can be native on one host and entirely missing on another, while submitting or merging a code review goes the other way. "This tool is broken" usually means "this connector does not carry it." Enumerate your own host rather than trusting the split above.

Method, not fact: in May 2026 one connector returned `Tool ... not found` for `list_customers`, `list_initiatives` and `get_status_updates`. All three worked on that same connector three months later. Re-verify any observation older than about 60 days, and never carry a blocklist forward untested. If a read genuinely fails, do not try its matching write — state the limitation and use a fallback.

## 7. Recipes

- **Issues.** `list_issues` with `fields` and filters, `get_issue` for depth, `list_comments` for discussion, `extract_images` for embedded screenshots.
- **Planning.** `list_projects` → `get_project` → `list_milestones`, with `get_status_updates` for the health narrative.
- **Code review.** `list_diffs` filtered by `repo`/`owner`/`status` → `get_diff` → `get_diff_threads`. Comment and resolve on request; `submit_diff_review` and `merge_diff` need their own confirmation.
- **Releases.** `list_release_pipelines` → `list_releases` → `get_release`. Notes cover one release or a range.
