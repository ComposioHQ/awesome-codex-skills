---
name: scope-checkpoint
description: Pause and re-scope implementation when a task starts expanding beyond the requested PR boundary. Use when review feedback, failing tests, compatibility work, or adjacent discoveries could pull implementation into extra product surfaces, broad cleanup, architectural hardening, or follow-up slices. Especially useful during Ship runs or long-running implementation sessions.
---

# Scope Checkpoint

## Overview

Use this skill as a circuit breaker, not a standing implementation philosophy.
Its job is to keep the current PR honest and bounded when new work appears
during implementation.

## Checkpoint

When scope starts expanding, stop and write a short checkpoint before changing
more code:

- Original requested outcome
- Current PR boundary
- New issue or surface discovered
- Classification
- Decision

Keep the checkpoint brief. Its purpose is to prevent accidental scope expansion,
not to create another plan.

## Classification

Classify each discovered issue before acting:

1. **Current-PR Blocker**
   Blocks the requested outcome, breaks touched behavior, creates a regression
   from this change, or invalidates required verification. Fix it now.

2. **Required Compatibility**
   Existing tests, callers, fixtures, or workflows are legitimate and must be
   updated for the new contract to pass honestly. Fix it now, but keep the work
   tied to the current PR boundary.

3. **Follow-Up**
   Real issue, but not required for this PR to be correct and verifiable. Record
   it clearly and do not implement it in this PR.

4. **Speculative**
   Future-proofing, cleanup, abstraction, broad hardening, or convenience work
   without evidence that it is needed for this PR. Do not implement it.

## Decision Rules

- Do not let a real but non-blocking issue redefine the task.
- Do not broaden a PR from one product slice into API, export, UI, reset,
  acceptance, release, or backfill work unless the user explicitly expands the
  boundary.
- Do not use this skill to ignore failed verification. If a failure invalidates
  the current PR, fix the smallest necessary surface.
- Do not weaken verification, review, security, merge, or closeout gates. Scope
  control limits new product/code scope; it does not bypass evidence needed to
  prove the current PR honestly.
- If the classification changes the product boundary or the safe PR boundary is
  unclear, ask the user for the boundary rather than continuing to expand.

## Output Shape

Use this shape when reporting the checkpoint:

```md
Scope checkpoint:
- Original outcome:
- Current PR boundary:
- New issue:
- Classification:
- Decision:
```

Example:

```md
Scope checkpoint:
- Original outcome: ship the core Ledger workflow slice.
- Current PR boundary: transaction IDs, Receiving, Checking, Withdraw, Settle.
- New issue: admin Ledger export still needs the new Transaction ID field.
- Classification: Follow-Up.
- Decision: record a follow-up; do not add export work to this PR.
```
