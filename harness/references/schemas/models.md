# OpenAI Model ID Registry (SoT)

**Single authoritative source of model IDs** referenced by Codex agent templates. Updating only this file propagates changes to all templates.

## Model Assignment by Role

| Role Tier                                          | Model ID       | Notes                                                        |
| -------------------------------------------------- | -------------- | ------------------------------------------------------------ |
| Orchestrator, Architect (complex reasoning/design) | `gpt-5.5`      | 256K ctx, deep reasoning, research, multi-step planning      |
| Worker (Coder, Analyst, Reviewer, Operator)        | `gpt-5.5`      | 1M ctx, large codebase, refactoring, 80% SWE-Bench           |
| State Manager (dedicated CRUD)                     | `gpt-5.4-mini` | 400K ctx, fast and low-cost ($0.30/1M) — simple file read/write only |

> Warning: Hard-coding an incorrect model ID in an agent TOML will cause a runtime error.

## model_reasoning_effort Selection Criteria

| Value    | Suitable Agents         | Characteristics                                      |
| -------- | ----------------------- | ---------------------------------------------------- |
| `low`    | State Manager           | Simple CRUD, speed and cost priority                 |
| `medium` | Analyst, Researcher     | Research and documentation, sufficient reasoning     |
| `high`   | Coder, Reviewer, QA     | Complex implementation and debugging                 |
| `xhigh`  | Orchestrator, Architect | Multi-step agent reasoning and planning (highest cost) |

## Update Protocol

When a new model is released, update only this file:

1. Modify model IDs in the table above (add a new model row or replace an existing ID).
2. Apply the same change to the `model` field in `references/schemas/agent-worker.template.toml`.
3. All agents subsequently created by the harness will use the new ID.
4. **Existing generated agents require manual updates** (edit `.codex/agents/*.toml` directly).
