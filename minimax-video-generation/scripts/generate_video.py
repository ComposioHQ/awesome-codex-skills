#!/usr/bin/env python3
"""Generate a video with MiniMax (text-to-video or image-to-video).

The MiniMax video API is asynchronous. This script runs the full flow:

  1. Submit a generation task   -> POST /v1/video_generation      (returns task_id)
  2. Poll the task status       -> GET  /v1/query/video_generation (returns status, file_id)
  3. Retrieve and download it   -> GET  /v1/files/retrieve          (returns download URL)

Authentication uses the MINIMAX_API_KEY environment variable as a Bearer token.
Only the Python standard library is required.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_MODEL = "MiniMax-Hailuo-2.3"
MODELS = [
    "MiniMax-Hailuo-2.3",
    "MiniMax-Hailuo-2.3-Fast",
    "MiniMax-Hailuo-02",
    "T2V-01-Director",
    "T2V-01",
    "I2V-01-Director",
    "I2V-01-live",
    "I2V-01",
]

# Regional API bases. The video endpoints live under /v1 on each host.
REGION_BASES = {
    "global_en": "https://api.minimax.io",
    "cn_zh": "https://api.minimaxi.com",
}

SUBMIT_PATH = "/v1/video_generation"
QUERY_PATH = "/v1/query/video_generation"
RETRIEVE_PATH = "/v1/files/retrieve"

# Terminal task statuses returned by the query endpoint.
SUCCESS_STATES = {"Success"}
FAILURE_STATES = {"Fail"}


def _api_key():
    key = os.environ.get("MINIMAX_API_KEY", "").strip()
    if not key:
        sys.exit("Error: set the MINIMAX_API_KEY environment variable to your MiniMax API key.")
    return key


def _check_base_resp(payload):
    """Raise if the MiniMax base_resp reports a non-zero status code."""
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
    """Return a value usable as first_frame_image: a URL or a base64 data URI."""
    if value.startswith("http://") or value.startswith("https://") or value.startswith("data:"):
        return value
    if not os.path.isfile(value):
        sys.exit("Error: first-frame image not found: {}".format(value))
    mime = mimetypes.guess_type(value)[0] or "image/jpeg"
    with open(value, "rb") as fh:
        encoded = base64.b64encode(fh.read()).decode("ascii")
    return "data:{};base64,{}".format(mime, encoded)


def submit_task(base, key, args):
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

    mode = "image-to-video" if args.first_frame_image else "text-to-video"
    print("Submitting {} task (model={})...".format(mode, args.model))
    payload = _request("POST", base + SUBMIT_PATH, key, body)
    _check_base_resp(payload)
    task_id = payload.get("task_id")
    if not task_id:
        sys.exit("No task_id returned by the API: {}".format(json.dumps(payload)[:300]))
    print("Task submitted: task_id={}".format(task_id))
    return task_id


def poll_task(base, key, task_id, poll_interval, timeout):
    query = base + QUERY_PATH + "?" + urllib.parse.urlencode({"task_id": task_id})
    deadline = time.monotonic() + timeout
    last_status = None
    while True:
        payload = _request("GET", query, key)
        _check_base_resp(payload)
        status = payload.get("status", "")
        if status != last_status:
            print("Task status: {}".format(status))
            last_status = status
        if status in SUCCESS_STATES:
            file_id = payload.get("file_id")
            if not file_id:
                sys.exit("Task succeeded but no file_id was returned.")
            return file_id
        if status in FAILURE_STATES:
            sys.exit("Task failed: {}".format(json.dumps(payload)[:300]))
        if time.monotonic() >= deadline:
            sys.exit("Timed out after {}s waiting for task {}.".format(timeout, task_id))
        time.sleep(poll_interval)


def retrieve_download_url(base, key, file_id):
    query = base + RETRIEVE_PATH + "?" + urllib.parse.urlencode({"file_id": file_id})
    payload = _request("GET", query, key)
    _check_base_resp(payload)
    file_info = payload.get("file") or {}
    url = file_info.get("download_url") or file_info.get("backup_download_url")
    if not url:
        sys.exit("No download URL found for file_id={}: {}".format(file_id, json.dumps(payload)[:300]))
    return url


def download(url, out_dir, file_id):
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "minimax-video-{}.mp4".format(file_id))
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
    parser.add_argument("--first-frame-image", dest="first_frame_image",
                        help="Local image path or URL to animate (image-to-video).")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=MODELS,
                        help="Model to use (default: %(default)s).")
    parser.add_argument("--region", default="global_en", choices=sorted(REGION_BASES),
                        help="API region (default: %(default)s).")
    parser.add_argument("--duration", type=int, help="Requested clip duration in seconds.")
    parser.add_argument("--resolution", help="Requested output resolution (e.g. 768P, 1080P).")
    parser.add_argument("--prompt-optimizer", dest="prompt_optimizer",
                        action="store_true", default=None, help="Enable prompt optimization.")
    parser.add_argument("--no-prompt-optimizer", dest="prompt_optimizer",
                        action="store_false", help="Disable prompt optimization.")
    parser.add_argument("--fast-pretreatment", action="store_true",
                        help="Enable fast pretreatment.")
    parser.add_argument("--callback-url", dest="callback_url",
                        help="Callback URL for task status updates.")
    parser.add_argument("-o", "--output", default="/mnt/user-data/outputs/",
                        help="Output directory (default: %(default)s).")
    parser.add_argument("--poll-interval", type=float, default=10.0,
                        help="Seconds between status checks (default: %(default)s).")
    parser.add_argument("--timeout", type=float, default=600.0,
                        help="Maximum seconds to wait for the task (default: %(default)s).")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.prompt and not args.first_frame_image:
        sys.exit("Error: provide a text prompt, a --first-frame-image, or both.")

    key = _api_key()
    base = REGION_BASES[args.region]

    task_id = submit_task(base, key, args)
    file_id = poll_task(base, key, task_id, args.poll_interval, args.timeout)
    url = retrieve_download_url(base, key, file_id)
    dest = download(url, args.output, file_id)
    print("Done. Saved video to {}".format(dest))


if __name__ == "__main__":
    main()
