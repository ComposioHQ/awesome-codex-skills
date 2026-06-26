---
name: chrome-ask-gemini-launcher
description: Create, diagnose, and repair a macOS Google Chrome launcher that starts Chrome with Gemini in Chrome / Ask Gemini feature flags. Use when a user says the Ask Gemini button is missing, Gemini in Chrome disappears after restart, AI Innovations is absent, Chrome needs a Dock launcher for Ask Gemini, or Chrome vertical tabs should be preserved while enabling Ask Gemini. Focuses on macOS Chrome and avoids modifying the official Google Chrome.app bundle.
---

# Chrome Ask Gemini Launcher

## Workflow

1. Confirm the user is on macOS with Google Chrome installed at `/Applications/Google Chrome.app` unless they provide another path.
2. Run diagnostics first:

```bash
python3 scripts/install_macos_launcher.py diagnose
```

3. If the user wants the launcher, install it:

```bash
python3 scripts/install_macos_launcher.py install --dock
```

4. If the user uses Chrome vertical tabs, preserve them with `--vertical-tabs auto` (default) or force them with `--vertical-tabs on`.
5. Do not patch or replace `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`. That fragile approach can trigger Google's "Verify it's you" flow and can be undone by Chrome updates.
6. After install, verify with:

```bash
python3 scripts/install_macos_launcher.py diagnose
```

## Installer

Use `scripts/install_macos_launcher.py` for deterministic work. It can:

- Create `~/bin/chrome-ask-gemini`.
- Create `~/Applications/Chrome Ask Gemini.app`.
- Generate an app icon from Chrome's icon, with an `AI` badge when Pillow is available.
- Add the launcher to the Dock when `--dock` is passed.
- Preserve existing vertical tabs when the profile already has `vertical_tabs.enabled = true`.
- Print profile and feature-state diagnostics without changing Chrome.

Useful examples:

```bash
# Create launcher and add it to Dock.
python3 scripts/install_macos_launcher.py install --dock

# Preserve vertical tabs if already enabled.
python3 scripts/install_macos_launcher.py install --dock --vertical-tabs auto

# Force vertical tabs on for users who want tabs on the left.
python3 scripts/install_macos_launcher.py install --dock --vertical-tabs on

# Use a non-default Chrome profile.
python3 scripts/install_macos_launcher.py install --profile-directory "Profile 2" --dock

# Test in a temporary location without touching Dock.
python3 scripts/install_macos_launcher.py install --app-dir /tmp --script-path /tmp/chrome-ask-gemini --no-dock --no-profile-prefs
```

## Safety Rules

- Keep the launcher separate from the official Chrome app.
- Tell the user the workaround depends on Chrome feature flags and may need updates after Chrome changes internal feature names.
- Do not complete Google identity, age, CAPTCHA, or account verification prompts for the user.
- If Chrome is already running without the required flags, the generated launcher quits and reopens Chrome so the flags take effect.
- If the Ask Gemini button still does not appear, read `references/troubleshooting.md`.

## Output

Report the created paths, whether the Dock was updated, and the verification evidence:

- The launcher script path.
- The `.app` path.
- Whether the Chrome process includes `Glic` feature flags.
- Whether `VerticalTabs` was included or preserved.
