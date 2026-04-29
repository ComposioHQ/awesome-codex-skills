# Harness Evolution Protocol

The detailed workflow for Step 7 in `SKILL.md`. A harness is not a static artifact built once and finished — it is a system that continuously evolves based on user feedback. Load this file first when entering the "Operations/Maintenance" branch from Step 0, or when a user requests "harness inspection/audit/sync/expansion" or similar.

---

## Table of Contents

1. [Post-Execution Feedback Collection](#1-post-execution-feedback-collection)
2. [Feedback Incorporation Paths](#2-feedback-incorporation-paths)
3. [Change History Management](#3-change-history-management)
4. [Evolution Triggers](#4-evolution-triggers)
5. [Operations/Maintenance Workflow](#5-operationsmaintenance-workflow)

---

## 1. Post-Execution Feedback Collection

After each harness execution completes, request feedback from the user.

- "Are there any areas in the results you would like to improve?"
- "Are there any changes you would like to make to the agent configuration or workflow?"

If there is no feedback, move on. Do not pressure the user, but always offer the opportunity.

---

## 2. Feedback Incorporation Paths

The modification target differs depending on the type of feedback.

| Feedback Type       | Modification Target               | Example                                                       |
| ------------------- | --------------------------------- | ------------------------------------------------------------- |
| Output quality      | The relevant agent's skill        | "Analysis too superficial" → add depth criteria to skill      |
| Agent role          | Agent definition `.toml`          | "Security review also needed" → add new agent                 |
| Workflow order      | Orchestrator skill                | "Validation should come first" → reorder Steps                |
| Team composition    | Orchestrator + agents             | "These two can be merged" → merge agents                      |
| Missing trigger     | Skill description                 | "Doesn't work with this phrasing" → expand description        |

---

## 3. Change History Management

All changes are recorded in the **Change History** table in AGENTS.md (same as the history section in the Step 5-4 AGENTS.md template).

```markdown
**Change History:**
| Date       | Change           | Target                          | Reason                                  |
|------------|------------------|---------------------------------|-----------------------------------------|
| 2026-04-05 | Initial setup    | Entire harness                  | -                                       |
| 2026-04-07 | Added QA agent   | agents/qa-inspector.toml        | Feedback: insufficient output validation|
| 2026-04-10 | Added tone guide | skills/content-creator          | Feedback: "too stiff"                   |
```

---

## 4. Evolution Triggers

Evolution is proposed not only when the user explicitly says "modify the harness," but also in the following situations:

- When the same type of feedback recurs 2 or more times.
- When a pattern of repeated agent failures is detected.
- When the user is observed bypassing the orchestrator and working manually.

---

## 5. Operations/Maintenance Workflow

Systematically performs inspection, modification, and synchronization of an existing harness. Follow this workflow when entering the "Operations/Maintenance" branch from Step 0.

### Step 1: Status Audit

- Compare the file list in `.codex/agents/` against the agent configuration in the orchestrator skill → generate a discrepancy list.
- Compare the directory list in `.agents/skills/` against the skill configuration in the orchestrator skill → generate a discrepancy list.
- Report audit results to the user.

### Step 2: Incremental Addition/Modification

- Perform agent/skill additions, modifications, or deletions per user request.
- Classify the change type and determine which Step to execute: see `references/expansion-matrix.md` — `classify_change()`.
- Make changes one at a time; run Step 3 immediately after each change.

> **In-flight evolution safety:** If skill/agent files are modified while the harness is currently running (`_workspace/checkpoint.json` status: `"in_progress"` or `"partial"`), the orchestrator will restore its position on the next cycle re-entry by reading `current_stage`, `current_step`, and `active_pattern` from checkpoint.json. Therefore, **already-completed Steps are not re-executed**, and execution resumes from the `current_step` restore point when entering the next Step. Modified agent/skill files take effect from the next time the orchestrator calls that agent. However, if the modification affects the agent or exit conditions of the currently running Step, suggest to the user that they either manually re-run that Step (roll back `current_step` in `checkpoint.json`) or restart from the beginning.

### Step 3: Update AGENTS.md Change History

- Record the date, change content, target, and reason in the change history table.

### Step 4: Change Validation

- Validate the structure of modified agents/skills (per Step 6-1 criteria).
- If the modification scope affects triggers, validate triggers (per Step 6-4 criteria).
- For large-scale changes (architecture changes, 3+ agents added/removed), also perform Step 6-3 (execution test) and 6-5 (dry run).
- Final check: confirm AGENTS.md matches the actual files.
