# Skill:指向性地圖(系統全貌導覽視覺化)

- 建立:2026-08-25|更新:2026-08-25(Owner 澄清語義+首版已建)|作者:A0/Fable5|狀態:**已建 v1**
- Owner 澄清(msg 3999 前後):指向性地圖=**幫助了解系統全貌的導覽圖**,不是地理地圖。

## 成品位置

- `docs/system-map/index.html` — 單檔互動地圖,瀏覽器直接開,免金鑰免安裝。
- 內容:指揮層(Owner→bot→Fable5→Codex/hermes/Antigravity/win-01/OpenClaw)、七個每日產品(launchd 時刻表)、資料層(三個 repo)、外部能力(TWSE/OpenRouter 三鑰匙/NotebookLM/Firecrawl/聲音生成)、通道(TelbotFin)。
- 互動:點節點→右欄顯示「它是誰、誰指向它、它指向誰、檔案在哪」,並亮起相關箭頭;上方按層過濾。

## 維護規則(所有 agent 共用)

1. 系統拓撲變了(新 agent、新產品 job、新外部能力、通道改動)→ 改 index.html 裡的 NODES/EDGES 兩個陣列即可,不用動繪圖程式。
2. 每個節點的 paths 必須是真實檔案位置——這張圖同時是新 agent 的入門導覽,錯的路徑比沒有更糟。
3. 節點描述用 Owner 看得懂的話(說人話),工程細節放 paths 指向的文件。
4. 不放任何金鑰、token、客戶個資;chat_id 等識別碼也不放(圖可能被截圖分享)。

## 待辦

- 併入 WordPress/SEO 線的細節節點(等 Antigravity 巡檢資料)。
- 若 Owner 早前另有舊版指向性地圖檔案,找到後把有用的元素併入本版。
