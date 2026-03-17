# Context Compression Guide — 防 Prompt Too Long 技能書
版本：v2.0 | 建立：2026-03-15 | 更新：2026-03-17 | 維護者：A4 Pipeline Agent

本文件提供 MAPLAB AI 系統在對話 context 接近上限時的**標準應對流程**。
v2.0 加入程式開發專用的防爆策略、GitHub API 操作節約技巧、實戰踩坑紀錄。

---

## 為什麼會爆？

Claude context window 約 200,000 tokens。以下操作特別燒 token：

| 操作 | 單次消耗 | 危險等級 |
|------|---------|---------|
| get_page_text 完整頁面 | 2,000-10,000 | 中 |
| read_page (all) 含完整 DOM | 5,000-50,000 | 極高 |
| GitHub API 回傳 JSON（含 base64 content） | 3,000-15,000 | 高 |
| Colab 長輸出（unzip 122k files） | 5,000-20,000 | 高 |
| 每輪對話（含系統 prompt） | 500-2,000 | 低 |
| JavaScript fetch 結果存 window 變數 | 0（不進 context） | 安全 |

一個典型 session 的 token 預算分配：
- 系統 prompt + 規則：~30,000
- 對話摘要（壓縮後）：~10,000-20,000
- 剩餘可用：~150,000
- 安全水位（70%）：~105,000 → 超過就要開始節約

---

## 第一層防線 — 預防（最重要）

### 規則 1：一個 session 只做一件大事

不要在同一個 session 裡又讀文件又寫程式又 debug 又更新 3 個 repo。
一個 session 的合理容量：
- 讀 2-3 個文件 + 寫 1 個 PR + 更新 1 個 state 檔
- 或：debug 1 個問題 + 修復 + 驗證
- 或：Colab 執行 1 個任務 + 確認結果 + 記錄

### 規則 2：讀文件選對工具

| 目的 | 用什麼 | 不要用什麼 |
|------|--------|-----------|
| 讀文章/文件內容 | get_page_text | read_page (all) |
| 找特定按鈕/輸入框 | find('按鈕名稱') | read_page (all) |
| 操作表單 | read_page (interactive) | read_page (all) |
| 確認 GitHub commit 成功 | 看 fetch response name | get_page_text 整頁 |

### 規則 3：GitHub API 結果不要讀 content 欄位

GitHub Contents API 回傳的 JSON 含 base64 encoded content，非常大。

```
# 省 token 的做法：
# 1. 只讀 SHA（確認檔案存在）
# 2. 用 raw.githubusercontent.com 讀內容（比 API JSON 小）
# 3. fetch 結果存 window 變數，不印出來

# 正確：用 raw URL 讀
navigate('https://raw.githubusercontent.com/user/repo/main/path/file.py')
get_page_text()  # 純文字，最省

# 錯誤：用 API + 解碼整個 JSON response
navigate('https://api.github.com/repos/user/repo/contents/path/file.py')
get_page_text()  # JSON + base64 = 超大
```

### 規則 4：JavaScript fetch 結果存 window，不印出來

```javascript
// 正確：結果存 window 變數，只印關鍵資訊
fetch(url).then(r => r.json()).then(d => {
  window._result = d;
  // 只取需要的欄位
});
// 之後用 window._result.sha 取值

// 錯誤：直接印整個 response
fetch(url).then(r => r.text()).then(t => t);  // 整個 JSON 進 context
```

### 規則 5：Colab 輸出控制

Colab cell 輸出會全部進 context。大量檔案操作用 quiet mode：

```bash
# 正確：-q 安靜模式 + 只印摘要
unzip -n -q file.zip -d /output/
echo 'Done. Files:' $(find /output/ -type f | wc -l)

# 錯誤：不加 -q，每個檔案都印
unzip -n file.zip -d /output/  # 122,200 行輸出全進 context
```

### 規則 6：不重複讀同一個檔案

讀過一次就記住。不要每次操作前都重新 get_page_text 確認。
特別是 project_state.md、AGENT_RULES.md 這類大文件 — 一個 session 讀一次就夠了。

---

## 第二層防線 — 監測

### 估算目前用量

Agent 自我檢查清單：
- 這個 session 讀了幾個文件？（每個 ~5,000 tokens）
- 執行了幾次 read_page / get_page_text？
- GitHub API 來回了幾次？
- 對話已經幾輪了？

### 警戒水位

| 水位 | 預估用量 | 動作 |
|------|---------|------|
| 安全 | <100k tokens | 正常工作 |
| 注意 | 100-140k | 開始節約，合併操作 |
| 警告 | 140-170k | 停止讀新文件，只做必要操作 |
| 危險 | 170k+ | 立即存檔 + 交接下個 session |

### 直覺判斷法

如果你覺得「這個 session 做了很多事」，大概已經到注意水位了。
具體指標：
- 對話超過 20 輪 → 注意
- 讀了 5+ 個文件 → 注意
- GitHub API 來回 10+ 次 → 警告
- read_page (all) 用了 3+ 次 → 警告

---

## 第三層防線 — 應急 SOP（已經爆了）

### 遇到 'prompt is too long' 時：

1. **停止** — 不要再呼叫任何工具
2. **生成階段存檔摘要** — 格式如下：

```
## 階段存檔 — [日期時間]

### 已完成
- [任務1]：[狀態]
- [任務2]：[狀態]

### 中斷點
- 當前任務：[卡在哪一步]
- 下一步：[接下來要做什麼]

### 關鍵狀態
- 重要 URL / folder ID / SHA
- 尚未 commit 的變更

### 下個 session 開場語（給使用者複製）
接續上次任務。上次進行到 [X]，下一步 [Y]。
請先讀：[project_state.md URL]
```

3. **優先 commit** — 如果有未 commit 的程式碼，先 commit 再結束
4. **更新 project_state.md** — 記錄中斷點，讓下一棒知道

---

## 程式開發專用策略

### 寫 .py 檔到 GitHub：一次 commit 一個檔案

不要在一個 session 裡連續寫 5 個 .py。每個檔案的 content 做 base64 encode 就很大。
一個 session 寫 1-2 個 .py + 更新 1 個 .md = 合理上限。

### 不要用 read_page 讀 GitHub 檔案內容

GitHub 的 code view 頁面 DOM 結構極深。
讀檔案永遠用 raw.githubusercontent.com + get_page_text。

### Debug 時只讀 error message，不讀整個 page

```
# 正確：find error message
find('error message')  # 只取錯誤訊息

# 錯誤：read_page 整個 Colab 頁面
read_page(tabId)  # Colab DOM 極大，一次吃 30k+ tokens
```

### 長 Python 檔案：先寫完再一次 commit

不要寫一半 → 確認 → 再寫一半 → 確認。每次確認都消耗 context。
先在腦中（或 window 變數中）組裝完整內容，一次 PUT 到 GitHub。

---

## 實戰踩坑紀錄

| Session | 踩坑 | 原因 | 教訓 |
|---------|------|------|------|
| A4 Session 2 | 多次 read_page Colab + Drive DOM | DOM 結構極大 | 改用 find + screenshot |
| A4 Session 3 | 反覆讀 GitHub API JSON | base64 content 太大 | 改用 raw URL + get_page_text |
| 通用 | session 超過 30 輪還在操作 | 沒有分段意識 | 加入水位自我檢查 |

---

## 版本記錄

| 版本 | 日期 | 變更摘要 | 更新者 |
|------|------|---------|--------|
| v1.0 | 2026-03-15 | 初始建立：應急 SOP + 預防策略 + 精簡讀取技巧 | A1 Handbook Agent |
| v2.0 | 2026-03-17 | 大幅擴充：三層防線架構 + 程式開發專用策略 + GitHub API 節約 + Colab 輸出控制 + 實戰踩坑紀錄 | A4 Pipeline Agent |