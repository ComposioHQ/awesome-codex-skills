# Use Cases: harness Trigger Utterance → Processing Path Catalog

A catalog of **8 practical utterance patterns** and the processing path for each utterance (mode branching → pattern selection → workflow.md structure → artifacts) when calling `harness` to build, extend, or operate a harness. Use this as a reference by matching the closest scenario when a new domain is received.

> **Reading order:** §1 Utterance → Mode mapping → §2 8 Scenarios (by domain) → §3 Non-trigger utterances (false-positive prevention) → §4 Phase application guide.

---

## 1. Utterance → Mode Mapping

`harness` branches into a mode at Phase 0 immediately after the trigger (see SKILL.md Phase 0). Mode by utterance pattern:

| Utterance Pattern                                                               | Mode                   | Entry Phase                                            | Representative Keywords                                |
| ----------------------------------------------------------------------- | ---------------------- | ----------------------------------------------------- | ------------------------------------------ |
| "Build/configure/design a codex harness for X domain, create a codex agent team" | **New Build**          | Phase 1 → Phase 6 (full)                                | "configure", "create", "design", "build", "setup" |
| "Add Y feature/agent to the existing harness"                                | **Existing Extension**          | `expansion-matrix.md` matrix entry → partial Phase execution | "add", "extend", "supplement", "new agent"    |
| "Inspect/audit/report status of the harness"                                        | **Operations/Maintenance**      | `evolution-protocol.md` workflow                    | "inspect", "audit", "status", "drift", "sync"  |
| "Revise/re-run/supplement previous results"                                            | **Operations (Partial Re-run)** | Phase 0 branches based on checkpoint.json status               | "re-run", "revise", "previous results", "again"      |

> **Naming convention (Jira title convention) enforced:** Once the domain is determined, all Stage·Step names must be deliverable noun phrase kebab-case (e.g., `sso-integration`, `requirements-gathering`). Placeholders like `main`·`step1` are blocked by the workflow.md schema validator (see orchestrator-template.md).

---

## 2. Eight Scenarios

### Scenario A: SSO Authentication Feature Build (Multi-stage, pipeline + producer_reviewer)

- **Utterance:** "Add SSO authentication to the Go backend. From design through implementation and QA."
- **Mode:** New Build
- **Pattern selection rationale:** Analysis → design → implementation are sequentially dependent (pipeline) + quality gate iteration needed for implementation artifacts (producer_reviewer).
- **Stage/Step structure:**
  ```
  Stage 1: research-plan        (user approval gate: required)
    Step 1: requirements-gathering   pattern=pipeline
    Step 2: architecture-design      pattern=pipeline
  Stage 2: implementation-review     (last stage)
    Step 1: code-and-review-loop     pattern=producer_reviewer (max 3)
  ```
- **Agents:** `@sso-researcher`, `@sso-planner`, `@go-developer`, `@qa-reviewer`
- **Artifacts:** `_workspace/sso-integration/{research.md, plan.md, qa_verdict.json}`, `src/auth/*.go`
- **Reference example:** `references/examples/full-bundle/sso-style.md`

### Scenario B: Large-Scale Code Migration (Single stage, supervisor)

- **Utterance:** "Python 2 → 3 migration. Batch process 80 files."
- **Mode:** New Build
- **Pattern selection rationale:** N homogeneous tasks batched dynamically at runtime → supervisor (main claims from tasks.md).
- **Stage/Step structure:**
  ```
  Stage 1: python3-migration
    Step 1: batch-migrate    pattern=supervisor    active agents: [@migrator-1, @migrator-2, @migrator-3]
    Step 2: integration-test pattern=pipeline       active agents: [main]
  ```
- **Agents:** `@migration-supervisor` (task registration), `@migrator-{1..N}` (worker pool)
- **Artifacts:** `_workspace/python3-migration/tasks.md`, migrated files, `final/migration_report.md`
- **Reference example:** `references/examples/team/03-supervisor.md`

### Scenario C: Content Creation + Review Loop (Single stage, producer_reviewer)

- **Utterance:** "Draw one webtoon episode. Use an artist-editor loop."
- **Mode:** New Build
- **Pattern selection rationale:** Single deliverable + quality gate iteration (PASS/FIX/REDO).
- **Stage/Step structure:**
  ```
  Stage 1: webtoon-episode
    Step 1: produce-and-review   pattern=producer_reviewer (max 3)
  ```
- **Agents:** `@webtoon-artist`, `@webtoon-reviewer`
- **Artifacts:** `_workspace/webtoon-episode/panels/*.png`, `review_report.md`, `final/episode.md`
- **Reference example:** `references/examples/team/02-producer-reviewer.md`

### Scenario D: Parallel Research + Integrated Report (Single stage, fan_out_fan_in)

- **Utterance:** "Research 4 competitors simultaneously and create an integrated report."
- **Mode:** New Build
- **Pattern selection rationale:** N independent investigations in parallel + integration step.
- **Stage/Step structure:**
  ```
  Stage 1: competitor-research
    Step 1: parallel-scan   pattern=fan_out_fan_in   active agents: [@official, @media, @community, @background]
    Step 2: synthesize      pattern=pipeline          active agents: [@report-writer]
  ```
- **Agents:** `@official`, `@media`, `@community`, `@background`, `@report-writer`
- **Artifacts:** `_workspace/competitor-research/{task_*.json, final/research_report.md}`
- **Reference example:** `references/examples/team/01-fan-out-fan-in.md`

### Scenario E: Incident Analysis (handoff + persistence)

- **Utterance:** "Analyze production DB timeouts. We have 100GB of logs."
- **Mode:** New Build
- **Pattern selection rationale:** The next specialist is determined dynamically based on analysis results (handoff) + must support interruption and resumption with large-volume logs (persistence).
- **Stage/Step structure:**
  ```
  Stage 1: incident-resolution
    Step 1: triage            pattern=handoff           active agents: [@incident-triage]
    Step 2: targeted-fix      pattern=producer_reviewer active agents: [dynamically determined — handoff_chain]
  ```
- **Agents:** `@incident-triage`, `@db-fixer`, `@network-fixer`, `@app-fixer`
- **Artifacts:** `_workspace/incident-resolution/{handoff_chain, final/incident_report.md}`, checkpoint.json `handoff_chain` tracking
- **Reference example:** `references/examples/team/05-handoff-persistence.md`

### Scenario F: Full-Stack Feature Development (hierarchical)

- **Utterance:** "Add a payment module. Run frontend, backend, and DB simultaneously."
- **Mode:** New Build
- **Pattern selection rationale:** Heterogeneous teams (frontend, backend, DB) + 2-level delegation (team lead → worker).
- **Stage/Step structure:**
  ```
  Stage 1: payment-feature       (user approval gate: required — design review)
    Step 1: cross-team-design    pattern=hierarchical   active agents: [@frontend-team-lead, @backend-team-lead]
    Step 2: parallel-implement   pattern=hierarchical   active agents: [@ui-designer, @state-engineer, @api-designer, @db-engineer]
  Stage 2: integration-validate
    Step 1: cross-check          pattern=pipeline       active agents: [@project-architect]
  ```
- **Agents:** `@project-architect` (full design + validation), 2 team leads, 4 workers
- **Artifacts:** `_workspace/payment-feature/{00_architecture.md, frontend/, backend/, final/integration_report.md}`
- **Reference example:** `references/examples/team/04-hierarchical.md`

### Scenario G: Adding a Security Validation Stage to an Existing Harness (Extension Mode)

- **Utterance:** "Add a security validation Stage to the existing SSO harness. After QA."
- **Mode:** Existing Extension
- **Classification (expansion-matrix.md):** "Stage/Step Addition" — Stage count increases (2 → 3).
- **Phases executed:** Phase 2 (workflow.md redesign) + Phase 3 (`@security-auditor` agent addition) + Phase 5 (orchestrator modification) + Phase 6-6 (resume flow test).
- **Change result:**
  ```
  Stage 1: research-plan         (existing)
  Stage 2: implementation-review (existing)
  Stage 3: security-audit        (new, user approval gate: required)
    Step 1: vulnerability-scan   pattern=fan_out_fan_in
    Step 2: pen-test             pattern=pipeline
  ```
- **AGENTS.md change history entry is required.**
- **Reference:** `references/expansion-matrix.md` Case D.

### Scenario H: Partial Re-run of Previous Analysis Results (Operations/Partial Re-run)

- **Utterance:** "Regenerate only plan.md from last week's SSO analysis. Keep research as is."
- **Mode:** Operations (Partial Re-run)
- **Phase 0 branching:** `checkpoint.json status: "completed"` detected → partial re-run mode.
- **Processing:**
  1. Confirm impact scope with the user (user input request).
  2. Preserve `research.md` in `_workspace/sso-integration/`, delete `plan.md`.
  3. Roll back checkpoint.json to `current_stage: "research-plan"`, `current_step: "architecture-design"`, `status: "in_progress"`.
  4. Re-run from Step 2. Determine whether to re-run subsequent Stages after impact analysis.
- **Reference:** `references/orchestrator-template.md` Step 0 (resume vs partial vs new) + `references/evolution-protocol.md`.

---

## 3. Non-Trigger Utterances (False-Positive Prevention)

The following utterances **do not call harness**. Respond directly or call another skill.

| Utterance                               | Reason                              | Handling                                                                               |
| ---------------------------------- | --------------------------------- | ---------------------------------------------------------------------------------- |
| "Fix the bug in this function"              | Single code edit — no harness needed | Direct code editing                                                                     |
| "Explain how to use channels in Go"    | Simple question                         | Direct response                                                                          |
| "Run the tests once"              | Single command                         | Execute shell command directly                                                                  |
| "Edit just one item in tasks.md"    | Single edit on an existing artifact             | Direct `apply_patch` (but if the main agent is responsible for the update, call the orchestrator) |
| "Fix one line in the orchestrator code" | Single edit                         | Edit directly. But if the flow changes, enter operations mode (`evolution-protocol.md`)            |

> **Borderline utterances (ambiguous):** "Add one agent" — adding a single agent enters **extension mode** (run only Phase 3·4·5). Determine Phases via the expansion-matrix.md matrix.

---

## 4. Phase Application Guide

| Mode          | Phases Executed                                                 | Key Artifacts                                                                                                                                               |
| ------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| New Build     | Phase 1 ~ Phase 6 (full)                                   | `.codex/agents/*.toml`, `.agents/skills/{orchestrator}/SKILL.md`, `AGENTS.md`, `_workspace/_schemas/`, workflow.md, findings.md, tasks.md, checkpoint.json |
| Existing Extension     | Determined by expansion-matrix.md matrix (typically Phase 2·3·5·6-6) | Changed files only + `AGENTS.md` change history                                                                                                  |
| Operations/Maintenance | Phase 0 → evolution-protocol.md                            | Audit report + drift corrections                                                                                                                  |
| Partial Re-run   | Phase 0 (checkpoint rewind) → from Phase 2                  | Affected artifacts only                                                                                                                         |

> **Common requirements regardless of mode:** (1) **Plan Mode entry** — `/plan` or `Shift+Tab`; always use Plan Mode first for complex multi-step tasks, (2) Phase 0 status audit, (3) Zero-Tolerance failure protocol (up to 2 retries (3 total) → Blocked + user input request), (4) Stage·Step naming convention validation.

---

## 5. When No Match Is Found

If none of the 8 scenarios closely matches the domain:

1. **Pattern decomposition:** Draw the task's dependency graph and match against the 7 core patterns (parallel / sequential / loop / dynamic assignment / heterogeneous delegation / dynamic routing).
2. **Stage boundaries:** Set Stage boundaries at points where user approval is needed.
3. **Combine similar scenarios:** E.g., serially combine scenarios like "parallel research (D) → SSO implementation (A)".
4. **Agent design:** Apply interaction style + tool mapping from `references/agent-design-patterns.md`.
5. **Request user input when uncertain.** Do not guess the harness structure — confirm with the user.
