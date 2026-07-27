# `_workspace/_schemas/` Source-of-Truth (Codex CLI Version)

Runtime schema definitions (single source of truth). At runtime, orchestrator Step 1 reads each file and writes to `_workspace/_schemas/` via shell commands or `apply_patch`.

## Files

| File                             | Type                           | Purpose                                                          |
| -------------------------------- | ------------------------------ | ---------------------------------------------------------------- |
| `task.schema.json`               | JSON Schema (Draft 7)          | Worker report validation for `_workspace/tasks/task_{agent}_{id}.json` |
| `checkpoint.schema.json`         | JSON Schema (Draft 7)          | Validation SoT for `_workspace/checkpoint.json` — parsed by `state.py` at runtime |
| `findings.template.md`           | Markdown skeleton              | Data broker initialization for `_workspace/findings.md`         |
| `tasks.template.md`              | Markdown table skeleton        | Task board initialization for `_workspace/tasks.md`             |
| `workflow.template.md`           | Markdown block skeleton        | Stage-Step declaration reference for `_workspace/workflow.md`   |
| `models.md`                      | Model ID registry (SoT)        | Authoritative OpenAI model IDs for agent creation               |
| `agent-worker.template.toml`         | Agent TOML template            | Reference for generating worker agent `.codex/agents/{name}.toml` |
| `agent-orchestrator.template.md`     | Orchestrator SKILL.md template | Reference for generating orchestrator skills                    |
| `agent-state-manager.template.toml`  | State manager agent TOML template | Reference for generating State Manager `.codex/agents/state-manager.toml` (optional) |
| `state.py`                           | Python state manager CLI          | Deployed to `_workspace/state.py` at init — targeted reads/writes to minimize token usage |

> Only `README.md` is not copied to the workspace. 9 files go to `_workspace/_schemas/`. `state.py` is deployed separately to `_workspace/state.py` (callable as `python _workspace/state.py`).

## Lifecycle

1. **Skill init time:** Maintainer edits files in `references/schemas/` (SoT). When model IDs change, update the `model` field in `models.md` + `agent-worker.template.toml`.
2. **Step 1 of orchestrator (runtime):** Synchronizes 9 files to `_workspace/_schemas/` and deploys `state.py` to `_workspace/state.py`.
3. **Agent creation (Phase 3):** Main reads `_workspace/_schemas/agent-worker.template.toml`, performs variable substitution, and writes to `.codex/agents/{name}.toml`.
4. **Worker write time:** worker reads `_workspace/_schemas/task.schema.json` before producing `task_*.json`.
5. **Main validation time:** main reads `_schemas/*.schema.json` and validates `task_*.json` / `checkpoint.json`.
6. **State reads/writes:** orchestrator calls `python _workspace/state.py` instead of raw `cat`/`apply_patch` on state files to reduce token usage.

## Why duplicate into `_workspace/`?

- **Self-contained workspace:** Resume / handoff / forensic review only needs `_workspace/`.
- **Drift detection:** snapshots the schema version active at init.
- **Worker isolation:** workers access `_workspace/` only.
