<h1 align="center">Awesome Codex Skills</h1>

<p align="center">
  <a href="./README.md">English</a> | <b>简体中文</b>
</p>

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

一个精选列表，收集可在 Codex CLI 和 API 中自动化工作流的实用 Codex skills。


> **想让 skills 不只是生成文本？** Codex 可以发送邮件、创建 issue、发布 Slack 消息，并在 1000+ 应用中执行操作。[查看方法 →](./connect/)

---

## 快速开始：将 Skills 添加到 Codex

### 使用 Skill Installer 安装（推荐）

```bash
git clone https://github.com/ComposioHQ/awesome-codex-skills.git
cd awesome-codex-skills
# Install one or more skills into $CODEX_HOME/skills (defaults to ~/.codex/skills)
python skill-installer/scripts/install-skill-from-github.py --repo ComposioHQ/awesome-codex-skills --path meeting-notes-and-actions
```

安装器会获取该 skill，并将其放入 `$CODEX_HOME/skills/<skill-name>`。重启 Codex 后即可加载新 skills。

### 手动安装

1. 将所需的 skill 文件夹（例如 `./spreadsheet-formula-helper`）复制到 `$CODEX_HOME/skills/`（默认是 `~/.codex/skills/`）。
2. 重启 Codex，让它加载新的 metadata。
3. 在下一次会话中，描述任务或提到 skill 名称；Codex 会根据 `description` frontmatter 触发匹配的 skills。

---

## 目录

- [Bernstein](https://github.com/chernistry/bernstein) - 带 Codex CLI 适配器的多智能体编排器。可在隔离的 git worktrees 中并行运行 Codex agents，并带有质量门禁。
- [什么是 Codex Skills?](#什么是-codex-skills)
- [Skills](#skills)
  - [开发与代码工具](#开发与代码工具)
  - [生产力与协作](#生产力与协作)
  - [沟通与写作](#沟通与写作)
  - [数据与分析](#数据与分析)
  - [元工具与实用工具](#元工具与实用工具)
- [在 Codex 中使用 Skills](#在-codex-中使用-skills)
- [创建 Skills](#创建-skills)
- [贡献](#贡献)
- [加入社区](#加入社区)

## 什么是 Codex Skills?

Codex skills 是模块化的指令包，用来告诉 Codex 按你希望的方式执行某类任务。每个 skill 都位于自己的文件夹中，并包含一个 `SKILL.md`，其中写有 metadata（name + description）和逐步指导。Codex 会读取 metadata 来决定何时触发某个 skill，并且只在触发后加载正文，从而保持上下文精简。

## Skills

### 开发与代码工具

- [brooks-lint](https://github.com/hyhmrright/brooks-lint) - 基于六本经典工程书籍的 AI 代码审查工具，提供带书籍引用、严重程度标签和四种分析模式（PR review、architecture audit、tech debt、test quality）的衰退风险诊断。安装：`python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo hyhmrright/brooks-lint --path skills/brooks-lint --name brooks-lint`
- [codebase-migrate/](./codebase-migrate/) - 以可审查的批次执行大型代码库迁移和多文件重构，并配套 CI 验证。
- [codebase-recon](https://github.com/yujiachen-y/codebase-recon-skill) - 先分析 git 历史再阅读代码，用于理解代码库；通过自动缩放分析暴露热点、bug 磁铁、bus factor、项目动量和高风险文件（hotspot ∩ bug-magnet）。安装：`python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo yujiachen-y/codebase-recon-skill --path skills/codebase-recon --name codebase-recon`
- [create-plan/](./create-plan/) - 为编码任务快速起草简洁的执行计划。
- [deploy-pipeline/](./deploy-pipeline/) - 端到端 Stripe → Supabase → Vercel 发布流水线，包含验证与回滚。
- [Emdash Skills](https://github.com/megabytespace/claude-skills) - 14 类自主产品构建操作系统：CF Workers + Hono + Angular + D1 + Stripe。通过一句提示词即可部署 SaaS，包含 94 份参考文档、18 个 agents，并支持 Codex-native `.agents/skills/`。
- [gh-address-comments/](./gh-address-comments/) - 使用 `gh` 处理当前分支上打开的 GitHub PR 中的 review 或 issue 评论。
- [gh-fix-ci/](./gh-fix-ci/) - 检查失败的 GitHub Actions checks，总结失败原因并提出修复方案。
- [mcp-builder/](./mcp-builder/) - 使用最佳实践和评估工具构建、评估 MCP servers。
- [pr-review-ci-fix/](./pr-review-ci-fix/) - 通过 Composio CLI 实现自动 GitHub/GitLab PR review 与 CI 自动修复循环。
- [sentry-triage/](./sentry-triage/) - 通过将 stack frames 映射到本地源码来诊断 Sentry issues，无需复制粘贴。
- [webapp-testing/](./webapp-testing/) - 运行有针对性的 Web 应用测试并总结结果。
- [AuraKit](https://github.com/smorky850612/Aurakit) - 一体化 skill 框架：46 种模式、23 个 sub-agents、6 层 OWASP 安全、10 个生命周期 hooks，约节省 55% token。安装：`npx @smorky85/aurakit`
- [Vibe-Skills](https://github.com/foryourhealth111-pixel/Vibe-Skills) - 受治理的 Codex skill harness，用于分阶段、测试驱动的工作：通过需求冻结、计划审批、执行、验证证据和跨会话记忆来路由 340+ skills。

### 生产力与协作

- [connect/](./connect/) - 通过 Composio CLI 将 Codex 连接到 1000+ 应用，实现真正的操作（Slack、GitHub、Notion 等）。
- [connect-apps/](./connect-apps/) - 为 Claude 配置 Composio CLI 连接，并从 shell 启动 app workflows。
- [issue-triage/](./issue-triage/) - 对 Linear 或 Jira backlog 进行分流，并从终端运行 bug sweeps。
- [linear/](./linear/) - 管理 Linear 中的 issues、projects 和团队工作流。
- [meeting-insights-analyzer/](./meeting-insights-analyzer/) - 分析会议 transcript，提取主题、风险和后续事项。
- [meeting-notes-and-actions/](./meeting-notes-and-actions/) - 将会议 transcript 转换为摘要，包含决策和标注负责人的 action items。
- [internal-comms/](./internal-comms/) - 为合适的语气和受众撰写内部公告、更新和 stakeholder messaging。
- [invoice-organizer/](./invoice-organizer/) - 标准化并提取 invoice 数据，便于跟踪和报告。
- [notion-knowledge-capture/](./notion-knowledge-capture/) - 将聊天或笔记转换为结构化 Notion pages，并正确建立链接。
- [notion-meeting-intelligence/](./notion-meeting-intelligence/) - 结合 Notion context 和 Codex research 准备会议材料。
- [notion-research-documentation/](./notion-research-documentation/) - 综合多个 Notion sources，生成带引用的 briefs、comparisons 或 reports。
- [notion-spec-to-implementation/](./notion-spec-to-implementation/) - 将 Notion specs 转换为实现计划、任务和进度跟踪。
- [support-ticket-triage/](./support-ticket-triage/) - 对客户支持 tickets 进行分类、优先级判断、下一步建议和回复草稿撰写。
- [file-organizer/](./file-organizer/) - 整理、重命名和清理文件，让工作区保持有序。
- [paperjsx/](./paperjsx/) - 从结构化 JSON 生成 PPTX presentations、DOCX documents、XLSX spreadsheets，以及 PDF invoices/reports/charts。通过 `@paperjsx/mcp-server` 本地运行，无需 API key，也不会发起网络调用。
- [skill-share/](./skill-share/) - 在团队成员之间共享 skills 和可复用指令。

### 沟通与写作
- [codex-sms-verification](https://github.com/virtualsms-io/codex-sms-verification) - 外部仓库：通过 VirtualSMS MCP 为 AI agents 提供真实 SIM 的 SMS verification。覆盖 145+ 国家、2000+ 服务，同时支持 hosted（mcp.virtualsms.io）和本地 stdio transports。

- [email-draft-polish/](./email-draft-polish/) - 按合适的语气和受众起草、改写或压缩邮件。
- [changelog-generator/](./changelog-generator/) - 根据 commits 或 summaries 生成清晰的 changelogs。
- [content-research-writer/](./content-research-writer/) - 进行研究并撰写带来源引用的内容。
- [novel-writing](https://github.com/wgwtest/novel-writing) - 外部仓库：用于 fiction planning、chapter drafting、scene continuation 和 revision 的公开 Codex skill。
- [tailored-resume-generator/](./tailored-resume-generator/) - 根据职位描述定制简历，并体现可量化影响。
- [unslop](https://github.com/MohamedAbdallah-14/unslop) - 外部仓库：CLI 和 MCP server，用于移除文本中的 AI 写作痕迹：tricolons、em-dash 过度使用、hedging stacks 和 sycophancy openers。适用于 Codex、Claude Code、Gemini CLI 和 Cursor，支持五档强度和 lint-only audit 模式。

### 数据与分析

- [spreadsheet-formula-helper/](./spreadsheet-formula-helper/) - 编写和调试 spreadsheet formulas、pivots 和 array formulas。
- [competitive-ads-extractor/](./competitive-ads-extractor/) - 分析竞品广告并提取结构化洞察。
- [datadog-logs/](./datadog-logs/) - 通过 Composio CLI 从 shell 过滤 Datadog logs，支持 JSON-friendly 输出和 digest workflows。
- [developer-growth-analysis/](./developer-growth-analysis/) - 分析 Codex chat history，识别编码模式和学习缺口。
- [lead-research-assistant/](./lead-research-assistant/) - 研究 leads，并用 firmographic data 丰富 records。
- [domain-name-brainstormer/](./domain-name-brainstormer/) - 基于条件和检查项构思可用域名。
- [raffle-winner-picker/](./raffle-winner-picker/) - 以审计友好的日志随机选择 winners。
- [langsmith-fetch/](./langsmith-fetch/) - 拉取 LangSmith project/test data 进行分析。
- [helium-mcp/](./helium-mcp/) - 通过 MCP 搜索实时新闻并进行 bias scoring，获取 live market data、ML options pricing 和平衡的新闻综合。

### 元工具与实用工具

- [brand-guidelines/](./brand-guidelines/) - 将 OpenAI/Codex 品牌颜色和排版应用到 artifacts。
- [agent-deep-links/](./agent-deep-links/) - 为 Codex、Cursor 和 VS Code 构建并验证 deep links，包含 Slack-safe formatting 和 fallback guidance。
- [canvas-design/](./canvas-design/) - 生成结构化 canvas layouts 和 design artifacts。
- [image-enhancer/](./image-enhancer/) - 按可配置 presets 放大并优化 images。
- [slack-gif-creator/](./slack-gif-creator/) - 为 Slack 生成带 captions 和 styling 的 GIFs。
- [theme-factory/](./theme-factory/) - 创建可复用的 theme tokens 和 palettes。
- [video-downloader/](./video-downloader/) - 下载并准备 videos，便于离线查看。
- [template-skill/](./template-skill/) - 用于构建新 skills 的 starter template。
- [skill-installer/](./skill-installer/) - 用于从 curated lists 或 GitHub paths 安装 skills 的辅助 scripts。
- [skill-creator/](./skill-creator/) - 用 progressive disclosure 构建高效 Codex skills 的指导。

## 在 Codex 中使用 Skills

- Skills 位于 `$CODEX_HOME/skills`（默认 `~/.codex/skills`）。每个子文件夹都需要包含带有 `name` 和 `description` frontmatter 的 `SKILL.md`。
- 安装或更新 skill 后，重启 Codex，让它重新加载 metadata。
- 在会话中自然描述任务；Codex 会自动触发 description 与请求匹配的 skills。你也可以直接提到 skill 名称，让 Codex 将其纳入考虑。
- 如需验证安装，请列出已安装 skills（`ls ~/.codex/skills`）并检查 metadata（`head ~/.codex/skills/<skill>/SKILL.md`）。

## 创建 Skills

Skill 布局：

```
skill-name/
├── SKILL.md          # Required: instructions + YAML frontmatter
├── scripts/          # Optional: helper scripts for deterministic steps
├── references/       # Optional: long-form docs loaded only when needed
└── assets/           # Optional: templates or files used in outputs
```

基础 SKILL.md 模板：

```markdown
---
name: my-skill-name
description: What the skill does and when Codex should use it.
---

# My Skill Name

Clear instructions and steps for Codex to execute the task.
```

最佳实践：

- 保持 `description` 对触发时机的描述足够完整；正文则聚焦于执行步骤。
- 使用 progressive disclosure：将详细 references 放入 `references/`，并只在 `SKILL.md` 中按需引用。
- 为可重复或确定性的操作包含 scripts，并说明 Codex 何时应运行它们。
- 避免在 skill 文件夹内放置额外 docs（README、changelog），以保持上下文精简。

## 贡献

欢迎提交 PR。请添加真实、可复用的 skills，保持 descriptions 精确，并包含必要的 scripts 或 references。如果添加新 skills，请确保 `description` 清楚说明 Codex 何时应该触发它，并测试 metadata 是否能放入上下文限制。

## 加入社区

- [加入我们的 Discord](https://discord.com/invite/composio) - 与其他正在构建 Codex skills 的开发者交流。
- [在 X 关注我们](https://twitter.com/composio) - 获取新 skills 和功能更新。
- 有问题？[support@composio.dev](mailto:support@composio.dev)

---

<p align="center">
  <b>加入数千名正在构建可落地 agents 的开发者</b>
</p>

<p align="center">
  <a href="https://dashboard.composio.dev/login?utm_source=Github&utm_content=AwesomeCodexSkills">
    <img src="https://img.shields.io/badge/Get_Started_Free-4F46E5?style=for-the-badge" alt="Get Started"/>
  </a>
</p>
