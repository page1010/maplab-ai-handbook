# A8 影音內容產線技能書（Video Pipeline Skills）

> 負責角色：A8 影音內容產線
> 建立：2026-04-19 | 版本：v1.0

---

## 一、核心產線 SOP：一篇文章 → 3 種內容

### 步驟 1：素材準備（5 分鐘）
- 從 A2（MAPLAB 文章）或 B1（InnerFlowLab 文章）取得原文
- 確認配圖（從 A4 照片庫拉高分照片，或 Owner 提供）
- 確認品牌線（MAPLAB 中文 vs InnerFlowLab 英文）

### 步驟 2：NotebookLM Podcast 生成（5 分鐘）
1. 開 NotebookLM → 新 Notebook
2. 上傳文章（PDF / Google Doc / 貼文字）
3. 點 Audio Overview → 等待生成（約 3-5 分鐘）
4. 下載音檔（.wav）
5. 備註：英文效果最佳，中文品質不穩定
6. 產出：10-15 分鐘 podcast 式雙人對話

### 步驟 3：Gemini Flash 拆 Shorts 腳本（2 分鐘）
Prompt 範本：
```
請把以下文章拆成 3-5 段 YouTube Shorts 腳本。
每段要求：
- 50 字以內（中文）/ 30 words 以內（英文）
- 開頭第一句是 hook（吸引前 3 秒注意力）
- 附建議配圖描述（從已有照片裡選）
- 附建議字幕文字

文章內容：
[貼文章]
```

### 步驟 4：Google Vids 組裝影片（10 分鐘/支）
1. 開 Google Vids → 新專案
2. 輸入腳本文字 → 自動排版
3. 上傳配圖 → 對應每段腳本
4. 調整字幕位置/大小
5. 匯出（9:16 直式，1080x1920）

### 步驟 5：多平台發布
| 平台 | 格式 | 注意事項 |
|------|------|---------|
| YouTube Shorts | 9:16, ≤60 秒 | 標題含關鍵字、加 #Shorts tag |
| YouTube 長片 | 16:9 or 音檔配靜態圖 | Podcast 用，加時間戳章節 |
| IG Reels | 9:16, ≤90 秒 | 封面圖要另外設計 |
| TikTok | 9:16, ≤60 秒 | 同 Shorts 素材直接上傳 |
| Threads | 圖文 | 截取 Shorts 精華幀 + 金句文字 |
| Facebook Reels | 9:16 | 選擇性，同 Shorts 素材 |

---

## 二、兩條內容線的差異

### MAPLAB 線（中文）
- 素材：活動照片、品項照片、場景頁文章
- 語氣：專業、溫暖、活動感
- Shorts 主題範例：
  - 「30 秒看懂戶外婚宴外燴」
  - 「派對外燴必點 TOP 5」
  - 「企業尾牙外燴場地佈置 before/after」
- NotebookLM：中文效果有限，優先用 Shorts

### InnerFlowLab 線（英文）
- 素材：Substack 文章、旅遊照片、個人筆記
- 語氣：個人、反思、真實
- Shorts 主題範例：
  - "One thing I learned building AI systems"
  - "Travel journal: morning market in [地點]"
- NotebookLM：英文 Audio Overview 效果最佳，主力產出

---

## 三、品質檢查清單

### Shorts 發布前
- [ ] 前 3 秒有 hook
- [ ] 字幕可讀（字體大小、對比度）
- [ ] 9:16 直式，無黑邊
- [ ] 時長 ≤ 60 秒
- [ ] 標題含關鍵字
- [ ] 縮圖/封面吸引人

### Podcast 發布前
- [ ] 音檔品質正常（無雜音、斷句自然）
- [ ] YouTube 標題 + 描述含關鍵字
- [ ] 時間戳章節已加
- [ ] 配圖/封面已設定

---

## 四、免費額度管理

| 工具 | 免費額度 | 注意事項 |
|------|---------|---------|
| NotebookLM | 免費，有每日生成上限 | 一天約 3-5 個 Audio Overview |
| Gemini Flash | 1,500 requests/day | 腳本拆段消耗極小 |
| Google Vids | Workspace 方案內含 | 確認帳號已開通 |
| YouTube | 無限上傳 | 新帳號前 24h 限 15 分鐘影片 |

---

## 五、協作觸發點

| 事件 | A8 動作 |
|------|---------|
| A2 發新 WordPress 文章 | 收到通知 → 跑產線 → MAPLAB Shorts |
| B1 發新 Substack 文章 | 收到通知 → NotebookLM podcast + Shorts |
| A4 完成照片分類批次 | 檢查新素材，更新可用照片庫 |
| Owner 提供旅遊照片 | B1 寫文 + A8 做影音 |
