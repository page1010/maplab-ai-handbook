# A2/A3 Workbench Integrity Report — 2026-05-11

## Summary

這次修復確認：A2/A3 工作台不是單一連結錯誤，而是「正式 git repo / 下載副本 / 桌面素材庫」三者分裂。

正式真相源固定為：

- `/Users/pagemacmini/maplab-ai-handbook`

臨時來源與桌面工作區：

- `/Users/pagemacmini/Downloads/maplab-ai-handbook-main`：非 git 下載副本，只能作為遷移來源。
- `/Users/pagemacmini/Desktop/wordpress 素材庫`：桌面素材與草稿工作區。
- `/Users/pagemacmini/Desktop/MAPLAB_A2A3_Workbench`：桌面 command 捷徑與 OpenClaw jobs。

## Findings

### 1. Truth source split

- 正式 repo 是 git repo，但缺少 A2/A3 workbench docs、handoff board、產生器與技能書。
- 下載副本不是 git repo，卻保存了最新 A2/A3 workbench 文件與產生器。
- `CURRENT_STATUS.md` 在兩邊版本不同：正式 repo 為 v6.0，下載副本為 v4.0。

### 2. Broken quick links

修復前，以下檔案各有 13 個 broken links：

- `/Users/pagemacmini/Downloads/maplab-ai-handbook-main/docs/a2a3/handoff-board.html`
- `/Users/pagemacmini/Desktop/wordpress 素材庫/handoff.html`

原因：

- 快捷入口錯指到 `wordpress 素材庫/*.command`。
- HTML 使用不存在的 `run_wordpress_*` / `schedule_wordpress_*`。
- 實際存在的是 `MAPLAB_A2A3_Workbench/*.command` 與 `run_wp_*` / `schedule_wp_*`。

### 3. Work package mismatch

- 最新 manifest 只承認 5 個 B2B 工作包：
  - `opening-event-catering-tainan`
  - `meeting-refreshment-catering-tainan`
  - `brand-event-catering`
  - `catering-corporate-tainan`
  - `school-event-catering-tainan`
- 桌面資料夾仍殘留先前 8 類工作包。
- 後續以 manifest 的 5 個 B2B 包為準；週歲、婚禮、宗教須重新評估後再重建。

### 4. Public/private content boundary

公開稿不應包含：

- 價格區間
- 內部核對日期
- `file://` 本機 Google Drive 路徑

這些只能存在於：

- `brief.md`
- `source_bridge.md`
- internal QA board
- tracking / source matrix

### 5. Generated images removed

Owner 判定今天生成的圖片不可用後，已清除桌面 A2/A3 工作台的圖片衍生物。

清理範圍：

- `ads/*/assets`
- `ads/*/preview-assets`
- `wordpress/*/assets`
- `wordpress/*/preview-assets`
- `contact-sheets`
- `ig-assets`
- `source_2025_curated`

清理結果：

- Removed generated image derivatives: 228
- Remaining generated images in scoped folders: 0
- Google Drive 原圖未刪除。
- repo 文字、manifest、HTML、prompt、SEO payload 未刪除。

## Changes Made

- `docs/a2a3/*` 從下載副本收回正式 repo。
- `automation/seo_factory/build_a2a3_workbench.py` 收回正式 repo。
- `automation/seo_factory/config/scenario_pages.json` 收回正式 repo。
- `skills/a2a3-workbench-material-library-guide.md` 收回正式 repo。
- `build_a2a3_workbench.py` 新增：
  - command link 修正
  - `run_wp_*` / `schedule_wp_*` 命名
  - HTML link checker
  - public output safety checker
  - gallery asset existence checker
- `pitfalls.md` 建立，記錄這次真相源分裂、壞連結、公開/內部分層、圖片 QA 失敗。

## Verification

產生器在圖片清除前完成一次驗證：

- Pages: 5
- Gallery assets verified: 25
- Food assets used: 5
- Verified HTML links: 16 files
- Verified public outputs: 15 files

圖片清除後，HTML 中的圖片預覽不可視為可發布畫面；下一輪必須先重新選圖，再重建 preview。

## Next Rules

1. 不在非 git 下載副本做正式工作。
2. 不把未審核圖片放進 public draft。
3. 不在 public draft 寫價格、內部日期或本機 Drive 路徑。
4. 每次生成 handoff / preview 後必跑 link checker。
5. A2/A3 工作包數量必須與 `source_manifest.json` / `handoff_manifest.json` 一致。

## Resume Prompt

```
角色：A1 / A2 governance
任務：接續 A2/A3 workbench integrity repair
狀態：
- 正式 repo: /Users/pagemacmini/maplab-ai-handbook
- 下載副本只作遷移來源，不再當工作目錄
- A2/A3 docs、產生器、scenario config、技能書已收回正式 repo
- handoff links 與 command 命名已修正
- 產生器已加入 link checker + public output safety checker
- Owner 判定今日生成圖片不可用；桌面素材庫的圖片衍生物已清除 228 個
下一步：
1. 不要重跑產生器生圖，除非先完成新圖片 QA。
2. 先重新建立素材選圖標準與來源清單。
3. 再重建 5 個 B2B work package preview。
4. 最後才進 WordPress / Rank Math 草稿。
```
