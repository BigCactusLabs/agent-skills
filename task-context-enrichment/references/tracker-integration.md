# Tracker integration and preservation

Choose the writer from the target repository's instructions and available tools. This skill does not require a particular tracker. Verify command help or connector fields before using them; do not copy another repository's configuration, statuses, IDs, or timestamp exclusions.

## Before writing

Capture the original record and its stable identity/revision. Identify the intended context field and the tracker-managed fields that an update is expected to change. Everything else is protected, including task text, acceptance checkboxes, plans, existing notes, assignments, priorities, statuses, references, and dependencies.

Re-read the task immediately before mutation. If it changed, review the new version and rebuild the proposed update against it; do not send a stale whole-record replacement. Use conditional updates when the real API supports them. A read-then-write check is not atomic; do not claim stronger concurrency protection than the tool provides.

If a concurrent edit changes the task contract, hold that packet for review and continue independent tasks. If it only adds unrelated notes, preserve them when constructing the append. An ambiguous write result requires a readback before retrying, so a timeout does not duplicate the context section.

## Backlog.md

Use the repository's CLI workflow. Read its instructions and the installed command help. Versions that expose these fields support structured reads and appended implementation notes:

```bash
backlog task view TASK-101 --json
backlog task edit TASK-101 --append-notes "$context_text"
backlog doctor
```

Substitute the actual ID and pass multiline text as a structured process argument when scripting. Do not edit managed task Markdown directly. Do not copy CLI-rendered section markers into a text argument: some versions wrap them again and can corrupt neighboring sections.

Use `--append-notes` for a first enrichment pass when available. Before a repeat pass, inspect existing context and preserve unrelated notes. Do not use a replacement flag with only the new packet. Inspect auto-commit and remote-operation settings so a local context edit does not silently take another action.

For filesystem-backed tasks, compare the parsed record and file diff after the CLI write. Apart from the intended note and known bookkeeping, preserve content exactly. Read back through the CLI too; a plausible Markdown diff alone does not prove that the tracker still parses the sections correctly.

## GitHub, Linear, and other remote trackers

Use the supported CLI or structured connector and any applicable provider workflow skill. The user's request must cover updating those records. A draft-only request stays in local artifacts.

Choose a supported notes field or append a clearly delimited context section to the body. Preserve the original body and embedded acceptance checkboxes. Send only the fields needed for the change; optional fields, empty arrays, and null values can clear metadata. Do not add comments, mentions, assignments, or notifications as a substitute for the requested context field without authorization for that action.

Read back the updated record. Compare protected fields and confirm the exact context appears once. If the provider normalizes Markdown, compare parsed structure as well as content rather than requiring byte identity that the provider does not preserve. Keep the returned revision or update timestamp with the accepted packet.

## Verification boundary

Keep discovery and mutation serial for each record, and keep one tracker writer per batch. Worker reports are not write instructions. Apply only the lead-approved packet that matches the current task identity and contract.

Verify the final changed set against both the task inventory and the pre-existing workspace state. Do not demand a clean working tree when the user began with edits. Unchanged reviewed tasks, held packets, and successful updates are different outcomes and should have separate counts.
