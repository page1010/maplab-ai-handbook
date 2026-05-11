# System Evolution Stories — 系統進化故事集

> **用途**：記錄 MAPLAB AI 系統建置過程中的設計決策、踩坑經驗、架構演進的完整故事。
> 不只記「怎麼修」，更記「為什麼這樣做」「Owner 怎麼想」「學到什麼」。

---

## 與其他文件的差異

| 文件 | 記什麼 | 誰看 |
|------|--------|------|
| `skills/experience-log.md` | 技術踩坑的快速查表（EXP 編號） | Agent 卡住時查 |
| `skills/troubleshooting-hub.md` | 症狀→解法對照表 | Agent debug 用 |
| **本目錄（stories）** | 完整故事：背景、決策過程、Owner 原話、學到的事 | 寫文章、回顧、新 Agent 理解系統脈絡 |
| `skills/auto/` | checkpoint.sh 自動生成的技能檔 | 防止重複踩坑 |

**簡單說**：experience-log 是「答案」，stories 是「過程」。

---

## 誰可以寫

所有 Agent（A0-A8, B1）和 Owner 都可以新增故事。
A1 負責定期審查：把反覆出現的 pattern 從故事中提煉成技能檔（`skills/`）。

---

## 檔案命名

格式：`YYYY-MM-DD-簡短描述.md`

例如：
- `2026-04-17-a0-a1-role-design.md`
- `2026-04-18-rule-priority-design.md`
- `2026-04-20-innerflowlab-system-setup.md`

---

## 故事格式

```markdown
# YYYY-MM-DD — 標題

> 記錄者：Agent 名稱
> 日期：YYYY-MM-DD
> 背景：一句話說明為什麼會有這個故事

---

## Owner 原始需求/提問
> 引用 Owner 的原話（保留語氣和脈絡）

## 過程
（發生了什麼、試了什麼、怎麼決定的）

## 決策紀錄
| 決策 | 選擇 | 理由 |
|------|------|------|

## 學到的事
1. ...
2. ...

## 相關文件
- ...
```

---

## 故事→技能轉換

A1 每週巡檢時檢查本目錄：
1. 有沒有新故事尚未提煉成技能
2. 同一個 pattern 是否出現 2 次以上
3. 如果是 → 用 `bash scripts/generate-skill.sh` 生成技能檔到 `skills/auto/`
4. 在故事檔底部加上 `→ 已提煉為技能：skills/auto/xxx.md`

---

## 目前故事索引

| 日期 | 故事 | 關鍵學習 |
|------|------|---------|
| 2026-03-23 | [Gemini API 選擇](2026-03-23-gemini-api-selection.md) | REST 直打 vs Python Library、GPS 比 Vision AI 快 1000 倍 |
| 2026-03-23 | [Sheets 當資料庫](2026-03-23-sheets-as-database.md) | 小規模業務用 Sheets 比 DB 進入成本低 10 倍 |
| 2026-03-27 | [Bot 記憶斷裂與 A0/A1 架構](2026-03-27-bot-memory-and-agent-architecture.md) | `-c` flag 解決記憶、Agent 按能力分不按層級分 |
| 2026-04-17 | [A0/A1 角色定位](2026-04-17-a0-a1-role-design.md) | A1 當 A0 的大腦，不是互換角色 |
| 2026-04-18 | [規則衝突優先級](2026-04-18-rule-priority-design.md) | Owner 規則 > 技術效率 > 速度 |
| 2026-04-20 | [InnerFlowLab 系統建置](2026-04-20-innerflowlab-system-setup.md) | 子域名 vs 主站、WP API 接口、Meta App 前置條件、跨平台 API 一次做完、Substack 收費模型 |
