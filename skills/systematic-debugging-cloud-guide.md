# Systematic Debugging Cloud Guide — 雲端除錯技能包
版本：v1.0 | 2026-03-17 | A4 Pipeline Agent

改編自 superpowers systematic-debugging + defense-in-depth + condition-based-waiting。

---

## 鐵律

沒找到根因不准提修法。修 3 次沒好 = 質疑架構。

---

## 四階段

### Phase 1：根因調查
1. 完整讀 error（通常直接寫了答案）
2. 重現（Colab 跑一次能觸發？）
3. 查最近改動（GitHub API 看 diff）
4. 收集證據（加 print 看實際資料流）

### Phase 2：模式分析
1. 找能動的範例
2. 比較差異
3. 列出每個差異

### Phase 3：假說驗證
1. 形成假說（根因是 X，因為 Y）
2. 最小變更測試（一次一個變數）
3. 成功 → Phase 4；失敗 → 新假說

### Phase 4：修復
1. 只修根因
2. 驗證修復
3. 修 3 次沒好 → 停，質疑方法

---

## Colab 常見 Debug

| 症狀 | 根因 | 解法 |
|------|------|------|
| IndentationError | type tool 不保持縮排 | 改用 %%bash |
| ValueError: mount failed | Drive 已掛載 | ls 確認，繼續跑 |
| Cell 卡住 | idle timeout | screenshot 看是否斷線 |
| ImportError | 缺套件 | !pip install |
| 輸出截斷 | stdout 上限 | 寫到檔案 |

## GitHub API 常見 Debug

| 症狀 | 根因 | 解法 |
|------|------|------|
| 409 Conflict | SHA 過期 | 重新 GET sha |
| 404 Not Found | 路徑或 branch 錯 | 確認 URL |
| 422 Unprocessable | 重複 branch / 格式錯 | 讀 message |
| fetch undefined | 非同步沒回來 | wait(2) 再讀 |
| window 變數消失 | navigate 換頁 | 同頁做完 |

## Drive 常見 Debug

| 症狀 | 根因 | 解法 |
|------|------|------|
| 看不到檔案 | 不同帳號 authuser | /u/0/ vs /u/1/ |
| 容量不夠 | 家庭群組共用 | 清垃圾桶 |
| 分享佔空間 | 計入分享者配額 | 不分享，用 Colab |

---

## 防禦性驗證（4 層）

| 層 | 目的 | 例 |
|-----|------|-----|
| 入口 | 拒絕明顯錯誤 | folder_id 空 → raise |
| 業務 | 資料合理性 | count=0 → 警告 |
| 環境 | 防錯誤環境 | 非 Colab → 跳過 mount |
| 日誌 | 追查資訊 | 每 call 印 id + count |

---

## Condition-Based Waiting

等條件，不等時間。

```python
# 正確
while not done():
    if elapsed > 60: raise TimeoutError
    time.sleep(2)

# 錯誤
time.sleep(30)  # 猜的
```

---

## 紅旗（= 回到 Phase 1）

- 「試試改 X」（沒根因就猜修）
- 「一起改多個跑測試」
- 「不太懂但先試」
- 「再試一次」（第 3 次了）
- 「快點修好就行」（急 = 更該走流程）

| v1.0 | 2026-03-17 | 初始版本 | A4 |