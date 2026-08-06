---
name: tinyfish-mcp
description: Use TinyFish MCP when Codex needs to search the web, browse websites, extract clean page content, run multi-step web automation, batch multiple runs, or create browser sessions through the TinyFish MCP server.
---

# TinyFish MCP — Web Search, Fetch, and Browser Automation

Use this skill when you need TinyFish's MCP server to handle public web discovery, page extraction, or browser automation from an MCP-compatible assistant.

## Prerequisites

Install the TinyFish MCP server in Codex with one command:

```bash
npx -y install-mcp@latest https://agent.tinyfish.ai/mcp --client codex
```

The installer writes the server config to `~/.codex/config.toml` and walks through the OAuth flow. Restart Codex after install so the tools are discovered.

Other clients work the same way — swap `codex` for `claude-code`, `claude`, `cursor`, or `windsurf`.

If you prefer to configure it manually, add this to your MCP client config:

```json
{
  "mcpServers": {
    "tinyfish": {
      "url": "https://agent.tinyfish.ai/mcp"
    }
  }
}
```

Notes:
- TinyFish MCP uses **OAuth 2.1**.
- The first connection opens a browser for authentication.
- A raw unauthenticated probe can return `401`; that is expected until OAuth completes.
- After adding or changing the server, restart the client so the tools are discovered.

## Available Tools

### Web Automation
- `run_web_automation` — run a multi-step automation from a URL and a natural-language goal
- `run_web_automation_async` — submit a long run and return a run ID immediately
- `get_run` — inspect one automation run
- `list_runs` — list prior automation runs
- `cancel_run` — cancel a run

### Batch Automation
- `batch_create` — start multiple automations at once
- `batch_status` — check the status of multiple runs
- `batch_cancel` — cancel multiple runs

### Web Search
- `search` — search the web and return structured results with titles, snippets, and URLs
- `get_search_usage` — inspect search usage history

### Content Extraction
- `fetch_content` — fetch and clean page content from one or more URLs
- `list_fetch_usage` — inspect fetch usage history

### Browser Sessions
- `create_browser_session` — create a remote browser session for direct CDP-based control
- `list_browser_sessions` — inspect browser sessions

## Usage Patterns

- **Discover sources**: use `search` when you need candidate URLs or current results.
- **Read pages**: use `fetch_content` when you already have URLs and want clean page text.
- **Interact with a site**: use `run_web_automation` when clicks, form fills, or multi-step browsing are needed.
- **Run long jobs**: use `run_web_automation_async` or `batch_create` for longer or parallel work.
- **Control a browser directly**: use `create_browser_session` when the task needs Playwright, Puppeteer, Selenium, or manual CDP control.

## Practical Rules

- Prefer `search` before `fetch_content` when you do not yet know the right URLs.
- Prefer `fetch_content` over automation when you only need page text.
- Prefer `run_web_automation` over ad hoc scraping when the site needs interaction.
- Prefer `batch_create` for independent pages that can be processed in parallel.
- Keep each run goal narrow and specific.
- Keep source URLs attached to summaries and findings.
- For bot-protected sites (Cloudflare, DataDome, CAPTCHAs, "Access Denied" responses), pass `browser_profile: "stealth"` to `run_web_automation`.

## Common Pitfalls

1. **Trying to use TinyFish MCP like a static API-key REST tool.**
   - Fix: TinyFish MCP is OAuth-based; connect through the MCP client.

2. **Using `run_web_automation` when page text is enough.**
   - Fix: use `fetch_content` for read-only extraction.

3. **Fetching before you know what to fetch.**
   - Fix: search first, then fetch the best candidates.

4. **Using browser sessions when a simple fetch is enough.**
   - Fix: reserve `create_browser_session` for advanced direct-control workflows.

5. **Losing provenance.**
   - Fix: keep the source URL next to every important claim.

## Verification Checklist

- [ ] TinyFish MCP is configured in the client
- [ ] OAuth has completed successfully
- [ ] The right tool was chosen: search, fetch, automation, batch, or browser session
- [ ] Important claims are tied to source URLs
- [ ] Browser automation was only used when interaction was actually needed
