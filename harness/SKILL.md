---
name: harness
description: "A meta-skill for designing a specialized subagent team in the Codex CLI environment. Domain analysis → Agent TOML definitions (.codex/agents/) → Skill creation (.agents/skills/) → AGENTS.md initialization. Triggers: 'set up codex harness', 'create codex agent team', 'build codex harness', '{domain} codex automation'. Also use this skill for follow-up tasks (modification/refinement/re-execution/expansion)."
---

# Skill: Codex Harness Orchestrator

> **Required before starting:** Match the `references/usage-examples.md` scenarios against the user's utterance.

## Core Principles

1. **7 Architecture Patterns:** Pipeline · Fan-out/Fan-in · Expert Pool · Producer-Reviewer · Supervisor · Hierarchical · Handoff
2. **Agent Definition:** TOML format — `.codex/agents/{name}.toml`
3. **Skill Format:** SKILL.md — `.agents/skills/{name}/SKILL.md`
4. **Project Context:** `AGENTS.md` — Path hierarchy: global `~/.codex/AGENTS.md` → repo `AGENTS.md` → subdirectory (more specific file takes precedence). Short and precise files are better than long and vague ones.
5. **State Persistence:** `_workspace/` file-based brokering
6. **Permission Control:** TOML `sandbox_mode` field — `read-only | workspace-write | danger-full-access`
7. **Subagent Constraint:** Only the orchestrator may spawn subagents. `max_depth=1` (default) enforced.
8. **File I/O:** Prefer `apply_patch` (surgical edits). New files via shell write.
9. **Zero-Tolerance Failure Protocol:** Arbitrary skipping is strictly prohibited. Maximum 2 retries (3 attempts total) → `Blocked`.

## Plan Mode

**Always run the Plan Mode procedure before building a multi-stage harness.**

- Activation: Collect context via `request_user_input` → clarifying questions → build a solid plan, then implement
- Required cases: New builds, architecture changes, Stage additions
- May be skipped: Simple single-item tasks with a clearly scoped change (e.g., minor skill checklist edits)

### Plan Mode Procedure (request_user_input-based)

```
PROCEDURE plan_mode(user_request):
    // 1. Context collection
    questions ← []
    IF domain/goal is unclear:
        questions.append("Please describe the goal and domain of the harness you want to build in detail.")
    IF pattern cannot be determined:
        questions.append("Do you have a preference for the agent team structure (Pipeline, Fan-out, Supervisor, etc.)?")
    IF agent count/roles are unclear:
        questions.append("Please list the agent roles you need.")

    IF questions is not empty:
        CALL request_user_input(questions)   // Bundle all questions into one call
        RETURN                               // Re-enter after receiving responses

    // 2. Plan presentation and user approval
    plan_summary ← Summary of domain, pattern, agent list, Stage/Step structure
    CALL request_user_input(
        "We will build the harness with the following plan. Shall we proceed?\n\n{plan_summary}"
    )
    RETURN                                   // Enter Phase 1 after approval
```

> `request_user_input` delivers multiple questions in a single call. Multiple unnecessary calls are prohibited.

## Useful Slash Commands

| Command    | Purpose                                                          |
| ---------- | ---------------------------------------------------------------- |
| `/plan`    | Toggle Plan Mode (same as Shift+Tab)                             |
| `/compact` | Summarize previous context in a long thread — saves context      |
| `/fork`    | Branch while preserving the current thread — use for experiments |
| `/resume`  | Resume a saved conversation                                      |
| `/review`  | Code review — compare base branch, uncommitted changes, specific commit |

> **Thread Strategy:** 1 harness = 1 thread. Use `/compact` when context grows large. Use `/fork` for branching experiments. Start a new thread when the unit of work changes.

## Workflow

### Phase 0: Status Audit (Mode Branching)

Check for the existence of `.codex/agents/`, `.agents/skills/`, `AGENTS.md`, `_workspace/checkpoint.json`:

| State                         | Mode          | Entry Phase                              |
| ----------------------------- | ------------- | ---------------------------------------- |
| None exist                    | New build     | Phase 1                                  |
| Some exist                    | Expansion     | Phase 1 (see expansion-matrix.md)        |
| checkpoint.json `in_progress` | Resume        | Resume from Phase 5                      |
| checkpoint.json `blocked`     | Ops/Modify    | Resolve blockage, then resume Phase 5    |

### Phase 1: Domain Analysis + Pattern Matching

1. Analyze user request → Extract domain, goals, and constraints.
2. Match against `references/usage-examples.md` scenarios → Derive pattern and Stage/Step structure.
3. Check non-trigger utterances — prevent false positives.

### Phase 2: Virtual Team Design

1. Separate agent responsibilities (single responsibility principle).
2. Select pattern (see `references/agent-design-patterns.md`).
3. Determine `sandbox_mode` for each agent:

   | Agent Type              | sandbox_mode         | Rationale                                                               |
   | ----------------------- | -------------------- | ----------------------------------------------------------------------- |
   | Researcher / Analyst    | `read-only`          | File reading and web research only, no writes                           |
   | Architect / Planner     | `read-only`          | Reports design output to findings.md only (orchestrator writes for it)  |
   | Coder / Developer       | `workspace-write`    | Directly creates and modifies code and documentation files              |
   | Reviewer / QA Inspector | `workspace-write`    | Creates report files + runs tests                                       |
   | State Manager           | `workspace-write`    | CRUD on checkpoint, task, and findings files                            |
   | Operator / Deployer     | `danger-full-access` | Executes external processes such as kubectl, terraform, etc.            |

4. **Subagent constraint check:** Agents other than the orchestrator must not spawn subagents.

### Phase 3: Agent TOML Creation

Create `.codex/agents/{name}.toml`. Reference: `references/schemas/agent-worker.template.toml`.

Required fields: `name`, `description`, `developer_instructions`, `model`, `sandbox_mode`, `model_reasoning_effort`.

> `model_reasoning_effort` guidelines: `low` (StateManager) / `medium` (Analyst, Researcher) / `high` (Coder, QA, Reviewer) / `xhigh` (Orchestrator, Architect). Details: `references/schemas/models.md`.

> **Model ID SoT:** `references/schemas/models.md` — do not guess arbitrary model IDs.

### Phase 4: Procedure Skill Creation

Write `.agents/skills/{orchestrator-name}/SKILL.md`. Reference: `references/schemas/agent-orchestrator.template.md`.

Bundle schema files: Copy all 9 schemas from `references/schemas/` → `.agents/skills/{name}/references/schemas/`.

### Phase 5: Integration and Orchestration

1. Create `_workspace/`, `_workspace/{plan_name}/`, `_workspace/tasks/`, `_workspace/_schemas/`.
2. Schema sync: Copy all 9 schemas from `references/schemas/` → `_workspace/_schemas/`.
3. Write `workflow.md` — Stage-Step structure, 6 required fields, verifiable exit conditions.
4. Initialize `findings.md` (sections by pattern).
5. Initialize `tasks.md`.
6. Create `checkpoint.json` (status: `in_progress`).
7. **Update AGENTS.md** — Add harness pointer:

   ```markdown
   ## Harness: {plan_name}

   - Agents: {agent list + .codex/agents/ paths}
   - Skills: {skill list + .agents/skills/ paths}
   - Workflow: \_workspace/workflow.md
   - Checkpoint: \_workspace/checkpoint.json
   ```

### Phase 6: Validation

- [ ] `.codex/agents/*.toml` required fields complete (name, description, developer_instructions, model, sandbox_mode, model_reasoning_effort)
- [ ] `.agents/skills/*/SKILL.md` frontmatter name and description validated
- [ ] workflow.md schema validated (6 required fields + verifiable exit conditions, no natural language)
- [ ] workflow.md cycle check
- [ ] `_workspace/_schemas/` all 9 files present
- [ ] `AGENTS.md` harness section added
- [ ] `checkpoint.json` status is `in_progress`

## Pattern-based Codex Coordination

Based on Codex subagent spawn. Default parallel execution — sequential execution is separated by skill directives per stage:

| Pattern             | Codex Coordination Method                                                                    |
| ------------------- | -------------------------------------------------------------------------------------------- |
| `pipeline`          | Sequential spawn per stage — confirm previous stage `task_*.json` status=done before next   |
| `fan_out_fan_in`    | Parallel spawn → ATOMIC aggregation after all complete                                       |
| `producer_reviewer` | Spawn producer → check task → spawn reviewer → check verdict                                |
| `expert_pool`       | Automatic routing based on Codex description                                                 |
| `supervisor`        | Dynamic spawn based on tasks.md claim                                                        |
| `hierarchical`      | Spawn team lead → team lead spawns workers (`max_depth=2` required: `.codex/config.toml`)   |
| `handoff`           | Parse `[NEXT_AGENT:name]` → sequential spawn                                                 |

## Output Artifacts

```
{project}/
├── .codex/
│   ├── agents/{name}.toml              # Agent definition (TOML)
│   └── skills/{orchestrator}/
│       ├── SKILL.md
│       └── references/schemas/         # Schema copies (9 files)
├── _workspace/
│   ├── _schemas/
│   ├── workflow.md
│   ├── findings.md
│   ├── tasks.md
│   ├── checkpoint.json
│   └── tasks/task_{agent}_{id}.json
└── AGENTS.md                           # Harness pointer + project context
```

## Error Handling

Zero-Tolerance: Agent failure → maximum 2 retries → if unresolved, set task\_\*.json status=blocked + HALT.

## Reference Documents

- `references/usage-examples.md` — Trigger utterance scenarios + mode mapping
- `references/agent-design-patterns.md` — 7 patterns + Codex sandbox permission mapping
- `references/orchestrator-template.md` — Step 0~5 pseudocode (Codex version)
- `references/schemas/models.md` — Model ID source of truth (OpenAI)
- `references/schemas/agent-worker.template.toml` — Worker agent TOML reference
- `references/schemas/` — Runtime schema SoT (9 files)
