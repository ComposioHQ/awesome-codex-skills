# TokRepo MCP tool catalog

Loaded only when Codex asks for the full tool list. The 12 tools the
TokRepo MCP server exposes:

## Read-only (no confirmation needed)

| Tool | Purpose |
|---|---|
| `tokrepo_discover` | Planning-time capability discovery. Returns ranked candidates with trust + fit + next-call hints. |
| `tokrepo_search` | Filtered search by query / kind / target / policy. |
| `tokrepo_detail` | Read an asset's files, metadata, trust score. |
| `tokrepo_verify` | Trust + permission envelope + install plan hash + policy gate. |
| `tokrepo_install_plan` | Typed install plan (preconditions, actions, rollback, verification). |

## Lifecycle (default `dry_run: true`)

| Tool | Purpose |
|---|---|
| `tokrepo_codex_install` | Install or stage an asset for Codex. |
| `tokrepo_installed` | List locally installed assets. |
| `tokrepo_update` | Check / apply updates. |
| `tokrepo_uninstall` | Remove an asset. |
| `tokrepo_rollback` | Roll back a previous install session. |

## Supply (default safe; never auto-publishes)

| Tool | Purpose |
|---|---|
| `tokrepo_handoff_plan` | Inspect reusable local work and return a packaging plan. |
| `tokrepo_push` | Publish explicit files after human confirmation. |

## Verification commands

```bash
# Check version + hosted-MCP reachability
npx -y tokrepo@latest whoami
curl -s https://tokrepo.com/.well-known/tool-catalog.json | jq '.tools[].name'

# Run a real discovery against production
npx -y tokrepo@latest agent-check "audit this repo for SQL injection" --offline --json
```
