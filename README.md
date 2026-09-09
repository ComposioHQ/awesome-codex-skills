<h1 align="center">Awesome Codex Skills</h1>

<p align="center">
<a href="https://dashboard.composio.dev/login?utm_source=Github&utm_medium=Youtube&utm_campaign=2025-11&utm_content=AwesomeCodexSkills">

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

## Give your skills real-world actions

Skills tell your agent **how** to work. An MCP Gateway gives it secure access to the tools it needs.

Composio [MCP Gateway](https://composio.dev/mcp-gateway) provides a single MCP endpoint for 1,000+ integrations with built-in authentication, team-based access controls, audit logs, and production-ready reliability.

---

## Quickstart: Add Skills to Codex

### Install with the Skill Installer (recommended)

```bash
git clone https://github.com/ComposioHQ/awesome-codex-skills.git
cd awesome-codex-skills
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

- [Bernstein](https://github.com/chernistry/bernstein) - Multi-agent orchestrator with Codex CLI adapter. Runs parallel Codex agents in isolated git worktrees with quality gates.
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

- [brooks-lint](https://github.com/hyhmrright/brooks-lint) - AI code reviews grounded in six classic engineering books — decay risk diagnostics with book citations, severity labels, and four analysis modes (PR review, architecture audit, tech debt, test quality). Install: `python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo hyhmrright/brooks-lint --path skills/brooks-lint --name brooks-lint`
- [bringyour-migration-auditor](https://github.com/unitedideas/bringyour-mcp/tree/main/skills/bringyour-migration-auditor) - Audit Claude Code to Codex harness migrations for AGENTS.md/CLAUDE.md scope, hooks, MCP config, skills, secrets, and validation notes. Install: `python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo unitedideas/bringyour-mcp --path skills/bringyour-migration-auditor --name bringyour-migration-auditor`
- [codebase-migrate/](./codebase-migrate/) - Run large codebase migrations and multi-file refactors in reviewable batches with CI verification.
- [codebase-recon](https://github.com/yujiachen-y/codebase-recon-skill) - Analyze git history to understand a codebase before reading any code — surfaces hotspots, bug magnets, bus factor, momentum, and high-risk files (hotspot ∩ bug-magnet) via auto-scaled analysis. Install: `python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo yujiachen-y/codebase-recon-skill --path skills/codebase-recon --name codebase-recon`
- [create-plan/](./create-plan/) - Quickly draft concise execution plans for coding tasks.
- [deploy-pipeline/](./deploy-pipeline/) - End-to-end Stripe → Supabase → Vercel release pipelines with verify and rollback.
- [Emdash Skills](https://github.com/megabytespace/claude-skills) - 14-category autonomous product-building OS: CF Workers + Hono + Angular + D1 + Stripe. One-line prompts to deployed SaaS with 94 reference docs, 18 agents, and Codex-native `.agents/skills/` support.
- [gh-address-comments/](./gh-address-comments/) - Address review or issue comments on the open GitHub PR for the current branch using `gh`.
- [gh-fix-ci/](./gh-fix-ci/) - Inspect failing GitHub Actions checks, summarize failures, and propose fixes.
- [mcp-builder/](./mcp-builder/) - Build and evaluate MCP servers with best practices and an evaluation harness.
- [pr-review-ci-fix/](./pr-review-ci-fix/) - Automated GitHub/GitLab PR review plus CI auto-fix loop via the Composio CLI.
- [sentry-triage/](./sentry-triage/) - Diagnose Sentry issues by mapping stack frames to local source — no copy-paste.
- [webapp-testing/](./webapp-testing/) - Run targeted web app tests and summarize results.
- [AuraKit](https://github.com/smorky850612/Aurakit) - All-in-one skill framework: 46 modes, 23 sub-agents, 6-layer OWASP security, 10 lifecycle hooks, ~55% token savings. Install: `npx @smorky85/aurakit`
- [Vibe-Skills](https://github.com/foryourhealth111-pixel/Vibe-Skills) - Governed Codex skill harness for staged, test-driven work: routes 340+ skills through requirement freeze, plan approval, execution, verification evidence, and cross-session memory.
- [polywave](https://github.com/blackwell-systems/polywave-codex) - Parallel agent coordination with structural merge safety. Scout decomposes, Wave agents implement in isolated worktrees with disjoint file ownership. Same protocol on Claude Code and Codex.

### Productivity & Collaboration

- [connect/](./connect/) - Connect Codex to 1000+ apps via the Composio CLI for real actions (Slack, GitHub, Notion, etc.).
- [connect-apps/](./connect-apps/) - Wire up Composio CLI connections for Claude and kick off app workflows from the shell.
- [issue-triage/](./issue-triage/) - Triage Linear or Jira backlogs and run bug sweeps from the terminal.
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
- [paperjsx/](./paperjsx/) - Generate PPTX presentations, DOCX documents, XLSX spreadsheets, and PDF invoices/reports/charts from structured JSON. Runs locally via `@paperjsx/mcp-server` — no API key, no network calls.
- [skill-share/](./skill-share/) - Share skills and reusable instructions across teammates.
- [Taisly Agent Kit](https://github.com/taisly/agent) - Publish approved short-form videos from Codex with a bundled skill, CLI, and remote MCP server for TikTok, Instagram Reels, YouTube Shorts, X, and Facebook.

### Communication & Writing
- [codex-sms-verification](https://github.com/virtualsms-io/codex-sms-verification) - External repo: real-SIM SMS verification for AI agents via VirtualSMS MCP. 145+ countries, 2000+ services, both hosted (mcp.virtualsms.io) and local stdio transports.

- [email-draft-polish/](./email-draft-polish/) - Draft, rewrite, or condense emails for the right tone and audience.
- [changelog-generator/](./changelog-generator/) - Create clear changelogs from commits or summaries.
- [content-research-writer/](./content-research-writer/) - Research and draft content with sourced citations.
- [diasporic-intelligence](https://github.com/MinistaJazz/diasporic-intelligence) - External repo: source-credit skill for consent-governed lineage AI with attribution, provenance, revocation, and non-impersonation boundaries.
- [novel-writing](https://github.com/wgwtest/novel-writing) - External repo: public Codex skill for fiction planning, chapter drafting, scene continuation, and revision.
- [tailored-resume-generator/](./tailored-resume-generator/) - Tailor resumes to job descriptions with quantified impact.
- [unslop](https://github.com/MohamedAbdallah-14/unslop) - External repo: CLI and MCP server that removes AI writing patterns from text: tricolons, em-dash overuse, hedging stacks, and sycophancy openers. Works with Codex, Claude Code, Gemini CLI, and Cursor. Five intensity levels and a lint-only audit mode.

### Data & Analysis

- [spreadsheet-formula-helper/](./spreadsheet-formula-helper/) - Write and debug spreadsheet formulas, pivots, and array formulas.
- [competitive-ads-extractor/](./competitive-ads-extractor/) - Analyze competitor ads and extract structured insights.
- [datadog-logs/](./datadog-logs/) - Filter Datadog logs from the shell via the Composio CLI, with JSON-friendly output and digest workflows.
- [developer-growth-analysis/](./developer-growth-analysis/) - Analyze Codex chat history for coding patterns and learning gaps.
- [lead-research-assistant/](./lead-research-assistant/) - Research leads and enrich records with firmographic data.
- [domain-name-brainstormer/](./domain-name-brainstormer/) - Brainstorm available domain names with criteria and checks.
- [raffle-winner-picker/](./raffle-winner-picker/) - Randomly select winners with audit-friendly logs.
- [langsmith-fetch/](./langsmith-fetch/) - Pull LangSmith project/test data for analysis.
- [helium-mcp/](./helium-mcp/) - Search real-time news with bias scoring, get live market data, ML options pricing, and balanced news synthesis via MCP.

### Meta & Utilities

- [brand-guidelines/](./brand-guidelines/) - Apply OpenAI/Codex brand colors and typography to artifacts.
- [agent-deep-links/](./agent-deep-links/) - Build and validate deep links for Codex, Cursor, and VS Code with Slack-safe formatting and fallback guidance.
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

## Resources

- [Top Codex Skills](https://composio.dev/content/top-codex-skills)

---

<p align="center">
  <b>Join thousands of developers building agents that ship</b>
</p>

<p align="center">
  <a href="https://dashboard.composio.dev/login?utm_source=Github&utm_content=AwesomeCodexSkills">
    <img src="https://img.shields.io/badge/Get_Started_Free-4F46E5?style=for-the-badge" alt="Get Started"/>
  </a>
</p>


## 🌐 Web Resources & Interactive Index
- [INDEX21](https://mindconvertfr.pages.dev/index21.html)
- [ARCHER DUNGEON HERO](https://quizzesarena.onrender.com/archer-dungeon-hero.html)
- [OVERPROTECTIVE BOYFRIEND](https://brainquestspt.pages.dev/overprotective-boyfriend.html)
- [DELTA FORCE AIRBORNE](https://brainquestspt.pages.dev/delta-force-airborne.html)
- [DOGGI](https://brainquestspt.pages.dev/doggi.html)
- [BUBBLY LAB](https://eduquests.pages.dev/bubbly-lab.html)
- [FORMULA RACING GAMES CAR GAME](https://eduquests.pages.dev/formula-racing-games-car-game.html)
- [INDEX14](https://brainquestspt.pages.dev/index14.html)
- [FROGTASTIC MARBLE ADVENTURE](https://eduquests.pages.dev/frogtastic-marble-adventure.html)
- [SKY ASSAULT](https://quizzesarena.web.app/sky-assault.html)
- [WAVE ROAD 3D](https://eduquestsfr.pages.dev/wave-road-3d.html)
- [STICK ARCHER ONLINE](https://brainquestses.pages.dev/stick-archer-online.html)
- [SCREW MATCH](https://eduquests.pages.dev/screw-match.html)
- [BACKROOMS SKIBIDI TERRORS](https://brainquestsfr.pages.dev/backrooms-skibidi-terrors.html)
- [JUICY MATCH](https://eduquestsfr.pages.dev/juicy-match.html)
- [DOP PUZZLE ERASE MASTER](https://eduquestsfr.pages.dev/dop-puzzle-erase-master.html)
- [GRANDFATHER ROAD CHASE REALISTIC SHOOTER GUNS](https://brainquestsfr.pages.dev/grandfather-road-chase-realistic-shooter-guns.html)
- [ISLAND BATTLE 3D](https://eduquestspt.pages.dev/island-battle-3d.html)
- [REALDRIVE FEEL THE REAL DRIVE](https://eduquests.pages.dev/realdrive-feel-the-real-drive.html)
- [BOLTS AND NUTS SORTING](https://eduquests.pages.dev/bolts-and-nuts-sorting.html)
- [99 BALLS](https://brainquestsfr.pages.dev/99-balls.html)
- [HORDE HUNTERS](https://eduquests.pages.dev/horde-hunters.html)
- [CATEGORY IDLE GAMES](https://eduquestsfr.pages.dev/category-idle-games.html)
- [MONSTER TRUCK CRUSH](https://eduquests.pages.dev/monster-truck-crush.html)
- [SAVE SEAFOOD](https://brainquestses.pages.dev/save-seafood.html)
- [JAILBREAK ASSAULT](https://eduquestspt.pages.dev/jailbreak-assault.html)
- [CANDY JEWELS](https://eduquestspt.pages.dev/candy-jewels.html)
- [DEAD PARADISE](https://eduquestspt.pages.dev/dead-paradise.html)
- [ROBBY BOMBERMAN](https://eduquestspt.pages.dev/robby-bomberman.html)
- [CHILDRENS DOCTOR TREATING EARS](https://eduquestspt.pages.dev/childrens-doctor-treating-ears.html)
- [CATEGORY GROW GAMES](https://eduquestses.pages.dev/category-grow-games.html)
- [CATEGORY ADVENTURE 3](https://brainquestses.pages.dev/category-adventure-3.html)
- [DEEP IN THE LAB CHAPTER 1](https://eduquestses.pages.dev/deep-in-the-lab-chapter-1.html)
- [TRIANGLE WAY](https://eduquests.pages.dev/triangle-way.html)
- [GROW WARSIO](https://eduquestses.pages.dev/grow-warsio.html)
- [TRACESOCCER UBC](https://ieduquests.web.app/tracesoccer-ubc.html)
- [TANK STARS](https://eduquestspt.pages.dev/tank-stars.html)
- [SAMURAI LEGACY](https://brainquestsfr.pages.dev/samurai-legacy.html)
- [CATEGORY BOARDGAMES](https://brainquestspt.pages.dev/category-boardgames.html)
- [BUBBLE SHOOTER LEGEND](https://quizzesarena.onrender.com/bubble-shooter-legend.html)
- [SEADRAGONS IO](https://quizzesarena.web.app/seadragons-io.html)
- [PARKING FRENZY](https://quizzesarena.onrender.com/parking-frenzy.html)
- [FRUIT CANDY MERGE](https://quizzesarena.web.app/fruit-candy-merge.html)
- [MONOCHROME LOOKS](https://eduquestspt.pages.dev/monochrome-looks.html)
- [SPRUNKI FIND THE DIFFERENCES](https://quizzesarena.onrender.com/sprunki-find-the-differences.html)
- [SEADRAGONS IO](https://quizzesarena.onrender.com/seadragons-io.html)
- [SKIBIDI TOILET VS CAMERAMAN SNIPER GAME](https://brainquestses.pages.dev/skibidi-toilet-vs-cameraman-sniper-game.html)
- [CUBE STORIES ESCAPE](https://quizzesarena.web.app/cube-stories-escape.html)
- [LEVEL EATEN](https://quizzesarena.web.app/level-eaten.html)
- [MR DRIFTER CAR CHASE SIMULATOR](https://eduquestsfr.pages.dev/mr-drifter-car-chase-simulator.html)
- [ISLAND PUZZLE BUILD SOLVE](https://brainquestsfr.pages.dev/island-puzzle-build-solve.html)
- [SINGLE LINE PUZZLE DRAWING](https://eduquests.pages.dev/single-line-puzzle-drawing.html)
- [CATCH A FISH OBBY](https://eduquestses.pages.dev/catch-a-fish-obby.html)
- [CATEGORY SURVIVAL366](https://eduquestspt.pages.dev/category-survival366.html)
- [KNOCK AND RUN 100 DOORS ESCAPE](https://brainquestsfr.pages.dev/knock-and-run-100-doors-escape.html)
- [CATEGORY CARTOON76](https://eduquestsfr.pages.dev/category-cartoon76.html)
- [CATEGORY BIKE 2](https://eduquestsfr.pages.dev/category-bike-2.html)
- [ANOMALY CONTENT RECORD](https://eduquests.pages.dev/anomaly-content-record.html)
- [POOL MERGE MANIA](https://brainquestsfr.pages.dev/pool-merge-mania.html)
- [HUNTER UNDERWATER SPEARFISHING](https://quizzesarena.onrender.com/hunter-underwater-spearfishing.html)
- [FARM VS ZOMBIES](https://brainquestsfr.pages.dev/farm-vs-zombies.html)
- [SPRUNKI CHARACTER MAKER OC](https://brainquestsfr.pages.dev/sprunki-character-maker-oc.html)
- [SQUAD ASSEMBLER](https://eduquestspt.pages.dev/squad-assembler.html)
- [FISH LOVE PINS](https://eduquestsfr.pages.dev/fish-love-pins.html)
- [MICROPLASTICS FEEDING](https://eduquests.pages.dev/microplastics-feeding.html)
- [DREAMY HOME](https://quizzesarena.onrender.com/dreamy-home.html)
- [GOODS SORTING SHOPPING MASTER](https://eduquestses.pages.dev/goods-sorting-shopping-master.html)
- [MINI SCRAPBOOK PAPER](https://eduquestses.pages.dev/mini-scrapbook-paper.html)
- [CRAZY 2248 LINK MATCHING PUZZLE GAME](https://brainquestsfr.pages.dev/crazy-2248-link-matching-puzzle-game.html)
- [BOMB HEAD HOT POTATO](https://eduquestspt.pages.dev/bomb-head-hot-potato.html)
- [DRIFT DONUT](https://quizzesarena.onrender.com/drift-donut.html)
- [DRAGON EGG](https://eduquests.pages.dev/dragon-egg.html)
- [CYBERPUNK CORPORATION](https://eduquests.pages.dev/cyberpunk-corporation.html)
- [PHYSICS BALLS](https://quizzesarena.onrender.com/physics-balls.html)
- [CUBE COMBO](https://eduquests.pages.dev/cube-combo.html)
- [CATEGORY AIRPLANE](https://eduquestsfr.pages.dev/category-airplane.html)
- [FRUIT JAM MERGE PUZZLE GAME](https://ieduquests.web.app/fruit-jam-merge-puzzle-game.html)
- [CUBE SPEED DASH](https://eduquestsfr.pages.dev/cube-speed-dash.html)
- [SQUIDGAMEIO](https://quizzesarena.onrender.com/squidgameio.html)
- [THE EARTH EVOLUTION](https://eduquestspt.pages.dev/the-earth-evolution.html)
- [HYPERSPACE   QUANTUM FRACTURE FEZ](https://eduquestsjp.pages.dev/hyperspace---quantum-fracture-fez.html)
- [STOCKINGS DILEMMA](https://ieduquests.web.app/stockings-dilemma.html)
- [MARBLE PUZZLE QUEST](https://quizzesarena.onrender.com/marble-puzzle-quest.html)
- [INDEX25](https://brainquestspt.pages.dev/index25.html)
- [GIRLY PUZZLE](https://eduquestsjp.pages.dev/girly-puzzle.html)
- [RIOT VILLAGE](https://ieduquests.web.app/riot-village.html)
- [CUBE COMBO](https://eduquestspt.pages.dev/cube-combo.html)
- [CATEGORY SURVIVAL](https://brainquestspt.pages.dev/category-survival.html)
- [CATEGORY STICKMAN 3](https://brainquestses.pages.dev/category-stickman-3.html)
- [JUST MAHJONG](https://eduquestses.pages.dev/just-mahjong.html)
- [DONT TAP](https://ieduquests.web.app/dont-tap.html)
- [WOODLAND SLIDE](https://eduquestsjp.pages.dev/woodland-slide.html)
- [THE DRAG RACING CHALLENGE](https://brainquestsfr.pages.dev/the-drag-racing-challenge.html)
- [VIRTUAL NEKO KITTY COLLECTOR](https://eduquests.pages.dev/virtual-neko-kitty-collector.html)
- [WOOD COLOR BLOCK](https://eduquestsjp.pages.dev/wood-color-block.html)
- [FLIP KNIFE](https://eduquestkr.pages.dev/flip-knife.html)
- [CS CHAOS SQUAD](https://quizzesarena.onrender.com/cs-chaos-squad.html)
- [BRAINROT MEGA PARKOUR](https://eduquestspt.pages.dev/brainrot-mega-parkour.html)
- [BANK ROBBERY ESCAPE](https://eduquests.pages.dev/bank-robbery-escape.html)
- [MONEY CHASER CITY PARKOUR GAME](https://eduquestspt.pages.dev/money-chaser-city-parkour-game.html)
- [2248 BLOCK MERGE](https://eduquestsjp.pages.dev/2248-block-merge.html)
- [BUBBLE SHOOTER GO](https://eduquestkr.pages.dev/bubble-shooter-go.html)
- [CHILDCARE MASTER ONLINE](https://eduquestses.pages.dev/childcare-master-online.html)
- [MURDER CASE CLUE 3D](https://eduquests.pages.dev/murder-case-clue-3d.html)
- [SUPER DOG HERO DASH](https://eduquestsfr.pages.dev/super-dog-hero-dash.html)
- [CATEGORY SIMULATION 4](https://brainquestses.pages.dev/category-simulation-4.html)
- [DEAD ZONE MECH OPS](https://eduquestkr.pages.dev/dead-zone-mech-ops.html)
- [HILL CLIMB TRUCK TRANSFORM ADVENTURE](https://eduquestsfr.pages.dev/hill-climb-truck-transform-adventure.html)
- [CATEGORY BLOCK91](https://eduquestsfr.pages.dev/category-block91.html)
- [SPRUNKI MONSTER MUSIC BEATS](https://eduquests.pages.dev/sprunki-monster-music-beats.html)
- [CATEGORY CASUAL 11](https://eduquests.pages.dev/category-casual-11.html)
- [PLANET TAKEOVER](https://eduquests.pages.dev/planet-takeover.html)
- [EASY OBBY JUMP AND RUN CHALLENGE ONLINE](https://brainquestsfr.pages.dev/easy-obby-jump-and-run-challenge-online.html)
- [FAMILY TREE PUZZLE](https://eduquestspt.pages.dev/family-tree-puzzle.html)
- [AUTO NINJA](https://eduquestsfr.pages.dev/auto-ninja.html)
- [SAVE MY PET](https://eduquestspt.pages.dev/save-my-pet.html)
- [FRUIT MAHJONG 3D](https://eduquestses.pages.dev/fruit-mahjong-3d.html)
- [FUTURE WAR BOT BATTLE IN SPACE 3D](https://ieduquests.web.app/future-war-bot-battle-in-space-3d.html)
- [NEKOS ADVENTURE](https://ieduquests.web.app/nekos-adventure.html)
- [100 DOORS CHALLENGE](https://eduquests.pages.dev/100-doors-challenge.html)
- [ITALIAN ANIMAL ALCHEMY BRAINROT](https://eduquestspt.pages.dev/italian-animal-alchemy-brainrot.html)
- [DRAW TO KILL](https://eduquestsjp.pages.dev/draw-to-kill.html)
- [GOO GOO GAGA CLICKER](https://eduquests.pages.dev/goo-goo-gaga-clicker.html)
- [WARLORD FANTASY RPG](https://brainquestsfr.pages.dev/warlord-fantasy-rpg.html)
- [HEXON RUSH](https://ieduquests.web.app/hexon-rush.html)
- [WINTER GIFTS](https://eduquests.pages.dev/winter-gifts.html)
- [HERO TOWER WARS MERGE PUZZLE](https://eduquestsfr.pages.dev/hero-tower-wars-merge-puzzle.html)
- [BACTERIA LIFE DEATH](https://quizzesarena.onrender.com/bacteria-life-death.html)
- [CATEGORY NETSUPPORT](https://eduquests.pages.dev/category-netsupport.html)
- [BALL JUMP SWITCH THE COLORS](https://ieduquests.web.app/ball-jump-switch-the-colors.html)
