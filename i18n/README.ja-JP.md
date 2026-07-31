<h1 align="center">Awesome Codex Skills (日本語)</h1>

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

Codex CLIおよびAPI全体のワークフローを自動化するための実用的なCodex Skillの厳選リスト。

---

## ⚡ Skillに実 worldのアクションを提供

SkillはAgentに**どのように**作業するかを指示します。MCP Gatewayは必要なツールへの安全なアクセスを提供します。

Composio [MCP Gateway](https://composio.dev/mcp-gateway)は、1,000以上のアプリ統合に対して、認証、アクセス制御、監査ログを備えた単一のMCPエンドポイントを提供します。

---

## 🚀 クイックスタート: CodexにSkillを追加

### Skill Installerでインストール（推奨）

```bash
git clone https://github.com/ComposioHQ/awesome-codex-skills.git
cd awesome-codex-skills
# 1つ以上のSkillを $CODEX_HOME/skills（デフォルト: ~/.codex/skills）にインストール
python skill-installer/scripts/install-skill-from-github.py --repo ComposioHQ/awesome-codex-skills --path meeting-notes-and-actions
```

インストーラーがSkillを取得し、`$CODEX_HOME/skills/<skill-name>`に配置します。Codexを再起動して新しいSkillを読み込みます。

---

## 📚 目次

- [Bernstein](https://github.com/chernistry/bernstein) - Codex CLIアダプター付きマルチエージェントオーケストレーター。
- [Codex Skillsとは？](#codex-skillsとは)
- [Skillsリスト](#skillsリスト)
  - [開発 & コードツール](#開発--コードツール)
  - [生産性 & コラボレーション](#生産性--コラボレーション)
  - [コミュニケーション & 執筆](#コミュニケーション--執筆)
  - [データ & 分析](#データ--分析)
- [CodexでのSkillの使用](#codexでのskillの使用)
- [コミュニティに参加](#コミュニティに参加)

---

## ❓ Codex Skillsとは？

Codex Skillsは、Codexにタスクの実行手順を指示するモジュール式の手順パッケージです。各Skillは`SKILL.md`を含む独立したフォルダに保存されます。

---

## 🛠️ Skillsリスト

### 開発 & コードツール

- [codebase-migrate/](../codebase-migrate/) - CI検証付きで大規模なコードベースの移行を実行。
- [codebase-recon](https://github.com/yujiachen-y/codebase-recon-skill) - git履歴を分析してコードベースの構造を把握。
- [create-plan/](../create-plan/) - コーディングタスクの実行計画を迅速に作成。
- [deploy-pipeline/](../deploy-pipeline/) - Stripe → Supabase → Vercel のエンドツーエンドデプロイ。
- [gh-fix-ci/](../gh-fix-ci/) - 失敗したGitHub Actionsのログを解析して修正案を提示。
- [mcp-builder/](../mcp-builder/) - ベストプラクティスに基づいてMCPサーバーを構築・評価。

### 生産性 & コラボレーション

- [connect/](../connect/) - Composio CLI経由でCodexを1000+のアプリに接続。
- [connect-apps/](../connect-apps/) - シェルからComposioアプリの接続を設定。
- [composio-skills/](../composio-skills/) - Composio統合用の800+の専用自動化Skillにアクセス。
- [meeting-notes-and-actions/](../meeting-notes-and-actions/) - 会議の文字起こしを要約とアクションアイテムに変換。

---

## 💬 コミュニティに参加

- [Discordに参加](https://discord.com/invite/composio) - 他のデベロッパーと交流。
- [Xをフォロー](https://twitter.com/composio) - 最新の機能とSkillのアップデート。
