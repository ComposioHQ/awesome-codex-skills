# Subagent Orchestration Real-World Examples (Codex CLI)

Real-world examples for 5 architecture patterns. **In the Codex CLI environment, direct communication between subagents is not possible**, so all team communication is brokered by the main agent via `_workspace/findings.md` and `_workspace/tasks.md`.

> **Note:** Team APIs such as `TeamCreate`, `SendMessage`, and `TaskCreate` from Claude Code do not exist in Codex CLI. Subagent invocation is performed via **@agent-name directives**, and parallel execution is implemented as consecutive calls within a single response turn.
> **Stage-Step structure required:** The orchestrator in every example reads `checkpoint.json` (`status`, `current_stage`, `current_step`) in Step 0 to determine the execution mode, and creates `workflow.md` in Step 1 (Resume mode reads the existing file). Example 1's orchestrator workflow is the reference implementation; all other examples apply the same pattern.

---

## Example Index

| #   | Pattern               | Domain Example       | Agent Count | Key Characteristics                                                     | File                                                                               |
| --- | --------------------- | -------------------- | ----------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 1   | Fan-out/Fan-in        | Research Team        | 4           | Parallel investigation then consolidation, data conflict arbitration    | [examples/team/01-fan-out-fan-in.md](examples/team/01-fan-out-fan-in.md)           |
| 2   | Producer-Reviewer     | Webtoon Production   | 2           | PASS/FIX/REDO loop, full agent file examples included                   | [examples/team/02-producer-reviewer.md](examples/team/02-producer-reviewer.md)     |
| 3   | Supervisor            | Code Migration       | 1+N         | Runtime dynamic task assignment, tasks.md claim mechanism               | [examples/team/03-supervisor.md](examples/team/03-supervisor.md)                   |
| 4   | Hierarchical          | Full-stack App Dev   | 5           | 2-level delegation, team lead intermediate coordination, full agent file examples included | [examples/team/04-hierarchical.md](examples/team/04-hierarchical.md)               |
| 5   | Handoff + Persistence | System Debugging     | 4           | [NEXT_AGENT] parsing, large log resumption                              | [examples/team/05-handoff-persistence.md](examples/team/05-handoff-persistence.md) |

### Pattern Selection Guide

| Situation                                                            | Recommended Pattern             |
| -------------------------------------------------------------------- | ------------------------------- |
| Run independent tasks in parallel then consolidate                   | Fan-out/Fan-in (Example 1)      |
| Improve generation quality through iterative review                  | Producer-Reviewer (Example 2)   |
| Process large volumes of homogeneous tasks, track progress in real time | Supervisor (Example 3)       |
| Heterogeneous domain team, 2-level specialization delegation needed  | Hierarchical (Example 4)        |
| Unknown root cause, expert selection depends on analysis results     | Handoff (Example 5)             |
| Processing large data with pause/resume needed                       | Handoff + Persistence (Example 5) |

---

## Output Pattern Summary

### Agent Definition Files

- Path: `.codex/agents/{agent-name}.toml` (project) or `~/.codex/agents/{agent-name}.toml` (user).
- Required TOML fields: `name`, `description` (assertive, including follow-up keywords), `model` (actual ID: see `references/schemas/models.md`), `sandbox_mode` (per role), `model_reasoning_effort` (per role: `low` · `medium` · `high` · `xhigh` — per `references/schemas/models.md`).
- Required sections: core role, working principles, input/output protocol, collaboration protocol (Codex CLI), error handling.

### findings.md Standard Section Structure

Standard sections initialized by the orchestrator in Phase 1:

| Section Name          | Purpose                                                           | Primarily Used Pattern              |
| --------------------- | ----------------------------------------------------------------- | ----------------------------------- |
| `[Key Insights]`      | Core summary of research and analysis results                     | Fan-out/Fan-in                      |
| `[Key Keywords]`      | Common keywords for injection into agent prompts                  | Fan-out/Fan-in                      |
| `[Shared Vars/Paths]` | Shared paths, API contracts, and persistence resume points between agents | All patterns               |
| `[Data Conflicts]`    | Records conflicting information between agent outputs             | Fan-out/Fan-in, Supervisor, Handoff |
| `[Change Requests]`   | Rework instructions                                               | Producer-Reviewer                   |
| `[Next Step Guide]`   | Guide for what the next agent should focus on                     | Pipeline, Hierarchical              |

Initialize only the sections needed for the pattern. Omit unused sections.

### tasks.md Base Schema

Task list format registered by the orchestrator in Phase 1:

```
| ID | Task Name | Assigned Agent | Priority | Complexity | Status |
|----|-----------|----------------|----------|------------|--------|
| 1  | ...       | @migrator-1    | High     | Large      | Todo   |
```

- **Status values**: `Todo` → `In-Progress` → `Done` | `Blocked`
- **Main agent updates only**: Workers write only to `task_{agent}_{id}.json`. The main agent collects and atomically updates tasks.md.
- **Blocked items**: Request user confirmation, then mark the relevant row status as `Blocked`.

### Skill File Structure

- Path: `.codex/skills/{skill-name}/SKILL.md`.
- Large knowledge bases are split into `references/` (Progressive Disclosure).

### Orchestrator Skill

- Top-level skill that coordinates the entire team. Covers Phase 0 (re-run detection) through Phase 5 (preservation and reporting).
- Template: see `references/orchestrator-template.md`.
- No direct communication between subagents — all collaboration is brokered via `findings.md`, `tasks.md`, and `checkpoint.json`.
- `_workspace/workflow.md` Stage-Step declaration in Phase 1; read every cycle to call only the `active agents` for the current step. On agent failure: maximum 2 retries (3 total) → if unresolved, `Blocked` + request user confirmation. Arbitrary skipping is strictly prohibited.
