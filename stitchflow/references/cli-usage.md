# Local CLI Usage

All commands run from:

```bash
cd "${STITCH_STARTER_ROOT:-$HOME/.agents/stitch-starter}"
```

## List projects and screens

```bash
npm run list
```

Use this when you need to discover existing `projectId` and `screenId` values.

## Generate a new screen

```bash
npm run generate -- --prompt "..."
```

Optional flags:

- `--project-id 123456789`
- `--title "Project Name"`
- `--device DESKTOP|MOBILE|TABLET|AGNOSTIC`

## Edit a screen

If `latest-screen.json` exists, you can edit without ids:

```bash
npm run edit -- --prompt "..."
```

Or target a specific screen:

```bash
npm run edit -- --project-id 123 --screen-id abc --prompt "..."
```

## Generate variants

```bash
npm run variants -- --prompt "..." --variant-count 3
```

Useful options:

- `--creative-range REFINE|EXPLORE|REIMAGINE`
- `--aspects LAYOUT,COLOR_SCHEME,IMAGES,TEXT_FONT,TEXT_CONTENT`
- `--project-id 123 --screen-id abc`

## Output layout

Each run creates a folder under:

```text
${STITCH_STARTER_ROOT:-$HOME/.agents/stitch-starter}/runs/<timestamp>-<operation>-<slug>/
```

Typical artifacts:

- `result.json` or `variants.json`
- `screen.html`
- `screen.png` or `screen.jpeg`
- `html-url.txt`
- `image-url.txt`

The most recent single-screen result is tracked in:

```text
${STITCH_STARTER_ROOT:-$HOME/.agents/stitch-starter}/runs/latest-screen.json
```
