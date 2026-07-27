# Skill Testing & Iterative Improvement Guide

Methodology for validating and iteratively improving the quality of skills created in the harness. Supplementary reference for `SKILL.md` Phase 6 (validation and testing). This guide is written on the premise of the **Codex CLI orchestration environment** (no direct communication between sub-agents; the main agent acts as Grader and Analyzer).

---

## Table of Contents

1. [Testing Framework Overview](#1-testing-framework-overview)
2. [Writing Test Prompts](#2-writing-test-prompts)
3. [Execution Testing: With-skill vs Baseline](#3-execution-testing-with-skill-vs-baseline)
4. [Quantitative Evaluation: Assertion-Based Scoring](#4-quantitative-evaluation-assertion-based-scoring)
5. [Using Specialized Agents (Grader / Comparator / Analyzer)](#5-using-specialized-agents-grader--comparator--analyzer)
6. [Iterative Improvement Loop](#6-iterative-improvement-loop)
7. [Description Trigger Validation](#7-description-trigger-validation)
8. [Workspace Structure](#8-workspace-structure)

---

## 1. Testing Framework Overview

Skill quality validation is a combination of **qualitative evaluation** and **quantitative evaluation**.

| Evaluation Type | Method | Suitable Skills |
|---|---|---|
| **Qualitative** | User directly reviews the output | Subjective quality such as writing style, design, creative work |
| **Quantitative** | Automated assertion-based scoring | Objectively verifiable items such as file creation, data extraction, code generation |

Core loop: **Write → Parallel test execution → Evaluate → Improve → Re-test**

In Codex CLI, since there is no communication between sub-agents, **the main agent doubles as the Grader and Analyzer, or invokes a dedicated QA agent (`@grader`)** to perform scoring.

---

## 2. Writing Test Prompts

### 2-1. Principles

Test prompts should be **specific and natural sentences that an actual user would input**. Abstract or artificial prompts have low test value.

### 2-2. Bad Examples

```
"Process the PDF"
"Extract the data"
"Generate a chart"
```

### 2-3. Good Examples

```
"In 'Q4_Sales_Final_v2.xlsx' in the downloads folder, use column C (Sales) and
column D (Cost) to add a profit margin (%) column. Then sort descending by
profit margin."
```

```
"Extract the table on page 3 of this PDF and convert it to CSV. The table header
spans 2 rows — the first row is the category and the second row is the actual
column name."
```

### 2-4. Prompt Diversity

- Mix **formal / casual** tone
- Mix **explicit / implicit** intent (cases where file format is stated directly vs. must be inferred from context)
- Mix **simple / complex** tasks
- Some prompts should include abbreviations, typos, and casual expressions

### 2-5. Coverage

Start with 2–3 prompts, designed to cover:
- 1 core use case
- 1 edge case
- (Optional) 1 composite task

---

## 3. Execution Testing: With-skill vs Baseline

### 3-1. Comparative Execution Structure (Codex CLI Parallel Invocation)

For each test prompt, invoke two sub-agents **in parallel within a single response turn**.

**With-skill execution:**
```
Invoke @tester-with-skill
  Prompt: "{test prompt}"
  Skill path specified: .codex/skills/{skill-name}/
  Output path: _workspace/{skill-name}/iteration-N/eval-{id}/with_skill/outputs/
```

**Baseline execution:**
```
Invoke @tester-baseline
  Prompt: "{test prompt}"  (same)
  Skill path not provided (skill not activated)
  Output path: _workspace/{skill-name}/iteration-N/eval-{id}/without_skill/outputs/
```

In Codex CLI, agent-level parallelism is achieved by calling multiple sub-agents consecutively within a single response turn. (Shell commands can be executed simultaneously in the background with `&`, but this is separate from evaluation agent invocations.)

### 3-2. Baseline Selection

| Situation | Baseline |
|---|---|
| New skill creation | Same prompt run without the skill |
| Improving an existing skill | Previous skill version (snapshot) — reuse results preserved in the iteration-N-1 directory |

### 3-3. Capturing Timing/Cost Data

Save elapsed time and tokens **immediately** from the agent completion notification. This is only accessible at the time of notification and cannot be recovered afterward.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

Since Codex CLI includes token/time metadata in execution results, the main agent records this in `_workspace/{skill-name}/iteration-N/eval-{id}/{variant}/timing.json` via `apply_patch`.

---

## 4. Quantitative Evaluation: Assertion-Based Scoring

### 4-1. Assertion Writing Principles

When output can be verified objectively, define assertions for automated scoring.

**Good assertions:**
- Can be objectively determined as true/false
- Has a descriptive name so it is clear what is being checked just from the result
- Validates the **core value** of the skill

**Bad assertions:**
- Those that always pass regardless of whether the skill is used (e.g., "output exists")
- Those that require subjective judgment (e.g., "is well written")

### 4-2. Programmatic Validation

If an assertion can be verified by code, write it as a script. It is faster and more reliable than visual inspection, and can be reused across iterations.

In Codex CLI, the main agent runs validation scripts (Python, shell, etc.) via the shell and records results in `grading.json`.

### 4-3. Caution with Non-Discriminating Assertions

Assertions that pass 100% in **both configurations (With-skill / Baseline)** do not measure the differential value of the skill. Remove such assertions or replace them with more challenging ones.

### 4-4. Scoring Result Schema

```json
{
  "expectations": [
    {
      "text": "Profit margin column was added",
      "passed": true,
      "evidence": "Confirmed 'profit_margin_pct' column in column E"
    },
    {
      "text": "Sorted descending by profit margin",
      "passed": false,
      "evidence": "Original order preserved without sorting"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total": 2,
    "pass_rate": 0.50
  }
}
```

This schema is stored at the path `_workspace/{skill-name}/iteration-N/eval-{id}/{variant}/grading.json`.

> **Path distinction:**
> - **Long-term iterative improvement (this file):** `_workspace/{skill-name}/iteration-N/eval-{id}/{variant}/grading.json`
> - **One-time validation during harness construction (`SKILL.md` Phase 6):** `_workspace/evals/{timestamp}/grading.json`
>
> Since the two paths serve different purposes, they can coexist. When aggregating in Phase 6, scan both paths or specify the target path explicitly.

---

## 5. Using Specialized Agents (Grader / Comparator / Analyzer)

In the Codex CLI environment, since direct communication between sub-agents is not possible, the main agent **sequentially invokes** dedicated evaluation agents and brokers results via `findings.md` and `grading.json`.

### 5-1. Grader (Scorer)

Performs assertion-based scoring and cross-validates by extracting verifiable claims from the output.

**Role:**
- Pass/fail determination per assertion + providing evidence
- Extract factual claims from output and verify them
- Feedback on the quality of the eval itself (suggest when assertions are too easy or ambiguous)

**Recommended shell commands:** shell `cat`, shell `grep`.

### 5-2. Comparator (Blind Evaluator)

Anonymizes the two outputs as A/B and judges quality without knowing which was produced with the skill.

**When to use:** When you want to rigorously confirm "is the new version really better?". Can be omitted in general iterative improvement.

**Evaluation criteria:**
- Content: accuracy, completeness
- Structure: organization, formatting, usability
- Overall score

**Codex CLI note:** The main agent must anonymize the two outputs as `_workspace/.../variant_A.md` and `variant_B.md`, then pass only the paths to the Comparator. If "with_skill"/"without_skill" labels are exposed in the prompt, the blind nature is compromised.

### 5-3. Analyzer (Analyst)

Analyzes statistical patterns from benchmark data:
- Non-discriminating assertions (both configurations pass → no discriminating power)
- High-variance evals (results vary greatly between runs → unstable)
- Time/token trade-offs (skill improves quality but also increases cost)

Results are recorded in `_workspace/{skill-name}/iteration-N/benchmark.json` and in the [Key Insights] section of `findings.md`.

**`benchmark.json` schema:**
```json
{
  "iteration": 1,
  "timestamp": "2026-04-25T12:00:00Z",
  "eval_count": 3,
  "with_skill": {
    "pass_rate": 0.83,
    "avg_tokens": 45230,
    "avg_duration_ms": 18500
  },
  "without_skill": {
    "pass_rate": 0.50,
    "avg_tokens": 38100,
    "avg_duration_ms": 12300
  },
  "skill_delta": {
    "pass_rate_improvement": 0.33,
    "token_overhead": 7130,
    "duration_overhead_ms": 6200
  },
  "non_discriminating": ["eval-simple-csv-export"],
  "high_variance": [],
  "notes": "Simple CSV export assertion passes in both configurations — candidate for removal"
}
```

---

## 6. Iterative Improvement Loop

### 6-1. Collecting Feedback

Show the output to the user and collect feedback. Empty feedback is interpreted as "no issues".

### 6-2. Improvement Principles

1. **Generalize the feedback** — narrow fixes that only match the test example are overfitting. Fix at the principle level.
2. **Remove what doesn't earn its weight** — read the transcript; if the skill is causing the agent to do unproductive work, delete it.
3. **Explain the why** — even if the user's feedback is brief, understand why it matters and reflect that understanding in the skill.
4. **Bundle repetitive work** — if the same helper script is generated in every test, include it in `scripts/` in advance.

### 6-3. Iteration Procedure

```
1. Modify the skill
2. Re-run all test cases in a new iteration-N+1/ directory
3. Present results to the user (compared to the previous iteration)
4. Collect feedback (request user confirmation if ambiguous)
5. Modify again → repeat
```

**Termination conditions:**
- User is satisfied
- All feedback is empty (no issues with any output)
- No more meaningful improvements

### 6-4. Draft → Review Pattern

When modifying a skill, write a draft and then **read it again with fresh eyes** and improve. Do not try to write it perfectly in one pass — go through a draft-review cycle.

---

## 7. Description Trigger Validation

The Codex CLI trigger router selects a skill based solely on the description. Therefore, the description is the skill's **only practical API**.

### 7-1. Writing Trigger Eval Queries

Write 20 eval queries — 10 should-trigger + 10 should-NOT-trigger.

**Query quality criteria:**
- Specific and natural sentences that an actual user would input
- Include specific details such as file paths, personal context, column names, company names
- Mix length, tone, and format variably
- Focus on **edge cases** rather than clear-cut answers

**Should-trigger queries (10):**
- Same intent expressed in various ways (formal/casual)
- Cases where the skill/file type is not explicitly mentioned but is clearly needed
- Non-mainstream use cases
- Cases that compete with other skills but this skill should win

**Should-NOT-trigger queries (10):**
- **Near-misses are the key** — queries with similar keywords but where a different tool/skill is appropriate
- Clearly unrelated queries ("write a fibonacci function") have no test value
- Adjacent domain, ambiguous phrasing, keyword overlap but different context

### 7-2. Existing Skill Conflict Validation

Confirm that the new skill's description does not overlap with the trigger area of existing skills.

1. Collect descriptions from the existing skill list (scan all `.codex/skills/*/SKILL.md` via shell `find` and shell `cat`).
2. Confirm that the new skill's should-trigger queries do not incorrectly trigger existing skills.
3. If a conflict is found, describe the **boundary conditions** in the description more clearly (explicitly state the differentiating points from similar skills).

### 7-3. Automated Optimization (Optional Advanced Feature)

When description optimization is needed:

1. Split 20 eval queries into Train (60%) / Test (40%).
2. Measure trigger accuracy with the current description.
3. Analyze failure cases and generate an improved description.
4. Select best description based on the Test set (not the Train set — to prevent overfitting).
5. Repeat up to 5 times.

> Codex CLI automation is performed by a script that calls `codex -p "..."` from the shell. Token costs are high, so run this as a final step after the skill has been sufficiently stabilized.

---

## 8. Workspace Structure

Directory structure for systematically managing test and evaluation results.

> **Naming distinction:** Here, `{skill-name}` is the **name of the skill being tested**. It is a separate level from `{plan_name}` in `_workspace/{plan_name}/` used during orchestration runs. Skill test results are stored under `_workspace/{skill-name}/`, and orchestration run outputs are stored separately under `_workspace/{plan_name}/`.

```
_workspace/{skill-name}/
├── iteration-1/
│   ├── eval-descriptive-name-1/
│   │   ├── eval_metadata.json
│   │   ├── with_skill/
│   │   │   ├── outputs/
│   │   │   ├── timing.json
│   │   │   └── grading.json
│   │   └── without_skill/
│   │       ├── outputs/
│   │       ├── timing.json
│   │       └── grading.json
│   ├── eval-descriptive-name-2/
│   │   └── ...
│   └── benchmark.json
├── iteration-2/
│   └── ...
└── evals/
    └── evals.json
```

**Rules:**
- Eval directories use **descriptive names** rather than numbers (e.g., `eval-multi-page-table-extraction`).
- Each iteration is preserved in an independent directory (overwriting a previous iteration is prohibited).
- `_workspace/` is not deleted — retained for post-hoc verification, audit trails, and blind comparison.
- `evals.json` accumulates **evaluation metadata for the entire session** (skill version, total number of iterations, final pass rate, etc.) to track long-term quality trends in the harness.

**`evals.json` schema:**
```json
{
  "skill_name": "pdf-extractor",
  "skill_version": "1.0.0",
  "created_at": "2026-04-25T10:00:00Z",
  "total_iterations": 3,
  "final_pass_rate": 0.85,
  "iterations": [
    {
      "iteration": 1,
      "eval_count": 3,
      "pass_rate": 0.67,
      "timestamp": "2026-04-25T10:00:00Z",
      "notes": "Initial version — 2 of 3 assertions passed"
    },
    {
      "iteration": 2,
      "eval_count": 3,
      "pass_rate": 0.83,
      "timestamp": "2026-04-25T11:00:00Z",
      "notes": "Re-tested after improving multi-step table processing"
    }
  ]
}
```

---

## Orchestrator Test Scenarios

An orchestrator must describe **at least 1 normal flow + 1 error flow + 1 resume flow** in the skill body.

> **Naming distinction:** "Orchestrator Steps 0~5" are the **internal execution steps of the orchestrator skill itself** (context check, initialization, agent invocation, QA, integration, reporting). This is a separate concept from the Stage/Step hierarchy in `workflow.md`.

### Normal Flow

1. User provides `{input}`.
2. Orchestrator Step 0 confirms `_workspace/` does not exist → selects initial run mode.
3. Orchestrator Step 1 initializes `workflow.md`·`tasks.md`·`findings.md`.
   - `workflow.md`: Record Stage 1 (`{plan_name}` deliverable kebab-case) / Step 1 (deliverable kebab-case) / active agent list. **Placeholders (`main`) are prohibited** — use Jira title convention.
   - `checkpoint.json`: Initialize `current_stage: "{deliverable-kebab}"`, `current_step: "{deliverable-kebab}"`, `active_pattern: {first step pattern}`, `status: "in_progress"`.
4. Orchestrator Step 2 runs [Step execution loop] — invokes the agent for the current Step in workflow.md.
   - Run @analyst → @coder sequentially (batch invocations where parallelism is possible).
5. Orchestrator Step 3 invokes @reviewer → confirms no conflicts in `findings.md`.
6. Orchestrator Step 4 generates `_workspace/{plan_name}/final_{output}.md`.
7. Orchestrator Step 5 delivers a summary report to the user.
8. **Expected result:** `_workspace/{plan_name}/final_{output}.md` exists, all items in `tasks.md` are `Done`.

### Resume Flow (Persistence Test)

1. @analyst invocation completes, session terminates due to network failure during @coder invocation.
2. User re-invokes → orchestrator Step 0 finds `checkpoint.json`.
3. Restore `current_stage`·`current_step` from `checkpoint.json` → confirm entry point for that step.
4. Confirm @analyst output exists → immediately resume from the @coder step.
5. **Expected result:** @analyst work is skipped, only @coder and subsequent work is completed.

### Error Flow (Fix Loop)

1. Orchestrator Step 3: @reviewer rejects @coder's output (security vulnerability found).
2. Orchestrator records rejection reason in `findings.md` [Change Requests].
3. Orchestrator re-invokes @coder, injecting @reviewer's report.
4. @coder fixes the vulnerability and generates new output.
5. @reviewer re-validation passes → orchestrator proceeds to Step 4.
6. Final report explicitly states "Error recovery: passed after @coder revision following @reviewer rejection".

### expert_pool Scenario — Ambiguous Classification Path

1. User inputs "please review both performance and security" (multiple domains mixed).
2. Orchestrator Step 2 expert_pool: CLASSIFY result is AMBIGUOUS.
3. Request user confirmation ("Expert list: which of [@perf-analyst, @security-analyst] would you like to assign this to?").
4. User responds with "@security-analyst".
5. Record `"- @security-analyst: directly specified by user"` in findings.md [Routing Rationale].
6. Invoke @security-analyst → record task file → termination condition satisfied.
7. **Expected result:** AMBIGUOUS path → user confirmation request triggered, user-specified agent selected.

### handoff Scenario — Standalone Completion Without [NEXT_AGENT]

1. @log-analyzer invoked → analysis complete, no `[NEXT_AGENT]` keyword in response.
2. Orchestrator enters ELSE branch: records `task_{log-analyzer}_{id}.json` (standalone completion).
3. Termination condition check → satisfied → step transition.
4. **Expected result:** handle_handoff not called, task file recorded based on active_agents[0].

---

## Reference Links

- The simplified form of the scoring schema (`grading.json`) is documented in `references/skill-writing-guide.md`.
- Phase 6 validation procedure follows the workflow Phase 6 section in `SKILL.md`.
- Stage-Step workflow details: `references/stage-step-guide.md`.
- **Stage-Step workflow test scenarios** (scenarios 1~6): See `references/stage-step-guide.md`.
