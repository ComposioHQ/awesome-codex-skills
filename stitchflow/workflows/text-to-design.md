---
description: Generate a new Stitch screen from a brief using the local starter toolkit.
---

# Workflow: Text-to-Design

## Steps

1. Read the user's brief and, if relevant, inspect the current project for style, layout, and component patterns.
2. Rewrite the brief into a structured Stitch prompt using [prompt-keywords](../references/prompt-keywords.md).
3. If the user named a Stitch project, use it. Otherwise create or reuse a suitable project by calling:

```bash
cd "${STITCH_STARTER_ROOT:-$HOME/.agents/stitch-starter}"
npm run list
```

4. Generate the screen:

```bash
cd "${STITCH_STARTER_ROOT:-$HOME/.agents/stitch-starter}"
npm run generate -- --prompt "..." [--project-id ...] [--device DESKTOP]
```

5. Read the output folder path from the command result and report back:
- project id
- screen id
- saved folder
- whether HTML and screenshot were downloaded

## Default behavior

- Default device: `DESKTOP`
- If the user wants exploration, follow generation with the [variants](variants.md) workflow
- If the layout is basically right but polish is off, use [edit-design](edit-design.md) instead of regenerating
