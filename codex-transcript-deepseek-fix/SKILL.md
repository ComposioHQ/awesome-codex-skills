---
name: codex-transcript-deepseek-fix
description: 修复 Codex CLI 桌面端会话在「同一会话内中途用 cc switch 切换 config（在 DeepSeek 与 OpenAI 之间换模型）」后回传报错的问题。症状包括 Invalid 'input[x].id' 要求以 msg 开头、reasoning content 数组超长、rs_resp_ item 404 not found、裸 UUID item id 等。适用于清理 ~/.codex/sessions 下的 transcript 脏数据。
---

# 修复 Codex 跨 Provider 切模型导致的 transcript 污染

## 背景与根因
Codex CLI（桌面端）会话 transcript 存在 `~/.codex/sessions/2026/MM/DD/rollout-<session>.jsonl`（`session_index.jsonl` 可定位会话名/id）。
问题最初由同一条会话中 **`cc switch` 切换 config** 触发——从 OpenAI 切到 DeepSeek、再切回 OpenAI（如 5.6）继续对话时，DeepSeek 适配层会写入与 OpenAI Responses API **不兼容**的数据，切回后整段历史作为 `input[]` 回传即报错。也就是说，根因是「同一会话内用 `cc switch` 切换了不同 provider 的 config」，而不仅是换模型本身。

真实 item 嵌套位置：
- `{"type":"response_item","payload":{...item}}` —— 普通事件
- `{"type":"compacted","payload":{"replacement_history":[...items]}}` —— 压缩事件，重建历史时**替换**之前所有 items
- 历史 error 仅出现在 `{"type":"event_msg","payload":{"type":"task_complete",...error...}}`，是**惰性日志文本**，无需清理

OpenAI 原生 id 前缀方案（同文件内真实 Codex 项即为标准）：
`message`→`msg_`、`function_call`→`fc_`、`custom_tool_call`→`ctc_`、`function_call_output`→`fco_`、`custom_tool_call_output`→`ctco_`、`reasoning`→`rs_`、`compaction`→`cmp_`。
`function_call` 项同时有 `id`（item id，需合规前缀）和 `call_id`（`call_...`，OpenAI 调用引用，已合法，勿改）。reasoning 项不应带明文 `content`（应为空，正文在 `message` 项）。

## 三类污染与修法（按出现顺序逐个修，每次先备份）
用 Python（`python3`）逐行 `json.loads` 处理。**先 `cp -p` 备份原文件再加时间戳**。

1. **message id 畸形 `resp_<uuid>_msg`**
   全局把 `resp_<uuid>_msg` → `msg_<uuid>`（保留 uuid 维持引用）。正则 `resp_([0-9a-fA-F-]+)_msg` 替换成 `msg_\1`。

2. **reasoning 明文 content（报 content 数组超长 / rs_resp_ 404）**
   - 先删「裸 UUID id 的 reasoning」项：id 匹配 `^[0-9a-f]{8}-...-[0-9a-f]{12}$` 且 type=reasoning → 整行丢弃（response_item）或从 replacement_history 移除（compacted）。
   - 再删「`rs_resp_<uuid>` 畸形 reasoning」项：id 以 `rs_resp_` 开头且 type=reasoning → 同样删除。成因：DeepSeek reasoning 项 id 原为 `resp_<uuid>_msg`，被第 1 步改成 `msg_<uuid>` 后未被删，Codex 回放又加 `rs_` 前缀成 `rs_resp_`，OpenAI 找不到（store:false 未持久化）→ 404。删掉是根治（重命名无效，因 OpenAI 从没持久化过该项）。
   - reasoning 是辅助信息，删掉不影响对话正文（正文在 `message` 项）。

3. **裸 UUID item id（`message`/`function_call`/`custom_tool_call`）**
   这些项 `id` 是纯 uuid 无前缀，回放必被 `Invalid 'input[x].id'` 拒。按类型前缀化：`message`→`msg_`、`function_call`→`fc_`、`custom_tool_call`→`ctc_`（同样处理 replacement_history）。其 `call_id` 已是 `call_...` 合法，且 item id 不被其它 item 的 id 引用 → **纯结构化改写 `it["id"]=f"{pfx}_{uuid}"` 即可，不要全局字符串替换以免误伤 content 文本**。

## 校验脚本（每轮修复后必跑）
- 解析每行 JSON 成功（坏行=0）。
- 无 `rs_resp_` / `resp_` 前缀 id，无裸 UUID id。
- reasoning 项无明文 `content` 数组（长度为 0）。
- 残留 `rs_` reasoning 应为 OpenAI 原生（保留），裸 UUID reasoning = 0。
- `wc -l` 与文件字节数正常（约 2754 行 / 80MB，视会话）。

## 注意事项
- 每次只改一个污染类，改完立即全量校验，避免一次大改后难以定位问题。
- 不要删 `custom_tool_call_output`/`function_call_output` 的 `output` 数组——那是 Codex 原生项，回放时自动转字符串，非污染。
- 根本避免：不要在同一会话混用 OpenAI 与 DeepSeek 模型；切回 OpenAI 后开新会话最稳。本机层面只能事后修 transcript。
- 修复后让用户**完全退出并重启 Codex 桌面端**（清内存旧缓存），再打开会话切 5.6 发消息验证。
