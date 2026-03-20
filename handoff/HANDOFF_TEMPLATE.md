# HANDOFF_TEMPLATE.md — AI Agent 交接模板

> 每次工作結束前必須填寫此模板，commit 到 handoff/ 資料夾。

---

## 使用方式

複製以下模板，填寫本次內容，commit 到 handoff/ 資料夾，檔名用日期：
handoff/YYYY-MM-DD-{agent-role}.md

例如：handoff/2026-03-12-handbook-agent.md

---

## 交接模板（複製此區塊填寫）

    # 交接紀錄 — {日期} {你的角色}

    ## 我是誰
    角色：{Handbook Agent / SEO Agent / Ads Team / Pipeline Agent / Master Data Agent / AI Reply Agent}
    任務來源：{CURRENT_EXECUTION_BOARD.md 或 用戶指令描述}

    ## 本次完成事項
    - [ ] {已完成事項 1，附可見產出：commit hash / URL}
    - [ ] {已完成事項 2}

    ## 驗證確認（Superpowers: verification-before-completion）
    - 產出 1：{commit hash，可直接驗證}
    - 產出 2：

    ## 未完成 / 卡點
    - {卡在哪裡，根因是什麼}
    - {需要用戶做什麼才能繼續}

    ## 下一棒待辦（按優先順序）
    P1 {角色}：{具體任務描述，給下一個 agent 直接執行}
    P2 {角色}：{具體任務描述}
    P3 {角色}：{具體任務描述}

    ## 不在我範圍內、但要提醒的事
    - {看到其他專案的事項，記錄在此，交給對應 agent}

    ## 關鍵資源（本次用到的）
    - GitHub repo：{連結}
    - 相關文件：{projects/ 或 skills/ 路徑}
    - 其他：

---

## 歷史交接紀錄（最新在上）

| 日期 | Agent 角色 | 完成事項摘要 | 下一棒主要任務 |
|---|---|---|---|
| 2026-03-14 | Master Data Agent | Schema v0.1 + field-naming-rules + table-relationship-map | A4 Pipeline 對接 |
| 2026-03-12 | Handbook Agent | 建立 AGENT_RULES.md v1.0 | 建立 projects/maplab-pipeline.md、skills/superpowers-guide.md |
| 2026-03-12 | SEO Detasys Agent | Post 498/1168 發布、GSC OAuth v1.3 | 本機跑 python ads_agent.py --mode gsc 驗證 v1.3 token |

---

*版本：v1.1 | 更新：2026-03-17 | 維護者：A1 Handbook Agent*
