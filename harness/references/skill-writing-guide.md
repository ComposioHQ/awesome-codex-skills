# Skill Writing Guide

A detailed writing guide for improving the quality of skills created in the harness. Supplementary reference for `SKILL.md` Phase 4 (specialized skill and orchestrator creation). Provides a writing style tailored to the Codex CLI sub-agent orchestration environment.

---

## Table of Contents

0. [Skill Directory Structure](#0-skill-directory-structure)
1. [Description Writing Patterns](#1-description-writing-patterns)
2. [Body Writing Style](#2-body-writing-style)
3. [Output Format Definition Patterns](#3-output-format-definition-patterns)
4. [Example Writing Patterns](#4-example-writing-patterns)
5. [Progressive Disclosure Pattern](#5-progressive-disclosure-pattern)
6. [Script Bundling Decision Criteria](#6-script-bundling-decision-criteria)
7. [Data Brokering & Coordination Patterns (Codex CLI Specific)](#7-data-brokering--coordination-patterns-codex-cli-specific)
8. [Data Schema Standards](#8-data-schema-standards)
9. [What Not to Include in a Skill](#9-what-not-to-include-in-a-skill)

---

## 0. Skill Directory Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown body
└── Bundled Resources (optional)
    ├── scripts/    - executable code for repetitive/deterministic tasks
    ├── references/ - reference documents loaded conditionally
    └── assets/     - files used in output (templates, images)
```

- `scripts/` — pre-bundle scripts that agents commonly write. Executed directly from the shell.
- `references/` — separates detailed content that is not frequently triggered. Agents load conditionally via shell `cat`.
- `assets/` — static files such as templates and images used in output.

---

## 1. Description Writing Patterns

The description is the **only trigger mechanism** for a skill. The Codex CLI trigger router looks only at the `name` + `description` from `.codex/skills/*/SKILL.md` to decide whether to use a skill.

### 1-1. Understanding the Trigger Mechanism

Codex tends not to invoke a skill for simple tasks that can be handled easily with basic tools. A simple request like "read this PDF" may not trigger even with a perfect description. The **more complex, multi-step, and specialized a task**, the higher the probability of triggering a skill.

### 1-2. Writing Principles

1. Describe **both what the skill does and the specific trigger situations**.
2. Specify **boundary conditions** that distinguish similar cases that should not trigger the skill.
3. Be slightly **"pushy"** — to compensate for the trigger router's tendency toward conservative judgment.
4. Always include **follow-up action keywords** (re-run, modify, revise, update, partial re-run). Without them, the skill effectively becomes dead code after the first execution.

### 1-3. Good Examples

```yaml
description: "Performs all PDF operations including reading PDF files, extracting text
  and tables, merging, splitting, rotating, watermarking, encrypting, decrypting,
  and OCR. When a .pdf file is mentioned or a PDF output is requested, this skill
  MUST be used. Especially useful when conversion, editing, or analysis is needed
  rather than a simple 'read' request. Also MUST be used when modifying, re-extracting,
  or regenerating a previously processed PDF."
```

```yaml
description: "All spreadsheet operations including adding columns, formula calculations,
  formatting, charts, and data cleaning for Excel, CSV, and TSV files. Use this skill
  whenever a user mentions a spreadsheet — even casually ('the xlsx in the downloads
  folder'). Also covers updating existing results, recalculating columns, and changing
  sort order."
```

### 1-4. Bad Examples

- `"A skill that processes data"` — too vague, file type and task are unclear.
- `"PDF-related tasks"` — no enumeration of specific actions, trigger situations not described.
- `"Performs X"` — missing follow-up action keywords, so the router ignores it from the second call onward.

---

## 2. Body Writing Style

### 2-1. Why-First Principle

When an LLM understands the reason, it makes correct judgments even in edge cases. Conveying context is more effective than imposing rigid rules.

**Bad example:**
```markdown
ALWAYS use pdfplumber for table extraction. NEVER use PyPDF2 for tables.
```

**Good example:**
```markdown
Use pdfplumber for table extraction. PyPDF2 is specialized for text extraction
and cannot preserve the row/column structure of tables. pdfplumber recognizes
cell boundaries and returns structured data.
```

### 2-2. Generalization Principle

When a problem is found in feedback or test results, generalize at the **principle level** rather than making a narrow fix that only fits the specific example.

**Overfitting fix:**
```markdown
If there is a column named "Q4 Sales", convert that column to numeric.
```

**Generalized fix:**
```markdown
If a column name contains keywords suggesting numeric values such as "sales",
"amount", or "quantity", convert that column to a numeric type. If conversion
fails, preserve the original value.
```

### 2-3. Imperative Tone

Use the imperative form ("do this", "use this") rather than descriptive forms ("this can be done", "it is possible to"). A skill is a set of instructions.

### 2-4. Context Economy

The context window is a shared resource. Ask whether every sentence justifies its token cost:
- "Is this something the agent already knows?" → Remove
- "Will the agent make a mistake without this explanation?" → Keep
- "Is one concrete example more effective than a long explanation?" → Replace with an example

---

## 3. Output Format Definition Patterns

Use this in skills where the format of the output matters:

```markdown
## Report Structure
Follow this template exactly:

# [Title]
## Summary
## Key Findings
## Recommendations
```

Keep format definitions concise, but including **real examples** makes them more effective. If an orchestrator (main agent) needs to automatically parse the output produced by a sub-agent, strictly fix the format specification using JSON schema or YAML.

---

## 4. Example Writing Patterns

Examples are more effective than long explanations:

```markdown
## Commit Message Format

**Example 1:**
Input: Add JWT token-based user authentication
Output: feat(auth): implement JWT-based authentication

**Example 2:**
Input: Fix bug where password visibility toggle button doesn't work on login page
Output: fix(login): fix password visibility toggle button behavior
```

**Conditions for good examples:**
- Input and output are presented as **pairs**
- Include at least 1 edge case or error case
- Domain-specific terms appear in the examples

---

## 5. Progressive Disclosure Pattern

Keep the `SKILL.md` body to **under 500 lines**, and separate detailed references, large data schemas, and domain-specific knowledge into files under `references/`. Guide the agent to load those files via shell `cat` only when needed.

### 5-1. Pattern 1: Domain-Based Separation

```
bigquery-skill/
├── SKILL.md (overview + domain selection guide)
└── references/
    ├── finance.md   (revenue, billing metrics)
    ├── sales.md     (opportunities, pipeline)
    └── product.md   (API usage, features)
```

If the user asks about revenue, only `finance.md` is loaded.

### 5-2. Pattern 2: Conditional Detail

```markdown
# DOCX Processing

## Document Creation
Create a new document using docx-js. → See [DOCX-JS.md](references/docx-js.md).

## Document Editing
For simple edits, modify the XML directly.
**If tracked changes are needed**: See [REDLINING.md](references/redlining.md).
```

### 5-3. Pattern 3: Large Reference File Structure

Reference files over 300 lines should include a table of contents at the top:

```markdown
# API Reference

## Table of Contents
1. [Authentication](#authentication)
2. [Endpoint List](#endpoint-list)
3. [Error Codes](#error-codes)
4. [Rate Limits](#rate-limits)

---

## Authentication
...
```

---

## 6. Script Bundling Decision Criteria

Observe agent transcripts during test runs. Bundle when you see the following patterns.

| Signal | Action |
|---|---|
| Same helper script created in 3 out of 3 tests | Bundle in `scripts/` |
| Same `pip install` / `npm install` run every time | Specify dependency installation step in the skill |
| Same multi-step approach repeated every time | Document as standard procedure in the skill body |
| Same workaround applied after similar error every time | Document known issues and solutions in the skill |

Bundled scripts must go through an **execution test**. Confirm actual execution results in the shell before including them in the skill.

---

## 7. Data Brokering & Coordination Patterns (Codex CLI Specific)

Write skills on the premise that in the Codex CLI environment, the main agent acts as a **Data Broker**. Since direct communication between sub-agents is not possible, skills follow these principles.

### 7-1. Standardizing Outputs

Strictly define the files generated by sub-agents to have a **structure that is easy for other agents or the main agent to read** (MD, JSON). Free-form output makes orchestration difficult.

### 7-2. Completion and Status Reporting (Completion Signals)

The method for reporting skill execution results to the orchestrator.

1.  **Atomic Status Reporting (Thread-safe):** Agents running in parallel do not directly modify `tasks.md`. Instead, they report by creating a `_workspace/tasks/task_{agent}_{id}.json` file.
2.  **Dynamic Handoff:** Used when the agent is outside its area of expertise or an additional specialist is needed.
    - **Format:** `[NEXT_AGENT: @expert-name] Reason: {specific reason}`
    - **Example:** `[NEXT_AGENT: @security-patcher] Reason: An authentication vulnerability was found during logic analysis, requiring specialized patching.`
3.  **Visibility:** All intermediate progress is updated in real time in the [Key Insights] section of `findings.md`.

### 7-3. External Input Requires User Confirmation

Do not guess when instructions are ambiguous or data conflicts arise. Explicitly state in the skill body "If X is uncertain, request user confirmation" to fix the user intervention point.

### 7-4. Procedural Skills Are Loaded Explicitly by the Orchestrator

In Codex CLI, a skill is activated by the orchestrator reading it via `cat .codex/skills/{name}/SKILL.md` and injecting it into the prompt. When writing a skill that **references or reuses another skill**, specify the skill name and when it should be loaded.

### 7-5. Orchestrator Skill Writing Rules (Required, drift prevention)

When writing orchestrator skills, **do not fall back to a flat "Step 1~N" list**. Always use the Stage (parent issue / Jira Issue) → Step (child issue / Jira Sub-issue) block format. This rule is mandatory to prevent recurrence of non-standard outputs like `examples/sso-dev-flow`.

| Prohibited | Allowed |
|------|------|
| `### Step 0: ...` `### Step 1: ...` flat headers | `### Stage 1: {name}` followed by `#### Step 1: {name}` nesting |
| Termination conditions like "upon QA approval", "when done", "sufficiently" | `"verdict=PASS in qa_verdict.json"`, `"status=done in task_*.json"` |
| Pattern unspecified or free notation ("sequentially") | 7 pattern enum (`pipeline`·`fan_out_fan_in`·`expert_pool`·`producer_reviewer`·`supervisor`·`hierarchical`·`handoff`) |
| Prose description in active agent body | Step block field `Active Agents: [@name1, @name2]` |
| Missing user approval gate | Stage block `User Approval Gate: required / none` specified |
| Missing max iteration count (especially producer_reviewer) | Step block `Max Iterations: 3` |
| Arbitrary sections in findings.md like `[Review: Phase]` | Standard sections like `[Key Insights]`·`[Change Requests]`·`[Shared Variables/Paths]` |
| Simply checking off tasks.md items | `_workspace/tasks/task_{agent}_{id}.json` persistence + tasks.md table update |

**Orchestrator SKILL.md Body Required Sections (Checklist):**

- [ ] Virtual team (agent · type · role · skill · output table)
- [ ] Step 0 (context check — checkpoint.json status-based branching)
- [ ] Step 1 (initialization — simultaneous creation of workflow.md·findings.md·tasks.md·checkpoint.json 5 files + schema validation step 1)
- [ ] Step 2 (Step execution loop — pattern-based invocation + termination condition check + automatic/approval switching)
- [ ] Step 3+ (pattern-specific processing — e.g., producer_reviewer loop, supervisor dynamic assignment)
- [ ] Error handling (Zero-Tolerance: retry ≤2 → Blocked + user confirmation request)

**Orchestrator Skill Directory Required Bundle (at time of creation):**

New orchestrator skills read their own `references/schemas/` at runtime (`codex-harness` is a meta-skill and is not activated at runtime), so the following **10 items** must always be bundled. The SoT is `codex-harness/references/schemas/` — copy as-is when creating new skills.

```
{project}/.codex/skills/{name}-orchestrator/
├── SKILL.md
└── references/
    └── schemas/
        ├── task.schema.json                    ← copy from codex-harness/references/schemas/
        ├── checkpoint.schema.json              ← same (SoT parsed by state.py at runtime)
        ├── workflow.template.md                ← same
        ├── findings.template.md                ← same
        ├── tasks.template.md                   ← same
        ├── models.md                           ← model ID SoT (required reference when creating agents)
        ├── agent-worker.template.toml          ← worker agent creation standard (TOML)
        ├── agent-orchestrator.template.md      ← orchestrator skill creation standard
        ├── agent-state-manager.template.toml   ← state manager agent creation standard (optional)
        └── state.py                            ← state manager CLI (deployed to _workspace/state.py at init)
```

> **Bundle Validation:** Step 1.3 reads all 10 items in `references/schemas/` via shell `cat`, so any missing file causes immediate runtime failure. Immediately after skill creation, confirm all 10 files exist with `ls .codex/skills/{name}/references/schemas/`.
> **Update Policy:** When `codex-harness` `references/schemas/` changes, propagate the same change to all derived orchestrator skills (drift prevention). The `_workspace/_schemas/` in an in-progress workspace is a snapshot and should be preserved.

> **Full bundle example (case integrating all outputs of one domain):** See `references/examples/full-bundle/sso-style.md`. A canonical package that simultaneously creates all 5 files: orchestrator SKILL.md + workflow.md + findings.md + tasks.md + checkpoint.json.

### 7-6. Flat Step → Stage-Step Migration Guide

The procedure for converting non-standard orchestrator skills previously written with only flat `Step 0~N` headers (e.g., `examples/sso-dev-flow` style) to the current Stage-Step model. **Directly corresponds to drift items #1 and #2 in `expansion-matrix.md`.**

**Identifying Migration Targets (Checklist):**

- [ ] SKILL.md body has 0 `### Stage` headers — only flat Steps exist
- [ ] workflow.md is not used (or replaced with a simple checklist)
- [ ] Termination conditions are in natural language ("QA approval", "when done", "sufficiently")
- [ ] No `_workspace/tasks/task_*.json` persistence (directly modifying tasks.md)
- [ ] `references/schemas/` directory is absent

**6-Step Migration:**

| Step | Task | Validation | Output |
|------|------|------|--------|
| **M1. Inventory** | Group the flat Step 0~N in the existing SKILL.md into domain work units (Work). Each group = candidate Stage. | Number of groups = number of Stage candidates, number of Steps within each group ≥ 1 | `migration_plan.md` draft |
| **M2. Stage Mapping** | Assign Stage names to each group (based on work meaning: `gather`·`design`·`validate`). Decompose sub-steps within each group into Steps (≡Tasks). | Stage/Step names match `[a-z][a-z0-9-]*` pattern | Stage-Step mapping table |
| **M3. Pattern Assignment** | Assign 1 of the 7 patterns to each Step (`pipeline`·`fan_out_fan_in`·`expert_pool`·`producer_reviewer`·`supervisor`·`hierarchical`·`handoff`). Free notation ("sequentially") is prohibited. | Passes enum check | Mapping table with pattern column added |
| **M4. Termination Condition Conversion** | Natural language → verifiable predicate. `"QA approval"` → `verdict=PASS in qa_verdict.json`, `"when done"` → `status=done in task_*.json`, `"sufficiently"` → `iterations ≥ N`. | Passes `orchestrator-template.md` Step 1.8 whitelist | Verified predicate column added |
| **M5. Create 5 Output Files** | Based on the mapping table, create `workflow.md` + `findings.md` + `tasks.md` + `checkpoint.json`. New SKILL.md body adopts the `references/orchestrator-template.md` skeleton. | `workflow.md` has 0 missing fields out of 6, cycle validation passes | New 5 files |
| **M6. Bundle schemas/** | Copy 10 items from `codex-harness/references/schemas/` to new skill's `references/schemas/` (task + checkpoint schemas + workflow/findings/tasks templates + models.md + agent-worker.template.toml + agent-orchestrator.template.md + agent-state-manager.template.toml + state.py). | 10 files exist at `ls .codex/skills/{new}/references/schemas/` | Bundle complete |

**Example conversion table (sso-dev-flow → 5-stage Stage-Step):**

| Existing (Flat) | New (Stage-Step + Pattern) | Termination Condition Conversion |
|------------|--------------------------|---------------|
| `Step 0: Requirements Gathering` | Stage `discover` / Step `gather` (`fan_out_fan_in`) | 4 `task_*.json status=done` |
| `Step 1: Design Review` | Stage `discover` / Step `design-review` (`producer_reviewer`) | `review_verdict.json verdict=PASS` |
| `Step 2: Implementation` | Stage `build` / Step `implement` (`pipeline`) | `_workspace/{plan}/code/*.go` files exist |
| `Step 3: Pass upon QA Approval` | Stage `validate` / Step `qa-loop` (`producer_reviewer`) | `qa_verdict.json verdict=PASS AND iterations ≤ 3` |
| `Step 4: Deployment` | Stage `validate` / Step `deploy` (`pipeline`) | `deployment.log status=success` |

**Backward Compatibility Policy:**

- Existing in-progress `_workspace/` is preserved — applied from new runs after migration.
- If `_schemas/` directory does not exist in the existing `_workspace/`, do not add it automatically (to ensure snapshot integrity). Requires user approval before new runs.
- Migration must be recorded in AGENTS.md change history: `[YYYY-MM-DD] {skill name}: flat Step → Stage-Step conversion (M1~M6)`.

**Post-Migration Validation:**

- [ ] All drift items #1, #2, #3 in `expansion-matrix.md` (flat Step, natural language termination conditions, required fields) pass
- [ ] `orchestrator-template.md` Step 1.8 (schema validation) + Step 1.9 (cycle validation) pass
- [ ] At least 1 test scenario runs successfully (see full-bundle/sso-style.md pattern)

---

## 8. Data Schema Standards

Follow the standard schemas below for consistency in data exchange between skills and evaluation.

### 8-1. eval_metadata.json

Metadata for each test case:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "User's task prompt",
  "assertions": [
    "Output contains X",
    "File was created in Y format"
  ]
}
```

### 8-2. grading.json

Assertion-based scoring results:

```json
{
  "expectations": [
    {
      "text": "Output contains 'Seoul'",
      "passed": true,
      "evidence": "Confirmed 'Seoul region data extraction' in step 3"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  }
}
```

**Field name caution:** The top-level array is `expectations`, and internal fields must use exactly `text`·`passed`·`evidence` (variants like `items`·`name`·`met`·`details` are prohibited). The harness Phase 6 validation and section 4 of `skill-testing-guide.md` assume this schema.

### 8-3. timing.json

Execution time and token measurement:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

Save `total_tokens` and `duration_ms` **immediately** from the agent completion notification. This data is only accessible at the time of notification and cannot be recovered afterward.

### 8-4. findings.md / tasks.md

Shared state files for the Codex CLI harness. When a skill updates these two files, it must adhere to the section specifications in `orchestrator-template.md`.

- `findings.md`: `[Key Insights]`, `[Key Keywords]`, `[Shared Variables/Paths]`, `[Data Conflicts]`, `[Change Requests]`, `[Next Step Instructions]` (use only sections needed for the pattern)
- `tasks.md`: `[ID]`, `[Agent]`, `[Task Description]`, `[Status]`, `[Evidence]`, `[Linked Outputs]`

---

## 9. What Not to Include in a Skill

- Supplementary documents such as `README.md`, `CHANGELOG.md`, `INSTALLATION_GUIDE.md`
- Meta information from the skill creation process (test results, iteration history, commit messages, etc.)
- User-facing documentation — a skill is **a set of instructions for an AI agent**.
- General knowledge that agents already know (language syntax, general CS concepts, etc.)
- Hardcoded values that only fit a specific test case (violation of the generalization principle)
