# 使用者回饋：報價系統 v2 — 2026-04-01

## 1. Apps Script 副本公式問題
- copyTo 複製分頁到新 Spreadsheet 後，VLOOKUP 公式指向原 Sheet 的 Items 表，新檔案裡沒有 Items 表所以公式變 #REF!
- makeCopy 複製整個檔案也不行，因為會連所有分頁一起複製
- 正確做法：複製時只保留品項名稱和數量（值），成本欄用 IMPORTRANGE 從母版 Items 表拉，或者直接把 Items 表也複製一份到新檔案（隱藏）
- Owner 原話：「副本公式這樣不行，本來只抓值有菜名，你這樣改全部不就變公式」

## 2. to B 企業客戶要加 Slide 功能
- 表單要有「是否需要 Slide」勾選
- 如果要 → 開一個 Drive 資料夾（以客戶公司名命名），放 Sheet + Slide
- 需要先看 A6 之前做的英文版 Slide 和報價經驗
- 參考：slides-quotation-system.md、A6 報價 SOP

## 3. QUOTE_DRAFT 母版 10 個改進
1. 加「人數」欄位 — 目前母版沒有人數
2. 熱客招待改隱藏行 — 客戶看到會要求優惠
3. 活動類型下拉放母版 — 方便業務在報價單上改
4. 條款區根據活動類型自動切換 toB/toC
5. 加「活動地點」欄位
6. 加「活動日期」欄位
7. I 欄（業務報價單價）加黃底提示
8. E33（報價總額）加粗放大
9. 加「備註」欄
10. 匯款資訊用公式連動條款版本

## 4. 活動類型 → 條款自動判斷
- 現在看「有沒有填公司名」判斷 toB/toC
- 應改成看活動類型：企業開幕/尾牙/記者會 = toB，週歲/婚禮/性別揭曉 = toC
- 同時保留「有填公司名就強制企業版」

## 5. Batch API + Prompt Caching 技能
- Batch API 50% 折扣 — 適合 A4 照片分類、SEO 文章生成（非即時）
- Prompt Caching 省 90% — 適合 Agent system 每次帶大量 system prompt
- 兩者疊加最多省 95%
- 需要寫成技能，要求所有 agent 在適用場景使用

## 下一個 session 要做的事
1. 修 Code.gs：makeCopy 改成 DriveApp.getFileById(SPREADSHEET_ID).makeCopy() 然後刪除非 QUOTE_DRAFT 的分頁
2. 研究 Batch API + Prompt Caching 寫成 skills/cost-optimization-guide.md
3. 母版改進（先做人數 + 熱客隱藏 + E33 顯眼）
4. A6 Slide 整合規劃
