# A6 Culture Loop — 第一輪批改蒸餾報告
> 批改者：Claude（independent-verifier）| 日期：2026-06-26
> 資料：42 筆代表性樣本（line_oa_csv_parser.py 萃取，已去識別化）
> 批改入口：Google Sheet https://docs.google.com/spreadsheets/d/1NxBso2ried_4uxFzQPDtDuUTZlx7BN5qrC9xO2oZhm4/edit

---

## 批改結果摘要

| 指標 | 數值 |
|---|---|
| 樣本數 | 42 |
| 正確 (✓) | 22 (52.4%) |
| 需修正 (✗) | 20 (47.6%) |
| PII 補修補 | 1 筆（姓名：麥琬如 → [姓名]，Sheet Row 39）|

### 各 Stage 精準度

| Stage | 抽樣數 | 正確 | 精準度 | 主要問題 |
|---|---|---|---|---|
| S6_PREDAY       | 4  | 4  | 100% | — |
| S2_DATA         | 3  | 3  | 100% | — |
| S4_PAYMENT_INFO | 2  | 2  | 100% | — |
| S4_BOOKING_ASK  | 2  | 2  | 100% | — |
| S5_PAYMENT      | 1  | 1  | 100% | — |
| S5_PAYMENT_ACK  | 1  | 1  | 100% | — |
| S2_DIETARY_ASK  | 1  | 1  | 100% | — |
| S3_QUOTE_INTRO  | 1  | 1  | 100% | — |
| S1_INQUIRY      | 3  | 2  | 67%  | 外帶取餐時程誤標 S1 |
| S3_BUDGET_CONFIRM| 3 | 1  | 33%  | 「預算」keyword 過早觸發 |
| S3_QUOTE_SEND   | 7  | 2  | 29%  | 與 S3_QUOTE_INTRO 混淆；S6 venue topics 混入 |
| S0_OPENING      | 2  | 0  | 0%   | 業務 reply 含「您好」就觸發，過於寬鬆 |
| S_PENDING       | 12 | 2  | —    | 10/12 可分類（有正確 stage）；真正 S_PENDING 僅 2 筆 |

---

## Prompt 缺口分析（根因 → 具體補救）

### GAP-1｜S3_QUOTE_SEND vs S3_QUOTE_INTRO 邊界未定義
**根因**：兩個 stage 的區別是「介紹框架」vs「傳送具體菜單」，但 heuristic 混用相同 keyword 池。  
**現象**：「下方幫您做方案介紹」、「費用$X萬起」等 INTRO 行為，被分類為 SEND。  
**prompt 該補的描述**：
> S3_QUOTE_INTRO = 業務說明服務範圍框架、低消、品數大綱、費用「區間」；  
> S3_QUOTE_SEND = 業務傳送具體菜單品項、照片、或具體報價金額（非區間）。  
> 判斷準則：業務 reply 含「★整體規劃服務範圍」、「費用是$X-$Y起」、「整體規劃的費用」→ INTRO；  
> 含「照片已傳送」、列出具體品項名稱（鹹點/甜點/飲品）、具體金額 → SEND。

**影響範例**：Row 13, 15 (INTRO), Row 18 (實際是 S6 venue setup)

---

### GAP-2｜S0_OPENING 過度觸發
**根因**：業務 reply 包含「您好」即觸發 S0，無視客人訊息內容。  
**現象**：客人已問「[日期]上午有檔期嗎」（有實質意圖），業務回「您好，目前可以安排」→ 被標為 S0。  
**prompt 該補的描述**：
> S0_OPENING 的充要條件：  
> ① 客人訊息是純問候/貼圖/第一次加好友，無具體詢問內容  
> ② 業務 reply 是自動歡迎或人工「您好」跟進，未要求任何資訊  
> 若客人已提及日期/人數/活動/場合/檔期詢問 → 至少是 S1_INQUIRY，不是 S0。

**影響範例**：Row 37, 38

---

### GAP-3｜S_PENDING 的 32.6% 大多可分類，只是缺前文上下文
**根因**：單一對對抽取（user→account adjacency）丟失了前面 N 輪的對話脈絡。  
**現象**：Row 1「當日或隔天過去」= S6_PREDAY；Row 11「一組14隻嗎」= S3_MENU_ADJUST；Row 12「去拿鑰匙」= S6_PREDAY。  
**prompt 該補的描述**：
> 短確認語分類規則（依「業務 reply 行為」判斷，不依「客人說什麼」）：  
> 業務 reply 提到「當天/到達/幾點/鑰匙/尺寸/走廊/桌子數量」→ S6_PREDAY  
> 業務 reply 提到「尾款/扣押金/金額確認」→ S4_PAYMENT_INFO  
> 業務 reply 提到「下週一/主廚做好給你」→ S4_BOOKING_ASK（後收尾）  
> 業務 reply 說「對」「好的」→ 保留 S_PENDING，需人工 + 上下文

**S6_PREDAY keyword 補充清單**：走廊、擺椅子、椅子、鑰匙、示意圖、尺寸、長×寬、桌子幾張、規劃師、停車、進場

---

### GAP-4｜S3_BUDGET_CONFIRM 過早觸發
**根因**：「預算」一詞即觸發，但業務如果仍在問日期/人數 → 還在 S2_DATA。  
**現象**：Row 30「有預算有推薦的嗎？/業務問「請問日期是哪天」→ 被標 S3_BUDGET_CONFIRM。  
**prompt 該補的描述**：
> S3_BUDGET_CONFIRM 觸發條件：  
> ① 客人「明確提出金額或預算 tier」（例：「預算一萬」「大概36K」「一萬左右」）  
> ② 業務 reply 不再問基本資料（無「請問日期/人數/地點」等問題）  
> 若業務仍在詢問日期/人數 → stage 仍為 S2_DATA，即使客人已提及預算。

---

### GAP-5｜外帶取餐時程 vs S1_INQUIRY 誤觸
**根因**：「外帶」關鍵字在 S1_INQUIRY 觸發，但「11:30取餐/跟你約11:45」是交付時程（S6）。  
**prompt 該補的描述**：
> 外帶路徑特殊規則：  
> 客人問「外帶有什麼/如何外帶/有無外帶服務」→ S1_INQUIRY  
> 客人說「大概X點取餐」且業務給具體時間 → S6_PREDAY（外帶交付時程）  
> 分判 key：有無具體時間點 + 業務是否回應具體安排

---

### GAP-6｜S3_MENU_ADJUST 和 S3_QUOTE_ACK 從未被產出
**根因**：這兩個 stage 在 KNOWN_STAGES 但 classify_stage() 無對應路徑。  
**S3_MENU_ADJUST 特徵**：  
> 客人問「可以換X嗎/幾隻一組/這個可以加嗎/寶寶水有嗎/飲料選項」  
> 業務給替代品、份數確認、「可以的/都含進去了」  

**S3_QUOTE_ACK 特徵**：  
> 客人說「了解/好的/謝謝」在收到報價/菜單後  
> 業務說「好的/需要調整嗎/如有問題請告知」  

---

## 召喚術修改提案（diff 格式，待 Owner 確認再改）

### 修改對象 A：`workbook/a6-training/line_oa_csv_parser.py` — `classify_stage()` 函式

```diff
--- a/workbook/a6-training/line_oa_csv_parser.py (current)
+++ b/workbook/a6-training/line_oa_csv_parser.py (proposed)

 def classify_stage(customer_text: str, business_text: str) -> str:
     bt = business_text
     ct = customer_text
     both = ct + " " + bt

-    # S6: pre-event day logistics — table layout, venue, vehicle, staff, timing
+    # S6: pre-event logistics — EXPAND keyword list
     if any(
         k in both
         for k in [
             "明天見", "幾點到", "活動當天", "到了唷", "我們到了",
-            "陳列", "撤場", "撤收", "規劃師", "車號", "服務人員",
-            "帶你們進來", "帶進來", "測量", "長寬", "桌子", "發票",
-            "統編", "請購", "承辦人", "委托書",
+            "陳列", "撤場", "撤收", "規劃師", "車號", "服務人員",
+            "帶你們進來", "帶進來", "測量", "長寬", "桌子", "發票",
+            "統編", "請購", "承辦人", "委托書",
+            # NEW: venue setup keywords from batch review
+            "走廊", "擺椅子", "椅子", "鑰匙", "示意圖", "幾張桌",
+            "停車", "進場", "幾點可以撤", "隔天過去", "當日看一下狀況",
         ]
     ):
         return "S6_PREDAY"

+    # S0_OPENING: only true first contact (customer message has no substantive inquiry)
+    # Move S0 check to BEFORE S1 but ADD constraint
+    _has_inquiry = any(k in ct for k in ["外燴","茶點","茶會","開幕","週歲","派對","到府","詢問","請問",
+                                          "日期","人數","場地","檔期","有嗎","可以","幾點","多少"])
+    if not _has_inquiry and any(k in bt for k in ["您好", "旅圖", "我們是", "Map Lab", "歡迎", "外燴品牌"]):
+        return "S0_OPENING"
+
     ...（其他 stage 不變）...

-    # S3: quote send / menu adjust / budget confirm
+    # S3_QUOTE_INTRO: business introduces service framework (not actual menu)
+    if any(k in bt for k in ["服務範圍", "★", "低消", "外燴整體", "出車", "整體規劃的費用", "低消是"]):
+        return "S3_QUOTE_INTRO"
+
+    # S3_MENU_ADJUST: specific item discussion (NEW — was never produced before)
+    if any(k in both for k in ["換品項", "換成", "改成", "幾隻", "一組", "可以加", "寶寶水", "飲料選項",
+                                 "替換", "換掉", "調整品項", "品項有沒有"]):
+        return "S3_MENU_ADJUST"
+
+    # S3_QUOTE_SEND: actual menu/photo delivery
     if "照片已傳送" in bt or "貼圖已傳送" in bt:
         return "S3_QUOTE_SEND"
     if any(
         k in both
         for k in [
-            "菜單", "換品項", "鹹點", "甜點", "飲品", "飲料",
-            "份數", "道", "幾款", "幾道", "調整", "提供報價",
-            "報價單", "估價單", "換成", "改成", "增加",
+            # Only when business actually sends specific menu items
+            "鹹點", "甜點", "飲品", "報價單", "估價單",
         ]
     ):
         return "S3_QUOTE_SEND"

-    if any(k in both for k in ["預算", "價位", "幾萬", "幾千", "提案", "評估"]):
+    # S3_BUDGET_CONFIRM: BOTH customer mentions amount AND business doesn't ask basic info
+    _business_asks_basics = any(k in bt for k in ["日期", "人數", "幾位", "地點", "場地"])
+    if (any(k in both for k in ["預算", "價位", "幾萬", "幾千", "提案", "評估"])
+            and not _business_asks_basics):
         return "S3_BUDGET_CONFIRM"

-    if any(k in bt for k in ["服務範圍", "★", "低消", "外燴整體", "出車", "整體規劃", "低消是"]):
-        return "S3_QUOTE_INTRO"
-
     ...

-    # S0: opening greeting
-    if any(k in bt for k in ["您好", "旅圖", "我們是", "Map Lab", "歡迎", "外燴品牌"]):
-        return "S0_OPENING"
+    # S0: greeting (fallback, only if no inquiry detected above)
+    if any(k in bt for k in ["您好", "旅圖", "我們是", "Map Lab", "歡迎", "外燴品牌"]):
+        return "S0_OPENING"   # still kept as fallback; _has_inquiry already checked above
```

### 修改對象 B：新增 `skills/a6-stage-labeling-rubric.md`

需新建此檔，定義：
1. 7 段 stage 的充要判斷條件（正面例 + 反面例各 2 筆）
2. S3_QUOTE_SEND vs INTRO 決策樹
3. 短確認語分類規則（依業務 reply 行為推斷）
4. 外帶路徑 vs 外燴路徑分判

### 修改對象 C：`chrome-extension/task-modules/A6.json` → `skills/a6-qa-examples.md`（目前標注「待建」）

在 A6 專用三件套第 7 項新增 stage rubric 引用：
```diff
-7. `skills/a6-qa-examples.md` — **QA 範例庫**（待建，每個活動類型 2-3 組真實對話 + 操作記錄）
+7. `skills/a6-qa-examples.md` — **QA 範例庫**（每個 stage 2-3 組已去識別化對話範例）
+8. `skills/a6-stage-labeling-rubric.md` — **Stage 標籤 Rubric**（7 段 SOP 的充要判斷條件 + 反例；culture loop distill）
```

---

## Culture Loop 抓到的系統性問題（呼應「評分太慷慨」）

| 問題 | 現象 | 根因 |
|---|---|---|
| Heuristic 過於慷慨給 S3_QUOTE_SEND | 任何含「菜單/換/調整」的業務回覆都算 | keyword 正向匹配，無反例/約束條件 |
| S0_OPENING 過度觸發 | 「您好」就算開場 | 未定義「客人已有實質意圖 → 不是 S0」的否定條件 |
| S3_BUDGET_CONFIRM 過早觸發 | 「有預算」 就標 S3 | 未設「業務行為還在問基本資料 → 仍是 S2」的約束 |
| S_PENDING 放棄太早 | 32.6% 標 S_PENDING，其中 83% 可分類 | 僅依客人訊息分類，未善用業務 reply 作訊號 |

**根本設計缺陷**：classify_stage 是純 keyword 正向匹配，**缺乏**：
1. 否定條件（「即使有 X，如果有 Y 則不標 Z」）
2. 業務 reply 優先（業務的問法比客人說什麼更能確定 stage）
3. Stage 互斥的 priority ordering（當多個 stage 都匹配時，選最晚的那個）

---

## 行動清單

- [ ] Owner 覆核 Sheet 批改結果（42 筆，重點看 S3_QUOTE_SEND 5 筆誤標）
- [ ] Owner 確認召喚術修改提案 A（classify_stage diff）
- [ ] A1/Owner 建立 `skills/a6-stage-labeling-rubric.md`（5 個 stage 各 2 筆正反例）
- [ ] 重跑 pipeline 套用新 classify_stage → 預期 S_PENDING 降至 <20%，S3_QUOTE_SEND 精準度 >70%
- [ ] 下一輪 culture loop：重新抽 42 筆 → 驗證改善
