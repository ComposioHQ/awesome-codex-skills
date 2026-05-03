---
name: swarmclaw
description: Use when setting up, operating, or troubleshooting SwarmClaw, the self-hosted runtime for persistent agent teams with memory, schedules, skills, delegation, MCP support, and local or Docker deployment.
---

# SwarmClaw

SwarmClaw is a self-hosted runtime for autonomous agent teams. It provides a local dashboard, durable memory, runtime skills, schedules, delegation, provider routing, MCP client/server support, and optional desktop, CLI, or Docker deployment.

Use this skill when the user wants to:

- install or launch SwarmClaw
- create or inspect persistent agents
- configure delegated CLI backends and provider credentials
- expose or consume MCP tools
- troubleshoot local runtime, provider, or dashboard issues
- design a workflow that needs scheduled or long-running agent coordination

## Project Links

- Website: https://swarmclaw.ai
- Docs: https://swarmclaw.ai/docs
- GitHub: https://github.com/swarmclawai/swarmclaw
- Package: https://www.npmjs.com/package/@swarmclawai/swarmclaw

## Install and Launch

For a global CLI install:

```bash
npm i -g @swarmclawai/swarmclaw
swarmclaw
```

Running `swarmclaw` starts the local server on `http://localhost:3456`.

For a repo checkout:

```bash
git clone https://github.com/swarmclawai/swarmclaw.git
cd swarmclaw
nvm use
npm run quickstart
```

For Docker:

```bash
git clone https://github.com/swarmclawai/swarmclaw.git
cd swarmclaw
mkdir -p data
touch .env.local
docker compose up -d --build
```

Then open `http://localhost:3456`.

## Operating Rules

- Prefer the local dashboard for creating agents, reviewing sessions, configuring providers, and managing credentials.
- Keep credentials in the SwarmClaw credential system or environment files. Do not paste secrets into prompts, logs, or committed files.
- Treat memory as durable state. Store stable preferences, project facts, decisions, and reusable lessons, not one-off scratch notes.
- Use skills for reusable procedures and tool-specific operating knowledge.
- Use delegation when a task can be isolated and given to a specialist agent or CLI backend.
- Use schedules for recurring checks, maintenance tasks, monitoring, or periodic research.
- Verify runtime state through the dashboard, API health checks, or CLI output before assuming an agent is running.

## Common Checks

Check the dashboard:

```text
http://localhost:3456
```

Check server health:

```bash
curl -sS http://127.0.0.1:3456/api/healthz
```

Inspect running processes when the server does not respond:

```bash
ps -Ao pid,ppid,stat,etime,command | grep -i swarmclaw
```

## MCP and Provider Guidance

SwarmClaw can act as part of an MCP workflow and can route work across local or remote providers. When configuring integrations:

- Confirm whether the user needs SwarmClaw to consume MCP servers, expose tools, or both.
- Keep MCP server credentials out of source control.
- Prefer local provider CLIs for private workspace tasks when the user wants local-first execution.
- Use hosted providers only when the workflow needs their models, APIs, or remote execution.
- Record working provider and MCP configuration choices in project docs when they affect repeatable setup.

## Troubleshooting

When SwarmClaw is not starting or an agent is not responding:

1. Confirm Node.js 22.6+ and npm 10+ are available.
2. Confirm the server is listening on `http://localhost:3456`.
3. Check whether another process already owns port `3456`.
4. Review `.env.local` and credential configuration without exposing secret values.
5. If using Docker, check `docker compose ps` and `docker compose logs`.
6. Re-run the relevant quickstart or build command after fixing dependency or environment issues.

For packaged desktop issues, use the platform-specific installer guidance in the upstream README and docs.
