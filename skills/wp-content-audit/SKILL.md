# Skill: wp-content-audit — WordPress 內容稽核

## 觸發條件
- 任何透過 WP REST API 新建或更新文章後
- 定期（每週 / 每次 SEO session 結尾）全站稽核
- Agent 寫完 WP 內容即將 publish 前

## 為什麼要做
防止 agent 把手寫 `<script>` / `<style>` / 禁用詞塞進 WP post content。
完整事件紀錄：`handoff/feedback/2026-04-07-wp-foodsafety-update-log.md`

## 禁用詞清單
**唯一來源**：`skills/seo-session-checklist.md` 的「SEO 文案禁用詞清單」章節。
本技能不重複維護禁用詞，執行時從那份檔案讀取。

## 稽核項目（audit.sh 執行 4 個檢查）

### 檢查 1：HTML 違規標籤
content 裡不能有：
- `<script>`
- `<style>`
- 自定義 inline JS event（onclick / onload 等）

### 檢查 2：禁用詞（食安/法規）
讀 `skills/seo-session-checklist.md` 的禁用詞清單，grep content

### 檢查 3：結構化資料重複
如果 content 裡有 `application/ld+json` → FAIL（Rank Math 已處理 head 的 schema，body 不該有）

### 檢查 4：過度承諾字眼
- 「保證」「100%」「完全無 X」「絕對」等

## 使用方式

### 單篇稽核
```bash
./scripts/wp-audit.sh <post_id>
```

### 全站稽核
```bash
./scripts/wp-audit.sh --all
```

### 定期稽核
由 `scripts/wp-audit-cron.sh` 每週執行一次，結果寫到 `data/wp-audit-log/{date}.md`

## 失敗處理
- 單篇失敗 → 立刻 rollback 該篇（或發 GitHub issue）
- 全站稽核多篇失敗 → 建立 handoff/feedback/{date}-wp-audit-report.md 讓 Owner 決定批次修

## 腳本位置
`scripts/wp-audit.sh` + `scripts/wp-audit-cron.sh`

## 相關
- `AGENT_RULES.md` Section 14（WP 內容生成規則）
- `skills/seo-session-checklist.md`（禁用詞唯一來源）
