# 2026-04-18 — AI Agent 亂串 API 導致 GCP 帳單 $3,000+/月

> 記錄者：A0 Dispatch
> 背景：Owner 收到 Google Cloud 月結單 $1,509 TWD（3月）+ $1,572 TWD（4月進行中），不是 Google Ads

## 發生了什麼

A4 照片分類 pipeline（Colab + Gemini Flash）在 3-4 月累計產生約 $3,000 TWD 的 GCP 帳單。

## 根因

1. A4 的 Colab 腳本（vision.py / S6-RESUME cell）用 Gemini 2.5 Flash API 做照片分類
2. API key 是從 Google AI Studio 建立的（aistudio.google.com），本來應該有免費額度
3. 但這個 API key 綁定在 GCP project「maplab-pipeline」上，而這個 project 有綁定 billing 帳戶（017929-BB3242-F57397）
4. 當免費額度用完後，Google 直接從 billing 帳戶收費，沒有任何警告
5. 3 月跑了 ~37,000 張照片分類（S5-S12），每張一次 Gemini API call，遠超免費額度

## 帳單明細

| 月份 | 金額 (TWD) | 主要服務 | 主要專案 |
|------|-----------|--------|--------|
| 2026/3 | $1,509 | Gemini API (100%) | maplab-pipeline |
| 2026/4 (截至 4/19) | $1,572 | Gemini API (100%) | maplab-pipeline |

## 為什麼沒被發現

1. AI agent（A4/A1）建立 pipeline 時只確認了 API 能用，沒有確認 billing 影響
2. 沒有設定預算警報（GCP 預設不設上限）
3. 免費額度用完後 GCP 靜默升級到付費，沒有明顯通知
4. Owner 不熟悉 GCP billing console，直到收到月結單才發現

## 系統教訓

**AI agent 自動串接 API 時必須確認的三件事：**
1. 這個 API 是免費還是付費？免費額度是多少？
2. API key 綁定的 GCP project 有沒有 billing？有的話超過免費額度會自動收費
3. 有沒有設預算警報？

**應該在 Agent 行為框架裡加入：**
- 建立任何 API 連接前，確認 billing 影響
- 所有 GCP project 必須設定預算警報（$0 或接近免費額度的上限）
- 定期（patrol.sh）檢查 GCP billing 有沒有異常費用

## 解決方案

1. 在 AI Studio 建一個不綁 billing 的 API key
2. 或在 GCP Console 設定每月預算上限
3. 在 patrol.sh 加入 GCP billing 檢查
4. 在 agent-behavior-framework 加入 API billing 確認規則
