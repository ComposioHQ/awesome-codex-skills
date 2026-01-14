<h1 align="center">Awesome Codex Skills</h1>

<p align="center">
<a href="https://platform.composio.dev/?utm_source=Github&utm_medium=Youtube&utm_campaign=2025-11&utm_content=AwesomeCodexSkills">

  <img width="1280" height="640" alt="Composio banner" src="codex_cover_image.png">
</a>
</p>

<p align="center">
  <a href="https://awesome.re">
    <img src="https://awesome.re/badge.svg" alt="Awesome" />
  </a>
  <a href="https://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome" />
  </a>
</p>
<div>
<p align="center">
  <a href="https://twitter.com/composio">
    <img src="https://img.shields.io/badge/Follow on X-000000?style=for-the-badge&logo=x&logoColor=white" alt="Follow on X" />
  </a>
  <a href="https://www.linkedin.com/company/composiohq/">
    <img src="https://img.shields.io/badge/Follow on LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="Follow on LinkedIn" />
  </a>
  <a href="https://discord.com/invite/composio">
    <img src="https://img.shields.io/badge/Join our Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Join our Discord" />
  </a>
  </p>
</div>

A curated list of practical Codex skills for automating workflows across the Codex CLI and API.

---

## Quickstart: Add Skills to Codex

### Install with the Skill Installer (recommended)

```bash
git clone https://github.com/ComposioHQ/awesome-codex-skills.git
cd awesome-codex-skills/awesome-codex-skills
# Install one or more skills into $CODEX_HOME/skills (defaults to ~/.codex/skills)
python skill-installer/scripts/install-skill-from-github.py --repo ComposioHQ/awesome-codex-skills --path meeting-notes-and-actions
```

The installer fetches the skill and places it in `$CODEX_HOME/skills/<skill-name>`. Restart Codex to pick up new skills.

### Manual install

1. Copy the desired skill folder (e.g., `./spreadsheet-formula-helper`) into `$CODEX_HOME/skills/` (defaults to `~/.codex/skills/`).
2. Restart Codex so it loads the new metadata.
3. In your next session, describe the task or mention the skill name; Codex will trigger matching skills based on their `description` frontmatter.

---

## Contents

- [What Are Codex Skills?](#what-are-codex-skills)
- [Skills](#skills)
  - [Development & Code Tools](#development--code-tools)
  - [Productivity & Collaboration](#productivity--collaboration)
  - [Communication & Writing](#communication--writing)
  - [Data & Analysis](#data--analysis)
  - [Meta & Utilities](#meta--utilities)
- [Using Skills in Codex](#using-skills-in-codex)
- [Creating Skills](#creating-skills)
- [Contributing](#contributing)
- [Join the Community](#join-the-community)

## What Are Codex Skills?

Codex skills are modular instruction bundles that tell Codex how to execute a task the way you want it done. Each skill lives in its own folder with a `SKILL.md` that includes metadata (name + description) and step-by-step guidance. Codex reads the metadata to decide when to trigger a skill and loads the body only after it fires, keeping context lean.

## Skills

### Development & Code Tools

- [create-plan/](./create-plan/) - Quickly draft concise execution plans for coding tasks.
- [gh-address-comments/](./gh-address-comments/) - Address review or issue comments on the open GitHub PR for the current branch using `gh`.
- [gh-fix-ci/](./gh-fix-ci/) - Inspect failing GitHub Actions checks, summarize failures, and propose fixes.
- [mcp-builder/](./mcp-builder/) - Build and evaluate MCP servers with best practices and an evaluation harness.
- [webapp-testing/](./webapp-testing/) - Run targeted web app tests and summarize results.

### Productivity & Collaboration

- [connect/](./connect/) - Connect Codex to 1000+ apps via Composio for real actions (Slack, GitHub, Notion, etc.).
- [connect-apps/](./connect-apps/) - Quickly wire up Composio app connections for actions and workflows.
- [linear/](./linear/) - Manage issues, projects, and team workflows in Linear.
- [meeting-insights-analyzer/](./meeting-insights-analyzer/) - Analyze meeting transcripts for themes, risks, and follow-ups.
- [meeting-notes-and-actions/](./meeting-notes-and-actions/) - Turn meeting transcripts into summaries with decisions and owner-tagged action items.
- [internal-comms/](./internal-comms/) - Craft internal announcements, updates, and stakeholder messaging.
- [invoice-organizer/](./invoice-organizer/) - Normalize and extract invoice data for tracking and reporting.
- [notion-knowledge-capture/](./notion-knowledge-capture/) - Convert chats or notes into structured Notion pages with proper linking.
- [notion-meeting-intelligence/](./notion-meeting-intelligence/) - Prepare meeting materials with Notion context plus Codex research.
- [notion-research-documentation/](./notion-research-documentation/) - Synthesize multiple Notion sources into briefs, comparisons, or reports with citations.
- [notion-spec-to-implementation/](./notion-spec-to-implementation/) - Turn Notion specs into implementation plans, tasks, and progress tracking.
- [support-ticket-triage/](./support-ticket-triage/) - Triage customer support tickets with categories, priority, next actions, and draft replies.
- [file-organizer/](./file-organizer/) - Organize, rename, and tidy files to keep workspaces clean.
- [skill-share/](./skill-share/) - Share skills and reusable instructions across teammates.

### Communication & Writing

- [email-draft-polish/](./email-draft-polish/) - Draft, rewrite, or condense emails for the right tone and audience.
- [changelog-generator/](./changelog-generator/) - Create clear changelogs from commits or summaries.
- [content-research-writer/](./content-research-writer/) - Research and draft content with sourced citations.
- [tailored-resume-generator/](./tailored-resume-generator/) - Tailor resumes to job descriptions with quantified impact.

### Data & Analysis

- [spreadsheet-formula-helper/](./spreadsheet-formula-helper/) - Write and debug spreadsheet formulas, pivots, and array formulas.
- [competitive-ads-extractor/](./competitive-ads-extractor/) - Analyze competitor ads and extract structured insights.
- [developer-growth-analysis/](./developer-growth-analysis/) - Analyze Codex chat history for coding patterns and learning gaps.
- [lead-research-assistant/](./lead-research-assistant/) - Research leads and enrich records with firmographic data.
- [domain-name-brainstormer/](./domain-name-brainstormer/) - Brainstorm available domain names with criteria and checks.
- [raffle-winner-picker/](./raffle-winner-picker/) - Randomly select winners with audit-friendly logs.
- [langsmith-fetch/](./langsmith-fetch/) - Pull LangSmith project/test data for analysis.

### Meta & Utilities

- [brand-guidelines/](./brand-guidelines/) - Apply OpenAI/Codex brand colors and typography to artifacts.
- [canvas-design/](./canvas-design/) - Generate structured canvas layouts and design artifacts.
- [image-enhancer/](./image-enhancer/) - Upscale and refine images with configurable presets.
- [slack-gif-creator/](./slack-gif-creator/) - Generate GIFs for Slack with captions and styling.
- [theme-factory/](./theme-factory/) - Create reusable theme tokens and palettes.
- [video-downloader/](./video-downloader/) - Download and prepare videos for offline review.
- [template-skill/](./template-skill/) - Starter template for building new skills.
- [skill-installer/](./skill-installer/) - Helper scripts to install skills from curated lists or GitHub paths.
- [skill-creator/](./skill-creator/) - Guidance for building effective Codex skills with progressive disclosure.

## Using Skills in Codex

- Skills live in `$CODEX_HOME/skills` (default `~/.codex/skills`). Each subfolder needs a `SKILL.md` with `name` and `description` frontmatter.
- After installing or updating a skill, restart Codex so it reloads metadata.
- In a session, describe the task naturally; Codex auto-triggers skills whose descriptions match the request. You can also mention a skill by name if you want it considered.
- To verify installation, list installed skills (`ls ~/.codex/skills`) and inspect metadata (`head ~/.codex/skills/<skill>/SKILL.md`).

## Creating Skills

Skill layout:

```
skill-name/
├── SKILL.md          # Required: instructions + YAML frontmatter
├── scripts/          # Optional: helper scripts for deterministic steps
├── references/       # Optional: long-form docs loaded only when needed
└── assets/           # Optional: templates or files used in outputs
```

Basic SKILL.md template:

```markdown
---
name: my-skill-name
description: What the skill does and when Codex should use it.
---

# My Skill Name

Clear instructions and steps for Codex to execute the task.
```

Best practices:

- Keep the `description` exhaustive about when to trigger; keep the body focused on execution steps.
- Use progressive disclosure: put detailed references in `references/` and call them out from `SKILL.md` only when needed.
- Include scripts for repeatable or deterministic operations; mention when Codex should run them.
- Avoid extra docs (README, changelog) inside the skill folder to keep context lean.

## Contributing

PRs welcome. Add real, reusable skills, keep descriptions precise, and include any needed scripts or references. If you add new skills, ensure the `description` clearly states when Codex should trigger and test that metadata fits within context limits.

## Join the Community

- [Join our Discord](https://discord.com/invite/composio) - Chat with other developers building Codex skills.
- [Follow on X](https://twitter.com/composio) - Updates on new skills and features.
- Questions? [support@composio.dev](mailto:support@composio.dev)

---

<p align="center">
  <b>Join thousands of developers building agents that ship</b>
</p>

<p align="center">
  <a href="https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeCodexSkills">
    <img src="https://img.shields.io/badge/Get_Started_Free-4F46E5?style=for-the-badge" alt="Get Started"/>
  </a>
</p>
