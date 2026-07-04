---
name: gemini-web-mcp
description: "Use when working in the gemini-web-mcp repository or using its Gemini Web MCP/skill servers: inspect the tool manifest, choose safe Gemini Web tools, manage chat history and native notebooks, validate Pro Web capability coverage, generate and verify media deliverables, update docs/tests/evaluations, or avoid unsafe destructive/private-account operations."
---

# Gemini Web MCP

Use this skill for this repository's Gemini Web MCP server and low-token skill server.

## Start Here

1. Prefer `gemini_get_tool_manifest` before choosing primary-server tools. It is always exposed by `src.server`, even when `GEMINI_TOOLS=core` or `GEMINI_TOOLS=prompts`.
2. Check manifest `current_enabled`, `groups`, and `workflows`; do not hard-code tool counts because the static manifest can include groups not loaded in the current process.
3. On the low-token server, prefer auth-free `account(action="manifest")` and `account(action="capabilities")` before account calls that initialize Gemini.
4. Prefer read-only discovery first: `gemini_doctor`, manifest/capabilities, `gemini_probe_web_features`, metadata-only history search, profile diagnostics, and inventory/list tools.
5. Treat `privacy=reads_private_chat_text` and other private text tools as explicit-user-intent tools: `gemini_read_chat`, `gemini_export_chat`, `gemini_search_chats(scan_turns=true)`, and research-report create actions that read chat text.
6. Treat destructive tools as requiring explicit user intent: `gemini_delete_chat`, `gemini_cleanup_test_artifacts(dry_run=false)`, `gemini_delete_scheduled_action`, `gemini_reset_session`, `gemini_manage_gems(action="delete")`, and prompt deletion.

## Tool Surfaces

- Primary MCP server: `src.server`
  - Use `GEMINI_TOOLS=model` or `chat` when an agent only needs to call Gemini models.
  - Use `GEMINI_TOOLS=history` when an agent only needs `gemini_history` for list/scan/search/read/export chat history.
  - Use `GEMINI_TOOLS=history-organize` when an agent needs `gemini_history`, `gemini_notebooks`, and explicit chat-to-Notebook moves.
  - Use `GEMINI_TOOLS=account-read` when an agent only needs `gemini_account_inventory` for read-only Web surface inventory.
  - Use `GEMINI_TOOLS=scheduled-admin` only for explicitly authorized scheduled-action create/delete workflows.
  - Default `GEMINI_TOOLS=core` remains the broad content workflow: chat, media, files, and research.
  - `GEMINI_TOOLS=all` is the full maintenance/verification surface, not a good default for general agents.
  - `GEMINI_TOOLS=prompts` adds local prompt management plus always-on manifest/cookie helpers.
- Low-token skill server: `src.skill_server`
  - Use `account(action="manifest")` for compact tool guidance.
  - Use `account(action="capabilities")` for the static Web capability map without cookies.
  - Use `account(action="features|links|usage|library|notebooks|scheduled|modes")` for compact account-surface inventory.
  - Use `history(action="list|search|read|export|delete")` for chat history.
  - Use `cleanup(dry_run=true)` before deleting test chats or scheduled actions by marker.
  - Use `scheduled(action="list|get|create|delete")` for compact scheduled-action workflows.
  - Use `create(type="music", model="pro")` or primary `gemini_generate_music` for Lyria 3 Pro music requests.
  - Use `doctor(validate_browser=false)` for low-cost local preflight before live account workflows.
  - Use `cookie(action="profiles")` before `cookie(action="get", profile="...")` when Chrome has multiple signed-in profiles.

## Chat History Workflow

1. Deep-scan metadata sources when completeness matters:
   - `gemini_history(action="scan", limit=..., offset=..., response_format="json")`
2. List or search metadata first:
   - `gemini_history(action="list", limit=..., offset=..., response_format="json")`
   - `gemini_history(action="search", query=..., scan_turns=false, response_format="json")`
3. Only scan turn text when the user asks for content search:
   - `gemini_history(action="search", query=..., scan_turns=true, turns_per_chat=..., max_chars_per_turn=...)`
4. Read/export one selected chat only after the user has indicated the target:
   - `gemini_history(action="read", chat_id=...)`
   - `gemini_history(action="export", chat_id=..., response_format="markdown"|"json")`
5. Move chats to native notebooks only after identifying both target chat and notebook:
   - `gemini_notebooks(action="list", ...)`
   - `gemini_move_chat_to_notebook(chat_id=..., notebook_id=...)`
   - `gemini_notebooks(action="chats", notebook_id=...)`
6. Delete only with explicit confirmation:
   - `gemini_delete_chat(chat_id=...)`

## Web Pro Coverage Rules

- `gemini_get_web_capabilities` is the static observed Pro Web surface map.
- `gemini_probe_web_features` checks observed read-only RPC reachability and must not expose raw private RPC bodies.
- Use `gemini_account_inventory(surface=...)` or the manifest `web_surface_inventory` workflow for read-only account inventory: public links, usage limits, native notebooks, library capabilities, scheduled actions, and tool mode status.
- Treat `gemini_list_library_capabilities` as localized template/capability discovery, not private Library asset export.
- Treat `gemini_get_tool_mode_status` as a read-only Canvas/Guided Learning mode-status probe; Canvas document mutation remains disabled.
- Guided Learning is exposed through chat `learning_mode`; prefer this over UI assumptions.
- Keep Drive picker, Canvas mutation, settings mutation, memory import mutation, public-link mutation, and unsupported scheduled-action recurrence/edit/toggle variants disabled until stable RPC contracts and explicit user authorization exist.

## Media Workflow

- For music/video/image generation requests, use the MCP tool path and finish only when the tool reports saved local media files or an explicit export failure.
- For Lyria 3 Pro/fullsong claims, verify raw backend markers and saved media duration; do not trust wrapper labels, model names, or chat prose alone.
- `gemini_generate_music` can recover media from raw chat payloads even when `response.media` is empty; inspect returned file paths and duration metadata before summarizing success.

## Scheduled Actions

- Use observed daily create, registry list, by-id get, and explicit delete by id through `gemini_create_scheduled_action`, `gemini_list_scheduled_actions`, `gemini_get_scheduled_action`, and `gemini_delete_scheduled_action`.
- Refresh Chrome cookies first when account context matters. If the registry is unexpectedly empty, call `gemini_list_browser_cookie_profiles`, then `gemini_get_cookie_from_browser(profile="...")` for the profile with Gemini cookies or scheduled registry entries.
- After create/delete, check `verification_status`; after create also check `readable_by_id_after_create`, and after delete check `deleted_by_id_after_delete` or `task_state_after_delete=deleted` before claiming the task is gone.

## Validation

Before finishing changes, run:

```bash
./.venv/bin/pytest -q
./.venv/bin/python -m py_compile src/tools/annotations.py src/tools/chat.py src/tools/media.py src/tools/file.py src/tools/research.py src/tools/prompts.py src/tools/manage.py src/server.py src/skill_server.py src/client_wrapper.py src/thinking_client.py src/constants.py
git diff --check
```

When changing manifest or capability metadata, also verify:

```bash
GEMINI_TOOLS=core ./.venv/bin/python - <<'PY'
import asyncio
from src.server import mcp
async def main():
    tools = await mcp.list_tools()
    print(len(tools), [t.name for t in tools if t.annotations is None])
asyncio.run(main())
PY
```

For skill-only changes, at minimum run the skill validator for both the local
project copy and the public repo skill copy:

```bash
for path in .codex/skills/gemini-web-mcp .agents/skills/gemini-web-mcp; do
  ./.venv/bin/python /Users/jack/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$path"
done
```

Keep `evaluations/gemini_web_mcp_contract.xml` aligned with `gemini_get_tool_manifest` and `gemini_get_web_capabilities`.
