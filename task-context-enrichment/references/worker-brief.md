# Worker brief and result packet

Use this for independent factual discovery. Fill in the task-specific inputs before dispatch; it is not permission to expand into implementation. Delegate through the available orchestrator workflow when one applies.

```text
Assignment: {stable ID}; revision {revision}; generation {generation}.
Role: bounded context-extraction worker. The lead owns decisions and integration.
Do not spawn agents.

Goal: prepare verified implementation context for {exact task IDs}, so a later
implementer can find the right code, preserve the task contract, and start work.

Workspace and baseline: {repository path, branch, commit, relevant dirty inputs}.
Inputs: {task snapshots/getter, repository instructions, known dependencies,
relevant decisions, and any evidence the repository excludes}.
Ownership: repository and tracker are read-only. Write only {output directory}.
Other workers may read overlapping source. The lead may update other task notes;
do not treat those additions as source changes or overwrite them.

Inspect each complete task, current source and callers, relevant tests, command
definitions, and dated evidence. Return factual context, not a new design.
Mark missing evidence and unresolved decisions explicitly. Verify whether a
limitation in old prose still exists in code. Do not turn a planned file or old
command into a current entry point. Include useful source paths in the note body.

No task mutations, implementation, builds, benchmarks, shared cache writes,
branch operations, commits, external messages, or permission bypass.
Use additional repositories or external research only if assigned and authorized.
If a new measurement is needed, describe it as future validation, not a result.

Output: {result path}, using the packet shape below. Keep individual notes to a
few useful paragraphs; use the task's complexity rather than a word-count quota.
For a long inspection, save {checkpoint path} with assignment/revision/generation,
completed evidence, unresolved items, and the next bounded action.

Acceptance: exact assigned task coverage, readable structured output, verified
current paths/anchors, clearly marked historical and missing references, no
repository/tracker mutations, and no invented decisions or validation results.

Report actual checks, deviations, uncertainty, and the result artifact path.
End DONE, CHECKPOINT, BLOCKED, or ESCALATE with the remaining work or reason.
```

Use a structured packet for a large batch; plain Markdown can be sufficient for a single local task. The following is a shape example, not evidence from a real repository:

```json
{
  "assignment_id": "image-inputs",
  "revision": 1,
  "generation": 1,
  "baseline": {"commit": "recorded commit", "dirty_inputs": []},
  "tasks": [
    {
      "id": "TASK-101",
      "body": "Current state: ...\n\nStart here: ...\n\nConstraints and dependencies: ...\n\nValidation to run: ...\n\nFirst step: ...",
      "evidence": [
        {
          "claim": "The current loader accepts JPEG inputs.",
          "kind": "current",
          "path": "src/image_loader.py",
          "needle": "SUPPORTED_FORMATS = {'png', 'jpeg'}"
        },
        {
          "claim": "An earlier experiment used PNG inputs only.",
          "kind": "historical",
          "path": "docs/research/loader-experiment.md",
          "needle": "The experiment accepts PNG only."
        },
        {
          "claim": "The task's planned profile fixture is absent.",
          "kind": "planned_missing",
          "path": "tests/fixtures/profiled-input.png"
        }
      ],
      "unresolved": ["The task leaves the output-profile policy undecided."]
    }
  ],
  "checks": ["Describe only checks actually performed."],
  "status": "DONE"
}
```

For an external task artifact, use its stable identifier/revision and a small supporting excerpt instead of pretending it is a local path. Avoid copying private source content into public notes.

Validate current and historical anchors against the recorded inputs; verify that a `planned_missing` path is absent and described as planned in the note. A historical anchor cannot establish present behavior. Keep raw worker output separate from the lead-approved packet so corrections have a traceable origin.

The lead should pay particular attention to reports that merely quote old notes, omit a sibling implementation path, confuse public and internal access, claim that a locally missing asset does not exist anywhere, or prescribe a new decision instead of identifying the task's existing contract.
