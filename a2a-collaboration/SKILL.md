---
name: a2a-collaboration
description: Standardized Agent-to-Agent (A2A) communication and collaboration. Enable Codex to interact with other agents using a common language for discovery, negotiation, and long-running tasks.
---

# A2A Collaboration

Enable Codex to communicate and collaborate with other gen AI agents built on diverse frameworks.

## Why Use A2A?

The [Agent2Agent (A2A) protocol](https://github.com/a2aproject/A2A) addresses the challenge of interoperability between opaque agentic applications. 

With this skill, Codex can:
- **Discover** other agents' capabilities via Agent Cards.
- **Collaborate** securely on long-running tasks.
- **Operate** without exposing internal memory or tools.

## Enabling A2A for Codex

To enable full A2A Protocol support for Codex, use the [Codex-A2A](https://github.com/liujuanjuan1984/codex-a2a).

### 1. Setup the A2A Implementation

Clone and run the A2A implementation that bridges Codex to A2A interfaces:

```bash
git clone https://github.com/liujuanjuan1984/codex-a2a.git
cd codex-a2a
# Follow installation steps in their repository
python -m pip install -r requirements.txt
python main.py
```

### 2. Interaction Methods

Once running, Codex is exposed through:
- **A2A HTTP+JSON endpoints**: `/v1/message:send`, `/v1/message:stream`
- **A2A JSON-RPC**: For standard methods and discovery.

## Use Cases

### Multi-Agent Workflows
Codex can now be part of a larger team where it acts as a specialized coding agent, receiving tasks from a primary orchestrator via A2A.

### Peer-to-Peer Task Delegation
Codex can delegate sub-tasks (e.g., specific data research) to other A2A-compatible agents and receive results asynchronously.
