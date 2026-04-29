# Orchestrator Skill Advanced Template (Codex CLI Version)

The orchestrator is the top-level skill used by the main agent to execute orchestration logic. Because the Codex CLI environment **does not support direct communication between sub-agents**, the main agent acts as the sole **Data Broker**, coordinating the team through `findings.md`, `tasks.md`, and `checkpoint.json`.

> **Note:** Sub-agent invocation uses Codex subagent spawn. Parallel: default. Sequential: separate stages via skill instructions. Parallel execution, shell background (dev server, etc.). Details on API differences from Claude Code (why `TeamCreate`, `SendMessage`, `TaskCreate` are absent): see `references/agent-design-patterns.md` § "Execution Mode: Orchestration".

## Orchestrator Base Structure (Data Broker Enhanced)

````markdown
---
name: {domain}-orchestrator
description: "{Domain} harness orchestrator. Coordinates a virtual team through shared discovery (findings.md), state persistence (checkpoint.json), and task management (tasks.md). {Initial trigger keywords}. Also use this skill for follow-up work ({domain} result modification / partial re-run / update / supplement / re-run / improve previous results) to maintain consistency."
---

# {Domain} Orchestrator

## Virtual Team Composition

> **Common Required Tools (table omitted):** Request user confirmation
> **Orchestrator-only:** `subagent spawn` — do not grant to worker sub-agents.

| agent     | type                    | role   | skill   | output        |
| --------- | ----------------------- | ------ | ------- | ------------- |
| {agent-1} | {custom or built-in}    | {role} | {skill} | {output-file} |
| {agent-2} | {custom or built-in}    | {role} | {skill} | {output-file} |

## Workflow

### Step 0: Context Check (Durable Execution)

Determine the entry path based on the state of `_workspace/checkpoint.json`. **Evaluate the table top-to-bottom in order** and execute the action of the first matching row.

| `_workspace/` | `ckpt.status`                | Additional condition              | Action                                                                                                 |
| ------------- | ---------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------ |
| absent        | —                            | —                                 | GOTO Step 1                                                                                            |
| present       | `in_progress` or `partial`   | —                                 | Read workflow.md → GOTO Step 2 ¹                                                                       |
| present       | `blocked`                    | response = "continue/resume/fix"  | Delete blocked task file ² → update checkpoint `{status:"in_progress"}` → GOTO Step 2                 |
| present       | `blocked`                    | response = "restart/reset"        | Back up `_workspace/` → `_workspace_{NOW()}/` → GOTO Step 1                                           |
| present       | `blocked`                    | other (including first entry)     | Report blocked reason ³ → request user confirmation → HALT                                            |
| present       | `completed`                  | request = "partial modification"  | Determine RESUME_FROM ⁴ → update checkpoint `{status:"partial", current_stage, current_step}` → GOTO Step 2 |
| present       | `completed`                  | other                             | Back up `_workspace/` → `_workspace_{YYYYMMDD_HHMMSS}/` → GOTO Step 1                                 |

¹ Auto-resume path after context limit exhaustion. No manual intervention required.

² Target for deletion: `_workspace/tasks/task_{ckpt.blocked_agent}_*.json` (identified by `ckpt.blocked_agent`). Do not touch Blocked files from other steps.

³ Blocked reason report format:

```
Previous execution Blocked. Reason: {ckpt.blocked_reason} | Agent: {ckpt.blocked_agent}
Please resolve the blocking cause and resume. ("continue" / "restart")
```

> After requesting user confirmation, re-evaluate this table on the next turn.

⁴ **Partial modification RESUME_FROM decision:**

| Request type                              | RESUME_FROM                                                          |
| ----------------------------------------- | -------------------------------------------------------------------- |
| "Modify agent X prompt/output"            | `{stage: ckpt.current_stage, agent: X}`                              |
| "Modify skill Y"                          | `{skill: Y}` (re-invoke only the relevant agents)                   |
| "Modify workflow.md / exit condition"     | `{stage: ckpt.current_stage, step: ckpt.current_step}`               |
| Scope unclear                             | `request_user_input("Confirm modification scope: which agent/skill/file?")` → RETURN |

---

### Step 1: Initialization

1. Parse `{plan_name}` from `user_input`. If absent, `request_user_input("Please specify a task name.")` → RETURN.
2. Create directories: `_workspace/`, `_workspace/{plan_name}/`, `_workspace/tasks/`, `_workspace/_schemas/`.
3. **Schema template sync (required):** Read the 5 files from this skill's `references/schemas/` directory and write them as-is to `_workspace/_schemas/`. For each file, execute one `cat` → `apply_patch` pair:

   | Source (skill reference path)                          | Destination (workspace path)                            |
   | ------------------------------------------------------ | ------------------------------------------------------- |
   | `references/schemas/task.schema.json`                  | `_workspace/_schemas/task.schema.json`                  |
   | `references/schemas/checkpoint.schema.json`            | `_workspace/_schemas/checkpoint.schema.json`            |
   | `references/schemas/workflow.template.md`              | `_workspace/_schemas/workflow.template.md`              |
   | `references/schemas/findings.template.md`              | `_workspace/_schemas/findings.template.md`              |
   | `references/schemas/tasks.template.md`                 | `_workspace/_schemas/tasks.template.md`                 |
   | `references/schemas/models.md`                         | `_workspace/_schemas/models.md`                         |
   | `references/schemas/agent-worker.template.toml`        | `_workspace/_schemas/agent-worker.template.toml`        |
   | `references/schemas/agent-orchestrator.template.md`    | `_workspace/_schemas/agent-orchestrator.template.md`    |
   | `references/schemas/agent-state-manager.template.toml` | `_workspace/_schemas/agent-state-manager.template.toml` |

   > `README.md`, `models.md`, and agent templates are for reference when creating agent definitions — the workspace copy serves as the creation baseline. `models.md` is the SoT for model IDs and must always be synced.
   > **`shell cp ...` is prohibited** — the skill reference path is unreachable via shell from the runtime working directory (user project root). Always use shell `cat` + `apply_patch`.

   **Operational rules:**
   - Worker agents must read `_workspace/_schemas/task.schema.json` before writing their own output.
   - The main agent must validate against the schema every time it updates `task_*.json` or `checkpoint.json`.
   - When the skill is updated, the new schema applies starting from the next init. Do not modify workspace schemas during an in-progress run (preserve the snapshot).
   - **SoT:** `references/schemas/`. The workspace copy is a snapshot at execution time.

4. Write `workflow.md` — use `_workspace/_schemas/workflow.template.md` as the starting point. Timing varies by pattern:

   | Pattern                                                                         | Authoring method                                               |
   | ------------------------------------------------------------------------------- | -------------------------------------------------------------- |
   | `pipeline` / `fan_out_fan_in` / `producer_reviewer` / `handoff` / `expert_pool` | Write immediately based on the user request                    |
   | `supervisor` / `hierarchical`                                                   | Call Discovery Agent first → write based on its output         |

5. Initialize `findings.md` — copy `_workspace/_schemas/findings.template.md`, then remove all sections except those required for the pattern:

   | Pattern                  | Sections                                                                              |
   | ------------------------ | ------------------------------------------------------------------------------------- |
   | All patterns (common)    | `[Shared Variables/Paths]`                                                            |
   | fan_out / fan_out_fan_in | + `[Key Insights]`, `[Key Keywords]`, `[Data Conflicts]`                              |
   | producer_reviewer        | + `[Change Requests]`                                                                 |
   | pipeline / hierarchical  | + `[Next Stage Instructions]`                                                         |
   | supervisor / handoff     | + `[Data Conflicts]`                                                                  |
   | expert_pool              | + `[Routing Rationale]` (format: `"- {agent}: {reason} (matched keywords: {keywords})"`) |

6. Initialize `tasks.md` — copy `_workspace/_schemas/tasks.template.md` (keep headers only, leave rows empty).
7. Create `checkpoint.json` — populate all fields from `_workspace/_schemas/checkpoint.schema.json`:

```json
{
  "execution_id": "YYYYMMDD_HHMMSS",
  "plan_name": "{plan_name}",
  "status": "in_progress",
  "current_stage": "{workflow.stages[0].name}",
  "current_step": "{workflow.stages[0].steps[0].name}",
  "active_pattern": "{first_step.pattern}",
  "stage_history": [],
  "step_history": [],
  "stage_artifacts": {},
  "handoff_chain": [],
  "tasks_snapshot": { "done": [], "current": null },
  "shared_variables": {},
  "last_updated": "NOW()"
}
```

> **`@state-manager` delegation pattern (optional):** If the virtual team includes `@state-manager`, delegate steps 5–7 (findings.md / tasks.md / checkpoint.json initialization) and all state updates in Step 2 via `subagent spawn`. The orchestrator focuses on reasoning and coordination; state I/O is handled by `@state-manager` (flash model) after schema validation. Interface: `OPERATION: state.init|checkpoint.update|task.upsert|findings.append|tasks.update|state.archive` + `PAYLOAD:` block. Full spec: `references/schemas/agent-state-manager.template.toml`.

> **Notation bridge:** `workflow.md` declares Stages and Steps using **markdown headers only** (`### Stage 1: {deliverable-name}`, `#### Step 1: {deliverable-name}`), not JSON. The `"current_stage": "{workflow.stages[0].name}"` in the checkpoint.json above is pseudocode meaning "the name parsed from the first `### Stage` header" — it is not a JSON array access.
> **Parsing example:** `### Stage 1: sso-integration` → `current_stage = "sso-integration"` / `#### Step 1: requirements-gathering` → `current_step = "requirements-gathering"`. The orchestrator reads `workflow.md` via shell `cat`, builds the Stage/Step list in header order, and references them by name (text).
> **Naming convention (required):** Placeholders such as `main`, `step1`, `task` are prohibited. Use kebab-case + deliverable-meaning noun phrases (Jira title convention). Violations are blocked by workflow.md schema validation.

8. **workflow.md schema validation (required immediately after writing, before cycle validation):**

   Check each Stage/Step block for **missing required fields**. Block immediately if even one is missing.

   | Check item                                                                                                                                  | Method                                                                                                                                                                            | Action on failure                                                                                                                                                   |
   | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | Stage fields: `exit_condition`, `next_stage`, `user_approval_gate`                                                                          | Confirm field presence under header via regex/parser                                                                                                                              | `request_user_input("workflow.md Stage {name} missing required fields: {missing_fields}. Please add them and retry.")` → HALT                                               |
   | Step fields: `pattern`, `active_agents`, `exit_condition`, `next_step`, `max_iterations`                                                    | Same                                                                                                                                                                              | Same                                                                                                                                                                |
   | `pattern` value = one of 7 (`pipeline` / `fan_out_fan_in` / `expert_pool` / `producer_reviewer` / `supervisor` / `hierarchical` / `handoff`) | Enum check                                                                                                                                                                        | `request_user_input("Pattern value violation: {value}. Choose one of the 7.")` → HALT                                                                                       |
   | `active_agents` format = `[@name, ...]`                                                                                                     | Regex `\[(@\w[\w-]*\s*,?\s*)+\]`                                                                                                                                                  | `request_user_input("active_agents format violation.")` → HALT                                                                                                              |
   | **`exit_condition` verifiable predicate**                                                                                                   | Keyword whitelist: `task_*.json`, `status=done`, `exists`, `verdict=`, `score >=`, `iterations >=`. Violation if no whitelist match AND natural-language keywords (`approved`, `sufficient`, `when complete`, `satisfied`, `appropriately`) are present | `request_user_input("Step {name} exit_condition is natural language ('{value}'). Rewrite as a verifiable predicate: file existence, JSON field value, iteration >= N.")` → HALT |
   | User approval gate absent                                                                                                                   | Not specified in Stage block                                                                                                                                                      | Same                                                                                                                                                                |
   | **Stage/Step naming convention (Jira title convention)**                                                                                    | Extract header name → regex `^[a-z][a-z0-9-]*$` match + no placeholder blacklist items (`main`, `step1`, `task`, `work`, `default`, `phase1`, `stage1`, `generic`)               | `request_user_input("Stage/Step name violation: '{name}'. Rewrite as kebab-case + deliverable noun phrase (e.g., sso-integration, requirements-gathering). No placeholders.")` → HALT |

9. **workflow.md cycle validation (after schema validation passes):**

   | Check item                   | Method                                                                                                   | Action on failure                                                                                           |
   | ---------------------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
   | Circular reference in Steps  | Trace `next_step` links for each Stage's Steps in order — if a previously visited Step name reappears → cycle | `request_user_input("Circular reference found in workflow.md: {Stage} → {cycle_path}. Please fix and retry.")` → HALT |
   | `done` not reached in Stage  | If the Step chain end is not `done`                                                                      | Same                                                                                                        |
   | Undefined Step reference     | If `next_step` value is a Step name that does not exist within the same Stage                            | Same                                                                                                        |

   > Both checks run exactly once before entering the Step 2 loop. Can be skipped on resume paths (Step 0 → Step 2) since workflow.md has already been validated.

10. GOTO Step 2.

---

### Step 2: Step Execution Loop

**At the start of each cycle:**

1. Read `workflow.md`, `checkpoint.json`, `findings.md`.
2. Extract `workflow[ckpt.current_stage][ckpt.current_step]` → `step_block`. If absent, log error in findings.md → request user confirmation → HALT.
3. Extract `active_agents`, `pattern`, `exit_cond`, `max_iterations` from `step_block`.
4. **Resolve symbolic placeholders:** If `active_agents` contains symbolic names like `@selected_expert`:
   - Read `checkpoint.shared_variables.selected_expert` → substitute with actual agent name.
   - If field absent → `request_user_input("The expert_pool Step has not been executed yet or selected_expert is not recorded. Which agent should be called?")` → RETURN.
     > This substitution applies at runtime only. Do not modify the workflow.md file itself.
5. **Pre-blocked check (required before calling any agent):** If any `_workspace/tasks/task_*.json` has `status=="blocked" AND agent IN active_agents` → update checkpoint to `blocked` → request user confirmation → RETURN. Never call the agent.
6. Access control: do not call any agent outside the `active_agents` list.
7. **findings.md context injection:** Include the full `findings.md` in the agent call prompt.

   ```
   subagent spawn(@{name}, prompt="""
   {task_description}

   ## Shared Context (findings.md)
   @{_workspace/findings.md}
   """)
   ```

   > Even if findings.md is empty, include the header — agents recognize the section structure.

**Agent invocation by pattern:**

| Pattern                      | Invocation method                                                                        | Post-completion recording                                                   |
| ---------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `pipeline` / `hierarchical`  | Sequential calls, record immediately after each agent                                    | findings.md, tasks.md, checkpoint.json                                      |
| `fan_out` / `fan_out_fan_in` | Parallel calls → after all complete, `COLLECT ALL task_*.json` → apply_patch ⁷           | tasks/task_{agent}_{id}.json, tasks.md, findings.md, checkpoint.json        |
| `producer_reviewer`          | —                                                                                        | GOTO Step 3                                                                 |
| `expert_pool`                | CLASSIFY → single agent sequential ⁵                                                    | findings.md[Routing Rationale], task file, tasks.md                         |
| `supervisor`                 | Parallel per batch → apply_patch after each batch                                        | tasks.md, checkpoint.json                                                   |
| `handoff`                    | Sequential, parse `[NEXT_AGENT]` keyword ⁶                                               | task file (receiver or first agent), findings.md, tasks.md                  |

⁵ **expert_pool details:**

1. CLASSIFY(user_request, active_agents): compare keywords vs description → return best agent or AMBIGUOUS.
2. AMBIGUOUS → `request_user_input("Expert list: {active_agents}")` → RETURN.
3. Record findings.md[Routing Rationale] → update checkpoint `shared_variables.selected_expert` → call agent → record task file.

⁶ **handoff details:**

1. Call `active_agents[0]`.
2. If response contains `[NEXT_AGENT: @{name}]`: `handle_handoff({name})` cycle detection → build next_prompt → call `{name}` → record `task_{name}_{id}.json`.
3. If `[NEXT_AGENT]` absent: record `task_{active_agents[0]}_{id}.json` (standalone completion).

⁷ **fan_out / fan_out_fan_in agent responsibility:** Each parallel agent writes `_workspace/tasks/task_{agent}_{id}.json` directly upon completing its work (the main agent does not write on their behalf). The main agent collects files via GLOB after all complete and merges them with apply_patch.

**Partial failure recovery (when some agent task files are not created):**

1. GLOB result file count < expected agent count → identify missing agents (set difference of active_agents minus GLOB results).
2. Re-invoke each missing agent with zero-tolerance (max 2 retries, 3 total attempts).
3. If still missing after retries → call `blocked_protocol(agent, task)` → HALT. Never force-advance with partial results.
4. Perform apply_patch only after all agent task files are confirmed.

**Exit condition check (by `exit_cond` type):**

| Type | Exit condition format                     | Check method                                                                                                                                      |
| ---- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| A    | All `task_*.json` have `status=done`      | GLOB → check `status` field exhaustively (`"done"` lowercase — per task.schema.json enum)                                                         |
| B    | Specific file exists                      | `EXISTS(path)`                                                                                                                                    |
| C    | JSON field value (e.g., `verdict=PASS`)   | READ file → compare field                                                                                                                         |
| D    | `iterations >= N`                         | Find the last entry in `step_history` array where `stage==current_stage AND step==current_step`, compare `.iterations` (linear search, not dict access) |

**When exit condition is met — Step/Stage transition:**

1. Record completion in checkpoint.json `step_history`.
2. If `step_block.next_step` is missing (field absent or null/empty) → log error in findings.md → request user confirmation → HALT.
3. If `next_step != "done"` → update checkpoint (`current_step`, `active_pattern`, `handoff_chain: []`) → re-enter top of Step 2 loop (proceed to next Step).
4. If `next_step == "done"` → GOTO Stage Transition Gate. (Details: `references/stage-step-guide.md` § "Stage Transition Protocol")

**When exit condition is not met:**

1. `iterations < max_iterations` → find entry in `step_history` array where `stage==current_stage AND step==current_step` and increment `.iterations` (add new entry if none exists) → if `active_pattern == "handoff"`, reset checkpoint.json `handoff_chain: []` (new iteration = new chain) → re-enter top of Step 2 loop (re-execute same Step).
2. Exhausted → log `"Step {current_step}: max_iterations exhausted, exit condition not met"` in findings.md → blocked_protocol. (Details: `references/orchestrator-procedures.md`)

---

### Step 3: Fix Loop (producer_reviewer only)

```
retries ← 0

WHILE retries < 3:
    CALL subagent spawn
    WRITE "_workspace/{plan_name}/{output}_v{retries+1}.md" ← producer result

    CALL subagent spawn
    READ "_workspace/tasks/task_{reviewer}_{id}.json" → review

    IF review.status == "done":  // PASS
        apply_patch { tasks.md ← PASS evidence, checkpoint.json ← tasks_snapshot updated }
        GOTO Step 4

    ELSE:  // FAIL
        retries += 1
        IF retries >= 3:
            UPDATE tasks.md ← task "blocked"
            request_user_input("Validation failed after 3 attempts. Requesting intervention.")
            RETURN
        WRITE findings.md["Change Requests"] ← review.evidence  // Inject feedback and retry
```

---

### Step 4: Integration and Final Output

1. `GLOB "_workspace/tasks/task_*.json"` → filter files with `status=="done"` → extract `artifact_path` from each → build `artifacts` list.
2. Check `[Data Conflicts]` section in findings.md → if conflicts exist, call reviewer agent to resolve. If unresolved, request user confirmation → RETURN.
3. `_workspace/{plan_name}/final_{output}.md` ← save after MERGE of artifacts.
   > MERGE: Read each agent output in role order and concatenate by section. Format determined by domain (Markdown: connect as `## {agent_name}\n{content}`, JSON: merge keys, code: list of file paths).

---

### Step 5: Archive and Report

1. Copy `findings.md`, `tasks.md` → `_workspace/{plan_name}/` (preserve detailed history).
2. Replace `findings.md` with summary: keep only `[Final Result Summary]` + `[Archive Path]` sections.
3. Update `checkpoint.json`: `status:"completed"`, `current_stage/step:"done"`, record completion in `stage_history`.
4. Report to user:

```
Completed: {plan_name}
Output:         _workspace/{plan_name}/final_{output}.md
Detailed log:   _workspace/{plan_name}/findings.md
Tasks:          _workspace/{plan_name}/tasks.md
```

## Data Persistence Protocol (checkpoint.json Schema)

> **Canonical spec.** Other files such as `stage-step-guide.md` reference this schema.

### Field Descriptions

| Field              | Type   | Description                                                                                                                                | Required      |
| ------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------- |
| `execution_id`     | string | Execution ID in `YYYYMMDD_HHMMSS` format.                                                                                                  | **Required**  |
| `plan_name`        | string | Execution plan identifier.                                                                                                                 | **Required**  |
| `status`           | string | `"in_progress"` \| `"completed"` \| `"partial"` \| `"blocked"`.                                                                            | **Required**  |
| `last_updated`     | string | ISO 8601 timestamp.                                                                                                                        | **Required**  |
| `current_stage`    | string | Name of the currently active stage. **Deliverable kebab-case required** (e.g., `"sso-integration"`); placeholders (`"main"`, etc.) prohibited. | **Required**  |
| `current_step`     | string | Name of the currently active step. **Deliverable kebab-case required** (e.g., `"requirements-gathering"`); placeholders (`"main"`, `"step1"`, etc.) prohibited. | **Required**  |
| `active_pattern`   | string | Execution pattern of the current step (e.g., `"pipeline"`).                                                                               | Recommended   |
| `stage_history`    | array  | Record of completed stages. Includes `started_at` + `completed_at`.                                                                       | Multi-stage   |
| `step_history`     | array  | Record of completed steps. Includes `iterations`.                                                                                         | Multi-stage   |
| `stage_artifacts`  | object | Mapping of key artifact paths per stage.                                                                                                   | Optional      |
| `tasks_snapshot`   | object | Snapshot of task completion status.                                                                                                        | Optional      |
| `shared_variables` | object | Runtime variables shared across multiple agents.                                                                                           | Optional      |
| `handoff_chain`    | array  | Order of agents called within the current step when using the Handoff pattern. Used for cycle detection. Reset on step transition.         | Handoff pattern |
| `blocked_agent`    | string | Name of the blocked agent when Blocked occurs. Recorded only on `status:"blocked"` transition.                                            | When blocked  |
| `blocked_reason`   | string | Cause of the Blocked state. Displayed to the user on resume.                                                                               | When blocked  |

### Schema Example

```json
{
  "execution_id": "20260425_103000",
  "plan_name": "blog-writing-run-001",
  "status": "in_progress",
  "last_updated": "2026-04-25T10:30:00Z",

  "current_stage": "refine",
  "current_step": "draft-review",
  "active_pattern": "producer_reviewer",

  "stage_history": [
    {
      "stage": "gather",
      "started_at": "2026-04-25T09:00:00Z",
      "completed_at": "2026-04-25T10:00:00Z"
    }
  ],
  "step_history": [
    {
      "stage": "gather",
      "step": "research",
      "completed_at": "2026-04-25T10:00:00Z",
      "iterations": 1
    }
  ],

  "stage_artifacts": {
    "gather": "_workspace/research/",
    "refine": "_workspace/draft.md"
  },
  "tasks_snapshot": { "done": ["T1", "T2"], "current": "T3" },
  "shared_variables": { "main_artifact": "_workspace/plan/02_code.md" },
  "handoff_chain": ["@incident-triage", "@db-fixer"]
}
```
````

## Split Task File Protocol (Split Task Schema)

The `_workspace/tasks/task_{agent}_{id}.json` schema used by sub-agents to report their own status during parallel execution.

```json
{
  "agent": "@coder",
  "task_id": "T2",
  "status": "done",
  "retries": 0,
  "evidence": "Reviewer PASS report: _workspace/plan/03_review.md",
  "artifact_path": "_workspace/plan/02_code.md"
}
```

> `status`: `"done"` | `"blocked"`. Transition to blocked when `retries >= 2` (0 and 1 allowed = 3 total attempts).

## Procedures & Principles

> Error handling (`handle_error` / `blocked_protocol` / `handle_handoff`), test scenarios, description keywords, authoring principles, Stage/Step reference:
> See **`references/orchestrator-procedures.md`**.
