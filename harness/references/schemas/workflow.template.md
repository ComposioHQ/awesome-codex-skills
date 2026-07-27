<!--
workflow.md schema — Stage (parent issue / Jira Issue) → Step (sub-issue / Jira Sub-issue) hierarchy. Static declaration.
MANDATORY fields per block (Zero-Tolerance: missing field → HALT).

NAMING CONVENTION (Jira issue title style — MANDATORY):
- Stage·Step name MUST be a deliverable-meaningful noun phrase in kebab-case.
- Format: ^[a-z][a-z0-9-]*$  (lowercase letter start, digits/hyphens allowed)
- BANNED placeholders: main, step1, task, work, default, phase1, stage1, generic
- ALLOWED examples: sso-integration, payment-flow, requirements-gathering, api-design, load-test
- Single-Stage / single-Step cases STILL follow this rule — no `main` shortcut.

Stage block required fields:
- exit condition:        "all steps complete" or verifiable predicate
- next stage:            {next_stage_name} | done
- user approval gate:    required | none (last stage)

Step (Task) block required fields:
- pattern:               pipeline | fan_out_fan_in | expert_pool | producer_reviewer | supervisor | hierarchical | handoff
- active agents:         [@name1, @name2, ...]   (must match .codex/agents/{name}.toml)
- exit condition:        VERIFIABLE PREDICATE (file exists / JSON field value / iterations ≥ N)
                         BANNED: "QA approved", "sufficient", "when complete", "satisfied" (subject to LLM interpretation)
- next step:             {next_step_name} | done
- max iterations:        integer (non-loop=1, loop ≤3)

Symbolic placeholders allowed in active agents (e.g. [@selected_expert]) — main resolves
at runtime via checkpoint.json shared_variables. workflow.md itself is NOT modified.
-->

<!-- Reference patterns (optional, no effect on execution): {STAGE_1}={pattern}, {STAGE_2}={pattern} -->

## Stage Definitions

### Stage 1: {{STAGE_1_NAME}}
- exit condition: all steps complete
- next stage: {{STAGE_2_NAME_OR_done}}
- user approval gate: {{required/none}}

#### Step 1: {{STEP_1_NAME}}
- pattern: {{PATTERN}}
- active agents: [{{@AGENT_1}}]
- exit condition: {{VERIFIABLE_PREDICATE}}
- next step: {{STEP_2_NAME_OR_done}}
- max iterations: {{N}}

<!-- Add more Step blocks within Stage 1 by copying the above. -->

<!-- Add Stage 2+ by copying the Stage block. Single-stage workflow: omit. -->
<!--
### Stage 2: {{STAGE_2_NAME}}
- exit condition: all steps complete
- next stage: done
- user approval gate: none (last stage)

#### Step 1: {{STEP_1_NAME}}
- pattern: {{PATTERN}}
- active agents: [{{@AGENT_2}}, {{@AGENT_3}}]
- exit condition: {{VERIFIABLE_PREDICATE}}
- next step: done
- max iterations: {{N}}
-->
