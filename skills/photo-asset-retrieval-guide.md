# skills/photo-asset-retrieval-guide.md — 素材撈取與 TA 歸位指南

> **狀態：正式（Owner 核准 2026-07-24；本機 main commit）。**
> 建立日 2026-07-24。來源 review bundle：`handoff/review-bundles/2026-07-24-素材資產發現/`。
> 相關：`skills/a4-fact-first-asset-matching.md`、`skills/maplab-photo-sourcing.md`、
> `skills/agent-output-convention.md`、`docs/seo-keyword-map.md`、`docs/real-cases-to-seo-matrix.md`。

## 這個 skill 現在能做什麼（能力摘要）

1. **依 A4 路徑子類別 + seo-keyword-map 撈素材**：從 `photo_alt_index.csv` 的
   `年份/catering/{wedding,corporate,birthday,dessert,other}` 桶直接撈某類素材，
   對到 `seo-keyword-map` 的 pillar/關鍵字；三個 TA 用「關鍵字→TA」對應表當**視圖**產出。
2. **補 drive_url 讓清單可用**：用 seo 檔名 join 實體 Drive 夾的 file_id →
   `https://drive.google.com/file/d/{id}/view`，把 A4 清單變成可點開清單。
3. **日期↔場次交叉（備援）**：婚禮/場次日期優先取 **mina 訂單 Sheet 標題**，
   次用 TimeTree（客戶/場地名）、`real-cases-to-seo-matrix.md`；
   ⚠️ A4 無拍攝日期，純 date-join 走不通，日期僅當備援線索。
4. **影像辨識輔助驗證**：素材落地本機後 `sips` 轉檔 + montage 拼圖逐批目視，
   確認事件脈絡；**以事件/資料夾脈絡為主、單張影像為輔**（甜點桌跨 TA 撞臉，單圖不可靠）。
5. **大量 Drive 檔落地策略**：優先「設離線 / 整碟鏡像後 `cp`」，次選 subagent 批次；
   **絕不在主 context 用 API 逐檔 base64 下載**（會爆 context）。
6. **一份素材跨對象/跨頻道復用**：schema 帶 audience（多值）＋ channel（WP/IG/YT/Pinterest），
   做一次分類、所有部門受惠。

## 輸入 / 輸出契約

- **輸入**：TA 或關鍵字（對 seo-keyword-map）；可選日期/場次線索。
- **輸出**：`MAPLAB_WORKSPACE/index/` 下的可用清單 CSV（檔名/A4描述/子類別/drive_url/TA視圖/confidence），
  必要時實體檔複製到 `/Volumes/MacExternal/MAPLAB_素材_依TA_.../TAx_.../`（複製不刪原檔）。

## 標準流程

1. 讀 `photo_alt_index.csv` → 依路徑子類別/關鍵字/ALT 篩候選。
2. join 實體夾 file_id 補 drive_url（注意 400 分頁上限、seo/原始檔名混用）。
3.（可選）交叉訂單 Sheet/TimeTree 日期補場次脈絡。
4. 落地本機（cp 或離線同步）→ sips+montage 逐批影像驗證。
5. 確認的入 TA 夾、疑似誤標另列清單給 Owner；清單存 `MAPLAB_WORKSPACE/index/`。

## 已知陷阱（見 system-map 增補 §5）

ASSET_LOG category 欄會壓平婚禮/HR（用路徑桶）；實體檔未同步本機；API 下載 base64 爆 context；
Drive 桌面版只能整碟鏡像；檔名 seo/原始混用降 join 命中；A4 無拍攝日期。

## 守則

唯讀撈取 + 少量落地驗證；不刪 Drive 原檔；不動 MacExternal 既有成果；清單先給 Owner 過目再入正式 TA 夾。
