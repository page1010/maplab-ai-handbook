# pitfalls.md

> Cold-start required. 每次修到重複錯誤，要把「觸發條件 / 根因 / 解法 / 預防」寫回這裡。

## 2026-05-11 — A4 asset root ID drifted across docs and scripts

- 觸發條件：Owner 要求「讓事實說話」，重新核對 A4 相片與素材存放位置。
- 根因：active docs/scripts 同時殘留三種 `MAPLAB_ASSETS` ID：舊 ID `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe`、一個 `O/0` 打錯的 ID、以及現行 ID；dashboard 和部分 credentials doc 仍指向舊 ID。
- 解法：用 Google Drive API 讀取 folder metadata；確認 `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy` 是目前 `MAPLAB_ASSETS`，且舊 ID API 回 404。active docs/scripts 統一更新到現行 ID，archive/review output 保留歷史原貌。
- 預防：任何資源位置更新前，先用 Drive/Sheets API 查 `id/name/parent/trashed`；不能只相信 repo 記錄或 dashboard HTML。

## 2026-05-11 — Do not move an active user working directory

- 觸發條件：Owner 發現 `/Users/pagemacmini/Downloads/maplab-ai-handbook-main` 工作目錄缺失。
- 根因：A1 將非 git 下載副本移到「沒用的資料夾」做隔離；雖然不是刪除，但該路徑正是目前 session 的 `cwd`，等同破壞工作環境。
- 解法：立即把資料夾原路徑恢復；治理報告改為「標記為非 canonical，不物理搬移」。
- 預防：清理/隔離任何使用者可見資料夾前，先確認是否為 active `cwd`、桌面入口、同步資料夾或近期工作區；移動前需 Owner 明確批准。

## 2026-05-11 — A2/A3 workbench built in non-git download copy

- 觸發條件：Owner 發現上方快速瀏覽連結壞掉，並懷疑 repo 紀錄寫壞。
- 根因：A2/A3 工作台文件與產生器被做在 `/Users/pagemacmini/Downloads/maplab-ai-handbook-main`，該資料夾不是 git repo；正式真相源 `/Users/pagemacmini/maplab-ai-handbook` 沒有收進同一批檔案。
- 解法：以 `/Users/pagemacmini/maplab-ai-handbook` 為唯一正式 repo，將 A2/A3 docs、產生器、技能書與 scenario config 收回正式 repo。
- 預防：任何可交接文件、產生器、技能書都必須先確認 `git status` 可追蹤；下載副本只能當暫存來源，不得作為正式工作目錄。

## 2026-05-11 — Generated HTML links pointed at stale command names

- 觸發條件：`handoff.html` / `handoff-board.html` 有 13 個 broken links。
- 根因：產生器改成建立 `run_wp_*` / `schedule_wp_*`，但 HTML 仍輸出舊的 `run_wordpress_*` / `schedule_wordpress_*`；快捷入口也錯指到 `wordpress 素材庫/*.command`。
- 解法：handoff board 產生器改用 `MAPLAB_A2A3_Workbench/*.command`，WordPress 任務按鈕改為 `run_wp_*` / `schedule_wp_*`，並在產生器結尾加入 link check。
- 預防：每次生成 HTML 後必跑 link checker；壞連結不得交給 Owner 當「可點擊面板」。

## 2026-05-11 — Public drafts mixed internal QA fields

- 觸發條件：WordPress preview / draft 中出現價格區間、內部日期與本機 Drive 線索。
- 根因：內部 QA、source bridge、公開草稿共用同一批欄位，沒有把「給人核對」和「可發布」分層。
- 解法：公開 `draft.md` / `copy.md` / WordPress preview 不得含價格、內部日期或 `file://`；日期、報價單推斷與本機素材路徑只放 `brief.md` / `source_bridge.md` / internal QA board。
- 預防：產生器結尾必跑 public output safety check，攔截價格、本機路徑與內部日期標籤。

## 2026-05-11 — Unreviewed generated photos must not become publish assets

- 觸發條件：Owner 判定今天生產的圖片不可用，要求不要保留。
- 根因：素材選圖與裁切未達可發布標準，且 preview / work package 把未審核圖片包裝成可交辦素材。
- 解法：刪除桌面 A2/A3 工作台中的圖片衍生物，保留文字、manifest、prompt 與治理紀錄；下一輪必須先完成圖片來源 QA，再重建圖包。
- 預防：未通過 Owner/visual QA 的圖片只能留在 internal review，不得放進 public draft 或 OpenClaw work package。

## 2026-05-11 — Repo records confused with live WordPress facts

- 觸發條件：Owner 指出「用接口進去看事實與現況，不是看人家寫給你的紀錄」。
- 根因：A2/A3 workbench 修復時先整理 repo 記錄與 local artifacts，沒有先用 WordPress / Rank Math 接口核對 live site。
- 解法：新增 live fact check：WP public REST 顯示 6 pages / 57 posts；planned workbench slugs 在 pages/posts 都是 0 match 且前台 404；Rank Math PRO 前台活著，但 analytics/score endpoints 未登入回 401。
- 預防：任何 WordPress / SEO / Rank Math 任務必須先查 live接口，再讀 repo 紀錄；repo 紀錄只減少斷點，不能作為現況證據。

## 2026-05-11 — Elementor page body ignored WP REST post_content edits

- 觸發條件：`/gender-reveal-party-tips/` 的 Rank Math title / description 已更新，但用 WP REST 追加的正文內連區塊只存在 raw `post_content`，前台沒有渲染。
- 根因：該頁前台由 Elementor data render，普通 `post_content` 不是實際畫面來源；同時原 Elementor HTML 區塊曾有 `</section` 斷尾，造成 raw content 與 rendered HTML 進一步不一致。
- 解法：Rank Math meta 可用 Rank Math REST 更新；但 Elementor-rendered 頁的正文、內連與 FAQ 必須走 Elementor data / wp-admin UI / Elementor 正式 API 驗證，不可只看 WP REST raw content。
- 預防：A2 修頁時同時檢查 `content.raw`、`content.rendered`、前台 HTML 三層；三者不一致時，以前台 HTML 為準。

## 2026-05-11 — Google recrawl submission cannot be inferred from old repo notes

- 觸發條件：Owner 問「所以是要去送資料給google確認對吧」，需要把 Rank Math 修復後的 URL 送進 Google 可發現/可重爬流程。
- 根因：repo 舊文件寫 GSC 已接通，但本機實際 `google-token.json` 只有 Drive/Sheets scope；`mcp-server-gsc` 可列出 `submit_sitemap` / `index_inspect` 工具，但目前憑證是 OAuth client，server 實際要求 service account 的 `private_key` + `client_email`。此外，Google sitemap ping 已 deprecated，Indexing API 也不是一般 WordPress 頁可用的萬用提交。
- 解法：先用 live HTTP 驗證 sitemap / robots / page indexability，再用 Rank Math Instant Indexing `/wp-json/rankmath/v1/in/submitUrls` 送出 8 個 URL，並把 GSC API 權限不足記錄在 review bundle。
- 預防：任何「提交 Google / GSC」任務必須分清楚四件事：sitemap 可發現、Rank Math indexing endpoint 是否 accepted、GSC URL Inspection 是否有 scope、Search Console UI Request Indexing 是否已人工點擊；不可把其中一項成功說成全部完成。
