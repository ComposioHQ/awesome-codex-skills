---
name: software-graph-analysis
description: Use Ontoly to build or query a deterministic Software Graph before searching files. Use when the user asks to explain a repository, trace a route/request flow, find dependencies, inspect services/controllers/modules, audit configuration or environment variables, analyze impact, or use Ontoly MCP. Do not use for generic architecture advice without repository evidence or for changing compiler behavior.
metadata:
  short-description: Analyze codebases with Ontoly's Software Graph
---

# Software Graph Analysis

Use this skill when a coding task needs repository understanding grounded in Ontoly's deterministic Software Graph.

Ontoly should provide the software knowledge. The agent should provide the workflow: verify the graph, query it, cite evidence, then inspect source only when the graph cannot answer.

## Workflow

1. Check whether the repository already has Ontoly output, such as `.ontoly/`, `SoftwareGraph.json`, diagnostics, statistics, or MCP configuration.
2. If no usable graph exists, run:

   ```bash
   ontoly build .
   ```

3. Check graph trust, diagnostics, graph hash, framework detection, and build timestamp.
4. Prefer Ontoly MCP capabilities or CLI graph queries before using repository-wide search.
5. Answer with evidence from the graph: node IDs, node kinds, relationships, source locations, diagnostics, and confidence.
6. Search files only when graph evidence is missing, stale, ambiguous, or contradicted by diagnostics.

## Common Questions

Use Ontoly for questions like:

- "Explain this repository."
- "Trace `POST /login`."
- "Which service owns authentication?"
- "What depends on `UserRepository`?"
- "What breaks if I remove this module?"
- "Where is `DATABASE_URL` used?"
- "Which packages depend on this package?"
- "Show unresolved imports, cycles, or dead code."

## Capability Mapping

| Task | Ontoly capability or query |
| --- | --- |
| Repository overview | ArchitectureSummary |
| Route/request trace | TraceExecution |
| Dependency tree | FindDependencies |
| Impact analysis | ImpactAnalysis |
| Configuration usage | FindConfigurationUsage |
| Authentication flow | FindAuthenticationFlow |
| Authorization checks | FindAuthorization |
| Framework coverage | FrameworkReport |
| Dead code review | FindDeadCode |

If the named capability is unavailable, use the closest deterministic graph query and state the fallback.

## Evidence Rules

Every answer should include:

- The graph artifact or MCP response used.
- Node IDs and relationship names when available.
- Source locations when available.
- Diagnostics that reduce confidence.
- A clear distinction between measured graph facts and inferred observations.

Do not invent graph facts. If Ontoly cannot answer, say what is missing and what fallback evidence was inspected.

## Troubleshooting

If `ontoly build .` fails, report the command, exit code, and diagnostic summary before falling back to source inspection.

If MCP is unavailable, query the persisted graph JSON or Ontoly CLI output and state that MCP was unavailable.

If multiple graph nodes match the user's target, show candidates with IDs, kinds, and locations rather than silently choosing one.
