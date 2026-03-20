# Verification Checklist Guide — 完成驗證技能包
版本：v1.0 | 2026-03-17 | A4 Pipeline Agent

改編自 superpowers verification-before-completion。

---

## 鐵律

沒有跑驗證就不能說完成。
「應該」「大概」「我有信心」= 停下來先跑驗證。

---

## 驗證關卡（5 步）

1. 辨識：什麼動作能證明？
2. 執行：跑那個動作
3. 讀取：看完整輸出
4. 確認：輸出支持宣稱？
5. 報告：帶證據說結果

---

## MAPLAB 驗證場景

| 宣稱 | 怎麼驗 | 不夠的驗證 |
|------|--------|-----------|
| commit 成功 | response.content.name 有值 | 「PUT 了應該成功」 |
| PR merge | merged === true | 「按了 merge」 |
| Colab cell 完成 | 底部有 === DONE === | 「Cell 停了」 |
| 解壓完成 | 最後行有 total files 數字 | 「跑很久應該好了」 |
| 檔案刪除 | 「已將 N 項移至垃圾桶」 | 「按了刪除」 |
| Drive 資料夾建好 | navigate 到 URL 看到內容 | 「點了新增」 |
| .py 語法正確 | Colab import 無錯 | 「看起來對」 |

---

## 禁用語（出現 = 停下來驗證）

- 「應該可以了」
- 「大概沒問題」
- 「看起來對了」
- 「我有信心」
- 「似乎成功」
- 「Done!」「Perfect!」（無證據）

---

## 多步驟驗證

5 步任務 → 每步各自驗證，不能只驗最後一步。

---

## 失敗處理

1. 如實報告（不掩蓋）
2. 記錄到 project_state.md Errors Log
3. 連續 3 次失敗 → 質疑方法本身

---

## 踩坑紀錄

| 宣稱 | 實際 | 教訓 |
|------|------|------|
| Cell 跑完了 | Colab 已斷線 | 滾到底部確認最新輸出 |
| Mount 成功 | ValueError: mount failed | 讀完整 error（這個是正常的）|
| 8 ZIP 都刪了 | 只刪了選中的 | 確認 N = 預期數 |

| v1.0 | 2026-03-17 | 初始版本 | A4 |