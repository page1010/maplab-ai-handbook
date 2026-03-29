# Gemini API 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

存放在 **Notion API Keys 保管室**：
- Notion 頁面 ID：`320ab0806d5c80e0be95f298399d2c44`
- 欄位：GEMINI_API_KEY

> ⚠️ Agent 不直接開 Notion。請 Owner 提供，或讓 A0 透過 Notion MCP 取出。

---

## 取用方法

### Colab（A4 Pipeline 主要使用環境）

```python
import os

# 在 Colab Secret 設定或直接設環境變數
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 使用 REST API（推薦，比 SDK 更穩定）
import requests

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
response = requests.post(url, json={
    "contents": [{"parts": [{"text": "prompt here"}]}]
})
```

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| ✅ A4 Colab 照片分類 | Gemini Vision API，批次處理相簿素材 |
| ✅ A2/A3 數據分析 | Google 生態系整合，GSC/Ads 數據解析 |
| ✅ A2 關鍵字研究 | Google 生態系原生整合 |

---

## 禁止操作

- ❌ 用在非 pipeline 的其他用途（如純文字生成，請改用 Claude）
- ❌ 把 API Key 明文寫進 GitHub

---

## 模型選擇（重要）

根據 `skills/photo-pipeline-toolkit-guide.md` 踩坑記錄：
- ✅ 使用：`gemini-2.5-flash`
- ❌ 已下架：`gemini-2.0-flash`
- ❌ 避免：`google.generativeai` Python library（proxy 斷線問題）
- ✅ 推薦：REST API `requests.post`（更快、更穩）

詳見 `skills/ai-model-guide.md`。
