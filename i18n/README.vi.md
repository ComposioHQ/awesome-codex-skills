<h1 align="center">Awesome Codex Skills (Tiếng Việt)</h1>

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

Danh sách tổng hợp các Codex Skills thực tế giúp tự động hóa quy trình làm việc trên Codex CLI và API.

---

## ⚡ Cung cấp khả năng hành động thực tế cho AI Agent của bạn

Skill định nghĩa cho AI Agent biết **CÁCH** làm việc. Một MCP Gateway cung cấp cho nó quyền truy cập an toàn vào các công cụ cần thiết.

Composio [MCP Gateway](https://composio.dev/mcp-gateway) cung cấp một endpoint MCP duy nhất cho 1.000+ tích hợp ứng dụng với tính năng xác thực tích hợp, phân quyền truy cập theo team, nhật ký kiểm toán (audit log) và độ tin cậy chuẩn production.

---

## 🚀 Hướng dẫn nhanh: Thêm Skills vào Codex

### Cài đặt bằng Trình cài đặt Skill (Khuyên dùng)

```bash
git clone https://github.com/ComposioHQ/awesome-codex-skills.git
cd awesome-codex-skills
# Cài đặt một hoặc nhiều skill vào $CODEX_HOME/skills (mặc định là ~/.codex/skills)
python skill-installer/scripts/install-skill-from-github.py --repo ComposioHQ/awesome-codex-skills --path meeting-notes-and-actions
```

Trình cài đặt sẽ tải skill về và đặt vào `$CODEX_HOME/skills/<skill-name>`. Khởi động lại Codex để nhận diện các skill mới.

### Cài đặt thủ công

1. Sao chép thư mục skill mong muốn (ví dụ: `./spreadsheet-formula-helper`) vào `$CODEX_HOME/skills/` (mặc định `~/.codex/skills/`).
2. Khởi động lại Codex để tải metadata mới.
3. Trong phiên làm việc tiếp theo, hãy mô tả tác vụ hoặc nhắc đến tên skill; Codex sẽ tự động kích hoạt các skill phù hợp dựa trên phần `description` ở frontmatter.

---

## 📚 Mục lục

- [Bernstein](https://github.com/chernistry/bernstein) - Bộ điều phối đa agent với adapter cho Codex CLI. Chạy song song các Codex agent trong các git worktree độc lập có kiểm soát chất lượng.
- [Codex Skills là gì?](#codex-skills-là-gì)
- [Danh sách Skills](#danh-sách-skills)
  - [Công cụ Lập trình & Dev](#công-cụ-lập-trình--dev)
  - [Năng suất & Cộng tác](#năng-suất--cộng-tác)
  - [Giao tiếp & Viết lách](#giao-tiếp--viết-lách)
  - [Dữ liệu & Phân tích](#dữ-liệu--phân-tích)
  - [Meta & Tiện ích](#meta--tiện-ích)
- [Cách sử dụng Skills trong Codex](#cách-sử-dụng-skills-trong-codex)
- [Cách tạo một Skill mới](#cách-tạo-một-skill-mới)
- [Đóng góp](#đóng-góp)
- [Tham gia Cộng đồng](#tham-gia-cộng-đồng)

---

## ❓ Codex Skills là gì?

Codex Skills là các gói hướng dẫn mô-đun dạy Codex cách thực hiện một tác vụ theo đúng yêu cầu của bạn. Mỗi skill nằm trong thư mục riêng chứa file `SKILL.md` bao gồm metadata (tên + mô tả) và hướng dẫn thực hiện từng bước. Codex đọc metadata để quyết định khi nào kích hoạt skill và chỉ tải phần nội dung chi tiết sau khi được kích hoạt, giúp giữ cho cửa sổ ngữ cảnh (context window) gọn nhẹ.

---

## 🛠️ Danh sách Skills

### Công cụ Lập trình & Dev

- [brooks-lint](https://github.com/hyhmrright/brooks-lint) - AI code review dựa trên 6 cuốn sách kỹ thuật kinh điển.
- [bringyour-migration-auditor](https://github.com/unitedideas/bringyour-mcp/tree/main/skills/bringyour-migration-auditor) - Kiểm tra chuyển đổi từ Claude Code sang Codex harness.
- [codebase-migrate/](../codebase-migrate/) - Chạy refactor và chuyển đổi codebase lớn theo từng đợt có xác nhận CI.
- [codebase-recon](https://github.com/yujiachen-y/codebase-recon-skill) - Phân tích lịch sử git để hiểu cấu trúc codebase.
- [create-plan/](../create-plan/) - Nhanh chóng lập kế hoạch thực thi cho các tác vụ lập trình.
- [deploy-pipeline/](../deploy-pipeline/) - Quy trình phát hành end-to-end từ Stripe → Supabase → Vercel.
- [gh-address-comments/](../gh-address-comments/) - Xử lý các nhận xét/review trên Pull Request mở bằng `gh`.
- [gh-fix-ci/](../gh-fix-ci/) - Kiểm tra các check lỗi trên GitHub Actions và đề xuất cách sửa.
- [mcp-builder/](../mcp-builder/) - Xây dựng và đánh giá các server MCP theo chuẩn best practices.
- [pr-review-ci-fix/](../pr-review-ci-fix/) - Tự động review PR và sửa lỗi CI qua Composio CLI.
- [sentry-triage/](../sentry-triage/) - Chẩn đoán lỗi từ Sentry và trỏ trực tiếp đến source code local.
- [webapp-testing/](../webapp-testing/) - Chạy test ứng dụng web targeted và tóm tắt kết quả.

### Năng suất & Cộng tác

- [connect/](../connect/) - Kết nối Codex với 1.000+ ứng dụng qua Composio CLI (Slack, GitHub, Notion...).
- [connect-apps/](../connect-apps/) - Cấu hình kết nối ứng dụng Composio từ terminal.
- [composio-skills/](../composio-skills/) - Truy cập 800+ skill tự động hóa ứng dụng chuyên biệt cho Composio.
- [issue-triage/](../issue-triage/) - Phân loại backlog Linear/Jira và dọn lỗi từ terminal.
- [linear/](../linear/) - Quản lý issue, dự án và quy trình làm việc trong Linear.
- [meeting-notes-and-actions/](../meeting-notes-and-actions/) - Biến bản ghi cuộc họp thành tóm tắt và công việc cần làm.
- [internal-comms/](../internal-comms/) - Soạn thảo thông báo nội bộ và cập nhật cho bên liên quan.
- [invoice-organizer/](../invoice-organizer/) - Chuẩn hóa và trích xuất dữ liệu hóa đơn báo cáo.
- [notion-knowledge-capture/](../notion-knowledge-capture/) - Chuyển đổi cuộc trò chuyện thành trang Notion có cấu trúc.
- [file-organizer/](../file-organizer/) - Sắp xếp, đổi tên và làm sạch thư mục tập tin.

### Giao tiếp & Viết lách

- [email-draft-polish/](../email-draft-polish/) - Viết lại và chỉnh sửa email theo đúng văn phong.
- [changelog-generator/](../changelog-generator/) - Tạo changelog rõ ràng từ commits.
- [content-research-writer/](../content-research-writer/) - Nghiên cứu và soạn thảo nội dung có trích dẫn nguồn.
- [tailored-resume-generator/](../tailored-resume-generator/) - Tùy chỉnh CV phù hợp với mô tả công việc (JD).

---

## 🤝 Đóng góp

Rất hoan nghênh các Pull Request. Hãy đóng góp các skill thực tế có thể tái sử dụng, giữ mô tả chính xác và kèm theo các script/reference cần thiết.

---

## 💬 Tham gia Cộng đồng

- [Tham gia Discord](https://discord.com/invite/composio) - Trò chuyện với các nhà phát triển khác.
- [Theo dõi trên X](https://twitter.com/composio) - Cập nhật thông tin skill mới.
