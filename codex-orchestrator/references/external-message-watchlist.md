# ExternalMessage bridge: deferred option

Decision recorded 2026-09-09: keep the current headless Claude review path. It already supports background reviews and returns findings to Astra as tool evidence. The immediate benefit of adding an SDK bridge is small.

## When to revisit

Revisit when collecting and routing background results becomes a real bottleneck, or a persistent SDK-controlled Astra session needs automatic updates from reviewers, test runners, or other agents. `ExternalMessage` could supply that input path and reduce custom result-stream handling.

## What it provides

The Python SDK's `ExternalMessage` sends external content through `turn/start.toolOutput`, preserving tool-level authority below user and developer instructions. It starts a turn when idle or joins an active regular turn. Joining handles can independently collect the shared result. Claude remains review-only; Astra owns decisions and integration.

The sender name and namespace are labels, not authenticated identities. The bridge would still need task/revision/generation matching, message deduplication, reviewed-snapshot checks, and explicit handling of failed or stale reports. Keep large reports in artifacts with short summaries because tool output can be truncated.

## Availability at the last check

- Installed CLI `0.153.4` exposes `toolOutput` in its generated schema; the new SDK wrapper requires CLI `0.151.0` or later.
- Published `openai-codex` was `0.147.0`, pinned CLI `0.147.0`, and its inspected wheel did not contain `ExternalMessage`. The wrapper was present in repository source after PR #44086 merged on September 9.
- The SDK was absent from the default local Python environment. No SDK installation or end-to-end bridge test was performed.
- Normal SDK startup launches its own app-server process. Connecting to an existing desktop conversation is a separate integration to verify; this feature does not add missing native child messaging tools or restore Claude session persistence.

Recheck package releases, runtime compatibility, and the intended session connection before prototyping. A small parent-controlled adapter is the proposed scope: accept a commissioned review, validate its envelope and snapshot, deliver its findings as evidence, and let Astra decide the next action.

Sources checked 2026-09-09: [merged change](https://github.com/openai/codex/pull/44086), [SDK reference at the inspected revision](https://github.com/openai/codex/blob/fa7af3883df4d14861f825f9a6aadbe1ffebe63d/sdk/python/docs/api-reference.md#externalmessage), [app-server protocol](https://learn.chatgpt.com/docs/app-server), and [PyPI metadata](https://pypi.org/pypi/openai-codex/json). Registry and documentation pages can change; the availability notes above are a dated snapshot.
