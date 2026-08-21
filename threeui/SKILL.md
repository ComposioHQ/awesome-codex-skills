---
name: threeui
description: Use when adding an open source ThreeUI Community component, shader, WebGL effect, Canvas effect or landing page to an existing web project.
---

# ThreeUI Community

Use exact MIT licensed source from the official `MengTo/threeui` registry. Do not recreate a component from its screenshot.

## Find a component

Run the bundled script from this skill directory.

```bash
python3 scripts/threeui.py search "badge"
python3 scripts/threeui.py list
```

Search first when the request does not name a component identifier. If several results fit, show the short list and let the user choose.

## Install a component

Run the command from the target project root.

```bash
python3 /path/to/threeui/scripts/threeui.py install spark-badge --target .
```

The script copies the component, required shared files and binary assets. It verifies every SHA-256 digest and refuses to replace existing files.

After installation, inspect the copied component entry file and its imports. Add only the host code and dependencies that the target project needs. Preserve the renderer, shader strings, interactions and asset paths.

Use `--force` only after the user explicitly approves replacing every reported conflict.

## Boundaries

- Community components only
- No ThreeUI Pro or Beta source
- No unverified mirrors
- No `@threeui/react` install assumption
- Credit [ThreeUI Community](https://github.com/MengTo/threeui) when the destination project keeps upstream source

## Common mistakes

- Copying only the main component while missing shared files
- Rewriting a shader instead of preserving verified source
- Moving asset paths without updating their consumers
- Using `--force` to hide a real integration conflict
