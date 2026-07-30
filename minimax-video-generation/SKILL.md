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
- Python 3 (the script uses only the standard library — no extra packages required).

## Quick Start

Text-to-video:

```bash
python scripts/generate_video.py "A red fox running across a snowy field at sunrise"
```

Image-to-video (animate a starting frame):

```bash
python scripts/generate_video.py "The camera slowly zooms in" --first-frame-image ./frame.jpg
```

Both commands submit the task, poll until it completes, then download the finished MP4 to
`/mnt/user-data/outputs/`.

## Options

| Option | Description |
|--------|-------------|
| `prompt` (positional) | Text description of the video. Required for text-to-video; optional for image-to-video. |
| `--first-frame-image PATH_OR_URL` | Local image path or public URL used as the first frame. Switches the request to image-to-video. |
| `--model NAME` | Model to use (default `MiniMax-Hailuo-2.3`). |
| `--region {global_en,cn_zh}` | API region (default `global_en`). |
| `--duration N` | Requested clip duration in seconds (model-dependent). |
| `--resolution VALUE` | Requested output resolution (e.g. `768P`, `1080P`; model-dependent). |
| `--prompt-optimizer / --no-prompt-optimizer` | Enable or disable prompt optimization (enabled by default). |
| `--fast-pretreatment` | Enable fast pretreatment. |
| `--callback-url URL` | Receive task status updates via callback instead of polling. |
| `--output DIR` / `-o DIR` | Output directory (default `/mnt/user-data/outputs/`). |
| `--poll-interval SECONDS` | Seconds between status checks (default 10). |
| `--timeout SECONDS` | Maximum time to wait for the task (default 600). |

## Models

Default: `MiniMax-Hailuo-2.3`

Available: `MiniMax-Hailuo-2.3`, `MiniMax-Hailuo-2.3-Fast`, `MiniMax-Hailuo-02`,
`T2V-01-Director`, `T2V-01`, `I2V-01-Director`, `I2V-01-live`, `I2V-01`.

Use a `T2V-*` model for text-to-video and an `I2V-*` model when providing a first frame; the
`MiniMax-Hailuo-*` models support both modes.

## Regions

| Region | API base |
|--------|----------|
| `global_en` (default) | `https://api.minimax.io` |
| `cn_zh` | `https://api.minimaxi.com` |

## How It Works

1. **Submit** — `POST /v1/video_generation` with the model plus a `prompt` (text-to-video) or a
   `first_frame_image` (image-to-video). The response returns a `task_id`.
2. **Poll** — `GET /v1/query/video_generation?task_id=...` until the task `status` reaches a
   terminal state. On success the response includes a `file_id`.
3. **Retrieve** — `GET /v1/files/retrieve?file_id=...` to obtain the download URL, then download
   the rendered video to the output directory.

All requests authenticate with `Authorization: Bearer $MINIMAX_API_KEY`, and every response is
checked via `base_resp.status_code`.

## Examples

1. Text-to-video with a specific model and duration:
   ```bash
   python scripts/generate_video.py "Neon city skyline timelapse at night" --model MiniMax-Hailuo-02 --duration 6
   ```

2. Image-to-video from a local frame with a camera-motion prompt:
   ```bash
   python scripts/generate_video.py "Pan left across the landscape" --first-frame-image ./landscape.png --model I2V-01
   ```

3. Text-to-video in the `cn_zh` region saved to a custom directory:
   ```bash
   python scripts/generate_video.py "A calm mountain landscape animation" --region cn_zh -o ./out
   ```

## Notes

- Generation is asynchronous and may take a few minutes; increase `--timeout` for longer clips.
- Download URLs returned by the API are time-limited, so the script downloads the file
  immediately after the task succeeds.
- `--first-frame-image` accepts either a local file (encoded and sent inline) or a public URL.
