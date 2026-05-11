# 2026-03-23 — Gemini API 選擇：REST 直打 vs Python Library

> 記錄者：A1 系統總管（從 experience-log EXP-S001/S004/F002/F005 整理）
> 日期：2026-03-18 ~ 2026-03-23
> 背景：A4 需要用 Gemini Vision AI 分類 122,200 張照片，選錯 API 浪費了多個版本

---

## 問題

122,200 張照片需要 AI 分類（品項識別、場景判斷）。需要穩定、快速、能在 Colab 跑的方案。

## 試過的錯誤方向

1. **Vertex AI SDK** → 404（模型名稱格式與 Generative AI API 不同）
2. **google.generativeai library** → 400 Bad Request + PIL Image 問題 + Colab proxy 斷線後無法恢復
3. **AI Vision 判斷照片地點** → 完全不行（除非有店招），改用 GPS 座標秒殺

## 正確方向

**Gemini REST API**（requests.post 直接呼叫）：
- 310 張/小時 vs 160 張/小時
- 不依賴 proxy
- Colab 斷線重連後直接繼續

**GPS 座標判斷地點**：
- 從 Takeout JSON metadata 提取 GPS
- 零 API 成本、~5000 張/分鐘
- 準確度遠高於視覺判斷

## 學到的事

1. **REST API 永遠是最穩的選擇** — Python library 可能有版本問題、proxy 問題、encoding 問題
2. **不要用 AI 做 metadata 能解決的事** — GPS 比 Vision AI 快 1000 倍且免費
3. **看到 FutureWarning 就換方案** — 不要等到 400 Error 才換

## 相關文件
- experience-log: EXP-S001, EXP-S004, EXP-F002, EXP-F005
