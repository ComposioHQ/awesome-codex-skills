<!--
ORCHESTRATOR AGENT TEMPLATE — After variable substitution, save as `.codex/skills/{harness-name}/SKILL.md`.
The orchestrator is generated as a skill SKILL.md, not as an agent .md file.
Model ID SoT: references/schemas/models.md (always check models.md first before making changes)

Substitution variables:
  {{SKILL_NAME}}        kebab-case skill name (e.g. sso-dev-flow)
  {{DESCRIPTION}}       pushy description + trigger keywords + follow-up action keywords
  {{PLAN_NAME}}         subdirectory name under _workspace (e.g. sso)
  {{AGENT_TABLE}}       virtual team table rows (repeated)
  {{STAGE_STEP_SUMMARY}} workflow.md Stage/Step structure summary

Only the orchestrator can spawn subagents — worker agents are prohibited from doing so.
Model uses the thinking tier (responsible for complex reasoning and multi-step coordination).
-->

---

name: {{SKILL_NAME}}
description: "{{DESCRIPTION}}. Always use this skill for follow-up work (modifications/enhancements/re-runs)."

---

# Skill: {{SKILL_NAME}} Orchestrator

## Virtual Team

| Agent           | Type                   | Role   | Skill   | Output |
| --------------- | ---------------------- | ------ | ------- | ------ |
| {{AGENT_TABLE}} |

> Orchestrator model: `gpt-5.5` (responsible for design and reasoning). Verify model ID in: `references/schemas/models.md`

## Workflow

### Step 0: Context Check (Durable Execution)

Apply `references/orchestrator-template.md` Step 0 procedure. Branch based on `_workspace/checkpoint.json` status:

- `in_progress` → Resume (continue from current stage/step)
- `completed` → Confirm with user: partial re-run or fresh run
- Not present → Fresh run (proceed to Step 1)

### Step 1: Initialization

1. Create directories: `_workspace/{{PLAN_NAME}}/`, `_workspace/tasks/`, `_workspace/_schemas/`.
2. **Schema synchronization** — Copy 5 schema files + 3 agent templates from `references/schemas/` to `_workspace/_schemas/` via shell `cat` → `apply_patch` (see `references/orchestrator-template.md` Step 1.3).
3. Write `workflow.md` (variable substitution from `_workspace/_schemas/workflow.template.md`):
   {{STAGE_STEP_SUMMARY}}
4. Initialize `findings.md` (based on `_workspace/_schemas/findings.template.md`).
5. Initialize `tasks.md` (based on `_workspace/_schemas/tasks.template.md`).
6. Create `checkpoint.json` (validated against `_workspace/_schemas/checkpoint.schema.json` by `python _workspace/state.py` on write):
   ```json
   {
     "plan_name": "{{PLAN_NAME}}",
     "status": "in_progress",
     "current_stage": "{first Stage name}",
     "current_step": "{first Step name}",
     "active_pattern": "{first Step pattern}"
   }
   ```
7. **workflow.md schema validation** — 6 required fields + naming convention (no placeholders) + verifiable exit conditions + pattern enum. Violations cause HALT (see `references/orchestrator-template.md` Step 1.8).
8. **workflow.md cycle validation** (after passing schema validation).

### Step 2: Step Execution Loop

Apply `references/orchestrator-template.md` Step 2 standard procedure. Invoke agents per pattern, check exit conditions, handle Stage gates, update checkpoint.json.

## Error Handling

Zero-Tolerance: agent failure → up to 2 retries (3 total) → if unresolved, set `task_*.json` status=blocked and request user confirmation. Arbitrary skipping is strictly prohibited.

## Test Scenarios

> Required: at least **1 normal flow + 1 resume flow + 1 error flow**. Step 5 validation cannot pass without all three. Full scenario spec: `references/skill-testing-guide.md` § Orchestrator Test Scenarios.

### Normal Flow

1. User provides `{input}`.
2. Step 0: `_workspace/` absent → fresh run.
3. Step 1: Create `workflow.md` · `findings.md` · `tasks.md` · `checkpoint.json`. Stage/Step names follow Jira kebab-case convention (no placeholders like `main`).
4. Step 2: Invoke agents per workflow.md order (e.g., @{agent-1} → @{agent-2}).
5. Step 3+: QA / integration / reporting per workflow.md.
6. **Expected:** `_workspace/{{PLAN_NAME}}/final_{output}` exists, all `tasks.md` items `Done`.

### Resume Flow

1. @{agent-1} completes; session interrupted before @{agent-2} finishes.
2. User re-invokes → Step 0 detects `checkpoint.json` (`status: in_progress`).
3. Restore `current_stage` / `current_step` → skip completed work, resume from @{agent-2}.
4. **Expected:** @{agent-1} output reused as-is; only @{agent-2} and later steps re-execute.

### Error Flow

1. Step 3: @{reviewer} rejects @{agent-2}'s output.
2. Rejection reason recorded in `findings.md` [Change Requests].
3. @{agent-2} re-invoked with reviewer report injected → produces corrected output.
4. @{reviewer} re-validates → passes → proceed to next step.
5. **Expected:** Final report explicitly notes "Error recovery: @{agent-2} revised after @{reviewer} rejection".
