---
name: codex-pet-generator
description: Generate Codex desktop pet packages from one or more reference images. Use when a user wants a pet, mascot, or character reference turned into a folder named myPet containing a transparent 1536x1872 WebP spritesheet named spritesheet.webp plus pet.json metadata, with an 8x9 grid, 192x208 centered cells, and rows for idle, run right, run left, waving, jumping, failed, waiting, running, and review animations.
---

# Codex Pet Generator

## Output Contract

Create a final folder named `myPet` unless the user names another destination.
The folder must contain:

- `spritesheet.webp`
- `pet.json`

Optional debug output may include `spritesheet.png` when `--png` is used.

The final image must be:

- `1536x1872`
- transparent background
- `8` columns by `9` rows
- `192x208` per cell
- at most `8` frames per row
- one complete pet/mascot frame per cell
- centered consistently inside each cell
- consistent visual pet size across all rows/states; no state row should suddenly look much smaller or larger than the others

Rows from top to bottom:

1. `idle`
2. `run right` - the character should face/move toward screen right
3. `run left` - must be the horizontal mirror of row 2 by default
4. `waving`
5. `jumping`
6. `failed`
7. `waiting`
8. `running`
9. `review`

Direction is strict: do not swap rows 2 and 3. If the image generator outputs
them reversed, keep row 2 as the desired right-facing run source and let the
build script mirror row 2 into row 3.

`pet.json` must use this schema:

```json
{
  "id": "xxx-xxx",
  "displayName": "xxxxxx",
  "description": "xxxxx.",
  "spritesheetPath": "spritesheet.webp",
  "kind": "animal/person"
}
```

Infer `id`, `displayName`, `description`, and `kind` from the user's reference
image. Use `kind: "animal"` for animals, creatures, mascots, and non-human pets;
use `kind: "person"` for human or humanoid character pets. Do not change
`spritesheetPath`; it must always be exactly `"spritesheet.webp"`.

## Workflow

1. Use the `imagegen` skill or built-in image generation tool to create a green-screen source sheet from the user's reference image.
2. Save the generated source PNG in the working directory, for example `spritesheet-source.png`.
3. Infer `pet.json` metadata from the reference image.
4. Run `scripts/build_spritesheet.py` from this skill to remove the green background, normalize the sheet, and write the pet package.
5. Inspect the final WebP, a bottom-row crop, and the script's `body_width_range` / `body_height_range` metrics before finishing.
6. If any frame is clipped, visibly off-center, or a state row still looks much smaller/larger than the others, regenerate the source with stronger padding and consistent-scale requirements, then rerun the script.

## Generation Prompt Pattern

Use this prompt shape with the user's reference image:

```text
Use the uploaded reference image as broad character reference. Create a new original cute desktop pet mascot sprite sheet, not an exact copy of any existing copyrighted character unless the user owns it or explicitly supplied it as their own asset.

Create a single sprite sheet on a perfectly flat solid #00ff00 chroma-key background for background removal.

Sprite sheet layout: exactly 8 columns by 9 rows. Each cell contains one complete full-body mascot sprite, fully visible and centered, with very generous padding. Keep at least 20% empty green margin above the top of the character, below the feet, left, and right in every cell. Keep the character's main body at the same visual size in every row/state; do not draw idle tiny, running large, jumping tiny, or review/failed at a different scale. No sprite, ear, hair, foot, tail, motion line, prop, puff, or effect may touch or approach the cell edge. No grid lines, no labels, no text, no watermark, no extra characters, no shadows, no floor.

Rows from top to bottom, 8 frames per row:
1. idle: subtle breathing/standing frames.
2. run right: running toward screen right, right-facing/right-moving, 8-frame loop, fully contained. This is the authoritative run source.
3. run left: running toward screen left, left-facing/left-moving, 8-frame loop, fully contained. The build script will replace this row with a horizontal mirror of row 2 unless explicitly disabled.
4. waving: standing and waving one paw/hand, 8-frame loop.
5. jumping: crouch, lift, airborne, landing, 8-frame loop, fully contained.
6. failed: disappointed/failure reaction, drooping or dizzy expression, 8 frames.
7. waiting: waiting/thinking, small fidget, 8-frame loop.
8. running: energetic run loop, 8 frames, fully contained.
9. review: inspecting/reviewing a small checklist or magnifier-like cue, 8 frames, fully contained.

Style constraints: simple cute desktop pet mascot, clean outline, transparent-ready cutout, consistent scale across frames and across all 9 animation rows, no typography, no UI, no complex background, no gradients, no texture. The background must be exactly one uniform #00ff00 and #00ff00 must not appear inside the character or props.
```

If the generated bottom rows are clipped or too close to the row boundary, regenerate only rows 8 and 9 as an `8x2` green-screen source with the same padding language, then merge manually or rerun the script on a complete regenerated sheet.

## Build Script

Run:

```bash
python ~/.codex/skills/codex-pet-generator/scripts/build_spritesheet.py \
  --source spritesheet-source.png \
  --out-dir myPet \
  --pet-id yellow-rabbit \
  --display-name "Yellow Rabbit" \
  --description "A cheerful yellow rabbit Codex pet." \
  --kind animal \
  --png
```

The script:

- removes a green chroma-key background using border color sampling
- detects row gaps and frame groups from alpha projection/connected components
- crops each frame independently
- centers the main mascot component at the center of its `192x208` cell
- normalizes each animation row toward the same median main-body size by default, preventing state-to-state size jumps
- keeps props/effects inside the same cell when they fall within that frame group
- mirrors row 3 from row 2 by default, so row 2 is always `run right` and row 3 is always `run left`
- writes `spritesheet.webp` and `pet.json` into the output folder
- writes `spritesheet.png` only when `--png` is passed
- prints validation metrics including row scales, body width/height range, edge hits, and center error

The default `--scale-mode normalized` keeps row/state size consistent. Use
`--scale-mode fit-row` only when intentionally preserving the older behavior
where each row is independently enlarged to its maximum safe size.

Do not use `--no-mirror-run-left` for normal Codex pet generation. It exists only
for rare cases where the user explicitly wants to preserve a hand-authored row
3 that has already been verified as `run left`.

If metadata flags are omitted, the script writes a conservative default:
`id: "my-pet"`, `displayName: "My Pet"`, `description: "A custom Codex pet generated from a reference image."`, and `kind: "animal"`.

## Validation

Before answering:

- Confirm `spritesheet.webp` exists.
- Confirm `pet.json` exists in the same folder.
- Confirm `pet.json.spritesheetPath` is exactly `"spritesheet.webp"`.
- Confirm dimensions are exactly `1536x1872`.
- Confirm alpha extrema include `0` and `255`.
- Confirm script output reports `edge_hits 0`.
- Confirm `body_width_range` and `body_height_range` do not show a large spread, and visually check that no state row suddenly changes pet size.
- Open or render a preview of the full sheet.
- Verify row 2 is `run right` and row 3 is `run left`; if in doubt, rerun the script without `--no-mirror-run-left`.
- Also inspect rows 8 and 9; these are the most likely to be clipped.
