#!/usr/bin/env python3
"""Generate a video with MiniMax (text-to-video or image-to-video).

MiniMax video generation is asynchronous. This script supports both API versions:

  - MiniMax-H3 uses POST /v2/video_generation and polls
    GET /v2/query/video_generation/{task_id} for a direct output URL.
  - Earlier models use POST /v1/video_generation, poll
    GET /v1/query/video_generation, and retrieve the output with
    GET /v1/files/retrieve.

Authentication uses the MINIMAX_API_KEY environment variable as a Bearer token.
Only the Python standard library is required.
"""

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_MODEL = "MiniMax-H3"
V2_MODELS = {"MiniMax-H3"}
V1_MODELS = [
    "MiniMax-Hailuo-2.3",
    "MiniMax-Hailuo-2.3-Fast",
    "MiniMax-Hailuo-02",
    "T2V-01-Director",
    "T2V-01",
    "I2V-01-Director",
    "I2V-01-live",
    "I2V-01",
]
MODELS = [DEFAULT_MODEL] + V1_MODELS
RATIOS = ["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]

REGION_BASES = {
    "global_en": "https://api.minimax.io",
    "cn_zh": "https://api.minimaxi.com",
}

V2_SUBMIT_PATH = "/v2/video_generation"
V2_QUERY_PATH = "/v2/query/video_generation/{task_id}"
V1_SUBMIT_PATH = "/v1/video_generation"
V1_QUERY_PATH = "/v1/query/video_generation"
V1_RETRIEVE_PATH = "/v1/files/retrieve"

V2_SUCCESS_STATES = {"succeeded"}
V2_FAILURE_STATES = {"failed", "cancelled"}
V1_SUCCESS_STATES = {"Success"}
V1_FAILURE_STATES = {"Fail"}
V2_MAX_BODY_BYTES = 64 * 1024 * 1024


def _api_key():
    key = os.environ.get("MINIMAX_API_KEY", "").strip()
    if not key:
        sys.exit("Error: set the MINIMAX_API_KEY environment variable to your MiniMax API key.")
    return key


def _api_version(model):
    return "v2" if model in V2_MODELS else "v1"


def _check_base_resp(payload):
    """Raise if a v1 MiniMax response reports a non-zero status code."""
    base = payload.get("base_resp") or {}
    code = base.get("status_code")
    if code not in (None, 0):
        msg = base.get("status_msg", "unknown error")
        sys.exit("MiniMax API error (status_code={}): {}".format(code, msg))


def _request(method, url, key, body=None):
    data = None
    headers = {"Authorization": "Bearer {}".format(key)}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        sys.exit("HTTP {} from {}: {}".format(exc.code, url, detail))
    except urllib.error.URLError as exc:
        sys.exit("Network error calling {}: {}".format(url, exc.reason))
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        sys.exit("Unexpected non-JSON response from {}: {}".format(url, raw[:200]))


def _encode_first_frame(value):
    """Return a supported image URL, file reference, or base64 data URI."""
    supported_prefixes = ("http://", "https://", "data:", "mm_file://")
    if value.startswith(supported_prefixes):
        return value
    if not os.path.isfile(value):
        sys.exit("Error: first-frame image not found: {}".format(value))
    mime = mimetypes.guess_type(value)[0] or "image/jpeg"
    with open(value, "rb") as fh:
        encoded = base64.b64encode(fh.read()).decode("ascii")
    return "data:{};base64,{}".format(mime, encoded)


def _build_v2_body(args):
    if not args.prompt:
        sys.exit("Error: MiniMax-H3 requires a text prompt for every generation mode.")
    if len(args.prompt) > 7000:
        sys.exit("Error: MiniMax-H3 prompts must not exceed 7000 characters.")
    if args.duration is None or not 4 <= args.duration <= 15:
        sys.exit("Error: MiniMax-H3 requires --duration as an integer from 4 to 15 seconds.")

    resolution = args.resolution or "2K"
    if resolution != "2K":
        sys.exit("Error: MiniMax-H3 currently supports only --resolution 2K.")
    if args.prompt_optimizer is not None or args.fast_pretreatment:
        sys.exit("Error: prompt optimization and fast pretreatment are v1-only options.")
    if args.aigc_watermark is not None and args.region != "cn_zh":
        sys.exit("Error: --aigc-watermark is available only in the cn_zh region.")

    content = [{"type": "text", "text": args.prompt}]
    if args.first_frame_image:
        content.append({
            "type": "image_url",
            "image_url": {"url": _encode_first_frame(args.first_frame_image)},
            "role": "first_frame",
        })

    body = {
        "model": args.model,
        "content": content,
        "resolution": resolution,
        "duration": args.duration,
    }
    if args.ratio:
        body["ratio"] = args.ratio
    if args.callback_url:
        body["callback_url"] = args.callback_url
    if args.region == "cn_zh" and args.aigc_watermark is not None:
        body["aigc_watermark"] = args.aigc_watermark

    if len(json.dumps(body).encode("utf-8")) > V2_MAX_BODY_BYTES:
        sys.exit("Error: MiniMax-H3 request bodies must not exceed 64 MB.")
    return body


def _build_v1_body(args):
    if args.ratio:
        sys.exit("Error: --ratio is available only with MiniMax-H3.")
    if args.aigc_watermark is not None:
        sys.exit("Error: --aigc-watermark is available only with MiniMax-H3 in cn_zh.")

    body = {"model": args.model}
    if args.first_frame_image:
        body["first_frame_image"] = _encode_first_frame(args.first_frame_image)
        if args.prompt:
            body["prompt"] = args.prompt
    else:
        if not args.prompt:
            sys.exit("Error: a text prompt is required for text-to-video.")
        body["prompt"] = args.prompt

    if args.prompt_optimizer is not None:
        body["prompt_optimizer"] = args.prompt_optimizer
    if args.fast_pretreatment:
        body["fast_pretreatment"] = True
    if args.duration is not None:
        body["duration"] = args.duration
    if args.resolution:
        body["resolution"] = args.resolution
    if args.callback_url:
        body["callback_url"] = args.callback_url
    return body


def submit_task(base, key, args):
    api_version = _api_version(args.model)
    if api_version == "v2":
        path = V2_SUBMIT_PATH
        body = _build_v2_body(args)
    else:
        path = V1_SUBMIT_PATH
        body = _build_v1_body(args)

    mode = "image-to-video" if args.first_frame_image else "text-to-video"
    print("Submitting {} task (model={}, api={})...".format(mode, args.model, api_version))
    payload = _request("POST", base + path, key, body)
    if api_version == "v1":
        _check_base_resp(payload)
    task_id = payload.get("task_id")
    if not task_id:
        sys.exit("No task_id returned by the API: {}".format(json.dumps(payload)[:300]))
    print("Task submitted: task_id={}".format(task_id))
    return api_version, str(task_id)


def poll_task(base, key, api_version, task_id, poll_interval, timeout):
    if api_version == "v2":
        quoted_task_id = urllib.parse.quote(task_id, safe="")
        query = base + V2_QUERY_PATH.format(task_id=quoted_task_id)
    else:
        query = base + V1_QUERY_PATH + "?" + urllib.parse.urlencode({"task_id": task_id})

    deadline = time.monotonic() + timeout
    last_status = None
    while True:
        payload = _request("GET", query, key)
        if api_version == "v2":
            task = payload.get("task") or {}
            status = str(task.get("status", "")).lower()
            success_states = V2_SUCCESS_STATES
            failure_states = V2_FAILURE_STATES
        else:
            _check_base_resp(payload)
            task = payload
            status = payload.get("status", "")
            success_states = V1_SUCCESS_STATES
            failure_states = V1_FAILURE_STATES

        if status != last_status:
            print("Task status: {}".format(status))
            last_status = status
        if status in success_states:
            if api_version == "v2":
                output = task.get("content") or {}
                url = output.get("url")
                if not url:
                    sys.exit("Task succeeded but no task.content.url was returned.")
                return {"download_url": url, "result_id": task.get("id") or task_id}
            file_id = payload.get("file_id")
            if not file_id:
                sys.exit("Task succeeded but no file_id was returned.")
            return {"file_id": str(file_id), "result_id": str(file_id)}
        if status in failure_states:
            sys.exit("Task failed: {}".format(json.dumps(task)[:300]))
        if time.monotonic() >= deadline:
            sys.exit("Timed out after {}s waiting for task {}.".format(timeout, task_id))
        time.sleep(poll_interval)


def retrieve_download_url(base, key, file_id):
    query = base + V1_RETRIEVE_PATH + "?" + urllib.parse.urlencode({"file_id": file_id})
    payload = _request("GET", query, key)
    _check_base_resp(payload)
    file_info = payload.get("file") or {}
    url = file_info.get("download_url") or file_info.get("backup_download_url")
    if not url:
        sys.exit("No download URL found for file_id={}: {}".format(file_id, json.dumps(payload)[:300]))
    return url


def download(url, out_dir, result_id):
    os.makedirs(out_dir, exist_ok=True)
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "-", str(result_id)).strip("-") or "result"
    dest = os.path.join(out_dir, "minimax-video-{}.mp4".format(safe_id))
    print("Downloading video to {}...".format(dest))
    try:
        with urllib.request.urlopen(url, timeout=120) as resp, open(dest, "wb") as fh:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                fh.write(chunk)
    except (urllib.error.URLError, OSError) as exc:
        sys.exit("Failed to download video: {}".format(exc))
    return dest


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate a video with MiniMax (text-to-video or image-to-video)."
    )
    parser.add_argument("prompt", nargs="?", help="Text description of the video.")
    parser.add_argument(
        "--first-frame-image",
        dest="first_frame_image",
        help="Local image path, public URL, data URI, or mm_file:// reference.",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL, choices=MODELS,
        help="Model to use (default: %(default)s).",
    )
    parser.add_argument(
        "--region", default="global_en", choices=sorted(REGION_BASES),
        help="API region (default: %(default)s).",
    )
    parser.add_argument("--duration", type=int, help="Clip duration in seconds; H3 requires 4-15.")
    parser.add_argument("--resolution", help="Output resolution; H3 supports 2K only.")
    parser.add_argument("--ratio", choices=RATIOS, help="H3 output aspect ratio.")
    parser.add_argument(
        "--prompt-optimizer", dest="prompt_optimizer", action="store_true", default=None,
        help="Enable v1 prompt optimization.",
    )
    parser.add_argument(
        "--no-prompt-optimizer", dest="prompt_optimizer", action="store_false",
        help="Disable v1 prompt optimization.",
    )
    parser.add_argument(
        "--fast-pretreatment", action="store_true", help="Enable v1 fast pretreatment.",
    )
    parser.add_argument(
        "--aigc-watermark", dest="aigc_watermark", action="store_true", default=None,
        help="Enable the H3 watermark in the cn_zh region.",
    )
    parser.add_argument(
        "--no-aigc-watermark", dest="aigc_watermark", action="store_false",
        help="Disable the H3 watermark in the cn_zh region.",
    )
    parser.add_argument(
        "--callback-url", dest="callback_url", help="Callback URL for task status updates.",
    )
    parser.add_argument(
        "-o", "--output", default="/mnt/user-data/outputs/",
        help="Output directory (default: %(default)s).",
    )
    parser.add_argument(
        "--poll-interval", type=float, default=10.0,
        help="Seconds between status checks (default: %(default)s).",
    )
    parser.add_argument(
        "--timeout", type=float, default=600.0,
        help="Maximum seconds to wait for the task (default: %(default)s).",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.prompt and not args.first_frame_image:
        sys.exit("Error: provide a text prompt, a --first-frame-image, or both.")

    key = _api_key()
    base = REGION_BASES[args.region]
    api_version, task_id = submit_task(base, key, args)
    result = poll_task(base, key, api_version, task_id, args.poll_interval, args.timeout)
    url = result.get("download_url")
    if not url:
        url = retrieve_download_url(base, key, result["file_id"])
    dest = download(url, args.output, result["result_id"])
    print("Done. Saved video to {}".format(dest))


if __name__ == "__main__":
    main()
