# Stage-Step Workflow Guide

A guide defining the workflow structure for all harnesses. Declares the Stage-Step hierarchy in `_workspace/workflow.md` so that the orchestrator executes deterministically. Referenced in SKILL.md Step 2 or Step 5.

---

## Table of Contents

1. [Concept Definitions](#1-concept-definitions)
2. [workflow.md Specification](#2-workflowmd-specification)
3. [checkpoint.json Schema](#3-checkpointjson-schema)
4. [Step and Stage Transition Protocol](#4-step-and-stage-transition-protocol)
5. [Verifiable Exit Condition Patterns](#5-verifiable-exit-condition-patterns)
6. [Per-Step Agent Access Control](#6-per-step-agent-access-control)
7. [Workflow Examples (5 Types)](#7-workflow-examples-5-types)
8. [Test Scenarios (6 Types)](#8-test-scenarios-6-types)

---

## 1. Concept Definitions

### Three-Level Hierarchy Model (Stage = Parent Issue, Step = Sub-issue)

Every harness is composed of a **Stage → Step → Agent** three-level hierarchy. **This directly borrows from Jira's issue hierarchy (Issue → Sub-issue).**

| Level | Jira Equivalent | Meaning | Transition Authority | Responsibility |
|------|-----------|------|---------|------|
| **Stage** | **Parent Issue (Issue / Story)** | A group of work items constituting a deliverable unit | User approval gate | Groups multiple sub-issues (Steps) to complete one deliverable. Transitions to the next Stage only after approval. |
| **Step** | **Sub-issue (Sub-issue)** | A single work item within a Stage | Orchestrator automatic | **1 Step = 1 pattern**. Holds 1 of the 7 core patterns + active agents + exit condition. Transitions automatically. |
| **Agent** | Task assignee | Step executor | Called within Step | Performs actual work. Access is controlled by the `active agents` list in the Step. |

> **Core semantics (borrowed from Jira):** Stage is the **parent issue**, Step is the **sub-issue**. A Stage itself is not a direct execution unit; the parent issue (Stage) completes only when all sub-issues (Steps) are done. The user approval gate operates at the parent issue (Stage) level — the same flow as getting PM approval before marking a Jira Story as Done.

> **Workflow ↔ Jira mapping example:**
> - Jira Story "Payment Module SSO Integration" = one Stage in workflow.md (`Stage 1: integrate-sso`)
> - Jira Sub-issue "Implement OAuth Callback Handler" = one Step in that Stage (`Step 2: implement-callback`)
> - Sub-issue assignee = `active agents` in the Step

Declare the Stage·Step structure in `_workspace/workflow.md`. The orchestrator always reads this file to determine the current stage and step.

> **workflow.md is a static declaration.** It is created once in Step 1 and the Stage·Step structure does not change during execution. When agent selection is determined dynamically (e.g., `[@selected_expert]`), that notation is a **runtime symbolic placeholder** — when the orchestrator enters that Step, it reads the `shared_variables.selected_expert` field from `checkpoint.json` and substitutes the actual agent name. The workflow.md file itself is not modified.
>
> **Naming convention distinction:** JSON keys in `shared_variables` use `selected_expert` (English snake_case). Symbolic placeholders in workflow.md use `[@selected_expert]` (can be any readable label). The two names do not need to match — the orchestrator reads the `selected_expert` value and substitutes it at the `[@selected_expert]` location, so the name format is at the implementer's discretion.

### Simple vs. Multi-Stage

| Type | Stage (Parent Issue) Count | Step (Sub-issue) Count | Usage Condition |
|------|---------------------|--------------------|----------|
| **Simple** | 1 (`main`) | 1 (`main`) | Completed with a single sub-issue and single pattern |
| **Multi-stage** | 2 or more, or 2+ Steps in one Stage | Multiple | Parent issue is decomposed into multiple sub-issues + exit conditions are verifiable + user can intervene at parent issue (Stage) gates |

---

## 2. workflow.md Specification

`_workspace/workflow.md` is required for all harnesses. Declares the Stage·Step structure; the orchestrator reads it every cycle.

> When writing, substitute variables in `_workspace/_schemas/workflow.template.md` (a copy synchronized in Step 1.3) and `apply_patch` to `_workspace/workflow.md`.

### Simple Workflow Example (1 stage + 1 step)

> **Naming note:** Placeholders like `main` or `step1` are prohibited. Stage and Step names must be kebab-case carrying the deliverable meaning (Jira title convention). No exceptions, even for single Stage and single Step cases.

```markdown
<!-- Reference pattern: fan_out_fan_in (no effect on execution, for documentation purposes) -->

## Stage Definitions

### Stage 1: blog-post
- Exit condition: all steps complete
- Next stage: done
- User approval gate: none

#### Step 1: parallel-research
- Pattern: fan_out_fan_in
- Active agents: [@researcher-a, @researcher-b, @researcher-c]
- Exit condition: all `_workspace/tasks/task_*.json` have status=done
- Next step: done
- Max iterations: 1
```

### Multi-Stage Workflow Example (2 stages + multiple steps)

```markdown
<!-- Reference pattern: fan_out_fan_in → producer_reviewer (no effect on execution, for documentation purposes) -->

## Stage Definitions

### Stage 1: gather
- Exit condition: all steps complete
- Next stage: refine
- User approval gate: required

#### Step 1: research
- Pattern: fan_out_fan_in
- Active agents: [@researcher-trend, @researcher-data]
- Exit condition: `_workspace/research/task_trend.json`, `task_data.json` all have status=done
- Next step: done
- Max iterations: 1

### Stage 2: refine
- Exit condition: all steps complete
- Next stage: done
- User approval gate: none (last stage)

#### Step 1: draft-review
- Pattern: producer_reviewer
- Active agents: [@writer, @editor]
- Exit condition: verdict=PASS in `_workspace/editor_verdict.json`
- Next step: done
- Max iterations: 3
```

### workflow.md Field Writing Rules

| Field | Writing Rule | Example |
|------|----------|------|
| `Active agents` | Declared only in Step blocks. Format `@name`, must match `.codex/agents/{name}.toml` | `[@writer, @editor]` |
| `Exit condition` | Only verifiable predicates allowed (file existence, JSON field value, numeric threshold) | all `task_*.json` have status=done |
| `Next step` | Next step name or `done` | `architecture` / `done` |
| `Next stage` | Next stage name or `done` | `validate` / `done` |
| `Max iterations` | Required for loop patterns (Producer-Reviewer, etc.) to prevent infinite loops | `3` |
| Stage `Exit condition` | `all steps complete` or a specific verifiable condition | `all steps complete` |

---

## 3. checkpoint.json Schema

> **The canonical source is `references/orchestrator-template.md` — "Data Persistence Protocol" section.** Refer to that file for full field descriptions and examples.

Additional fields needed in the Stage-Step workflow: `current_stage`, `current_step`, `active_pattern`, `stage_history`, `step_history`, `stage_artifacts`. All are included in the canonical schema.

---

## 4. Step and Stage Transition Protocol

### Step Transition vs. Stage Transition Comparison

| Item | Transition Authority | User Approval | checkpoint.json Update |
|------|---------|-----------|---------------------|
| **Step transition** | Orchestrator automatic | Not required | `current_step`, `step_history`, `handoff_chain: []` |
| **Stage transition** | Orchestrator after user approval | **Required** | `current_stage`, `current_step` (first Step of next Stage), `stage_history`, `handoff_chain: []` |

### Step Transition Protocol (Automatic)

The internal loop the orchestrator performs every cycle. Order must be strictly followed.

1. Read `current_stage`, `current_step` from `checkpoint.json`.
2. Read the exit condition from the matching step block in `workflow.md`.
3. Verify the exit condition (file scan, JSON field check).
4. **Not met** → Call the active agents for the current step pattern, then wait for the next cycle.
5. **Met** → Check `next step`:
   - Next step name → update checkpoint.json immediately → allow entry into the next step in the same turn.
   - `done` → proceed to Stage transition protocol.

### Stage Transition Protocol (Approval Required)

1. Confirm the last step of the current stage is `done`.
2. Report to the user in the format below.
3. **Approved:** Update checkpoint.json (current_stage, current_step, stage_history, handoff_chain: []).
4. **Rejected:** No change to checkpoint.json → ask "Which part would you like to revise?" → ATOMIC rollback to the specified step:
   - Update checkpoint.json: `current_step` ← specified step, `active_pattern` ← that step's pattern, `handoff_chain: []`, `last_updated` ← NOW().
   - Delete existing task files for that step's agents: `_workspace/tasks/task_{that_step_agents}_*.json`.
5. **[Prohibited]** Do not call the next stage agents in the same response turn as the approval.
6. **Re-entry:** User sends "continue" or similar → orchestrator re-runs Step 0 → detects `status: "in_progress"` + updated `current_stage`·`current_step` → enters Step 2 and immediately starts the first Step of the new Stage.

### User Approval Gate Format

```
Stage {current stage} complete:
  Step {step-1}: {exit condition} ✓
  Step {step-2}: {exit condition} ✓

Next Stage: {next stage}
  Step list: [{step-1}, {step-2}]
  First Step active agents: {agent list}
  First Step exit condition: {condition}

Proceed? [Y/N]
```

---

## 5. Verifiable Exit Condition Patterns

| Recommended (Verifiable) | Prohibited (LLM Arbitrary Interpretation) |
|---|---|
| All `_workspace/tasks/task_*.json` have status=done | "Gathered enough" |
| verdict=PASS in `_workspace/critic_verdict.json` | "Review is satisfactory" |
| score ≥ threshold in `_workspace/coverage.json` | "Quality is good" |
| Specific file exists (`_workspace/integrated.md`) | "Integration is done" |
| iterations ≥ max_iterations for that step in step_history | "Iterated enough" |

---

## 6. Per-Step Agent Access Control

Codex CLI agent frontmatter does not support custom fields. Access control is performed via the **`active agents` list in the step block of workflow.md**.

```
Before calling an agent, verify:
1. Find the current_stage → current_step block in workflow.md.
2. Read the `active agents` list for that step.
3. If the target is in the list → allow the call.
4. If not in the list → hold the call; report to the user if needed:
   "@writer is not an active agent in the current step ({current_stage}/{current_step})."
```

---

## 7. Workflow Examples (5 Types)

| # | Domain | Pattern Combination | Stage (Parent Issue) Count | Step (Sub-issue) Count | File |
|---|--------|----------|---------|---------|------|
| 1 | Blog post writing | gather=fan_out_fan_in → write=producer_reviewer | 2 | 2 | [examples/step/01-blog-post.md](examples/step/01-blog-post.md) |
| 2 | Issue triage | triage=(expert_pool+pipeline) → review=producer_reviewer | 2 | 3 | [examples/step/02-issue-triage.md](examples/step/02-issue-triage.md) |
| 3 | Architecture design | design=pipeline(3 Steps) → validate=fan_out_fan_in | 2 | 4 | [examples/step/03-architecture-design.md](examples/step/03-architecture-design.md) |
| 4 | Feature implementation (single Stage, multiple Tasks) | feature-build = research(fan_out) → implement(pipeline) → review(producer_reviewer) | 1 | 3 | [examples/step/04-single-stage-multi-task.md](examples/step/04-single-stage-multi-task.md) |
| 5 | Product lifecycle (multiple Stages, multiple Tasks) | discovery(fan_out+pipeline) → build(pipeline+supervisor+producer_reviewer) → validate(fan_out+pipeline) | 3 | 7 | [examples/step/05-multi-stage-multi-task.md](examples/step/05-multi-stage-multi-task.md) |

---

## 8. Test Scenarios (6 Types)

Detailed configuration, expected behavior, and pass criteria: [examples/step/test-scenarios.md](examples/step/test-scenarios.md)

| # | Purpose | Key Verification Point | Pass Criteria |
|---|------|----------------|----------|
| 1 | Simple workflow.md structure verification | Whether Stage 1 + Step 1 are created | No Stage 2 block + `main/main` structure |
| 2 | Multi-stage workflow trigger | Automatic multi-stage selection from utterance | 2 or more Stage blocks exist |
| 3 | Step exit condition not met → transition blocked | Prohibit entering the next Step when tasks are incomplete | Stage 2 agent call does not occur |
| 4 | Step automatic transition (no approval needed) | Transition without user intervention when exit condition is met | Next Step agent is called without an approval request |
| 5 | Stage transition gate (approval required) | Approval gate activates when Stage is complete | Approval request occurs + next Stage agent not called |
| 6 | Per-step agent access control | Block calls to agents not in the current Step list | Inactive agent call does not occur |
