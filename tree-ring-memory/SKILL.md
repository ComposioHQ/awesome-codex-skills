---
name: tree-ring-memory
description: Use Tree Ring Memory for local-first AI-agent memory lifecycle work: project-scoped recall, explicit memory writes, evidence records, audit, forgetting, redaction, consolidation, and source-linked DOX/Revolve sync without storing raw transcripts.
metadata:
  short-description: Local-first memory lifecycle for AI agents
---

# Tree Ring Memory

Tree Ring Memory is a framework-agnostic memory lifecycle layer for AI agents.
Use it when Codex needs durable project memory without treating raw conversation
transcripts as memory.

The public runtime is a Rust CLI with SQLite/FTS storage, recall, audit,
forgetting, redaction, deterministic consolidation, JSONL import/export,
DOX/Revolve source adapters, framework discovery, and a Ratatui terminal TUI.

## When To Use

Use this skill before:

- resuming a repo where prior project memory may affect the task
- making architecture, storage, security, privacy, or release decisions
- repeating a workflow where prior failures may matter
- responding to a durable user preference or correction
- closing meaningful work and deciding what future agents should retain

Use it after:

- tests, review, production behavior, or an incident validated a lesson
- an approach failed and should not be repeated
- the user explicitly said something should be remembered
- a decision, warning, preference, or future follow-up should survive the session

## Discover The Local Setup

If the project has Tree Ring initialized, read the project-local guidance first:

```bash
.tree-ring/SKILL.md
.tree-ring/CLI.md
```

Then inspect the installed command surface:

```bash
tree-ring --help
tree-ring recall --help
tree-ring remember --help
tree-ring evidence --help
tree-ring audit --help
tree-ring forget --help
tree-ring maintain --help
```

If Tree Ring is not installed, use the project install paths:

```bash
brew tap TerminallyLazy/tree-ring
brew install tree-ring
```

or:

```bash
curl -fsSL https://raw.githubusercontent.com/TerminallyLazy/Tree-Ring-Memory/main/install.sh | sh
```

## Recall Workflow

Before risky or repeat work, query narrowly and keep scope local when possible:

```bash
tree-ring recall "release changes" --scope project
tree-ring recall "sqlite migration" --scope project
tree-ring recall "user preference" --scope global
```

Use recalled memory as context, not authority. Verify against source files,
tests, issues, PRs, docs, and current runtime state before acting.

## Write Workflow

Write concise memory only when it is likely to help future work:

```bash
tree-ring remember "Run project-scoped recall before release changes." --event-type lesson --scope project
```

Prefer specific event types when supported by the local CLI:

- `decision`
- `lesson`
- `warning`
- `correction`
- `user_preference`
- `tool_result`
- `summary`
- `hypothesis`

Store the durable lesson, decision, warning, or follow-up. Do not store the full
conversation.

## Evidence Workflow

Use evidence records for evaluated outcomes:

```bash
tree-ring evidence \
  --outcome observed \
  --summary "Installer smoke test passed in an isolated HOME." \
  --evidence-ref "ci/install-smoke/2026-07-07"
```

Outcome guidance:

- `promoted`: durable truth backed by strong evidence
- `rejected`: failed or rolled-back approach to keep visible as a scar
- `deferred`: future idea or unresolved option
- `observed`: normal evaluated result

Do not promote weak or unreviewed claims to durable truth.

## Source Adapter Workflow

Use dry runs before syncing structured project sources:

```bash
tree-ring dox sync --source-root . --dry-run
tree-ring revolve sync --source-root revolve --dry-run
tree-ring integrations scan --source-root .
```

Only write adapter summaries when they are concise, useful, and source-linked.
Imported memory does not replace `AGENTS.md`, Revolve records, tests, issues,
PRs, or docs.

## Rings

Use the smallest durable ring that fits:

- `cambium`: active or recent task context
- `outer`: recent decisions and task lessons
- `inner`: older compressed project knowledge
- `heartwood`: durable high-confidence truths
- `scar`: failures, regressions, rejected approaches, warnings
- `seed`: unresolved ideas, hypotheses, follow-ups

Prefer `outer` or `seed` unless the user confirms durability or the evidence is
strong.

## Privacy And Forgetting

Never use Tree Ring Memory as a hidden recorder.

Do not store:

- secrets, credentials, tokens, private keys, or recovery codes
- raw chain-of-thought or private scratchpad content
- temporary notes with no future value
- unverified claims as durable truth
- sensitive personal data unless the user explicitly asks and retention is safe
- copyrighted source text beyond short allowed excerpts

If memory is wrong, private, stale, or superseded, use audit and forget flows:

```bash
tree-ring audit --stale-after-days 60
tree-ring forget --help
```

Redact when a safe summary is useful. Delete when it should not be retained.
Supersede when a newer decision replaces an older one.

## Closeout Habit

At the end of meaningful work, ask:

- What did we decide?
- What did we learn?
- What should future agents avoid repeating?
- Did the user state a durable preference?
- Is there a future seed worth revisiting?
- Is any memory sensitive and better left unstored?

Only write memories that will materially improve future work.

Project: https://github.com/TerminallyLazy/Tree-Ring-Memory
