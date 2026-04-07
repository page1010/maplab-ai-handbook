# Skill: command-index — Owner 指令速查表

## 觸發條件

Owner 說以下任何一句話時，輸出下方速查表：
- 「技能」「列出技能」「我可以叫你做什麼」
- 「指令」「有哪些指令」「能做什麼」
- 「幫我列出全部」「功能清單」

---

## MAPLAB Kitchen 指令速查

| 你說... | AI 會做... | Skill | 狀態 |
|---------|-----------|-------|------|
| 巡檢 / 檢查進度 / 系統健檢 | 盤點 repo、掃描遺漏、輸出巡檢報告、修正歸位 + commit | system-audit | ✅ 已建立 |
| 新增品項 / 修正品項 / 更新照片 / 重新編號 | Items 表操作（新增/修正分類/更換照片）+ 重新編號 | items-management | ✅ 已建立 |
| clasp 部署 / 部署 Apps Script | Apps Script 部署到 Google（clasp pull + push） | clasp-deploy | ✅ 已建立 |
| 技能 / 列出技能 / 指令 | 列出這張速查表 | command-index | ✅ 已建立 |
| dashboard / 看板 | 更新/檢查 Task Board Dashboard 工作表 | (待建) | 🔲 待建 |
| 報價 / 新增報價 | 觸發 A5/A6 報價流程 | (待建) | 🔲 待建 |
| LINE 進件 / 新客戶 | A6 LINE 業務報價助手操作流程 | a6-telegram-window | ✅ 已建立 |
| 快速報價 / 急報價 | A6 Telegram 窗口快速報價 SOP | a6-rapid-quote-sop | ✅ 已建立 |
| 廣告 / 社群廣告 | A3 社群廣告操作（Meta Ads / 文案生成） | a3-social-ads-skills | ✅ 已建立 |
| 照片分類 / 照片整理 | A4 照片分類 pipeline（Gemini + Google Drive） | a4-photo-asset-skills | ✅ 已建立 |
| Canva修圖 / 品項照片 / 套濾鏡 | 用品牌色濾鏡標準調整食物照片 | canva-photo-filter | ✅ 已建立 |
| 轉檔 / HEIC 轉 JPG / 圖片格式轉換 | HEIC/HEIF/WEBP/PNG → JPG，轉換後上傳 Drive + 更新 K 欄 | image-convert | ✅ 已建立 |
| 客服 / 回覆訊息 | A7 客服回覆模板 + 補問流程 | a7-customer-service-skills | ✅ 已建立 |
| 報告 / 業務報告 | A5 報價引擎 + 品項數據分析 | a5-quotation-engine-skills | ✅ 已建立 |
| 開 AX / 召喚 AX / 跑 AX | 召喚對應角色的 Code session | summon-role | ✅ 已建立 |

---

## Skill 目錄結構

```
skills/
├── command-index/       ← 本 Skill（速查入口）
│   └── SKILL.md
├── system-audit/        ← 巡檢 SOP
│   └── SKILL.md
├── items-management/    ← Items 品項管理
│   └── SKILL.md
├── clasp-deploy/        ← Apps Script 部署
│   └── SKILL.md
├── summon-role/         ← 角色召喚 SOP（Code session + Extension 兩路徑）
│   └── SKILL.md
├── session-lifecycle/   ← Session 開始/結束規則
│   └── SKILL.md
├── image-convert/       ← HEIC/WEBP/PNG → JPG 轉換 + Drive 上傳
│   └── SKILL.md
├── check-rules/         ← Sheets 資料修改安全規則
│   └── sheets-data.md
├── a6-telegram-window.md      ← A6 Telegram 操作手冊
├── a6-rapid-quote-sop.md      ← A6 快速報價 SOP
├── a3-social-ads-skills.md    ← A3 廣告技能
├── a4-photo-asset-skills.md   ← A4 照片資產管理
├── a5-quotation-engine-skills.md ← A5 報價引擎
├── a7-customer-service-skills.md ← A7 客服技能
└── ...（其他參考指南）
```

---

## 給 AI 的說明

輸出速查表後，詢問 Owner：「你想做哪一個？」
如果 Owner 直接說了具體動作（例如「新增品項」），跳過速查表，直接執行對應 Skill。
