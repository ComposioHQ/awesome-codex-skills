#!/usr/bin/env bash
# Bootstrap TokRepo agent memory for this project.
# Writes .tokrepo/agent.json (machine-readable contract) + an AGENTS.md
# block that future Codex sessions will load before generating reusable
# artifacts. Safe to re-run; idempotent.
set -euo pipefail
npx -y tokrepo@latest init-agent --target codex
echo ""
echo "Done. Restart Codex so the new AGENTS.md + .tokrepo/agent.json are loaded."
