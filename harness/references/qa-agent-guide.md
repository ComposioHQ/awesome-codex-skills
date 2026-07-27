# QA Agent Design Guide

A guide for including a QA agent in a build harness. Based on bug patterns and root cause analyses discovered in real projects, this guide provides a verification methodology that systematically catches defects that QA tends to miss. This guide assumes a **Codex CLI orchestration environment** (no direct communication between sub-agents; the main agent acts as Data Broker).

---

## Table of Contents

1. Defect Patterns QA Agents Miss
2. Integration Coherence Verification
3. QA Agent Design Principles (Orchestration Mode)
4. Verification Result Reporting Protocol (JSON Protocol)
5. Verification Checklist Template
6. QA Agent Definition Template
7. Appendix: Lessons Learned from Real Cases

---

## 1. Defect Patterns QA Agents Miss

### 1-1. Boundary Mismatch

The most frequent defect. Two components are each implemented "correctly," but the contract breaks at the connection point.

| Boundary | Mismatch Example | Why It Gets Missed |
|---|---|---|
| API response → front-end hook | API returns `{ projects: [...] }`, hook expects `SlideProject[]` | Each is validated independently; no cross-comparison |
| API response field name → type definition | API uses `thumbnailUrl` (camelCase), type uses `thumbnail_url` (snake_case) | TypeScript generic casting causes the compiler to miss it |
| File path → link href | Page is at `/dashboard/create` but link points to `/create` | File structure and href are not cross-compared |
| State transition map → actual status update | Map defines `generating_template → template_approved`, but the transition is missing from code | Only checks that the map exists, does not trace the update code |
| API endpoint → front-end hook | API exists but has no corresponding hook (never called) | API list and hook list are not mapped 1:1 |
| Immediate response → async result | API immediately returns `{ status }`, front end accesses `data.failedIndices` | Only checks types without distinguishing sync/async responses |

### 1-2. Why Static Code Review Misses These

- **Limits of TypeScript generics:** `fetchJson<SlideProject[]>()` — even if the runtime response is `{ projects: [...] }`, compilation passes.
- **`npm run build` passing ≠ correct behavior:** With type casting, `any`, or generics, the build can succeed while the runtime fails.
- **Existence verification vs. connection verification:** "Does the API exist?" and "Does the API response match the caller's expectations?" are completely different verifications.
- **One-sided code review:** If the reviewer reads only the producer or only the consumer, a contract mismatch will never be visible.

---

## 2. Integration Coherence Verification

**Cross-comparison verification** areas that must be included in the QA agent.

### 2-1. API Response ↔ Front-End Hook Type Cross-Verification

**Method:** Compare the `NextResponse.json()` call site in each API route with the `fetchJson<T>` type parameter of the corresponding hook.

```
Verification steps:
1. Extract the shape of the object passed to NextResponse.json() in the API route
2. Check the T type of fetchJson<T> in the corresponding hook
3. Compare whether shape and T match
4. Check for wrapping (if API returns { data: [...] }, does the hook unwrap .data?)
```

**Patterns to watch especially:**
- Pagination API `{ items: [], total, page }` vs. front end expecting an array
- Mismatch between snake_case DB fields → camelCase API response → front-end type definitions
- Shape difference between immediate response (202 Accepted) vs. final result

### 2-2. File Path ↔ Link/Router Path Mapping

**Method:** Extract URL paths from page files under `src/app/` and compare against all `href`, `router.push()`, and `redirect()` values in the code.

```
Verification steps:
1. Extract URL patterns from page.tsx file paths under src/app/
   - (group) → removed from URL
   - [param] → dynamic segment
2. Collect all href=, router.push(, redirect( values in the code
3. Verify each link matches an actual existing page path
4. Watch for URL prefix of pages inside route groups (e.g., dashboard/ prefix)
```

### 2-3. State Transition Completeness Tracking

**Method:** Extract all `status:` updates from the code and compare against the state transition map.

```
Verification steps:
1. Extract the list of allowed transitions from the state transition map (STATE_TRANSITIONS)
2. Search all API routes for .update({ status: "..." }) patterns
3. Verify each transition is defined in the map
4. Identify transitions defined in the map but never executed in code (dead transitions)
5. Check for missing transitions from intermediate states (e.g., generating_template) to final states (template_approved)
```

### 2-4. API Endpoint ↔ Front-End Hook 1:1 Mapping

**Method:** List all API routes and front-end hooks to verify they pair up correctly.

```
Verification steps:
1. Extract a list of HTTP method endpoints from route.ts files under src/app/api/
2. Extract a list of fetch call URLs from use*.ts files under src/hooks/
3. Identify API endpoints not called by any hook → flag as "unused"
4. Determine whether "unused" is intentional (e.g., admin API) or accidental (missing call)
```

---

## 3. QA Agent Design Principles (Orchestration Mode)

In the Codex CLI environment, direct communication between sub-agents is not possible, so the orchestrator (main agent) handles coordination.

### 3-1. "Provide Both Sides Simultaneously" Principle

For the QA agent to catch boundary bugs, the main agent must **provide context from both sides** when making the call.

- **Method:** Use shell `cat` to read both the API route and the front-end hook, and specify both paths explicitly in the QA agent prompt.
- **Agent instruction:** Include "You must open both specified files and cross-compare them" in the system prompt.

### 3-2. Grant Execution Permissions, Not Just Read Access

Effective QA goes beyond simply reading files — it requires using shell `grep` to search for patterns and actually running test, lint, and type-check scripts via the shell. The QA agent should be set to `sandbox_mode = "workspace-write"` or higher to obtain shell execution permissions.

**Run long-running processes in the background.** In Codex CLI, background shell execution uses `&` (e.g., `npm run dev &`). Processes that do not terminate — such as dev servers, build watchers, and test daemons — should be launched in the background, and follow-up verifications such as `curl`, Playwright, or API tests should be run in the foreground within the same turn. This avoids foreground blocking while keeping the E2E/integration QA flow uninterrupted.

| Purpose | Execution Mode | Example |
|---|---|---|
| Lint, type check, unit tests | **Foreground** (results needed immediately) | `npm run lint`, `tsc --noEmit`, `pytest` |
| Dev server, API server | **Background** | `npm run dev &`, `python -m uvicorn app:app &` |
| Build watcher, file watcher | **Background** | `vite build --watch &`, `jest --watch &` |
| E2E verification after starting the above servers | Background + Foreground combination | Background dev server, foreground `curl`/Playwright |

Note: If the QA agent launched a background process, it must be terminated when done (`kill $PID` or `pkill`) and recorded in the "Cleanup" section of `qa_report.md` to avoid affecting the next QA invocation.

### 3-3. Prioritize "Cross-Comparison" Over "Existence Check" in Checklists

| Weak Checklist | Strong Checklist |
|---|---|
| Does the API endpoint exist? | Does the API endpoint's response shape match the corresponding hook's type? |
| Is the state transition map defined? | Does every status update in code match a transition in the map? |
| Does the page file exist? | Does every link in the code point to an actually existing page? |
| Is TypeScript strict mode on? | Is there no type safety bypassed via generic casting? |

### 3-4. Incremental QA

Do not verify everything in a single pass after full completion. Call the QA agent immediately after each module (producer + consumer) is complete to keep the feedback loop short.

- If the orchestrator places QA only at Step 4 (after full completion), bugs accumulate and early boundary mismatches propagate to subsequent modules.
- **Recommended pattern:** Run cross-verification of each backend API and its corresponding hook immediately after the API is complete.

### 3-5. Report First; Fixes Are Triggered by Orchestrator Re-invocation

In Codex CLI, the QA agent cannot send instructions directly to other agents. Discovered bugs are recorded in `_workspace/qa_report.md`, and **verification results (PASS/FAIL) are recorded in the split task file (`_workspace/tasks/task_{agent}_{id}.json`) to maintain coherence with the orchestrator**. The main agent reads this report and the split file, summarizes findings in `findings.md`, and then re-invokes the implementation agent if needed.

---

## 4. Verification Result Reporting Protocol (JSON Protocol)

The QA agent must produce split task files in the following format to ensure data coherence in a parallel execution environment.

- **File path:** `_workspace/tasks/task_{agent_name}_{task_id}.json`
- **Reporting schema:**
    ```json
    {
      "agent": "@qa-inspector",
      "task_id": "T101",
      "status": "done",        // "done" | "blocked" — base schema field
      "retries": 0,            // cumulative retry count. switch to blocked when retries ≥ 2 (0·1 allowed = 3 total attempts)
      "evidence": "E2E test passed. Logs saved at _workspace/qa/log.txt",
      "artifact_path": "_workspace/qa_report.md",  // follow base schema field name
      "result": "PASS"         // QA-only extension field. "PASS" | "FAIL" | null (when Blocked)
    }
    ```

> **Canonical schema:** For the normative definitions of the `agent·task_id·status·retries·evidence·artifact_path` fields, refer to `references/orchestrator-template.md` § "Split Task File Protocol". The schema above is an application example from the QA agent's perspective; only `result` is a QA-only extension field.

### Zero-Tolerance Retry Protocol

> **The canonical source is `references/orchestrator-procedures.md` — "Error Handling Decision Tree".** The following is an application summary from the QA agent's perspective.

The QA agent does not arbitrarily skip or ignore results on verification failure. Adhere strictly to the following procedure:

1. **Up to 2 retries (3 total):** Identify the cause of failure, change the approach, and retry. Increment `retries` with each retry.
2. **Still failing after 3 attempts → `blocked`:** Record `status: "blocked"`, `result: null`. Document the failure cause, attempt history, and required information in detail in the "Blocked Items" section of `qa_report.md`.
3. **Orchestrator escalation:** When the main agent detects `Blocked`, record `status: "blocked"` in `checkpoint.json` and request user confirmation. **Arbitrary skipping is strictly prohibited.** On restart, Step 0 detects the blocked state → displays the reason → waits for instructions.

---

## 5. Verification Checklist Template

A general integration coherence checklist to include in QA agent definitions. The key is to **read both components sharing a boundary simultaneously** and cross-compare for contract compliance. Select only the relevant sections based on the domain.

```markdown
### Integration Coherence Verification

#### Boundary Contract (Common to All Domains)
- [ ] Producer output type/format matches Consumer input expectations
- [ ] Shared constants/enum values are defined identically on both sides
- [ ] Null/undefined handling of optional fields is consistent on both sides
- [ ] Async vs. immediate response formats are clearly distinguished on the consumer side

#### Reference Integrity (Common to All Domains)
- [ ] All paths, identifiers, and links in the code point to actually existing targets
- [ ] Dynamic parameters/slots are filled with correct values

#### State Transition Completeness (When a State Machine Exists)
- [ ] All defined state transitions are executed in code (no dead transitions)
- [ ] All state change code matches transition definitions (no unauthorized transitions)
- [ ] No missing transitions from intermediate states to final states

#### Data Flow Coherence (Common to All Domains)
- [ ] Field names and types from sources (DB, file, API) are consistent throughout the entire pipeline
- [ ] Data transformations (type, case, unit) are handled explicitly

---

#### [Web App] API ↔ Frontend Connection
- [ ] Response shape of every API route matches the generic type of the corresponding hook
- [ ] Wrapped responses ({ items: [...] }) are unwrapped in the hook
- [ ] snake_case ↔ camelCase conversion is applied consistently
- [ ] Immediate response (202) and final result shape are distinguished on the front end
- [ ] Every API endpoint has a corresponding front-end hook that is actually called

#### [Web App] Routing Coherence
- [ ] All href/router.push values in code match actual page file paths
- [ ] Path validation accounts for route groups ((group)) being removed from the URL
- [ ] Dynamic segments ([id]) are filled with correct parameters
```

---

## 6. QA Agent Definition Template

Follows the official Codex CLI sub-agent format.

```toml
name = "qa-inspector"
description = "QA verification specialist. Verifies spec compliance, boundary integration coherence, and artifact quality. Always select this agent for quality review, bug inspection, and coherence verification requests."
model = "gpt-5.3-codex"
sandbox_mode = "workspace-write"
model_reasoning_effort = "high"

developer_instructions = """
# QA Inspector

## Core Role
Verify artifact quality against specs and **inter-module integration coherence**. Regardless of domain, the core is to read both components sharing a boundary simultaneously and cross-compare for contract compliance.

## Verification Priority

1. **Integration Coherence** (highest) — Boundary mismatches are the primary cause of runtime errors
2. **Functional Spec Compliance** — Contracts, state machines, data models
3. **Artifact Quality** — Format, completeness, readability (apply domain-specific standards)
4. **Internal Consistency** — Unused references, naming conventions, duplication

## Verification Method: "Read Both Sides Simultaneously"

Boundary verification must be done by **opening both the producer and the consumer at the same time** and comparing them.

| Verification Target | Producer (Left) | Consumer (Right) |
|---|---|---|
| Data contract | Output format/type definition | Input expectations/parsing logic |
| Path/reference | Defined paths, identifiers, links | Paths/identifiers used by the caller |
| State transition | Transition map/definition | Actual state change code |
| Data flow | Field names/types from source (DB, file, API) | Field names/types at downstream consumers |

> **Web app example:** `route.ts` NextResponse → `fetchJson<T>` hook / `src/app/` page path → `href` value / `STATE_TRANSITIONS` map → `.update({ status })` code

## Collaboration Protocol (Orchestration)

1. Record verification artifacts in `_workspace/qa_report.md`.
2. In the **"Fix Instructions"** section, specify discovered bugs concisely as `file:line + fix method`.
3. For boundary issues, list both the producer and consumer paths in the report so both agents can rework if needed.
4. The main agent (orchestrator) reads this report, summarizes findings in `findings.md`, and re-invokes the implementation agent if needed.
5. For ambiguous contracts (e.g., "Is this field optional?"), do not guess — confirm by requesting user input.
"""
```

---

## 7. Appendix: Lessons Learned from Real Cases

All content in this guide is drawn from lessons extracted from the actual bugs below.

| Bug | Boundary | Cause |
|---|---|---|
| `projects?.filter is not a function` | API → hook | API returns `{ projects: [] }`, hook expects an array |
| All dashboard links return 404 | File path → href | Missing `/dashboard/` prefix |
| Theme image not displayed | API → component | `thumbnailUrl` vs. `thumbnail_url` |
| Theme selection not saved | API → hook | select-theme API exists, but no corresponding hook |
| Create page waits forever | State transition → code | Missing `template_approved` transition code |
| `data.failedIndices` crash | Immediate response → front end | Accessing background result from the immediate response |
| 404 after completion viewing slides | File path → href | `/projects/` → `/dashboard/projects/` |

The common thread across all these bugs is that **each side looks correct on its own, but the issue only appears when both sides are examined together**. Therefore, the first principle of QA agent design is "read both sides simultaneously."
