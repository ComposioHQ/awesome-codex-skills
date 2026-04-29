# Subagent Orchestration Design Patterns (Codex CLI)

## Table of Contents

1. [Orchestration Mode Overview](#execution-mode-orchestration)
2. [Thread-safe Task Board Protocol](#thread-safe-task-board-protocol-preventing-parallel-write-conflicts)
3. [7 Core Architecture Patterns](#7-core-architecture-patterns)
4. [Multi-stage Workflow Composition](#multi-stage-workflow-composition)
5. [Persistence Protocol (Durable Execution)](#persistence-and-durability-protocol-durable-execution)
6. [Tool Permission Control and Type Mapping](#tool-permission-control-and-type-mapping-guide)
7. [Data Brokering Protocol](#data-brokering-protocol)
8. [Subagent Interaction Styles](#subagent-interaction-styles)
9. [Agent Separation Criteria](#agent-separation-criteria)
10. [Agent Definition Structure](#agent-definition-structure-codex-cli-official-format)
11. [Skill vs Agent Distinction](#skill-vs-agent-distinction)
12. [Skill ↔ Agent Connection Methods](#skill--agent-connection-methods)

---

## Execution Mode: Orchestration

In Codex CLI, the main agent acts as the **orchestrator** to coordinate subagents. Direct communication between subagents is not possible, but highly sophisticated collaboration can be achieved through the main agent's **brokering** and shared files.

```
[Main Agent (Orchestrator)]
  ├── Data Brokering (Data Broker / findings.md)
  ├── State Management (Atomic Task Board / tasks.md)
  ├── Persistence Management (Persistence / checkpoint.json)
  └── Shared Workspace (_workspace/{plan_name}/)
        ├── @subagent-A (specialized toolset + dedicated task_A.json)
        ├── @subagent-B (specialized toolset + dedicated task_B.json)
        └── @subagent-C (specialized toolset + dedicated task_C.json)
```

> **Difference from Claude Code:** Claude Code has an "agent team" mode based on `TeamCreate`/`SendMessage`/`TaskCreate` that allows team members to communicate and broadcast directly to each other, but **Codex CLI does not have this team API**. When inter-member communication is needed, the main agent reads outputs via shell `cat` and injects them into the next agent's prompt — a **file brokering** approach. Subagents are invoked by the orchestrator using `@agent-name` directives, and when parallel execution is required, it is implemented as consecutive calls within a single turn. (Background execution of shell commands themselves is separately supported with `&`.)

### Orchestration Model Selection Decision Tree

```
Are there 2 or more agents?
├── Yes → Is information exchange between agents required?
│         ├── Yes → Fan-out/Fan-in design where the main brokers via findings.md
│         │         (cross-validation, discovery sharing, real-time feedback quality improvement)
│         │
│         └── No → Simple fan-out where the main only collects results
│                  (one-pass patterns like produce-verify or expert pool)
│
└── No (1 agent) → Single subagent call
              (a single agent does not need orchestration)
```

> **Core Principle:** In Codex CLI, the premise that "the main agent is the sole broker" underpins all patterns. When selecting a pattern, first design "at what point and what information should the main agent broker?"

---

## Thread-safe Task Board Protocol (Preventing Parallel Write Conflicts)

When multiple agents run in parallel, data can be lost if they attempt to write to the shared file `tasks.md` simultaneously. To prevent this, follow the **Atomic Task Management** principles below.

### 1. Split Task Artifacts

- **Principle:** Subagents must never directly modify the shared `tasks.md`.
- **Implementation:** Each agent writes its task results to a **dedicated individual file** such as `_workspace/tasks/task_{agent_name}_{task_id}.json`.
- **Content:** Includes task status (`status`), evidence (`evidence`), and output path (`path`).

### 2. Sole Aggregator

- **Principle:** The sole write authority over `tasks.md` and `checkpoint.json` belongs to the **main agent (orchestrator)**.
- **Workflow:**
  1. The main agent calls parallel agents.
  2. Each agent creates its own individual task file and exits.
  3. The main agent scans with `shell ls _workspace/tasks/` and reads all individual files.
  4. The main agent performs an Atomic Update of `tasks.md` at once based on the data it has read.

---

## 7 Core Architecture Patterns

### 1. Pipeline — Sequentially Dependent Tasks

A flow where the output of the previous stage is used as the input of the next stage.

```
[Analysis] → [Design] → [Implementation] → [Validation]
```

- **Coordination:** Sequential calls. After the Nth agent completes, the main summarizes results to `findings.md` → injects into the (N+1)th agent's prompt.
- **Usage Example (Orchestrator's invocation style):**
  > **Main:** `` `@{analyst}`, please analyze the requirements and save them to `_workspace/{plan_name}/01_reqs.md`. Check the latest specification as needed.
(After completion)
**Main:** `` `@{coder}`, read `_workspace/{plan_name}/01_reqs.md` and implement while adhering to the [Key Constraints] in `findings.md`. Save the result to `_workspace/{plan_name}/02_code.md`.
- **Suitable for:** Novel writing (world-building → characters → plot → writing → editing), design → implementation → validation flows.
- **Caution:** A bottleneck delays the entire pipeline. Design each stage to be as independent as possible, and verify whether consecutive stages represent a "true dependency" needed at every point. Choosing a pipeline merely out of preference for sequential order means missing parallelization opportunities.

### 2. Fan-out/Fan-in — Parallel Investigation and Integration

Performs independent tasks simultaneously and combines the results into one.

```
         ┌→ [Expert A] ─┐
[Distribute] → ├→ [Expert B] ─┼→ [Integrate]
         └→ [Expert C] ─┘
```

- **Coordination:** Call `@A`, `@B`, `@C` consecutively in a single response turn → each saves outputs under `_workspace/{plan_name}/` → when the main calls the integration agent, it injects all output paths into the prompt.
- **Usage Example (Orchestrator's invocation style):**
  > **Main:** (batch calls within a single turn)
  >
  > 1. `` `@{researcher-market}`, research market trends and record them in `\_workspace/{plan_name}/mkt.md`.
  > 2. `` `@{researcher-tech}`, research technical feasibility and record it in `_workspace/{plan_name}/tech.md`.
(After all complete)
**Main:** `` `@{strategist}`, read both `_workspace/{plan_name}/mkt.md` and `_workspace/{plan_name}/tech.md`, resolve any conflicting data noted in the [Data Conflicts] section of `findings.md`, and formulate the final strategy.
- **Suitable for:** Comprehensive research (simultaneous investigation of official sources/media/community/background → integration), multi-module development.
- **Caution:** The quality of the integration stage determines overall quality. Since discoveries between experts may **conflict**, the main should include a [Data Conflicts] section in `findings.md` and instruct the integration agent to resolve conflicts without fail.

### 3. Expert Pool — Situational Expert Selection

Selects and calls the most suitable subagent based on the nature of the user's request.

```
[Router] → { Expert A | Expert B | Expert C }
```

- **Coordination:** The main agent classifies the input and calls only the agent for that domain.
- **Invocation style:** Always sequential calls. Do not call multiple experts simultaneously.
- **Usage Example (Orchestrator's invocation style):**
  > **Main:** (User request: "Improve React performance")
  > **Main:** `` `@{perf-expert}`, analyze the current code and find bottlenecks. `@{security-expert}` is excluded from this task.
- **Suitable for:** Multilingual support (native agents per language), code review (choosing security/performance/architecture experts), stack-specific specialized reviews.
- **Caution:** The classification accuracy of the router (main) is critical. If classification is ambiguous, clarify by requesting user confirmation, or call two experts simultaneously for cross-validation.

### 4. Producer-Reviewer — Quality Assurance Loop

A producer and reviewer iterate in a loop to refine outputs.

```
[Produce] → [Review] → (if issues) → [Produce] re-run
```

- **Coordination:** Main calls the producer → reads output and summarizes to `findings.md` → calls reviewer (injecting output path) → reads review report, and if there are issues, re-calls the producer (injecting the report).
- **Usage Example (Orchestrator's invocation style):**
  > **Main:** `` `@{writer}`, draft the document.
**Main:** `` `@{editor}`, review the draft and leave revision suggestions in `_workspace/{plan_name}/edit_notes.md` according to qa-standard criteria.
  > (If review result is 'Fail')
  > **Main:** `` `@{writer}`, revise the draft incorporating the feedback from `\_workspace/{plan_name}/edit_notes.md`. (Maximum 2 retries, 3 total)
- **Suitable for:** Webtoons (artist → reviewer → regeneration), high-quality code writing, technical document proofreading.
- **Caution:** **To prevent infinite loops, setting a maximum of 2 retries (3 total) is mandatory.** If still failing after 3 attempts, the main requests user confirmation to transfer decision-making to a human.

### 5. Supervisor — Dynamic Task Assignment

The main agent analyzes workload and dependencies at runtime to distribute tasks.

```
         ┌→ [Worker A]
[Supervisor] ─┼→ [Worker B]    ← Supervisor dynamically distributes based on status
         └→ [Worker C]
```

- **Coordination:** State management using `tasks.md`. The main splits the `Todo` list and batch-assigns to each worker. After a worker completes, the main **must verify success via `Evidence` or `qa_report.md`** before updating to `Done` and assigning the next batch.
- **Usage Example (Orchestrator's invocation style):**
  > **Main:** There are 50 migration tasks in `tasks.md`.
  >
  > 1. `` `@{worker-1}`, complete task IDs 1–10.
  > 2. `` `@{worker-2}`, complete task IDs 11–20.
(After completion report arrives)
**Main:** `@{worker-1}`, I have confirmed the outputs and test logs (`Evidence`). Since they passed, mark them as `Done` and now complete tasks 21–30. **If any tasks fail, do not skip them — stop immediately and report a solution.**
- **Suitable for:** Large-scale file migration, bulk data processing.
- **Difference from Fan-out:** Fan-out distributes tasks in advance with fixed assignments; Supervisor adjusts dynamically by observing progress.
- **Caution:** Set delegation units large enough so the supervisor (main) does not become a bottleneck (calling 1 file × 100 times < calling 10 files × 10 times).

### 6. Hierarchical Delegation — Recursive Problem Decomposition

A higher-level agent delegates recursively to lower-level agents. Complex problems are broken down step by step.

```
[Director] → [Team Lead A] → [Practitioner A1]
                           → [Practitioner A2]
           → [Team Lead B] → [Practitioner B1]
```

- **Coordination:** Nested agent calls with summarized context forwarding. Team lead agents split the instructions they receive and re-invoke practitioner agents.
- **Usage Example (Orchestrator's invocation style):**
  > **Main:** `` `@{frontend-lead}`, oversee the UI system construction.
**@{frontend-lead}:** (within the prompt) I will instruct `` `@{component-coder}` to implement the button component and `` `@{style-coder}` to implement the theme system.
- **Suitable for:** Full-stack application development (director → frontend lead → UI/logic/tests + backend lead → API/DB/tests), complex system architecture design.
- **Caution:** **More than 3 levels deep causes significant delays and context loss — 2 levels or fewer is recommended**. Team lead agents should summarize practitioner outputs before forwarding to the director, while preserving originals in `_workspace/{plan_name}/{team}/`.

### 7. Handoff — Agent-driven Delegation

Instead of the main pre-determining all paths, the practitioner agent performs a task and then recommends **"the most suitable expert for the next step"** to the orchestrator, transferring control.

- **Coordination:** When an agent leaves a `[NEXT_AGENT: @expert-name]` keyword and recommendation rationale at the end of its output, the orchestrator parses this and dynamically summons the next agent.
- **Routing Principle:** Agents consult the list of other agents in the project (based on descriptions) to make recommendations.
- **Usage Example (Orchestrator's invocation style):**
  > **Main:** `` `@{log-analyzer}`, analyze the error logs and identify the root cause. If specialized handling is needed, be sure to leave `[NEXT_AGENT: @{agent-name}] Reason: {specific reason}` at the end of your output.
(log-analyzer completes, end of output: `[NEXT_AGENT: @security-patcher] Reason: Authentication vulnerability found due to missing JWT validation`)
**Main:** (after parsing the keyword) `` `@{security-patcher}`, read `_workspace/{plan_name}/log_analysis.md` and patch the identified authentication vulnerability.
- **Suitable for:** Exploratory debugging (log analysis → reproduction attempt → handoff to fix specialist), complex support processes.
- **Caution:** Preventing circular handoffs (A → B → A) infinite loops is essential — the orchestrator tracks call history and does not re-summon an agent that has already been executed. If a handoff chain occurs 3 or more stages or there is no recommended target agent, transfer decision-making to the user via confirmation request. Detection pseudocode: see `references/orchestrator-procedures.md` — "handle_handoff".

---

## Multi-stage Workflow Composition

The 7 basic patterns are **combined at the Step level**. Declaring them in a Stage-Step structure allows each Step to have an independent pattern, enabling precise multi-stage workflows. Details: `references/stage-step-guide.md`.

| Workflow Type                        | Step Composition                                                                              | Example                                                                       |
| ------------------------------------ | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Parallel Collection → Review Loop** | Stage 1 / Step 1: fan_out_fan_in → Stage 2 / Step 1: producer_reviewer                      | Multilingual translation — parallel translation in 4 languages → native reviewer loop |
| **Sequential Design → Parallel Validation** | Stage 1 / Step 1-N: pipeline → Stage 2 / Step 1: fan_out_fan_in                      | Requirements · design · API design (sequential) → security · performance · compatibility validation (parallel) |
| **Classification → Expert Analysis → Review** | Stage 1 / Step 1: expert_pool, Step 2: pipeline → Stage 2 / Step 1: producer_reviewer | Issue classification → expert analysis → report review              |

### Multi-stage Workflow Coordination Points (Codex CLI)

| Scenario                    | Brokering Strategy                                                                                    | Caution                                                                                           |
| --------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Research + Analysis**     | Merge investigator outputs into `findings.md` in real time; log conflicting discoveries in the [Data Conflicts] section | If the integration agent cannot resolve conflicts, call for user confirmation |
| **Design + Implementation + Validation** | Design output → inject into implementation agent prompt → implementation result → inject into validation agent prompt | Between each stage, do not merely **pass file paths** — also extract **key constraints** into `findings.md` and inject them |
| **Supervisor + Workers**    | Synchronize state via `tasks.md`; workers read only their assigned tasks                              | Supervisor divides work by file so that multiple concurrently assigned workers do not modify the same file |
| **Production + Validation** | Produce → validation report (`qa_report.md`) → inject report into prompt on re-production             | Maximum 2 retries (3 total); request user confirmation if exceeded                               |

---

## Persistence and Durability Protocol (Durable Execution)

All orchestration workflows must have **Persistence** to guard against network failures, timeouts, and model errors.

### 1. Checkpoint Protocol (`checkpoint.json`)

The orchestrator creates or updates `_workspace/checkpoint.json` upon every agent task completion.

- **Required data:**
  - `last_successful_step`: The last successfully completed Step number or agent name.
  - `tasks_snapshot`: A summary of the current state data in `tasks.md`.
  - `shared_variables`: Key constants or variable values shared between agents.
- **Advantage:** Even if execution is interrupted, the checkpoint is detected at Step 0 and **resumption from the point of failure is immediately possible**.

### 2. Idempotency Guarantee Principles

- **Duplicate prevention:** Each agent checks whether its target output file already exists at the start of execution.
- **State-based skipping:** If the content is up to date and no modification is needed, the task is not performed and a completion signal is sent immediately to prevent token waste.
- **Atomic writing:** `tasks.md` is not changed to `Done` before file writing is complete.

---

## sandbox_mode Permission Control Guide

Codex CLI controls agent permissions with the single **`sandbox_mode`** field instead of a `tools:` array. Follow the principle of least privilege appropriate to the role.

### Available Operations per sandbox_mode

| sandbox_mode         | Available Operations                                                            | Representative Agents          |
| -------------------- | ------------------------------------------------------------------------------- | ------------------------------ |
| `read-only`          | shell `cat` · `find` · `grep` · `ls`, web fetch — no file writing              | Analyst, Architect             |
| `workspace-write`    | + `apply_patch`, shell `tee` · write, subagent spawn, test execution            | Coder, Reviewer, State Manager |
| `danger-full-access` | + external processes (kubectl, terraform, deploy, etc.)                         | Operator, Deployer             |

### Special-purpose Tools

Special tools confirmed in Codex CLI. Do not grant to general worker agents; allow only selectively for roles that require them.

| Tool                | Purpose                                              | Recommended Agents                                                                     |
| ------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `@agent-name` call  | Subagent invocation                                  | Orchestrator, Supervisor, Hierarchical team leads (Mid-level) only — prohibited for general workers |
| `save_memory`       | Persisting key information across sessions           | Orchestrator (as a supplement to checkpoints)                                          |
| `write_todos`       | Built-in to-do list management (lightweight alternative to `tasks.md`) | Orchestrator for single-agent tasks                           |
| `get_internal_docs` | Querying Codex CLI internal documentation            | Analyst, Architect                                                                     |

> **Caution:** `save_memory` does **not replace** file-based persistence via `checkpoint.json`. Files are more reliable when resuming a session. Use `save_memory` only for small amounts of data that are cumbersome to manage as files, such as agent personas or shared constants.

### MCP Tool Mapping Examples

- **GitHub specialist agent:** Assign only `mcp_github_*` tools, dedicated to issue management and PR handling.
- **Infrastructure specialist:** Restrict permissions with `mcp_kubernetes_*` or `mcp_terraform_*` tools.
- **Documentation specialist:** Assign mainly shell `curl` · `cat` for building a knowledge base.

### Model Selection Guide

| Agent Role                              | Model Tier                        | Where to Verify Actual IDs                    |
| --------------------------------------- | --------------------------------- | --------------------------------------------- |
| Orchestrator, Architect                 | **thinking tier** (`gpt-5.5`)     | `references/schemas/models.md` (SoT)          |
| Coder, Analyst, Reviewer, Operator      | **codex tier** (`gpt-5.3-codex`)  | `references/schemas/models.md` (SoT)          |
| State Manager                           | **mini tier** (`gpt-5.4-mini`)    | `references/schemas/models.md` (SoT)          |

> **Important:** Do not hard-code model IDs directly in code. Always verify with `_workspace/_schemas/models.md` via shell `cat` before using. OpenAI model IDs change periodically, and incorrect IDs will cause runtime errors.
> **Reason:** Workers have a narrow scope and are called repeatedly. The codex tier has speed and cost advantages over thinking. Only the Orchestrator and Architect use thinking.

`model_reasoning_effort` selection criteria and value list: see `references/schemas/models.md` (`low` / `medium` / `high` / `xhigh`).

---

## Data Brokering Protocol

The main agent brokers **Discoveries** between subagents in real time.

1. **Real-time recording:** Every time the main agent reads intermediate results, it summarizes key insights to `_workspace/findings.md`.
2. **Context injection:** When calling the next subagent, inject "Key discoveries so far: [findings.md content]" into the prompt.
3. **State synchronization:** Instruct all agents to read `_workspace/tasks.md` every time they are called, to understand the full context.
4. **Conflict brokering:** If agent outputs conflict, explicitly note in the [Data Conflicts] section of `_workspace/findings.md` → request arbitration from a specialist (typically the Reviewer).

## Subagent Interaction Styles

In addition to structural patterns, the orchestrator can choose the **style** in which it communicates with agents to maximize efficiency.

| Style                         | Invocation Method    | Characteristics                                                                 | When Suitable                                                       |
| :---------------------------- | :------------------- | :------------------------------------------------------------------------------ | :------------------------------------------------------------------ |
| **Full Delegation**           | Subagent call        | The subagent completes the task end-to-end (including file creation).           | Independent practical work such as coding, research, test execution. |
| **Consultative**              | Subagent call        | Returns only **"analysis opinion"** or **"checklist"** instead of deliverables. | Architecture review, security inspection, implementation strategy planning. |
| **Manual Intervention**       | `@agent_name`        | The user directly summons a specific agent from the terminal.                   | When the user wants to manually re-verify only a specific stage during harness execution. |

### Advanced Tips by Style

- **Using the consultative style:** Before the main agent writes code directly, summon `@architect` and ask only for "an opinion on what structure would be best." The main then records that opinion in `findings.md` and writes the code directly, resulting in less context loss.
- **Prompting manual intervention:** Guide the orchestrator to suggest to the user: "Would you like to call `@agent-name` directly to review the detailed logs?" when the orchestrator cannot resolve an error.
- **The power of tool isolation:** Consultative-style agents can be designed without `apply_patch` permission and with only shell `cat`, ensuring they provide only "knowledge" without accidentally touching code.

---

## Agent Separation Criteria

Four criteria for deciding whether to merge into a single agent or separate into distinct agents.

| Criterion         | Separate                                                              | Merge                                        |
| ----------------- | --------------------------------------------------------------------- | -------------------------------------------- |
| **Specialization** | Separate if domains (domain · language · stack) differ               | Merge if domains overlap                     |
| **Parallelism**   | Separate if independently executable (reduces delay via parallel calls) | Consider merging if sequentially dependent  |
| **Context**       | Separate if context burden is large (each reads only a small scope)  | Merge if lightweight and fast                |
| **Reusability**   | Separate if used by other teams/scenarios                            | Consider merging if used only by this team   |

**Additional Codex CLI considerations:** Every separation increases the main agent's brokering burden (updating `findings.md` before and after each agent call). Verify whether the benefit of separation outweighs the brokering overhead. When in doubt, start with a unified agent and separate when reuse requirements arise.

---

## Agent Definition Structure (Codex CLI Official Format)

> **When creating agent files:** Do not use inline examples — read **`_workspace/_schemas/agent-worker.template.toml`** (for workers) or **`agent-orchestrator.template.md`** (for orchestrators) via shell `cat`, substitute variables, then create. Model IDs must be verified from **`_workspace/_schemas/models.md`** — never guess arbitrarily.

```toml
name = "agent-name"
description = "1-2 sentence role description. List trigger keywords. Also specify that follow-up tasks (revision/supplementation/re-execution) should use this agent."
model = "{role tier ID verified from models.md}"  # ← Always refer to _workspace/_schemas/models.md
sandbox_mode = "{{SANDBOX_MODE}}"              # read-only(Analyst/Architect) | workspace-write(Coder/Reviewer/QA) | danger-full-access(Operator)
model_reasoning_effort = "high"   # low(StateManager) | medium(Analyst/Researcher) | high(Coder/QA) | xhigh(Orchestrator/Architect)

developer_instructions = """
# Agent Name — One-line Role Summary

You are a [role] specialist in [domain].

## Core Responsibilities

1. Responsibility 1
2. Responsibility 2

## Operating Principles

- Principle 1
- Principle 2

## Input/Output Protocol (Data Broker-based)

- **Input briefing:** Read the `findings.md` summary and the assigned task from `tasks.md` injected into the prompt at call time.
- **Output path:** `_workspace/{plan_name}/{step}/{agent}-result.md` (or the path specified by the orchestrator).
- **Format:** [File format, section structure, required fields]
- **Completion signal:** After recording the output, print the "completion keyword" specified in the prompt.

## Error Handling

- Missing required input → request supplementation via user confirmation request.
- Data conflict discovered → add to [Data Conflicts] in `findings.md` and mark as unable to proceed.
- Timeout/retry limit reached → report failure to the orchestrator with detailed logs.

## Relationship with Other Agents

- Predecessor: [Which agent's output does this agent depend on?]
- Successor: [Which agent consumes this agent's output?]
- Note: Direct communication between subagents is not possible. All collaboration goes through `findings.md`.
"""
```

> **Caution:** The "team communication protocol (SendMessage)" section of Claude Code agent definitions does not exist in Codex CLI. Instead, specifying file paths, completion signals, and briefing methods in the "Input/Output Protocol" serves the same role.

---

## Skill vs Agent Distinction

| Category       | Skill                                                                | Agent                                              |
| -------------- | -------------------------------------------------------------------- | -------------------------------------------------- |
| **Definition** | Procedural knowledge + tool bundle                                   | Expert persona + behavioral principles             |
| **Location**   | `.agents/skills/{name}/SKILL.md`                                     | `.codex/agents/{name}.toml`                        |
| **Trigger**    | Orchestrator auto-selects via user request keyword matching          | Orchestrator explicitly calls with `@{name}`       |
| **Size**       | Small to large (workflows)                                           | Small (role definition)                            |
| **Purpose**    | "**How** to do it"                                                   | "**Who** does it"                                  |
| **Statefulness** | Stateless (procedure re-executed on every call)                    | Persona and principles fixed, context maintained within session |

**Summary:** A skill is a **procedural guide** that an agent references when performing a task, and an agent is a **specialist role definition** that utilizes skills.

---

## Skill ↔ Agent Connection Methods

Three ways agents utilize skills.

| Method                     | Implementation                                                                              | When Suitable                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Direct skill file load** | Orchestrator reads via `cat .agents/skills/{name}/SKILL.md` and injects into prompt        | When the skill is an independent workflow and the user can call it directly |
| **Inline in prompt**       | Skill content is directly included in the agent definition body                             | When the skill is short (50 lines or fewer) and **exclusive** to this agent |
| **Reference load**         | Load `.agents/skills/{skill}/references/*.md` via shell `cat` as needed                    | When skill content is large and only **conditionally** needed             |

**Recommendation:**

- High reusability → skill
- Exclusive → inline
- Large + conditional → shell `cat` reference load

**Principle:** The orchestrator reads the necessary skill files via shell `cat` and injects them into the agent prompt. Behavioral principles, protocols, and checklists should almost always be separated into skills for higher reusability and maintainability.
