---
name: codex-profile-switching
description: Use when setting up, switching, auditing, or troubleshooting Codex CLI or Codex Desktop profiles, CODEX_HOME isolation, multi-account Codex workflows, or codex-profile installs.
---

# Codex Profile Switching

Use this skill when a user needs help separating Codex CLI or Codex Desktop
accounts, local state, sessions, plugins, connectors, logs, or settings across
work, personal, education, and client contexts.

## When To Use

- The user mentions `codex-profile`, `codex-profiles`, `CODEX_HOME`, Codex
  account switching, Codex Desktop profiles, or multiple Codex accounts.
- The user is copying or considering copying `auth.json` files.
- The user wants to inspect which Codex profile is logged in or where a profile
  lives on disk.
- The user needs a safe setup for separate work, personal, education, or client
  Codex environments.

Do not use this for provider API keys, SSH keys, GitHub CLI accounts, npm
tokens, AWS profiles, browser sessions, or OS-level sandboxing except to explain
that `CODEX_HOME` isolation does not cover those systems.

## Core Guidance

Prefer whole-home isolation through `CODEX_HOME` instead of copying token files.
`codex-profile` wraps that pattern so each profile has separate Codex auth,
config, sessions, plugins, connector state, caches, and logs.

Canonical project:

```sh
https://github.com/Ducksss/codex-profiles
```

Install options:

```sh
npm install -g codex-profile
brew install Ducksss/tap/codex-profile
```

The npm package is singular: `codex-profile`. It installs both
`codex-profile` and `codex-profiles` commands.

## Workflow

1. Confirm whether the user wants CLI, Desktop, or both.
2. Use read-only inspection first:

   ```sh
   codex-profile doctor
   codex-profile list
   codex-profile status
   codex-profile path personal
   ```

3. Create profile homes before login when needed:

   ```sh
   codex-profile init personal
   codex-profile init work
   ```

4. Start login or app launch only when requested:

   ```sh
   codex-profile login personal
   codex-profile cli work
   codex-profile app personal
   ```

5. For automation, prefer JSON output where available:

   ```sh
   codex-profile status --json
   codex-profile doctor --json
   ```

## Safety Rules

- Do not print, copy, edit, or move Codex token files.
- Do not recommend swapping `auth.json`; explain why whole `CODEX_HOME`
  isolation is safer.
- Ask for exact confirmation before removing a profile.
- Treat `default` specially: it maps to `~/.codex`; named profiles map to
  `~/.codex-<profile>`.
- Make clear that Codex profile isolation does not isolate unrelated tools such
  as GitHub CLI, SSH, npm, AWS, or browser credentials.

## Troubleshooting

- If a profile appears missing, run `codex-profile path <name>` and inspect that
  directory before recreating it.
- If Desktop launches with the wrong account, verify the app was launched via
  `codex-profile app <profile>` and not directly from the dock.
- If login state is unclear, use `codex-profile status <profile>` before taking
  action.
- If shell completions or upgrades are involved, run `codex-profile help` and
  `codex-profile doctor` to match the installed version's supported commands.

## Example Prompts

```text
Set up separate personal and work Codex profiles.
```

```text
Check which Codex profiles exist and which ones are logged in.
```

```text
Help me launch Codex Desktop with my client-a profile without touching auth.json.
```
