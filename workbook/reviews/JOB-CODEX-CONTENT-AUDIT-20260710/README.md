---
job_id: JOB-CODEX-CONTENT-AUDIT-20260710
tool: Codex (gpt-5.5, codex-cli 0.142.0)
called_by: A1 (Claude Code)
date: 2026-07-10
task: 57 篇舊文內鏈+語氣批量分析（唯讀，輸出建議清單）
output_file: output.md
status: ✅ 落檔完成
tokens_used: ~145,800
---

## 任務說明
對 MAPLAB WordPress 57 篇既有文章（唯讀，未動任何文章）做：
1. 內鏈機會 Top 10 分析（誰應鏈誰但可能未鏈）
2. 語氣複查優先順序（按 brand-voice-guide.md 規則找最高風險的 10 篇）
3. 系統性觀察

## 使用說明
`output.md` 包含結構化建議清單，所有建議需 A2/Owner 核准後才可實際修改 WordPress 文章。
建議第一優先：post 698 食安紅線（無麩質）已確認，需手動修正正文+JSON-LD 兩處。
