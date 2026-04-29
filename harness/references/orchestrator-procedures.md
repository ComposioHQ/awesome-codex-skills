# Orchestrator Procedures & Principles

Common error handling procedures, validation principles, and description writing guidelines applied when authoring orchestrator skills.
Used alongside the Step 0~5 pseudocode in `orchestrator-template.md`.

## Error Handling and Self-Healing

> **Canonical spec.** References to retry, Blocked, and user confirmation requests in other files (qa-agent-guide, agent-design-patterns, etc.) defer to this decision tree.

### Error Response Decision Tree (pseudocode)

```
PROCEDURE handle_error(agent, task, error_type):

    // ── Immediate user confirmation (no retry) ────────────────────────────
    IF error_type == "ambiguous_input" OR error_type == "missing_params":
        CALL request_user_input("Ambiguous input or missing parameters: {details}")
        RETURN

    IF error_type == "majority_failure":        // Majority of agents failed
        apply_patch "_workspace/tasks.md" ← record interruption point
        CALL request_user_input("Majority failure. Requesting confirmation to proceed.")
        RETURN

    // ── Automatic recovery (resume from Step 0) ───────────────────────────
    IF error_type == "timeout" OR error_type == "session_restart":
        // Re-running Step 0 detects checkpoint.json → resumes automatically
        // ※ Idempotency required: each agent must first check whether output files exist
        //   and skip already-completed work. Results must be identical regardless of how
        //   many times resumption occurs.
        GOTO Step 0
        RETURN

    // ── Data conflict ─────────────────────────────────────────────────────
    IF error_type == "data_conflict":
        RECORD findings.md ← "[Data Conflict]" section with source attribution
        @reviewer call (conflict_resolution_prompt)
        IF reviewer resolves conflict:
            RETURN
        ELSE:
            CALL request_user_input("Data conflict unresolved: {details}")
            RETURN

    // ── Retriable failure ─────────────────────────────────────────────────
    // Applies to: agent_failure | reviewer_reject | context_limit_exceeded
    // Applies to: handoff_no_candidate (no handoff target found)
    IF task.retries < 2:                        // fewer than 3 total attempts
        task.retries += 1
        RECORD findings.md ← "Retry {task.retries}/2: {error cause} → approach changed"
        @agent call (modified_prompt_with_feedback)
        RETURN

    // ── 3 attempts exhausted → Blocked protocol ───────────────────────────
    GOTO blocked_protocol

// ── Blocked Protocol (common) ─────────────────────────────────────────────
PROCEDURE blocked_protocol(agent, task):
    apply_patch "_workspace/tasks/task_{agent}_{id}.json":
        status  ← "blocked"
        result  ← null
        retries ← task.retries   // preserve final value
    RECORD findings.md ← "Final rejection: {reason} | Attempt history: {history}"
    // Advancing Step or Stage is strictly prohibited
    DO NOT UPDATE checkpoint.json  // Separation of concerns: blocked_protocol records to task file only.
                                   // The pre-blocked check in Step 2 detects the task file on the next
                                   // cycle entry and updates checkpoint to blocked. Direct update by
                                   // blocked_protocol would cause a duplicate update.
    CALL request_user_input("Blocked: @{agent} — {reason}. Requesting intervention.")
    HALT    // Arbitrary Skip or Done is strictly prohibited

// ── Special case: Handoff cycle detection ────────────────────────────────
// (Prevents A→B→A infinite loops. call_history = handoff_chain field in checkpoint.json)
PROCEDURE handle_handoff(next_agent):
    READ "_workspace/checkpoint.json" → ckpt
    call_history ← ckpt.handoff_chain ?? []     // empty array if absent

    IF next_agent IN call_history:
        RECORD findings.md ← "Circular handoff: {call_history} → {next_agent}"
        CALL request_user_input("Circular handoff detected: {path}. Requesting intervention.")
        HALT

    IF LENGTH(call_history) >= 3:               // more than 3 steps
        RECORD findings.md ← "Handoff exceeded 3 steps: {call_history}"
        CALL request_user_input("Handoff exceeded 3 steps. Requesting intervention.")
        HALT

    // Safe → update history then call
    apply_patch "_workspace/checkpoint.json":
        ckpt.handoff_chain ← APPEND(call_history, next_agent)
        ckpt.last_updated  ← NOW()
    @next_agent call (...)

// Reset handoff_chain on every Step transition
// (Reset handoff_chain: [] when updating checkpoint.json)
```

## Test Scenarios

> Full normal flow / resume flow / error flow scenarios: `references/skill-testing-guide.md` § **Orchestrator Test Scenarios** (3 types: normal flow / resume flow / error flow).

## Follow-up Action Keywords for description (Required)

An orchestrator description that contains **only initial trigger keywords is insufficient**. The following follow-up action expressions must be included, or the harness becomes effectively dead code after its first run.

- re-run / run again / update / modify / refine
- "only {part} of {domain} again", "based on previous results", "improve results"
- Domain-specific everyday expressions (e.g., for a launch strategy harness: "launch", "promotion", "trending", etc.)

If follow-up keywords are missing from `description`, the Codex CLI trigger router will stop selecting this skill from the second call onward.

## Writing and Execution Principles

1. **Emphasize the intermediary role:** The main agent does not merely invoke tools — it analyzes results and **enriches the input (context) for the next agent**.
2. **Persistence first:** Update files immediately after every major state change to guard against unexpected termination.
3. **Atomic state consolidation:** The orchestrator collects and merges split work files produced by parallel agents, preventing write conflicts at the source.
4. **Strict SandBox Mode isolation:** Do not assign tasks to agents that exceed their defined `sandbox_mode` scope.
5. **Ensure visibility:** All intermediate steps must be recorded to files via `findings.md` and `tasks.md`.
6. **Declare Step dependencies:** Declare dependencies through the Step order and exit conditions in workflow.md. The structure of Step N complete → enter Step N+1 must be clearly expressed in workflow.md.
7. **Realistic error assumptions:** Do not assume "everything succeeds." Include a rule that prohibits Stage advancement when a Step is Blocked.
8. **Test scenarios required:** Include at least 1 normal + 1 resume + 1 error scenario in the skill body. Without all three, Step 5 validation cannot pass.

## Stage/Step Transition Protocol

> Full details of the Step execution loop, Stage transition gate, and entry/exit control logic in Step 2:
> See **`references/stage-step-guide.md`**.
