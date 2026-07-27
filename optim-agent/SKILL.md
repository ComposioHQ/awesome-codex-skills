---
name: optim-agent
description: Use when the user wants to optimize configurable system parameters against a measurable scalar objective, especially for model training, inference, quantitative strategies, reinforcement learning, scientific workflows, or other expensive black-box evaluations where reading the project can improve trial selection.
---

# optim-agent

Act as the sampler inside any coding-agent session: Claude Code, Codex,
OpenCode/OpenClaw, or another agent that can read project files and run shell
commands. Read the project to understand parameter meaning and interactions,
propose one configuration, run the real evaluator, and record the result
through optim-agent's ask/tell API. Let the measured objective, not the agent's
intuition, decide what works.

## Load the workflow

Use this file as the operating guide for the active coding agent. In Codex, it
can be installed directly from GitHub:

```text
$skill-installer install https://github.com/Optim-Agent/optim-agent
```

In Claude Code, OpenCode/OpenClaw, or another coding-agent environment, place
this repository or `SKILL.md` in the agent-visible workspace and ask the agent
to follow the optim-agent workflow. The workflow does not depend on Codex-only
APIs; it needs file access, shell access, and Python.

Ensure the Python package is importable. Choose one source; do not install both:

```bash
# Stable release from PyPI
python -m pip install optim-agent

# Latest source from GitHub
python -m pip install "optim-agent @ git+https://github.com/Optim-Agent/optim-agent.git"
```

For a reproducible GitHub install, append `@<tag-or-commit>` after `.git`.

## Workflow

1. **Understand the system.** Read the evaluation entry point and every file
   that defines the target parameters. Record each parameter's type, legal
   range, semantics, interactions, and operational constraints.
2. **Define the experiment.** Confirm the scalar objective, `minimize` or
   `maximize`, trial budget, evaluation command, runtime/cost limit, and fixed
   workload or seed. For multiple metrics or hard constraints, agree on one
   scalar feasibility or penalty rule before running trials.
3. **Establish a baseline.** Evaluate the current/default configuration with the
   same command and environment used for every later trial.
4. **Initialize or resume.** Keep artifacts in the repository's ignored
   `.optim-agent-runs/` directory:

   ```bash
   if git rev-parse --git-dir >/dev/null 2>&1 && ! git check-ignore -q .optim-agent-runs/; then
     printf '/.optim-agent-runs/\n' >> "$(git rev-parse --git-path info/exclude)"
   fi
   ```

   ```python
   from pathlib import Path
   import optim_agent as oa

   run_dir = Path(".optim-agent-runs")
   run_dir.mkdir(exist_ok=True)
   study = oa.create_study(
       direction="minimize",
       storage=run_dir / "skill-study.json",
       seed=0,
   )
   print([(t.params, t.value, t.state) for t in study.trials])
   ```

5. **Run one informed trial.** Choose parameters from code understanding and all
   completed history, then use explicit ask/tell:

   ```python
   params = {"threshold": 0.72, "budget": 80}
   trial = study.ask(params)
   try:
       value = evaluate_system(**trial.params)
   except Exception:
       study.tell(trial, state="failed")
       raise
   else:
       study.tell(trial, value)
   ```

   For a deliberately stopped trial, report the latest valid intermediate
   metric first, then call `study.tell(trial, state="pruned")`.
6. **Select the next point.** Avoid accidental repeats, explore broadly before
   exploiting, respect bounds and constraints, and treat failed regions as
   evidence. If the evaluator is noisy, repeat promising configurations under
   the same workload before declaring a winner.
7. **Stop and report.** Stop at the approved budget or stopping condition.
   Report the baseline, best value and parameters, trial count, failed/pruned
   trials, convergence trend, and exact reproduction command.

## Recovery

JSON storage records a trial when `study.tell` runs. Before launching an
expensive external evaluation, save its parameters, command, and output path in
a per-trial directory under `.optim-agent-runs/`. After interruption, inspect
that output before rerunning: if a valid result exists, recreate the same point
with `study.ask(params)` and record it; otherwise rerun it deliberately.

Use SQLite storage (`skill-study.db`) only when the user explicitly wants
multiple processes. Sequential trials are the default because each proposal
should use the complete prior history.

## Rules

- Use ask/tell in skill mode; do not delegate proposal selection to
  `AgentSampler` when the session agent is meant to read and reason over code.
- Keep evaluation inputs and outputs isolated from production configuration.
- Never fabricate, infer, or manually improve an objective value.
- Record crashes as `failed`; record intentional early stops as `pruned`.
- Preserve the study and trial artifacts so the result is auditable and resumable.
- Do not tune secrets, credentials, or unbounded parameters.
