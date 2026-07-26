---
description: Generate multiple visual directions from a base Stitch screen using the local starter toolkit.
---

# Workflow: Variants

## Steps

1. Identify the base screen.
- Prefer the latest generated screen unless the user specifies another one.

2. Turn the user's request into a variants prompt that clearly defines what should vary:
- layout
- color scheme
- imagery
- text tone
- typography

3. Run:

```bash
cd "${STITCH_STARTER_ROOT:-$HOME/.agents/stitch-starter}"
npm run variants -- --prompt "..." --variant-count 3
```

Optional:

```bash
--creative-range REFINE|EXPLORE|REIMAGINE
--aspects LAYOUT,COLOR_SCHEME,IMAGES,TEXT_FONT,TEXT_CONTENT
```

4. Review the saved variant folders and summarize:
- what changed in each direction
- which variant is strongest
- which one should be edited next

## Default behavior

- Default variant count: `3`
- Default creative range: `EXPLORE`
- If the user explicitly wants only small polish differences, use `REFINE`
