---
description: Edit an existing Stitch screen through the local starter toolkit.
---

# Workflow: Edit-Design

## Steps

1. Identify the target screen.
- Prefer the latest screen if the user is iterating on the most recent result.
- Otherwise discover ids with:

```bash
cd "${STITCH_STARTER_ROOT:-$HOME/.agents/stitch-starter}"
npm run list
```

2. Rewrite the user request into a focused edit prompt.
Good edit prompts name:
- the section
- the component
- the visual change
- the intended effect

3. Run the edit command:

```bash
cd "${STITCH_STARTER_ROOT:-$HOME/.agents/stitch-starter}"
npm run edit -- --prompt "..."
```

Or target a specific screen:

```bash
cd "${STITCH_STARTER_ROOT:-$HOME/.agents/stitch-starter}"
npm run edit -- --project-id ... --screen-id ... --prompt "..."
```

4. Report:
- original or base screen id
- new screen id
- saved output folder
- whether the new direction is closer to the user's goal

## Best practice

- Keep each edit focused
- Prefer a few iterative edits over one overloaded prompt
- If the user wants multiple visual directions, switch to [variants](variants.md)
