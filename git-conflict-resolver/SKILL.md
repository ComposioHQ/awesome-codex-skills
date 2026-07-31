---
name: git-conflict-resolver
description: Safe and systematic resolution of git merge conflicts with intent analysis, build verification, and clean resolution staging. Use when merge or rebase conflicts occur (<<<<<<<, =======, >>>>>>> markers).
---

# Git Conflict Resolver

Safely and systematically resolve git merge conflicts by analyzing branch intent, preserving valid changes, and verifying build integrity.

## Workflow

### 1. Identify Conflict Files
Run git status to list all unmerged paths:
```bash
git status --porcelain | grep "^UU\|^AA\|^DD"
```

### 2. Inspect Conflict Context
For each conflicted file:
- Examine conflict markers (`<<<<<<< HEAD`, `=======`, `>>>>>>> incoming`).
- View recent commit history on both branches to understand the intent of each change:
  ```bash
  git log -n 5 --oneline HEAD -- <file>
  git log -n 5 --oneline MERGE_HEAD -- <file>
  ```

### 3. Resolve Conflicts
- **Do not guess or discard changes blindly.**
- Combine non-overlapping logic where both HEAD and incoming additions are required.
- Remove all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
- Ensure consistent code style, import statements, and function signatures.

### 4. Verify Resolution
- Run linters or type checks:
  ```bash
  npm run lint # or equivalent linter for the codebase
  ```
- Run relevant unit tests to verify no regressions were introduced during resolution:
  ```bash
  npm test # or equivalent test runner
  ```

### 5. Stage Resolved Files
Once verification succeeds, stage the resolved files:
```bash
git add <file>
```
