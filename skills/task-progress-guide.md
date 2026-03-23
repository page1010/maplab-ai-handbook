# task-progress-guide.md — 任務紀錄與接續技能書（必拿）

**這是所有 Agent、所有任務都必須讀的技能書。不可跳過。**

> 核心目的：讓每個 Agent 養成「做一步記一步」的習慣，確保 session 斷線時進度不丟、接手者不迷路、Owner 隨時知道你在幹嘛。

---

## 1. 為什麼這本是必拿

系統反覆出現的問題：
- Agent 一口氣衝到底，中間出錯不回報，最後才發現方向錯
- Session 斷線後新 Agent 接手，不知道上一個做到哪，從頭讀起浪費時間
- Agent 選了做法 A 但行不通，自己默默換成 B，Owner 不知道
- 大任務沒拆分，做到一半 context 爆掉，前面的進度全部丟失

這本技能書解決以上所有問題。PROTOCOL 有精簡版規則，這裡是完整版（含範例和原則）。

---

## 2. 每步紀錄（Progress Log）

**時機**：每完成一個可獨立描述的步驟，立即紀錄。不是做完全部才寫。

**格式**：
```
Progress Log #[序號]
- Done: [用一句話描述剛完成什麼]
- Result: [成功 / 失敗 / 部分完成 — 附具體證據]
- Next: [下一步要做什麼]
- Blocker: [卡住什麼，沒有就寫「無」]
```

**範例 — 成功的情況**：
```
Progress Log #3
- Done: 從 TimeTree IndexedDB 提取外燴事件資料
- Result: 成功，746 筆事件，392 個日期（2022-03 ~ 2025-06）
- Next: 將 JSON 寫入 GitHub data/timetree_events_2022_2026.json
- Blocker: 跨 origin（timetreeapp.com → github.com）無法直接傳 46KB 資料
```

**範例 — 失敗的情況**：
```
Progress Log #5
- Done: 嘗試用 navigator.clipboard.writeText 跨 tab 傳資料
- Result: 失敗 — DOMException: Document is not focused（瀏覽器安全限制）
- Next: 改用 BroadcastChannel 或 window.name 嘗試
- Blocker: 無，有替代方案可試
```

**原則**：
- Result 要有證據：數字、檔名、commit hash、錯誤訊息都算
- 失敗時寫為什麼失敗，不能只寫「沒成功」
- Blocker 不是恥辱，是資訊。寫出來才能解決

---

## 3. 子任務切割

**時機**：任務預估超過 5 個步驟時，開始前先拆。

**方法**：
1. 列出所有需要做的事（不管順序）
2. 分組：哪些可以獨立完成、哪些有前後依賴
3. 排序：依賴鏈決定順序
4. 每個子任務寫完成條件：什麼情況下才算做完

**格式**：
```
子任務清單（等 Owner 確認順序）

□ 子任務 1：[名稱]
  完成條件：[具體可驗證的條件]
  預估步驟：[幾步]

□ 子任務 2：[名稱]
  依賴：子任務 1
  完成條件：[具體可驗證的條件]
  預估步驟：[幾步]
```

**範例**（A1 跨部門溝通 — TimeTree 事件增強）：
```
子任務清單（等 Owner 確認順序）

□ 子任務 1：從 TimeTree IndexedDB 提取事件資料
  完成條件：取得含客戶名的外燴事件 JSON，排除抓週
  預估步驟：3 步

□ 子任務 2：將資料寫入 GitHub
  依賴：子任務 1
  完成條件：data/timetree_events_2022_2026.json commit 成功
  預估步驟：5 步（跨 origin 傳資料有難度）

□ 子任務 3：更新 CURRENT_STATUS + 通知 A5
  依賴：子任務 2
  完成條件：CURRENT_STATUS 最新決策登記 + A5 資料位置說明
  預估步驟：2 步
```

**原則**：
- 拆完先給 Owner 看，不要自己決定順序就開始做
- 每個子任務完成後打勾並寫 Progress Log
- 執行中發現要新增子任務 → 補上去並通知 Owner

---

## 4. 自動讀取下階段

**時機**：完成一個子任務後。

**核心觀念**：完成子任務後不要停下來等 Owner 說「繼續」。自己看清單，找到下一個未完成的子任務，讀需要的檔案，直接繼續。

**流程**：
1. 輸出當前子任務的 Progress Log（標記 ✅）
2. 檢查子任務清單，找下一個 □ 未完成項目
3. 該子任務需要讀新檔案？讀。不確定讀哪些？問 Owner
4. 繼續執行

**範例**：
```
Progress Log #4
- Done: 子任務 2 — JSON 已 commit 至 GitHub（bdab84c）
- Result: 成功，46,055 chars，746 events
- Next: 自動進入子任務 3 — 更新 CURRENT_STATUS + 通知 A5
- Blocker: 無

→ 子任務清單更新：
✅ 子任務 1：IndexedDB 提取
✅ 子任務 2：GitHub commit
□ 子任務 3：CURRENT_STATUS + A5 通知 ← 現在做這個

→ 讀取 CURRENT_STATUS.md 最新內容...繼續執行
```

**何時停下來問 Owner**：
- 遇到 Blocker 無法自己解決
- 方向偏移（§5）
- 子任務清單以外的新發現需要 Owner 決策
- 不確定下一步要讀哪些檔案

---

## 5. 接續 Prompt 生成（Resume Prompt）

**時機**：session 即將結束、或你判斷 context 快滿時。

**目的**：讓新 session 貼這段 prompt 就能無縫接手，不需要從頭讀所有文件。

**格式**：
```
Resume Prompt（貼入新 session 即可接續）
---
角色：[Agent 編號 + 名稱]
任務：[Task ID + 名稱]
已完成：
  ✅ [子任務 1]
  ✅ [子任務 2]
  □ [子任務 3] ← 從這裡接手
下一步：[具體要做什麼]
必讀檔案：[路徑清單]
注意事項：[踩過的坑、Owner 的決策、要避開的做法]
---
```

**範例**：
```
Resume Prompt（貼入新 session 即可接續）
---
角色：A1 Handbook Agent
任務：臨時 — TimeTree 事件資料增強 v2.0
已完成：
  ✅ 從 IndexedDB 提取 746 筆外燴事件
  ✅ JSON commit 至 data/timetree_events_2022_2026.json（bdab84c）
  □ 更新 CURRENT_STATUS 最新決策 ← 從這裡接手
下一步：編輯 CURRENT_STATUS.md 加入 TimeTree v2.0 記錄，然後通知 A5
必讀檔案：
  - CURRENT_STATUS.md（要編輯）
  - projects/maplab-master-data.md（A5 技術文件，確認通知格式）
注意事項：
  - 跨 origin 傳資料用 window.name 解決，clipboard/BroadcastChannel 都不行
  - 抓週事件已排除，Owner 明確要求
  - 不需要金額資料，Owner 明確說不用
---
```

**原則**：
- 必讀檔案寫具體路徑，不要寫「相關文件」
- 注意事項寫具體決策和失敗經驗，不要寫「Owner 有一些指示」
- 這段 prompt 是給零上下文的新 session 看的，要能自足

---

## 6. 方向偏移處理

**時機**：執行中發現原本選的做法行不通。

**錯誤做法**：自己默默換方案繼續做。
**正確做法**：停下來，回報 Owner，等指示。

**格式**：
```
方向偏移通知
- 原本做法：[A/B/C + 簡述]
- 遇到的問題：[為什麼行不通，附具體證據]
- 已嘗試：[試了什麼修復，結果如何]
- 可能的替代方案：
  A) [做法] — 優點 / 盲點
  B) [做法] — 優點 / 盲點
- 需要 Owner 決定：[具體問題]
```

**範例**：
```
方向偏移通知
- 原本做法：A — 用 clipboard API 跨 tab 傳 46KB JSON
- 遇到的問題：DOMException: Document is not focused。瀏覽器不允許非焦點 tab 寫入剪貼簿
- 已嘗試：
  1. navigator.clipboard.writeText → 失敗（同上）
  2. BroadcastChannel → 失敗（不同 origin）
  3. fetch POST 到 GitHub API → 失敗（private repo 無 auth token）
- 可能的替代方案：
  A) window.name — 優點：跨 origin 持久化 / 盲點：有瀏覽器大小限制，不確定 46KB 能不能放
  B) 下載成檔案再上傳 — 優點：一定成功 / 盲點：需要 Owner 手動操作，不符合「自己處理」的要求
  C) 分段用 tool output 傳 — 優點：不需要特殊技巧 / 盲點：output 限制 ~8K chars，46KB 要分 6 段，可能遺失
- 需要 Owner 決定：要試 A（window.name）嗎？如果失敗會改試 C
```

**原則**：
- 替代方案一樣要列盲點，不要因為急著解決就隱藏風險
- 「已嘗試」很重要 — 告訴 Owner 你不是一碰壁就放棄，也不是盲目重試

---

## 7. 臨時任務的紀錄

不在 TASK_QUEUE 裡的臨時任務，一樣遵守以上所有規則。差別只在收尾時：
- 不需要建 Task Card
- 完成後在 CURRENT_STATUS.md「最新決策」登記
- 如果規模大，建議 Owner 補建 TASK_QUEUE 條目

---

## 速查表

| 什麼時候 | 做什麼 | 詳見 |
|---------|--------|------|
| 完成一個步驟 | 寫 Progress Log | §2 |
| 任務開始前（>5 步） | 拆子任務清單 | §3 |
| 完成一個子任務 | 自動讀取下階段，繼續執行 | §4 |
| Session 快結束 / context 快滿 | 生成 Resume Prompt | §5 |
| 做法行不通 | 停下回報方向偏移 | §6 |
| 臨時任務完成 | 登記 CURRENT_STATUS | §7 |

---

*版本：v1.1 | 建立：2026-03-23 | 維護者：A1 Handbook Agent*
*v1.1 變更：每個章節補真實範例（TimeTree 任務）；新增 §4 自動讀取下階段；Progress Log 補失敗情況範例；速查表更新*
*v1.0：初始版本 — 從 AGENT_STARTUP_PROTOCOL v1.4 的執行中規則獨立成技能書*
