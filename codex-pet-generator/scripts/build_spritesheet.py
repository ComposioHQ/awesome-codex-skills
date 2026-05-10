#!/usr/bin/env python3
"""Build a centered transparent Codex pet spritesheet from a green-screen source.

Expected source: an 8x9 generated sprite sheet on a flat green chroma-key
background. Output folder: myPet by default, containing spritesheet.webp and
pet.json. The image is 1536x1872, transparent, 8 columns x 9 rows, 192x208 cells.
Row 2 is the authoritative run-right row; row 3 is generated as a horizontal
mirror of row 2 by default so run-left/run-right do not get swapped.
By default, each animation row is normalized toward the same main-body size so
state changes do not make the pet suddenly shrink or grow.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import median

from PIL import Image


COLS = 8
ROWS = 9
CELL_W = 192
CELL_H = 208
OUT_W = COLS * CELL_W
OUT_H = ROWS * CELL_H
DEFAULT_TARGET_BODY_W = 132.0
DEFAULT_TARGET_BODY_H = 156.0


@dataclass
class FrameSpec:
    content: Image.Image
    main_cx: float
    main_cy: float
    main_w: float
    main_h: float
    fit_limit: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Green-screen source PNG/WebP.")
    parser.add_argument("--out-dir", default="myPet", help="Output pet folder. Default: myPet.")
    parser.add_argument("--png", action="store_true", help="Also write a PNG copy.")
    parser.add_argument("--pet-id", default=None, help="pet.json id. Default: slugified display name or my-pet.")
    parser.add_argument("--display-name", default="My Pet", help="pet.json displayName.")
    parser.add_argument(
        "--description",
        default="A custom Codex pet generated from a reference image.",
        help="pet.json description.",
    )
    parser.add_argument("--kind", choices=["animal", "person"], default="animal", help="pet.json kind.")
    parser.add_argument(
        "--no-mirror-run-left",
        action="store_true",
        help="Keep source row 3 instead of mirroring row 2. Avoid for normal Codex pet generation.",
    )
    parser.add_argument("--transparent-threshold", type=float, default=12.0)
    parser.add_argument("--opaque-threshold", type=float, default=220.0)
    parser.add_argument("--component-threshold", type=int, default=250)
    parser.add_argument("--margin", type=int, default=18, help="Minimum cell margin for fitted content.")
    parser.add_argument(
        "--scale-mode",
        choices=["normalized", "fit-row"],
        default="normalized",
        help="normalized keeps body size consistent across rows; fit-row preserves the legacy per-row fit behavior.",
    )
    parser.add_argument(
        "--target-body-width",
        type=float,
        default=DEFAULT_TARGET_BODY_W,
        help="Target final median main-body width for each animation row.",
    )
    parser.add_argument(
        "--target-body-height",
        type=float,
        default=DEFAULT_TARGET_BODY_H,
        help="Target final median main-body height for each animation row.",
    )
    parser.add_argument("--max-scale", type=float, default=2.0, help="Maximum upscale factor.")
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "my-pet"


def border_key_color(im: Image.Image) -> tuple[int, int, int]:
    rgb = im.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    samples: list[tuple[int, int, int]] = []
    step = max(1, min(width, height) // 300)

    for x in range(0, width, step):
        samples.append(pixels[x, 0])
        samples.append(pixels[x, height - 1])
    for y in range(0, height, step):
        samples.append(pixels[0, y])
        samples.append(pixels[width - 1, y])

    # Group nearly-identical generated greens; then average the winning bucket.
    def bucket(color: tuple[int, int, int]) -> tuple[int, int, int]:
        return tuple((channel // 8) * 8 for channel in color)

    winner = Counter(bucket(color) for color in samples).most_common(1)[0][0]
    grouped = [color for color in samples if bucket(color) == winner]
    return tuple(round(sum(color[i] for color in grouped) / len(grouped)) for i in range(3))  # type: ignore[return-value]


def remove_chroma(
    im: Image.Image,
    transparent_threshold: float,
    opaque_threshold: float,
) -> Image.Image:
    rgba = im.convert("RGBA")
    key = border_key_color(rgba)
    out = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    src = rgba.load()
    dst = out.load()
    width, height = rgba.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = src[x, y]
            d = math.sqrt((r - key[0]) ** 2 + (g - key[1]) ** 2 + (b - key[2]) ** 2)
            if d <= transparent_threshold:
                alpha = 0
            elif d >= opaque_threshold:
                alpha = a
            else:
                t = (d - transparent_threshold) / max(1.0, opaque_threshold - transparent_threshold)
                alpha = round(a * t)

            if alpha:
                # Simple green despill for antialiased edges.
                max_rb = max(r, b)
                if g > max_rb:
                    g = round(max_rb + (g - max_rb) * 0.35)
            dst[x, y] = (r, g, b, alpha)

    print(f"key_color #{key[0]:02x}{key[1]:02x}{key[2]:02x}")
    return out


def alpha_bbox(region: Image.Image, threshold: int = 10) -> tuple[int, int, int, int] | None:
    alpha = region.getchannel("A")
    pix = alpha.load()
    width, height = region.size
    min_x, min_y, max_x, max_y = width, height, -1, -1
    for y in range(height):
        for x in range(width):
            if pix[x, y] > threshold:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if max_x < min_x:
        return None
    return (min_x, min_y, max_x + 1, max_y + 1)


def components_in_region(
    alpha: Image.Image,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    threshold: int = 10,
) -> list[dict[str, object]]:
    crop = alpha.crop((x0, y0, x1, y1))
    pix = crop.load()
    width, height = crop.size
    seen: set[tuple[int, int]] = set()
    output: list[dict[str, object]] = []

    for yy in range(height):
        for xx in range(width):
            if pix[xx, yy] <= threshold or (xx, yy) in seen:
                continue
            queue = [(xx, yy)]
            seen.add((xx, yy))
            area = 0
            min_x = max_x = xx
            min_y = max_y = yy
            sum_x = 0
            sum_y = 0
            for qx, qy in queue:
                area += 1
                sum_x += qx
                sum_y += qy
                min_x = min(min_x, qx)
                max_x = max(max_x, qx)
                min_y = min(min_y, qy)
                max_y = max(max_y, qy)
                for nx, ny in ((qx + 1, qy), (qx - 1, qy), (qx, qy + 1), (qx, qy - 1)):
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and pix[nx, ny] > threshold:
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            output.append(
                {
                    "area": area,
                    "bbox": (min_x + x0, min_y + y0, max_x + x0 + 1, max_y + y0 + 1),
                    "center": (sum_x / area + x0, sum_y / area + y0),
                }
            )
    return output


def row_breaks(im: Image.Image) -> list[int]:
    alpha = im.getchannel("A")
    pix = alpha.load()
    width, height = im.size
    counts = [sum(1 for x in range(width) if pix[x, y] > 10) for y in range(height)]
    breaks = [0]
    for i in range(1, ROWS):
        expected = round(i * height / ROWS)
        band = max(30, round(height / ROWS * 0.3))
        lo = max(0, expected - band)
        hi = min(height, expected + band)
        breaks.append(min(range(lo, hi), key=lambda y: counts[y]))
    breaks.append(height)
    return breaks


def extract_frame_specs(im: Image.Image, component_threshold: int, margin: int) -> list[list[FrameSpec]]:
    alpha = im.getchannel("A")
    width, _ = im.size
    breaks = row_breaks(im)
    rows: list[list[FrameSpec]] = []

    for row_index in range(ROWS):
        y0, y1 = breaks[row_index], breaks[row_index + 1]
        comps = [c for c in components_in_region(alpha, 0, y0, width, y1) if int(c["area"]) > component_threshold]
        mains = sorted(comps, key=lambda c: int(c["area"]), reverse=True)[:COLS]
        mains = sorted(mains, key=lambda c: c["center"][0])  # type: ignore[index]
        if len(mains) != COLS:
            raise RuntimeError(f"row {row_index + 1}: expected {COLS} main components, found {len(mains)}")

        centers = [c["center"][0] for c in mains]  # type: ignore[index]
        bounds = [0] + [round((centers[i - 1] + centers[i]) / 2) for i in range(1, COLS)] + [width]

        frames: list[FrameSpec] = []
        for col in range(COLS):
            gx0, gx1 = bounds[col], bounds[col + 1]
            group = im.crop((gx0, y0, gx1, y1))
            bbox = alpha_bbox(group)
            if bbox is None:
                raise RuntimeError(f"row {row_index + 1} col {col + 1}: empty frame")

            pad = 4
            left = max(0, bbox[0] - pad)
            top = max(0, bbox[1] - pad)
            right = min(group.size[0], bbox[2] + pad)
            bottom = min(group.size[1], bbox[3] + pad)
            content = group.crop((left, top, right, bottom))

            main_bbox = mains[col]["bbox"]  # type: ignore[index]
            main_cx = ((main_bbox[0] + main_bbox[2]) / 2) - gx0 - left
            main_cy = ((main_bbox[1] + main_bbox[3]) / 2) - y0 - top
            main_w = main_bbox[2] - main_bbox[0]
            main_h = main_bbox[3] - main_bbox[1]

            spans = [
                main_cx,
                content.size[0] - main_cx,
                main_cy,
                content.size[1] - main_cy,
            ]
            limits = []
            if spans[0] > 0:
                limits.append((CELL_W / 2 - margin) / spans[0])
            if spans[1] > 0:
                limits.append((CELL_W - margin - CELL_W / 2) / spans[1])
            if spans[2] > 0:
                limits.append((CELL_H / 2 - margin) / spans[2])
            if spans[3] > 0:
                limits.append((CELL_H - margin - CELL_H / 2) / spans[3])
            frames.append(
                FrameSpec(
                    content=content,
                    main_cx=main_cx,
                    main_cy=main_cy,
                    main_w=main_w,
                    main_h=main_h,
                    fit_limit=min(limits),
                )
            )
        rows.append(frames)

    return rows


def row_scales(
    specs: list[list[FrameSpec]],
    scale_mode: str,
    target_body_width: float,
    target_body_height: float,
    max_scale: float,
) -> list[float]:
    scales: list[float] = []
    print(f"scale_mode {scale_mode}")

    for row_index, frames in enumerate(specs):
        fit_limit = min(frame.fit_limit for frame in frames)
        median_body_w = median(frame.main_w for frame in frames)
        median_body_h = median(frame.main_h for frame in frames)
        if scale_mode == "fit-row":
            scale = min(max_scale, fit_limit)
        else:
            desired = min(target_body_width / median_body_w, target_body_height / median_body_h)
            scale = min(max_scale, desired, fit_limit)

        final_body_w = median_body_w * scale
        final_body_h = median_body_h * scale
        limited_by = []
        if scale == max_scale and scale < fit_limit:
            limited_by.append("max-scale")
        if scale == fit_limit:
            limited_by.append("fit-limit")
        if not limited_by:
            limited_by.append("target")
        print(
            "row_scale "
            f"row={row_index + 1} scale={scale:.4f} "
            f"median_body={final_body_w:.1f}x{final_body_h:.1f} "
            f"limited_by={'+'.join(limited_by)}"
        )
        scales.append(scale)

    body_widths = [median(frame.main_w for frame in frames) * scales[index] for index, frames in enumerate(specs)]
    body_heights = [median(frame.main_h for frame in frames) * scales[index] for index, frames in enumerate(specs)]
    print(f"body_width_range {min(body_widths):.1f}..{max(body_widths):.1f}px")
    print(f"body_height_range {min(body_heights):.1f}..{max(body_heights):.1f}px")
    return scales


def render_cells(specs: list[list[FrameSpec]], scales: list[float]) -> tuple[list[list[Image.Image]], float, int]:
    rows: list[list[Image.Image]] = []
    max_center_error = 0.0
    edge_hits = 0

    for row_index, frames in enumerate(specs):
        scale = scales[row_index]
        row_cells: list[Image.Image] = []
        for frame in frames:
            resized = frame.content.resize(
                (
                    max(1, round(frame.content.size[0] * scale)),
                    max(1, round(frame.content.size[1] * scale)),
                ),
                Image.Resampling.NEAREST,
            )
            paste_x = round(CELL_W / 2 - frame.main_cx * scale)
            paste_y = round(CELL_H / 2 - frame.main_cy * scale)
            cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
            cell.alpha_composite(resized, (paste_x, paste_y))
            bbox = alpha_bbox(cell)
            if bbox and (bbox[0] <= 0 or bbox[1] <= 0 or bbox[2] >= CELL_W or bbox[3] >= CELL_H):
                edge_hits += 1
            max_center_error = max(
                max_center_error,
                abs(paste_x + frame.main_cx * scale - CELL_W / 2),
                abs(paste_y + frame.main_cy * scale - CELL_H / 2),
            )
            row_cells.append(cell)
        rows.append(row_cells)

    return rows, max_center_error, edge_hits


def build_cells(
    im: Image.Image,
    component_threshold: int,
    margin: int,
    max_scale: float,
    scale_mode: str,
    target_body_width: float,
    target_body_height: float,
) -> tuple[list[list[Image.Image]], float, int]:
    specs = extract_frame_specs(im, component_threshold, margin)
    scales = row_scales(specs, scale_mode, target_body_width, target_body_height, max_scale)
    return render_cells(specs, scales)


def write_outputs(rows: list[list[Image.Image]], out_dir: Path, also_png: bool) -> Path:
    canvas = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    for row, cells in enumerate(rows):
        for col, cell in enumerate(cells):
            canvas.alpha_composite(cell, (col * CELL_W, row * CELL_H))

    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / "spritesheet.png"
    webp_path = out_dir / "spritesheet.webp"
    if also_png:
        canvas.save(png_path, format="PNG", optimize=True)
    canvas.save(webp_path, format="WEBP", lossless=False, quality=95, method=6, exact=True)
    return webp_path


def write_pet_json(out_dir: Path, pet_id: str | None, display_name: str, description: str, kind: str) -> Path:
    manifest = {
        "id": pet_id or slugify(display_name),
        "displayName": display_name,
        "description": description,
        "spritesheetPath": "spritesheet.webp",
        "kind": kind,
    }
    json_path = out_dir / "pet.json"
    json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return json_path


def main() -> int:
    args = parse_args()
    source = Path(args.source)
    if not source.exists():
        print(f"source not found: {source}", file=sys.stderr)
        return 2

    chroma_removed = remove_chroma(
        Image.open(source),
        transparent_threshold=args.transparent_threshold,
        opaque_threshold=args.opaque_threshold,
    )
    rows, max_center_error, edge_hits = build_cells(
        chroma_removed,
        component_threshold=args.component_threshold,
        margin=args.margin,
        max_scale=args.max_scale,
        scale_mode=args.scale_mode,
        target_body_width=args.target_body_width,
        target_body_height=args.target_body_height,
    )
    if not args.no_mirror_run_left:
        rows[2] = [cell.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for cell in rows[1]]
        print("direction_rows row2=run-right row3=mirror(row2)-run-left")
    else:
        print("direction_rows row2=run-right row3=source-row3 (--no-mirror-run-left)")

    out_dir = Path(args.out_dir)
    webp_path = write_outputs(rows, out_dir, args.png)
    json_path = write_pet_json(out_dir, args.pet_id, args.display_name, args.description, args.kind)
    print(f"wrote {webp_path} {OUT_W}x{OUT_H}")
    if args.png:
        print(f"wrote {out_dir / 'spritesheet.png'} {OUT_W}x{OUT_H}")
    print(f"wrote {json_path}")
    print("pet_json_spritesheetPath spritesheet.webp")
    print(f"edge_hits {edge_hits}")
    print(f"max_center_error {max_center_error:.2f}px")
    return 0 if edge_hits == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
