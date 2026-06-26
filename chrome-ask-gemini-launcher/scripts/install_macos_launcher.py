#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import plistlib
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

GEMINI_ENABLE_FEATURES = [
    "Glic",
    "GlicHorizontalTabToolbarButton",
    "GlicToolbarButtonLocation:glic-toolbar-button-location/RightOfOmnibox",
    "GlicActorUi",
    "GlicDefaultTabContextSetting",
    "GlicDefaultToLastActiveConversation",
    "GlicExperimentalTriggering",
    "GlicUseToolbarHeightSidePanel",
    "SyncGeminiThread",
]

GEMINI_DISABLE_FEATURES = [
    "GlicCountryFiltering",
    "GlicUseSessionCountryForFiltering",
    "GlicLocaleFiltering",
]

VERTICAL_TABS_FEATURES = ["VerticalTabsLaunch", "VerticalTabs"]

LAB_EXPERIMENTS = [
    "glic-actor@1",
    "glic-default-to-last-active-conversation@1",
    "glic-experimental-triggering@1",
    "glic@1",
    "glic-toolbar-height-side-panel@1",
    "glic-default-tab-context-setting@1",
    "sync-gemini-threads@1",
    "glic-horizontal-tab-toolbar-button@1",
    "glic-toolbar-button-location@2",
]


def run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def home() -> Path:
    return Path.home()


def chrome_app_default() -> Path:
    return Path("/Applications/Google Chrome.app")


def chrome_binary(chrome_app: Path) -> Path:
    return chrome_app / "Contents/MacOS/Google Chrome"


def chrome_icon(chrome_app: Path) -> Path:
    return chrome_app / "Contents/Resources/app.icns"


def chrome_support_dir() -> Path:
    return home() / "Library/Application Support/Google/Chrome"


def local_state_path() -> Path:
    return chrome_support_dir() / "Local State"


def preferences_path(profile_directory: str) -> Path:
    return chrome_support_dir() / profile_directory / "Preferences"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def is_macos() -> bool:
    return sys.platform == "darwin"


def chrome_running() -> bool:
    return run(["pgrep", "-x", "Google Chrome"]).returncode == 0


def chrome_version(chrome_app: Path) -> str:
    binary = chrome_binary(chrome_app)
    if not binary.exists():
        return "missing"
    result = run([str(binary), "--version"])
    return result.stdout.strip() or result.stderr.strip() or "unknown"


def current_chrome_commands() -> list[str]:
    result = run(["ps", "-axo", "command"])
    if result.returncode != 0:
        return []
    marker = "/Contents/MacOS/Google Chrome"
    return [
        line
        for line in result.stdout.splitlines()
        if marker in line and "Google Chrome Helper" not in line
    ]


def profile_info(profile_directory: str) -> dict:
    local_state = read_json(local_state_path())
    return (
        local_state.get("profile", {})
        .get("info_cache", {})
        .get(profile_directory, {})
    )


def vertical_tabs_enabled(profile_directory: str) -> bool:
    prefs = read_json(preferences_path(profile_directory))
    return bool(prefs.get("vertical_tabs", {}).get("enabled"))


def decide_vertical_tabs(mode: str, profile_directory: str) -> bool:
    if mode == "on":
        return True
    if mode == "off":
        return False
    return vertical_tabs_enabled(profile_directory)


def ensure_profile_prefs(profile_directory: str, include_vertical_tabs: bool) -> list[str]:
    changed: list[str] = []
    prefs_path = preferences_path(profile_directory)
    prefs = read_json(prefs_path)
    if prefs:
        browser = prefs.setdefault("browser", {})
        if browser.get("gemini_settings") != 0:
            browser["gemini_settings"] = 0
            changed.append("browser.gemini_settings")
        glic = prefs.setdefault("glic", {})
        for key, value in {
            "pinned_to_tabstrip": True,
            "default_tab_context_enabled": True,
            "tab_context_enabled": True,
        }.items():
            if glic.get(key) != value:
                glic[key] = value
                changed.append(f"glic.{key}")
        if include_vertical_tabs:
            vertical = prefs.setdefault("vertical_tabs", {})
            for key, value in {
                "enabled": True,
                "enabled_first_time": True,
                "collapsed_state": vertical.get("collapsed_state", True),
                "uncollapsed_width": vertical.get("uncollapsed_width", 193),
            }.items():
                if vertical.get(key) != value:
                    vertical[key] = value
                    changed.append(f"vertical_tabs.{key}")
        write_json(prefs_path, prefs)

    local_state = read_json(local_state_path())
    if local_state:
        experiments = local_state.setdefault("browser", {}).setdefault(
            "enabled_labs_experiments", []
        )
        desired = list(LAB_EXPERIMENTS)
        if include_vertical_tabs:
            desired.append("vertical-tabs@1")
        for item in desired:
            if item not in experiments:
                experiments.append(item)
                changed.append(f"enabled_labs_experiments:{item}")
        write_json(local_state_path(), local_state)
    return changed


def shell_string(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def launcher_script_text(
    chrome_app: Path,
    profile_directory: str,
    start_url: str,
    enable_features: list[str],
    disable_features: list[str],
) -> str:
    enable = ",".join(enable_features)
    disable = ",".join(disable_features)
    required_markers = ["Glic"]
    if "VerticalTabs" in enable_features:
        required_markers.append("VerticalTabs")
    marker_lines = "\n".join(
        f'  [[ "$command" == *{shell_string(marker)}* ]] || return 1'
        for marker in required_markers
    )
    return f"""#!/usr/bin/env bash
set -euo pipefail

CHROME_APP={shell_string(str(chrome_app))}
PROFILE_DIRECTORY={shell_string(profile_directory)}
START_URL="${{1:-{start_url}}}"
ENABLE_FEATURES={shell_string(enable)}
DISABLE_FEATURES={shell_string(disable)}

chrome_has_required_flags() {{
  local command
  command="$(ps -axo command | grep '/Contents/MacOS/Google Chrome' | grep -v 'Google Chrome Helper' | grep -v grep || true)"
  [[ -n "$command" ]] || return 1
{marker_lines}
  return 0
}}

if pgrep -x "Google Chrome" >/dev/null 2>&1; then
  if chrome_has_required_flags; then
    open -a "Google Chrome" "$START_URL"
    exit 0
  fi

  osascript -e 'tell application "Google Chrome" to quit' >/dev/null 2>&1 || true
  for _ in {{1..30}}; do
    if ! pgrep -x "Google Chrome" >/dev/null 2>&1; then
      break
    fi
    sleep 0.2
  done
  if pgrep -x "Google Chrome" >/dev/null 2>&1; then
    pkill -TERM -x "Google Chrome" >/dev/null 2>&1 || true
    sleep 0.8
  fi
fi

open -na "$CHROME_APP" --args \\
  "--profile-directory=$PROFILE_DIRECTORY" \\
  "--enable-features=$ENABLE_FEATURES" \\
  "--disable-features=$DISABLE_FEATURES" \\
  "$START_URL"
"""


def write_launcher_script(
    script_path: Path,
    chrome_app: Path,
    profile_directory: str,
    start_url: str,
    enable_features: list[str],
    disable_features: list[str],
) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(
        launcher_script_text(
            chrome_app, profile_directory, start_url, enable_features, disable_features
        ),
        encoding="utf-8",
    )
    script_path.chmod(script_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def plist_text(app_name: str, bundle_id: str, icon_name: str) -> bytes:
    data = {
        "CFBundleDevelopmentRegion": "en",
        "CFBundleDisplayName": app_name,
        "CFBundleExecutable": app_name,
        "CFBundleIconFile": icon_name,
        "CFBundleIdentifier": bundle_id,
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": app_name,
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1",
        "LSMinimumSystemVersion": "10.13",
        "LSUIElement": False,
    }
    return plistlib.dumps(data, sort_keys=False)


def app_executable_text(script_path: Path) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

exec {shell_string(str(script_path))} "$@"
"""


def draw_badged_icon(source_icon: Path, destination_icon: Path) -> bool:
    if shutil.which("iconutil") is None:
        shutil.copy2(source_icon, destination_icon)
        return False
    try:
        from PIL import Image, ImageDraw, ImageFilter, ImageFont
    except Exception:
        shutil.copy2(source_icon, destination_icon)
        return False

    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        source_set = temp_path / "source.iconset"
        output_set = temp_path / "output.iconset"
        output_set.mkdir()
        run(["iconutil", "-c", "iconset", "-o", str(source_set), str(source_icon)], check=True)

        font_candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]

        def font_for(size: int):
            for font_path in font_candidates:
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    pass
            return ImageFont.load_default()

        def add_badge(image):
            image = image.convert("RGBA")
            width, height = image.size
            scale = width / 1024.0
            badge = int(round(width * 0.36))
            margin = int(round(width * 0.045))
            x1 = width - margin - badge
            y1 = height - margin - badge
            x2 = width - margin
            y2 = height - margin
            radius = int(round(badge * 0.26))

            shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            offset = max(1, int(round(10 * scale)))
            shadow_draw.rounded_rectangle(
                (x1, y1 + offset, x2, y2 + offset),
                radius=radius,
                fill=(0, 0, 0, 105),
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(max(1, int(round(7 * scale)))))
            image = Image.alpha_composite(image, shadow)

            layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)
            draw.rounded_rectangle(
                (x1, y1, x2, y2),
                radius=radius,
                fill=(24, 119, 242, 255),
                outline=(255, 255, 255, 235),
                width=max(1, int(round(18 * scale))),
            )
            text = "AI"
            font = font_for(int(round(badge * 0.42)))
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            tx = x1 + (badge - text_width) / 2 - bbox[0]
            ty = y1 + (badge - text_height) / 2 - bbox[1] - int(round(badge * 0.015))
            draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))
            return Image.alpha_composite(image, layer)

        generated = []
        for src in source_set.glob("*.png"):
            image = Image.open(src)
            add_badge(image).save(output_set / src.name)
            generated.append(output_set / src.name)
        if not generated:
            shutil.copy2(source_icon, destination_icon)
            return False

        base = Image.open(max(generated, key=lambda p: Image.open(p).size[0])).convert("RGBA")
        slots = {
            "icon_16x16.png": 16,
            "icon_16x16@2x.png": 32,
            "icon_32x32.png": 32,
            "icon_32x32@2x.png": 64,
            "icon_128x128.png": 128,
            "icon_128x128@2x.png": 256,
            "icon_256x256.png": 256,
            "icon_256x256@2x.png": 512,
            "icon_512x512.png": 512,
            "icon_512x512@2x.png": 1024,
        }
        for name, size in slots.items():
            dest = output_set / name
            if not dest.exists():
                base.resize((size, size), Image.Resampling.LANCZOS).save(dest)
        run(["iconutil", "-c", "icns", "-o", str(destination_icon), str(output_set)], check=True)
    return True


def create_app(
    app_path: Path,
    app_name: str,
    bundle_id: str,
    script_path: Path,
    chrome_app: Path,
) -> bool:
    macos_dir = app_path / "Contents/MacOS"
    resources_dir = app_path / "Contents/Resources"
    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)

    icon_name = "ChromeAskGemini"
    (app_path / "Contents/Info.plist").write_bytes(plist_text(app_name, bundle_id, icon_name))
    executable = macos_dir / app_name
    executable.write_text(app_executable_text(script_path), encoding="utf-8")
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    badged = draw_badged_icon(chrome_icon(chrome_app), resources_dir / f"{icon_name}.icns")
    run(["xattr", "-dr", "com.apple.quarantine", str(app_path)])
    lsregister = Path(
        "/System/Library/Frameworks/CoreServices.framework/Frameworks/"
        "LaunchServices.framework/Support/lsregister"
    )
    if lsregister.exists():
        run([str(lsregister), "-f", str(app_path)])
    os.utime(app_path, None)
    return badged


def backup_file(path: Path, backup_dir: Path) -> Path | None:
    if not path.exists():
        return None
    backup_dir.mkdir(parents=True, exist_ok=True)
    dest = backup_dir / path.name
    shutil.copy2(path, dest)
    return dest


def add_to_dock(app_path: Path, app_name: str, backup_dir: Path) -> Path | None:
    dock_plist = home() / "Library/Preferences/com.apple.dock.plist"
    backup = backup_file(dock_plist, backup_dir)
    if not dock_plist.exists():
        raise FileNotFoundError(f"Dock plist not found: {dock_plist}")
    with dock_plist.open("rb") as f:
        dock = plistlib.load(f)
    apps = dock.setdefault("persistent-apps", [])
    app_url = app_path.resolve().as_uri() + "/"

    def item_url(item: dict) -> str:
        return (
            item.get("tile-data", {})
            .get("file-data", {})
            .get("_CFURLString", "")
        )

    apps[:] = [
        item
        for item in apps
        if app_name.replace(" ", "%20") not in item_url(item)
        and str(app_path.resolve()) not in item_url(item).replace("%20", " ")
    ]
    apps.append(
        {
            "tile-data": {
                "file-data": {
                    "_CFURLString": app_url,
                    "_CFURLStringType": 15,
                },
                "file-label": app_name,
                "file-type": 41,
            },
            "tile-type": "file-tile",
        }
    )
    with dock_plist.open("wb") as f:
        plistlib.dump(dock, f, sort_keys=False)
    run(["killall", "Dock"])
    return backup


def diagnose(args: argparse.Namespace) -> int:
    chrome_app = Path(args.chrome_app).expanduser()
    profile_directory = args.profile_directory
    prefs = read_json(preferences_path(profile_directory))
    local_state = read_json(local_state_path())
    info = profile_info(profile_directory)
    commands = current_chrome_commands()
    diagnostics = {
        "platform": sys.platform,
        "chrome_app": str(chrome_app),
        "chrome_exists": chrome_binary(chrome_app).exists(),
        "chrome_version": chrome_version(chrome_app),
        "profile_directory": profile_directory,
        "profile_info": {
            "name": info.get("name"),
            "user_name": info.get("user_name"),
            "is_glic_eligible": info.get("is_glic_eligible"),
            "is_consented_primary_account": info.get("is_consented_primary_account"),
            "is_managed": info.get("is_managed"),
        },
        "prefs": {
            "browser.gemini_settings": prefs.get("browser", {}).get("gemini_settings"),
            "glic.pinned_to_tabstrip": prefs.get("glic", {}).get("pinned_to_tabstrip"),
            "vertical_tabs.enabled": prefs.get("vertical_tabs", {}).get("enabled"),
        },
        "local_state": {
            "enabled_labs_experiments": local_state.get("browser", {}).get(
                "enabled_labs_experiments"
            )
        },
        "chrome_running": bool(commands),
        "chrome_main_commands": commands,
        "has_gemini_flags": any("Glic" in command for command in commands),
        "has_vertical_tabs_flags": any("VerticalTabs" in command for command in commands),
    }
    if args.json:
        print(json.dumps(diagnostics, ensure_ascii=False, indent=2))
    else:
        print(f"Chrome: {diagnostics['chrome_version']}")
        print(f"Profile: {profile_directory}")
        print(f"Account: {diagnostics['profile_info'].get('user_name')}")
        print(f"Local Glic eligible: {diagnostics['profile_info'].get('is_glic_eligible')}")
        print(f"Gemini setting: {diagnostics['prefs'].get('browser.gemini_settings')}")
        print(f"Glic pinned: {diagnostics['prefs'].get('glic.pinned_to_tabstrip')}")
        print(f"Vertical tabs enabled: {diagnostics['prefs'].get('vertical_tabs.enabled')}")
        print(f"Chrome running with Gemini flags: {diagnostics['has_gemini_flags']}")
        print(f"Chrome running with VerticalTabs flags: {diagnostics['has_vertical_tabs_flags']}")
    return 0


def install(args: argparse.Namespace) -> int:
    if not is_macos():
        raise SystemExit("This installer only supports macOS.")

    chrome_app = Path(args.chrome_app).expanduser()
    if not chrome_binary(chrome_app).exists():
        raise SystemExit(f"Google Chrome binary not found: {chrome_binary(chrome_app)}")
    if not chrome_icon(chrome_app).exists():
        raise SystemExit(f"Google Chrome icon not found: {chrome_icon(chrome_app)}")

    profile_directory = args.profile_directory
    include_vertical = decide_vertical_tabs(args.vertical_tabs, profile_directory)
    enable_features = list(GEMINI_ENABLE_FEATURES)
    if include_vertical:
        enable_features = VERTICAL_TABS_FEATURES + enable_features

    script_path = Path(args.script_path).expanduser()
    app_dir = Path(args.app_dir).expanduser()
    app_name = args.app_name
    app_path = app_dir / f"{app_name}.app"
    backup_dir = (
        home()
        / ".chrome-ask-gemini-launcher"
        / "backups"
        / time.strftime("%Y%m%d-%H%M%S")
    )

    if args.profile_prefs and chrome_running():
        print("Chrome is running; skipping profile preference edits to avoid overwrites.")
        pref_changes: list[str] = []
    elif args.profile_prefs:
        pref_changes = ensure_profile_prefs(profile_directory, include_vertical)
    else:
        pref_changes = []

    write_launcher_script(
        script_path,
        chrome_app,
        profile_directory,
        args.start_url,
        enable_features,
        GEMINI_DISABLE_FEATURES,
    )
    badged_icon = create_app(app_path, app_name, args.bundle_id, script_path, chrome_app)
    dock_backup = add_to_dock(app_path, app_name, backup_dir) if args.dock else None

    result = {
        "script_path": str(script_path),
        "app_path": str(app_path),
        "dock_updated": bool(args.dock),
        "dock_backup": str(dock_backup) if dock_backup else None,
        "backup_dir": str(backup_dir) if args.dock else None,
        "badged_icon": badged_icon,
        "vertical_tabs_included": include_vertical,
        "profile_pref_changes": pref_changes,
        "enable_features": enable_features,
        "disable_features": GEMINI_DISABLE_FEATURES,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--chrome-app", default=str(chrome_app_default()))
    shared.add_argument("--profile-directory", default="Default")

    parser = argparse.ArgumentParser(
        description="Create or diagnose a macOS Chrome Ask Gemini launcher."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    diagnose_parser = sub.add_parser(
        "diagnose",
        parents=[shared],
        help="Print Chrome/Gemini diagnostics.",
    )
    diagnose_parser.add_argument("--json", action="store_true")
    diagnose_parser.set_defaults(func=diagnose)

    install_parser = sub.add_parser(
        "install",
        parents=[shared],
        help="Create the launcher app and script.",
    )
    install_parser.add_argument("--app-name", default="Chrome Ask Gemini")
    install_parser.add_argument("--bundle-id", default="local.codex.chrome-ask-gemini")
    install_parser.add_argument("--app-dir", default=str(home() / "Applications"))
    install_parser.add_argument("--script-path", default=str(home() / "bin/chrome-ask-gemini"))
    install_parser.add_argument("--start-url", default="https://www.google.com/")
    install_parser.add_argument("--dock", dest="dock", action="store_true", default=False)
    install_parser.add_argument("--no-dock", dest="dock", action="store_false")
    install_parser.add_argument(
        "--vertical-tabs",
        choices=["auto", "on", "off"],
        default="auto",
        help="auto preserves an existing vertical-tabs preference.",
    )
    install_parser.add_argument(
        "--profile-prefs",
        dest="profile_prefs",
        action="store_true",
        default=True,
        help="Update safe Chrome profile prefs when Chrome is closed.",
    )
    install_parser.add_argument("--no-profile-prefs", dest="profile_prefs", action="store_false")
    install_parser.set_defaults(func=install)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
