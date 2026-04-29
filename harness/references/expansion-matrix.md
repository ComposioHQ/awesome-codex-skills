# Phase Selection Matrix for Extending an Existing Harness

Referenced when branching into **existing extension** mode from `SKILL.md` Phase 0. Determines the list of Phases to execute based on the type of change.

---

## Step 1: Change Type Classification Decision Tree

```
PROCEDURE classify_change(request):

    // ── Step A: Only workflow.md / Step structure changes? ─────────────────
    IF request affects ONLY ["workflow.md", "checkpoint.json logic"]:
        IF adds new Stage OR adds new Step:
            RETURN "Stage/Step Addition"
        ELSE:                               // exit condition, pattern name, or agent list adjustment
            RETURN "workflow.md Modification"

    // ── Step B: Only agent/skill files change? ──────────────────────────
    IF request affects ONLY [".codex/agents/*.toml", "references/skills/"]:
        IF adds new agent OR renames agent role:
            RETURN "Agent Addition"
        ELSE:                               // prompt, checklist, or tool list modification only
            RETURN "Skill Addition/Modification"

    // ── Step C: Architecture change threshold judgment ───────────────────
    // Classify as "Architecture Change" if ANY of the following conditions apply
    // Full pattern list: references/agent-design-patterns.md § "7 Core Architecture Patterns"
    Architecture change conditions:
      - Pattern change (e.g., pipeline → fan_out_fan_in)
      - Simultaneous reorganization of 3 or more agents (additions + deletions + role redefinitions combined)
      - Modification of orchestrator Step 2 core branching logic
      - Increase or decrease in Stage count

    IF ANY of architecture change conditions:
        RETURN "Architecture Change"

    // ── Step D: Multiple types occurring simultaneously ─────────────────
    // Priority (higher = broader scope):
    // Architecture Change > Stage/Step Addition > Agent Addition > Skill Addition/Modification > workflow.md Modification
    RETURN highest_priority_type(matched_types)
```

---

## Phase Selection Matrix

| Change Type        | Phase 1                    | Phase 2           | Phase 3             | Phase 4           | Phase 5                                                                                      | Phase 6  |
| ---------------- | -------------------------- | ----------------- | ------------------- | ----------------- | -------------------------------------------------------------------------------------------- | -------- |
| Agent Addition    | Skip (use Phase 0 results) | Placement decision only | **Required**            | If dedicated skill needed | Orchestrator modification                                                                          | **Required** |
| Skill Addition/Modification   | Skip                     | Skip            | Skip              | **Required**          | If connection changes                                                                                 | **Required** |
| Architecture Change    | Skip                     | **Required**          | Affected agents only | Affected skills only   | **Required**                                                                                     | **Required** |
| Stage/Step Addition  | Skip                     | **Required** (redesign) | If new agents needed | If new skills needed   | **Required** (workflow.md modification)                                                                  | **Required** |
| workflow.md Modification | Skip                     | Skip            | Skip              | Skip            | **Required** (workflow.md modification + verify reading logic coherence with `orchestrator-template.md` Step 0·Step 2) | **Required** |

---

## Decision Guide

**Agent Addition** — When a new role is created or an existing agent's workload becomes excessive. Phase 1 (domain analysis) is skipped because Phase 0 audit results are already available.

**Skill Addition/Modification** — Only methodology, checklists, or protocols change. Phase 1–3 are skipped because agent personas and architecture remain unchanged.

**Architecture Change** — Pattern change (e.g., Pipeline → Fan-out/Fan-in) or simultaneous reorganization of 3 or more agents. The broadest scope, so full review starts from Phase 2.

**Stage/Step Addition** — Inserting a Stage or Step into an existing workflow. Redesigning the Stage-Step structure in `workflow.md` (Phase 2) is required. Run Phase 3 and 4 as well if new agents or skills are needed.

**workflow.md Modification** — Only Stage/Step structure or exit conditions change; no agent or skill changes. After modifying `workflow.md` in Phase 5, you must verify that the orchestrator's Step 0 (checkpoint stage/step name matching) and Step 2 (step_block extraction path and exit_cond type) reading logic is coherent with the changed structure.

**Architecture change threshold** — Classify as an architecture change if any of the following apply:

| Condition                                 | Example                                    |
| ------------------------------------ | --------------------------------------- |
| Pattern change                            | pipeline → fan_out_fan_in               |
| Simultaneous reorganization of 3+ agents          | Combined additions + deletions + role redefinitions of 3 or more     |
| Modification of orchestrator Step 2 core branching | Step execution loop structure change                |
| Change in Stage count                        | Stage 1 → adding Stage 2, or deleting a Stage |

---

## Phase Execution Order Rules

Phases must be executed in **ascending numeric order**. Reverse execution is prohibited.

| Rule                         | Description                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Phase 4 → after Phase 3**   | Skills can only be connected after agents are defined. Running Phase 4 without Phase 3 is only allowed for the Skill Addition/Modification change type. |
| **Phase 5 → after Phase 3·4** | The orchestrator calls agents and skills, so the targets must be defined first.                                      |
| **Phase 6 → always last**    | Executed last regardless of change type.                                                                               |
| **"Skip" Phases**           | If drift (mismatch) is detected in the Phase 0 audit, run that Phase partially.                                                      |
| **Priority when overlapping**         | If multiple change types overlap, use the broadest scope (Architecture Change) as the baseline.                                              |

```
// Phase execution order dependencies
Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
          (agents)  (skills)  (orchest)  (verify)

// Independent execution allowed (other Phases not needed)
Skill Addition/Modification:   Phase 4 → Phase 6
workflow.md Modification: Phase 5 → Phase 6
```

---

## Validation Rules

- Even **"Skip"** Phases must be partially executed if a mismatch (drift) is detected in the Phase 0 audit.
- Phase 6 (validation) is **always required** regardless of change type.
- If multiple change types overlap, use the broadest scope (Architecture Change) as the baseline.

---

## Practical Case Examples

### Case A: Adding 1 Agent + 1 Dedicated Skill

**Situation:** An existing Pipeline harness now requires a security review agent (`@security-reviewer`) and a dedicated skill (`security-checklist`).

```
classify_change → "Agent Addition" (agent addition + skill addition combined → priority: Agent Addition > Skill Addition)

Phase execution:
  Phase 3: Create @security-reviewer.toml (new)
  Phase 4: Create security-checklist/SKILL.md (new)
  Phase 5: Modify orchestrator skill
    - Add @security-reviewer to team composition
    - Insert Step N (security-review)
    - Update workflow.md Stage·Step
    - Add "security review", "vulnerability check" keywords to description
  Phase 6: Structure validation + trigger validation (including new agent)

AGENTS.md change history: "@security-reviewer added | security review absence feedback"
```

### Case B: Strengthening an Existing Skill Checklist Only

**Situation:** Feedback that the review criteria of the `code-review` skill are insufficient → add checklist items.

```
classify_change → "Skill Addition/Modification" (no agent file or architecture changes)

Phase execution:
  Phase 4: Modify code-review/SKILL.md (add checklist items)
  Phase 6: Skill execution test (Phase 6-3) + trigger validation (Phase 6-4)
            Structure validation (Phase 6-1) can be omitted if no frontmatter changes

AGENTS.md change history: "code-review skill checklist strengthened | review quality feedback"
```

### Case C: Architecture Pattern Change (Pipeline → Fan-out/Fan-in)

**Situation:** Parallelizing 3 sequential analysis steps to improve speed. Includes role redefinition of 3 existing agents.

```
classify_change → "Architecture Change"
  Condition matched: pattern change (pipeline → fan_out_fan_in) + simultaneous reorganization of 3 agents

Phase execution:
  Phase 2: Redesign parallel fan-out structure (redefine workflow.md Stage-Step)
           Redesign findings.md·tasks.md·checkpoint.json flow
  Phase 3: Modify 3 affected agents
           - Reflect parallel call pattern
           - Redefine input/output paths (branching under _workspace/{plan_name}/)
  Phase 4: Modify skills related to parallel execution (if any)
  Phase 5: Full orchestrator rewrite
           - Replace Step execution loop with batch calls
           - Add checkpoint.json active_pattern update logic
  Phase 6: Dry-run test (Phase 6-5) is mandatory

AGENTS.md change history: "Architecture Pipeline→Fan-out/Fan-in change | analysis speed improvement goal"
```

### Case D: Adding Stage 2 (Validation Stage) to Existing Stage 1

**Situation:** A harness currently running with a single Stage (e.g., `sso-integration`) needs a final user validation Stage added.

```
classify_change → "Stage/Step Addition"
  Condition matched: Stage count increase (1 → 2)

Phase execution:
  Phase 2: Redesign workflow.md
           - Stage 1: sso-integration (existing, deliverable noun phrase)
           - Stage 2: user-validation (new, user approval gate: "complete after confirming validation results")
           Define Stage 2 exit conditions and transition protocol (names in kebab-case + deliverable meaning; generic placeholders like `main`·`validate` are prohibited)
  Phase 3: Add @qa-validator agent (responsible for new Stage)
  Phase 4: Create validation-checklist skill (if needed)
  Phase 5: Modify orchestrator
           - Add Stage 2 execution block
           - Add checkpoint.json Stage transition (sso-integration → user-validation) logic
           - Document user approval gate in AGENTS.md
  Phase 6: Resume flow test (Phase 6-6) required — mid-Stage interruption and resume scenario

AGENTS.md change history: "Stage 2 (user-validation) added | user validation gate absence feedback"
```

---

## Drift Handling Guide

When mismatch (drift) is found in the Phase 0 audit, resolve the drift before classifying the change type.

| Drift Type                                                   | Cause                                                                                                    | Resolution                                                                                                                                                                                                                    |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Agent file exists / not registered in AGENTS.md**                    | Agent was added but change history was not recorded in AGENTS.md                                                  | Correct AGENTS.md change history, then re-verify with Phase 6-1                                                                                                                                                                                 |
| **Registered in AGENTS.md / agent file missing**                      | File was deleted but not reflected, or name change not applied                                                                         | Confirm intent via user input request, then restore file or delete AGENTS.md entry                                                                                                                                                         |
| **Orchestrator references agent ≠ actual file**                 | File renamed during refactoring but not reflected                                                                               | Partial Phase 5 execution — correct agent name in orchestrator                                                                                                                                                           |
| **Skill description trigger conflict**                             | Keywords overlap with existing skill after adding a new skill                                                                    | Partial Phase 6-4 (trigger validation) execution — adjust description                                                                                                                                                          |
| **checkpoint.json current_step ≠ workflow.md step name**        | checkpoint.json not updated after modifying workflow.md                                                                   | Confirm current progress position via user input request, then manually correct checkpoint.json                                                                                                                                        |
| **Orchestrator SKILL.md flat Step list (no Stage hierarchy)** | Stage-Step model not applied at initial creation (e.g., flat `Step 0~4` headers as in `examples/sso-dev-flow`)                   | **Apply `skill-writing-guide.md` §7-6 Migration Guide 6 steps (M1~M6)** — inventory → Stage mapping → pattern assignment → exit condition conversion → write 5 artifacts → bundle schemas/. Canonical package: `references/examples/full-bundle/sso-style.md`. |
| **Exit condition is natural language ("QA approved", "enough", "when done")**     | LLM arbitrary interpretation expressions remain in workflow.md or orchestrator SKILL.md                                         | Apply `orchestrator-template.md` Step 1.7 schema validation routine → rewrite as verifiable predicates when whitelist violations are detected (`task_*.json status=done`·`{file}.json verdict=PASS`·`iterations ≥ N`, etc.)                                   |
| **workflow.md required fields missing**                               | One or more of `pattern`·`active agents`·`exit condition`·`next step`·`max iterations`·Stage `user approval gate` missing | Supplement immediately. Refer to the [MANDATORY] 6-field table in `SKILL.md` Phase 2-1. Missing → Zero-Tolerance Failure → user input request → HALT                                                                                                       |
| **findings.md using arbitrary sections** (`[Review: phase]`, etc.)         | Standard sections not followed                                                                                             | Convert to standard sections (`[Key Insights]`·`[Change Requests]`·`[Shared Variables/Paths]`, etc.). See "findings.md Standard Section Structure" table in `references/team-examples.md`                                                                   |
| **task\_\*.json persistence unused** (only simple tasks.md checkbox)         | Parallel agent reporting replaced by direct tasks.md modification — race condition risk                                     | Assign each agent the obligation to write `_workspace/tasks/task_{agent}_{id}.json`. Main collects with GLOB, then updates tasks.md via apply_patch                                                                                                    |

**Drift resolution principle:** If even one drift item exists, it must be resolved before executing the change type Phases. Drift resolution itself is confirmed with Phase 6-1 (structure validation) and recorded in the AGENTS.md change history.
