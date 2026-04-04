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
