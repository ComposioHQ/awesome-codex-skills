# Error handling

## Usage or subscription errors

If MCP returns usage/subscription/billing errors, tell the user what to do:

> HookRadar could not complete this because the workspace needs billing or usage attention. Open https://platform.hookradar.net/billing to manage your subscription and limits, then retry.

Do not blindly retry paid/write actions when usage is exhausted.

## Pending async jobs

For `add_*` and `analyze_*`:

- `started`: job is running. Poll `get_task_status` only briefly.
- `already_running`: do not start another job; read current data or wait.
- `already_done`: read analysis/result now.
- `not_applicable` or `failed`: terminal; explain the message.

If results are not ready, say the source/analysis is still collecting and avoid claiming that top results exist.

## Empty result after adding a source

Immediately empty results usually mean the parser has not finished. Say that clearly and suggest checking again soon.

## Auth/team errors

If no teams exist, offer `create_team`. If the team slug is unknown, call `list_teams` and ask the user to pick.
