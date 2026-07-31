<h1 align="center">Awesome Codex Skills (简体中文)</h1>

<p align="center">
<a href="https://dashboard.composio.dev/login?utm_source=Github&utm_medium=Youtube&utm_campaign=2025-11&utm_content=AwesomeCodexSkills">

  <img width="1280" height="640" alt="Composio banner" src="../codex_cover_image.png">
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

精选实用 Codex Skills 列表，用于跨 Codex CLI 和 API 自动化工作流。

---

## ⚡ 赋予您的 Skill 真实世界的行动能力

Skill 告诉您的 Agent **如何**工作。MCP Gateway 为其提供安全访问所需工具的权限。

Composio [MCP Gateway](https://composio.dev/mcp-gateway) 为 1,000+ 应用集成提供单一 MCP 端点，具备内置身份验证、团队访问控制、审计日志和生产级可靠性。

---

## 🚀 快速开始：添加 Skills 到 Codex

### 使用 Skill 安装器安装（推荐）

```bash
git clone https://github.com/ComposioHQ/awesome-codex-skills.git
cd awesome-codex-skills
# 安装一个或多个 skill 到 $CODEX_HOME/skills（默认为 ~/.codex/skills）
python skill-installer/scripts/install-skill-from-github.py --repo ComposioHQ/awesome-codex-skills --path meeting-notes-and-actions
```

安装程序会拉取 skill 并放置在 `$CODEX_HOME/skills/<skill-name>`。重启 Codex 以加载新 skill。

### 手动安装

1. 将所需的 skill 文件夹（例如 `./spreadsheet-formula-helper`）复制到 `$CODEX_HOME/skills/`（默认为 `~/.codex/skills/`）。
2. 重启 Codex 以加载新的元数据。
3. 在下一次会话中，自然描述任务或提及 skill 名称；Codex 将根据其 `description` 元数据自动触发匹配的 skill。

---

## 📚 目录

- [Bernstein](https://github.com/chernistry/bernstein) - 带 Codex CLI 适配器的多 Agent 编排器。在隔离的 git 工作树中并行运行 Codex agent，并附带质量把控。
- [什么是 Codex Skills？](#什么是-codex-skills)
- [Skills 列表](#skills-列表)
  - [开发与代码工具](#开发与代码工具)
  - [生产力与协作](#生产力与协作)
  - [沟通与写作](#沟通与写作)
  - [数据与分析](#数据与分析)
  - [Meta 与实用工具](#meta-与实用工具)
- [在 Codex 中使用 Skills](#在-codex-中使用-skills)
- [创建 Skills](#创建-skills)
- [贡献](#贡献)
- [加入社区](#加入社区)

---

## ❓ 什么是 Codex Skills？

Codex skills 是模块化的指令包，告诉 Codex 如何按照您期望的方式执行任务。每个 skill 存在于独立文件夹中，包含一个 `SKILL.md`（附带名称+描述元数据及逐步指导）。Codex 读取元数据以决定何时触发 skill，并仅在触发后加载主体内容，保持上下文高效简洁。

---

## 🛠️ Skills 列表

### 开发与代码工具

- [brooks-lint](https://github.com/hyhmrright/brooks-lint) - 基于 6 本经典工程书籍的 AI 代码审查。
- [bringyour-migration-auditor](https://github.com/unitedideas/bringyour-mcp/tree/main/skills/bringyour-migration-auditor) - 审查从 Claude Code 到 Codex harness 的迁移。
- [codebase-migrate/](../codebase-migrate/) - 带 CI 验证的大型代码库重构与迁移。
- [codebase-recon](https://github.com/yujiachen-y/codebase-recon-skill) - 分析 git 历史以深入理解代码库结构。
- [create-plan/](../create-plan/) - 快速草拟编码任务的简明执行计划。
- [deploy-pipeline/](../deploy-pipeline/) - 从 Stripe → Supabase → Vercel 的端到端发布流水线。
- [gh-address-comments/](../gh-address-comments/) - 使用 `gh` 处理 open PR 上的审查意见。
- [gh-fix-ci/](../gh-fix-ci/) - 检查 GitHub Actions 失败项并提供修复建议。
- [mcp-builder/](../mcp-builder/) - 构建与评估符合最佳实践的 MCP 服务器。
- [pr-review-ci-fix/](../pr-review-ci-fix/) - 通过 Composio CLI 实现自动 PR 审查与 CI 自动修复循环。
- [sentry-triage/](../sentry-triage/) - 诊断 Sentry 问题并映射至本地源码。
- [webapp-testing/](../webapp-testing/) - 运行针对性的 Web 应用测试并总结结果。

### 生产力与协作

- [connect/](../connect/) - 通过 Composio CLI 将 Codex 连接至 1000+ 应用（Slack, GitHub, Notion 等）。
- [connect-apps/](../connect-apps/) - 从终端配置 Composio 应用连接。
- [composio-skills/](../composio-skills/) - 访问 800+ 针对 Composio 集成的应用自动化 skill。
- [issue-triage/](../issue-triage/) - 分类 Linear/Jira 积压工作并在终端清理 bug。
- [linear/](../linear/) - 在 Linear 中管理 Issue、项目和团队工作流。
- [meeting-notes-and-actions/](../meeting-notes-and-actions/) - 将会议记录转为带行动项的总结。
- [internal-comms/](../internal-comms/) - 撰写内部公告与干系人更新。
- [invoice-organizer/](../invoice-organizer/) - 规范并提取发票数据用于跟踪与报告。
- [notion-knowledge-capture/](../notion-knowledge-capture/) - 将对话或笔记转化为结构化的 Notion 页面。
- [file-organizer/](../file-organizer/) - 整理、重命名并清理文件，保持工作区整洁。

---

## 🤝 贡献

非常欢迎提交 PR。请添加真实、可复用的 skill，保持描述准确，并包含所需的脚本或参考资料。

---

## 💬 加入社区

- [加入 Discord](https://discord.com/invite/composio) - 与其他构建 Codex skill 的开发者交流。
- [在 X 上关注我们](https://twitter.com/composio) - 获取最新 skill 和功能更新。
