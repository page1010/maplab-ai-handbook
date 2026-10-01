# 經驗分享 / Lessons Learned

## 目的
記錄所有 Agent 犯過的錯，避免重蹈覆轍。每位 Agent 開工前必讀。

---

## INCIDENT-001: Takeout ZIP 被刪導致 EXIF metadata 永久遺失

- 日期: 2026-03-17
- Agent: A4 (Pipeline Agent)
- 嚴重性: HIGH
- 資料影響: mina 帳號 122,200 張照片的 JSON sidecar metadata 永久遺失

### 事件經過
1. A4 從 Takeout ZIP 解壓時，只提取了圖片/影片檔案
2. 沒有同時提取 JSON metadata 檔案
3. 建議用戶清空垃圾桶回收空間
4. 用戶清空垃圾桶時，原始 Takeout ZIP 一起被刪除
5. 再回頭提取 JSON 時才發現 ZIP 已經不存在

### 根本原因
- 流程規劃不完整: 解壓時沒有一次性提取所有需要的檔案
- 建議清除前沒有確認依賴
- 缺乏不可逆操作的警覺

### 防範規則
> 在建議用戶執行任何不可逆操作前，必須：
> 1. 列出該資源中所有尚未提取/備份的資料
> 2. 確認所有提取工作已完成並驗證
> 3. 明確告知風險

---

## INCIDENT-002: Vertex AI 模型 404 — 模型名稱不存在

- 日期: 2026-03-18
- Agent: A4 (Pipeline Agent)
- 嚴重性: MEDIUM
- 影響: V2, V5 兩個版本浪費在不存在的模型上

### 事件經過
1. V2 使用 Vertex AI SDK + gemini-2.0-flash → 404 Publisher Model not found
2. V5 改用 gemini-1.5-flash → 同樣 404
3. 原因: Colab 環境中 Vertex AI SDK 版本可能不支援這些模型名稱

### 教訓
- Vertex AI 模型名稱格式與 Generative AI API 不同
- 在 Colab 環境中，google.generativeai + API key 比 Vertex AI SDK 更穩定
- 應先用最簡單的 API 調用方式驗證，再封裝

---

## INCIDENT-003: GitHub Raw Content 快取導致部署失敗

- 日期: 2026-03-18
- Agent: A4 (Pipeline Agent)
- 嚴重性: MEDIUM
- 影響: V6.1 修正後仍下載到舊版腳本

### 事件經過
1. PR #15 合併修正 unicode 問題
2. Colab curl 下載 raw.githubusercontent.com 仍拿到舊版
3. 加上 ?t=N 查詢參數後才拿到新版

### 防範規則
> 每次 merge PR 後，curl 下載必須加 ?t={timestamp} 快取破壞參數

---

## INCIDENT-004: PHOTO_ROOT 路徑錯誤

- 日期: 2026-03-18
- Agent: A4
- 嚴重性: LOW

### 事件經過
1. V6 設定 PHOTO_ROOT = /content/drive/MyDrive/MAPLAB/photos
2. 實際照片在 /content/drive/MyDrive/MAPLAB/photos/Takeout/Google 相簿/
3. 需要 debug cell 用 os.listdir 逐層檢查才找到

### 教訓
- 不要假設資料夾結構，先用 os.listdir 驗證
- Takeout 解壓後會有額外的 Takeout/ 和服務名稱/ 子目錄

---

## INCIDENT-005: google.generativeai 已棄用 — PIL Image 400 錯誤

- 日期: 2026-03-19
- Agent: A4
- 嚴重性: HIGH (CURRENT BLOCKER)

### 事件經過
1. V6.2/V6.3 使用 google.generativeai + API key
2. 傳入 PIL.Image 物件到 generate_content() → 400 Bad Request
3. gemini-2.0-flash 和 gemini-1.5-flash 都返回同樣的 400
4. FutureWarning 明確說 google.generativeai 已棄用
5. 400 URL 中有 %24alt=json%3Benum-encoding 暗示序列化問題

### 計畫修復方案
1. 優先: 改用 google.genai (新 SDK) + API key
2. 備選: 直接用 REST API + base64 圖片
3. 備選: 在 google.generativeai 中用 base64 而非 PIL Image

### 教訓
- 注意 FutureWarning — 棄用的套件可能有隱性 bug
- 多種 Google AI SDK 容易混淆: google.generativeai vs google.genai vs vertexai
- 應先用最小測試案例驗證 API 調用

---

## INCIDENT-006: 規範檔自己是缺陷的上游 — 廣告文案連退十一輪

- 日期: 2026-09-30 ~ 2026-10-01
- Agent: A0 / Fable5 線（廣告文案）
- 嚴重性: HIGH（已上帳號的 56 則文案單元有 41% 要重寫，全數 PAUSED 未燒錢）

### 事件經過

1. 十則廣告掛上帳號，值班紀錄寫「對禁語表全掃＝零違規」，據此宣稱文案沒問題
2. Owner 連續退了十一輪，從 9/30 15:33 到 10/01 16:01，約 27 小時
3. 每一輪都升一個閘門類別，從 4 類長到 15 類
4. 第十一輪（msg 6506）退掉的七則，**通過了當時全部十四類**

### 根本原因

不是十一個獨立失誤，是**一條沒標適用範圍的規範**長出來的十一種形狀。

`skills/brand-voice-guide.md` §二第 1 條寫「說場景，不硬講賣點：優先描寫空間、
時刻、人的感受、現場氛圍」。那是為官網形象頁寫的，沒有人標註它不適用於廣告。
照著寫出來的就是「白色蕾絲桌巾與金色層架」——空間有了、氛圍有了、人不見了。

**查缺陷的時候只查了產出，沒查產出依據的那份規範。**

### 四個分層教訓（照發現順序，後面的查不到前面的）

| 層 | 問的問題 | 查得到的工具 |
|---|---|---|
| 合規 | 有沒有講不該講的話 | 禁語表掃描 |
| 立場 | 主詞是不是看的人、有沒有在評論人家可憐 | `ad_copy_voice_check.sh` ①～⑬ |
| 分佈 | 整批攤開是不是同一個模子 | 同一支的 ⑭（corpus 層） |
| 事實 | 講的那件事我們到底做不做 | `docs/ADS_SERVICE_SCOPE.md` ＋ ⑮ |

**上層全過不代表下層沒事。** 合規過了只能說沒講不該講的，
把它寫成「文案檢查通過」就是謊報。

### 防範規則

> 1. **任何規範條文都要標適用範圍。** 沒標範圍的規則會被套到不適用的地方，
>    而且出事時沒有人會回頭懷疑規範本身。
> 2. **缺陷回溯要查到規範層。** 問「這個錯是照哪一條寫出來的」，
>    不是只問「這一句怎麼改」。
> 3. **規範是 SSOT，閘門是它的機器投影；要改射程先改規範再改腳本。**
>    反過來做會變成閘門說了算，而閘門沒辦法解釋為什麼。
> 4. **指章節不指行號。** 腳本註解原本寫「brand-voice-guide.md 第 57 行」，
>    手冊一改版就失效。
> 5. **升了閘門類別必須跑全量回歸。** 10/01 的實證：前一天升了兩類只跑新稿，
>    兩份正例測資從 PASS 翻成 FAIL 掛了一整天沒被看見。
>    落地：`scripts/ad_copy_gate_regression.sh`。

### 沉澱位置

- 寫作規範：`skills/brand-voice-guide.md` §十二（v1.2）
- 服務事實：`docs/ADS_SERVICE_SCOPE.md`
- 企業文化：`docs/OPERATING_CULTURE.md` 原則 12 第 1～14 條（v2.6）
- 機器層：`scripts/ad_copy_voice_check.sh` 15 類 ＋ `ad_copy_gate_regression.sh`
- 回歸測資：`tests/fixtures/ad_copy_*`（8 份反例必 FAIL、2 份正例必 PASS）