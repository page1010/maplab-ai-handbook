# GAS 專案架構問題記錄
date: 2026-04-04

## 問題描述

目前所有 `.gs` 檔混在同一個 Bound Script（「傳line對話到外燴系統sheet」），這是錯誤的架構。

## 正確架構

| 專案 | 應包含的檔案 |
|------|------------|
| 報價系統 GAS 專案 | `Code.gs`、`createSlides.gs`、`QuoteForm.html`、`setup-template.gs` |
| LINE 對話專案 | `LineWebhook.gs` |

## 本次修正

**Bug**：`createSlides.gs:109` — `presentation.moveSlide(slide, index)` 不是 Slides API 的方法。

**修正**：改為 `slide.move(index)`（Slide 物件的實例方法）。

## 待辦（下次 session）

- [ ] 將 `createSlides.gs`、`QuoteForm.html`、`setup-template.gs` 從 LINE 對話專案移出
- [ ] 建立獨立的報價系統 GAS 專案，並重新 clasp 綁定
- [ ] `LineWebhook.gs` 留在原 LINE 對話專案
- [ ] 更新 `clasp.json` / `.clasp.json` 分別對應兩個專案的 scriptId

## 踩坑：clasp 指向錯的 GAS 專案

### 事實
- 報價系統 GAS 專案（正確）：MAPLAB_外燴系統_v0.1，Script ID = 1JIiPW_OUwNzB4VHS4k0KHi7LYDdPlFgHWejotsY4KE3KdLTc3EB-0vpc
- LINE 對話 GAS 專案（錯誤）：傳line對話到外燴系統sheet，Script ID = 1Fkl34P7p395k0YzwY8hyhz7DAAsgA3CBgyumx9ImSOFoXu771lFABSi7
- .clasp.json 一直指向 LINE 專案 → 所有 clasp push 都推到錯的地方
- 報價系統專案裡的程式碼從頭到尾沒被 A0 動過

### 報價系統專案裡已有的檔案（Owner 或之前 agent 建的）
beautifyV2.gs, createSlides.gs, fixTemp.gs, generateProposal.gs, import2025.gs, populateTerms.gs, quoteDraft_v03.gs, QuoteForm.html, quoteSystemV2.gs, reorganizeItems.gs, slidesV2.gs, 未命名.gs

### 教訓
- 開始工作前必須確認 .clasp.json 指向正確的 GAS 專案
- 透過 Sheet 的「擴充功能 > Apps Script」確認 Bound Script 的 Script ID
- 不要假設 repo 裡的 .clasp.json 是對的
