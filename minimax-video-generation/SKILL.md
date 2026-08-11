---
name: minimax-video-generation
description: Generate videos with MiniMax from a text prompt (text-to-video) or a starting image (image-to-video). Use this skill when the user asks to create, render, or animate a video from a description or an image. Handles asynchronous task submission, task-status polling, and downloading the finished video.
---

# MiniMax Video Generation

Create videos with MiniMax's video generation API. The API is asynchronous: you submit a
generation task, poll the task until it finishes, then download the rendered file. The bundled
script (`scripts/generate_video.py`) runs that full flow for you.

## When to Use This Skill

- Generate a video clip from a text prompt (text-to-video)
- Animate a still image into a video (image-to-video)
- Turn a storyboard or scene description into a short rendered clip

## Prerequisites

- A MiniMax API key. Set it in the `MINIMAX_API_KEY` environment variable:
  ```bash
  export MINIMAX_API_KEY="your-api-key"
  ```
- Python 3 (the script uses only the standard library; no extra packages required).

## Quick Start

Text-to-video:

```bash
python scripts/generate_video.py "A red fox running across a snowy field at sunrise" --duration 6
```

Image-to-video (animate a starting frame):

```bash
python scripts/generate_video.py "The camera slowly zooms in" --first-frame-image ./frame.jpg --duration 6
```

Both commands submit the task, poll until it completes, then download the finished MP4 to
`/mnt/user-data/outputs/`.

## Options

| Option | Description |
|--------|-------------|
| `prompt` (positional) | Text description. Required for H3 and v1 text-to-video; optional only for v1 image-to-video. |
| `--first-frame-image PATH_OR_URL` | Local image path, public URL, or data URI used as the first frame. H3 also accepts `mm_file://` references. |
| `--model NAME` | Model to use (default `MiniMax-H3`). |
| `--region {global_en,cn_zh}` | API region (default `global_en`). |
| `--duration N` | Requested clip duration. Required for H3 and must be an integer from 4 to 15. |
| `--resolution VALUE` | Requested output resolution. H3 supports `2K`, which is used by default. |
| `--ratio VALUE` | H3 aspect ratio: `adaptive`, `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, or `9:16`. |
| `--prompt-optimizer / --no-prompt-optimizer` | Enable or disable prompt optimization for v1 models. |
| `--fast-pretreatment` | Enable fast pretreatment for v1 models. |
| `--aigc-watermark / --no-aigc-watermark` | Configure the H3 watermark in the `cn_zh` region. |
| `--callback-url URL` | Also request task status updates at a callback URL; the script continues polling. |
| `--output DIR` / `-o DIR` | Output directory (default `/mnt/user-data/outputs/`). |
| `--poll-interval SECONDS` | Seconds between status checks (default 10). |
| `--timeout SECONDS` | Maximum time to wait for the task (default 600). |

## Models

Default: `MiniMax-H3` (v2 API)

Also available through the v1 API: `MiniMax-Hailuo-2.3`, `MiniMax-Hailuo-2.3-Fast`, `MiniMax-Hailuo-02`,
`T2V-01-Director`, `T2V-01`, `I2V-01-Director`, `I2V-01-live`, `I2V-01`.

H3 supports text-to-video and first-frame image-to-video. For older models, use a `T2V-*` model
for text-to-video and an `I2V-*` model when providing a first frame; the `MiniMax-Hailuo-*`
models support both modes.

## Regions

| Region | API base |
|--------|----------|
| `global_en` (default) | `https://api.minimax.io` |
| `cn_zh` | `https://api.minimaxi.com` |

## How It Works

For `MiniMax-H3`:

1. **Submit**: `POST /v2/video_generation` with `model`, a typed `content` array, `resolution`,
   and `duration`. Text is always required; an image-to-video request adds an `image_url` item
   with the `first_frame` role.
2. **Poll**: `GET /v2/query/video_generation/{task_id}` until `task.status` is `succeeded` or
   `failed`.
3. **Download**: On success, download the direct URL from `task.content.url`.

For v1 models, the script submits to `POST /v1/video_generation`, polls
`GET /v1/query/video_generation?task_id=...`, and calls
`GET /v1/files/retrieve?file_id=...` to obtain the download URL.

All requests authenticate with `Authorization: Bearer $MINIMAX_API_KEY`. The v1 response path is
also checked via `base_resp.status_code`.

## Examples

1. Text-to-video with a specific model and duration:
   ```bash
   python scripts/generate_video.py "Neon city skyline timelapse at night" --duration 6 --ratio 16:9
   ```

2. Image-to-video from a local frame with a camera-motion prompt:
   ```bash
   python scripts/generate_video.py "Pan left across the landscape" --first-frame-image ./landscape.png --duration 6
   ```

3. Text-to-video in the `cn_zh` region saved to a custom directory:
   ```bash
   python scripts/generate_video.py "A calm mountain landscape animation" --duration 6 --region cn_zh -o ./out
   ```

## Notes

- Generation is asynchronous and may take a few minutes; increase `--timeout` for longer clips.
- H3 requires a non-empty text prompt for both text-to-video and image-to-video requests.
- Download URLs returned by the API are time-limited, so the script downloads the file
  immediately after the task succeeds.
- Local first-frame images are encoded as data URIs before submission.
