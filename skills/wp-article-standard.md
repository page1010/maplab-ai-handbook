# WordPress 文章標準 + 安全編輯 SOP（A2 / Codex 共用）

版本：v1.0 | 建立：2026-06-15 | 維護：A2
> 目的：讓 A2、Codex、OpenClaw 任何 agent 改 maplabkitchen.com 文章時，格式 / 語氣 / SEO / 圖片 / 暗號完全一致，並用同一套可驗證、可回復的安全流程。搭配讀：`skills/brand-voice-guide.md`、`skills/maplab-visual-spec.md`、`skills/gdrive-to-wordpress-upload-guide.md`、`pitfalls.md`。

---

## 0. 🍁 真文章暗號（強制）

- **Owner 親寫 / 人工確認過的文章**，`post_content` 開頭埋：`<!-- 🍁 MAPLAB-AUTHENTIC v1 -->`
- 這是 HTML 註解：**讀者看不到、原始碼可 grep**。用來區隔「人工真文章」與「agent 批量產出」。
- 規則：**agent 不可自行給文章蓋 🍁**。只有 Owner 確認「這篇是我的 / 已人工審過」才標。
- 偵測：`grep -l 'MAPLAB-AUTHENTIC'`。批量產出的文章一律無此標。

## 1. 統一文章結構（由上而下）

1. `<!-- 🍁 MAPLAB-AUTHENTIC v1 -->`（若為真文章）
2. H1 = WP 標題（地區＋場景＋外燴，例：台南品牌活動外燴｜…）
3. 開頭引言（1–2 段，說場景不硬賣）
4. **快速索引**（TOC）：`<h2 id="quick-index">快速索引</h2>` + 錨點清單，連到各 H2/H3 的 `id`
5. 主體：案例 / 教學 / FAQ（每個主段落 H3 都要有 `anchor`/`id`）
6. CTA（聯絡我們 / LINE 詢問）
7. 內部連結區（hub→spoke，延伸閱讀）

> **TOC 標籤統一用「快速索引」**（Owner 2026-06-15 指定）。舊批量文章用「📋 本文目錄」，掃站時逐步遷移成「快速索引」。

## 1.5 SEO 草稿交稿必填欄位（2026-07-03 缺陷棘輪新增）

> **生成階段就要填完，不能省。** 欄位空白 = 草稿不合格，不得進 `docs/seo-publish-checklist.md` 閘門。

| 欄位 | 要求 | 說明 |
|---|---|---|
| **核准版字數** | 整數（含空格前後正文總字元數） | `seo_publish_gate.py` A-1 用來計算 ratio |
| **核准版前 500 字 SHA256（前 16 碼）** | 16 位 hex 字串 | 生成者在交稿 front-matter 填入，閘門比對 |
| **已解析內鏈表** | `slug → live URL / 待確認 / 404禁連` 逐行列出 | 所有 `INTERNAL_LINK_RECHECK_REQUIRED` 在交稿時就要解析狀態，不允許以「生成後再查」為由留白 |
| **精選圖 WP media ID** | 整數，或明確填 `待補（Owner 指定後補）` | 發布時 `featured_media ≠ 0` 是 C-1 的閘門條件；若此時無法提供，Owner 必須明確知道 |
| **真實 LINE URL** | 完整 href（非 `/【待填】`） | CTA `href` 必須在草稿交稿時填入；不知道就問 Owner，不能留佔位 |

**實作方式（選擇一種）：**
- 在草稿 `.md` 檔頭加 YAML front-matter：
  ```yaml
  ---
  approved_char_count: 3220
  approved_fp_500: "a1b2c3d4e5f60001"
  internal_links:
    corporate-catering-tainan: "https://www.maplabkitchen.com/corporate-catering-tainan/"
    tainan-corporate-catering-cost: "待確認（REST 尚未驗證）"
    line-official: "https://lin.ee/xxxxx"
  featured_media_id: 924
  ---
  ```
- 或在交稿 message 開頭用標準化表格列出，方便獨立閘門跑者核對。

---

## 2. 品牌語氣（硬規則，違反即不合格）

- 禁說服式對比句型：**「不是…而是…」「不僅…更…」「不需要…而是…」「雖然不…但…」**（`brand-voice-guide.md` 第4點）。正向描述空間、節奏、感受。
- 禁誇張促銷語。
- **嚴禁把內部指令印進文案**：例如「可補在…情境」「適合作為…案例」「這類照片可作…輔助」。直接寫給終端客戶看的最終文案。
- 偵測 AI 腔：`grep -E '不是.{0,12}而是|不僅.{0,12}更|不需要.{0,12}而是|雖然不.{0,8}但'`

## 3. 圖片規範

- 全部 `webp`；命名 `maplab-{場景}-{描述}.webp`；alt = `台南{場景}外燴—{食物特寫/現場紀錄}`。
- **沒有照片的文章至少補 1 張**（featured + 內文）。
- **不可用別人的照片**：只能用 Owner 實拍池（見 §6）。發現非自有食物照立即換掉。
- 找圖先用事實鏈，不要只看畫面（`pitfalls.md` 2026-05-12）：
  `python3 tools/ai_workbook/cli.py asset-case-match --year 2025 --limit 120`
- 公開內容**不得含**價格、內部日期、`file://`、本機路徑（`pitfalls.md` 2026-05-11）。

## 4. 「agent 批量廢文 / 崩壞尾巴」辨識與清除

**真正的崩壞訊號（要清）：**
- `段落 N：…` 這種編輯用標籤殘留在 H3
- 紅字 `[圖片未能載入: xxx.webp]` 之類佔位文字
- 同一段 H3/圖/段落**重複 2 次以上**
- 未解析的 raw `<svg viewBox …>` 佔位

**不是廢文（別誤刪）：**
- `歷年案例精選` H2 本身是**合法區塊**，只要它底下是真案例（有真實活動名＋真圖）就保留。
- 只有當它底下塞的是 `段落 N` / 重複佔位時才是廢文。

## 4.5 Elementor vs 經典 Gutenberg（編輯前**必查**，否則白做）

本站是**混合**的：經典 Gutenberg 文章可用 WP REST 改 `post_content`；**Elementor 文章的 post_content 改了不會渲染**（前台從 `_elementor_data` 渲染，`pitfalls.md` 2026-05-11）。編輯前先分類：

```bash
curl -s -K "$CFG" ".../wp/v2/posts/{id}?context=edit&_fields=id,meta" \
 | python3 -c "import sys,json;print(json.load(sys.stdin)['meta'].get('_elementor_edit_mode','classic'))"
# 回 'builder' = Elementor（REST 改不動，走 Elementor UI / Owner Chrome）
# 否則 = 經典（REST 可改）
```

**2026-06-15 全站分類結果（58 篇）**
- **Elementor（12，REST 不可改正文）**：1205, 698, 450, 403, 345, 332, 322, 261, 253, 247, 238, 219
- **經典（46，REST 可改）**：其餘全部，含 pillar 683、945(已修)、全部 2026-03 矩陣頁
- Elementor 文章的 TOC/內文/補圖要走 wp-admin Elementor 編輯器或 Owner Chrome；REST 只能改它的 Rank Math meta / featured image。

## 5. 安全編輯 SOP（WP REST，已驗證可用 — 僅限經典文章）

> Cloudways 上 **Basic Auth 對標準 posts 端點可用**（2026-06-15 實測 200）。憑證在 Notion 保管室 `320ab0806d5c80e0be95f298399d2c44`，**只可短暫取用、絕不寫進 repo/log/memory/review/最終回覆**。

```bash
# 1. 建立 curl 設定（mode 600，放 /tmp，用完刪）
umask 077; CFG=/tmp/.maplab_wp.cfg
B64=$(printf '%s' 'EMAIL:APP_PASSWORD' | base64)
printf 'header = "Authorization: Basic %s"\n' "$B64" > "$CFG"; unset B64

# 2. 讀 raw（context=edit 才有 block markup）
curl -s -K "$CFG" ".../wp/v2/posts/{id}?context=edit&_fields=content"

# 3. 在本機改好 content（保留 Gutenberg <!-- wp:* --> 區塊結構）

# 4. 寫回（不傳 status = 維持原狀態；不發布、不刪除）
curl -s -K "$CFG" -X POST ".../wp/v2/posts/{id}" \
  -H "Content-Type: application/json" --data @payload.json

# 5. 用完刪憑證
rm -f "$CFG" payload.json
```

**三層驗證（強制，`pitfalls.md` 2026-05-11 Elementor 坑）：**
1. `content.raw`（authed）：改動正確、🍁 在、廢文已清
2. `content.rendered`（public REST）：前台會渲染的內容
3. **實際前台 HTML + Chrome tab 實跑**：`get_page_text` 看閱讀邏輯；Elementor 渲染的頁 raw 改了可能不顯示 → 以前台為準
- 若前台仍是舊的 → WP Rocket 快取，需清快取。

**邊界：** status 一律不設 `publish`（編輯既有發布文維持原狀態即可）；**禁 DELETE**；禁改 Rank Math 付費 / Ads / GTM / Pixel。分類刪併等不可逆動作只出建議，Owner 拍板。

## 6. 圖片素材池（冷啟動就要知道）

> **配圖完整指引見 `skills/maplab-photo-sourcing.md`（必讀）。** 重點：先用桌面已整理素材，別憑檔名猜盜圖，一定要視覺核對。
- **文章/案例圖（首選，已 webp+SEO 命名+本機）**：`~/Desktop/案例分享wordpress用_webp/`（30 張真實案例）
- **單一菜色圖（首選，依 item_id）**：`~/Desktop/item 圖片夾/`（52 張）↔ `data/items_master.json`（102 品項）
- 補充：`~/Desktop/外燴照片（擺設）/`(119)、`~/Desktop/2025案例/`(147)
- 最後手段：A4 場景索引 `data/photo_alt_index.db`（lb99104/mina 雲端 MAPLAB_ASSETS，~28K，**有重複/壞檔，需 API + 驗證**）
- ⚠️ 698 等 Owner 手做頁禁改圖；別用「英文檔名=stock」判斷自有與否。

## 7. 收尾（每次必做）

- Progress Log / Handoff Checkpoint（`AGENT_STARTUP_PROTOCOL.md`）
- 改檔對應清單：**哪個案例/內容 → 放進哪個 URL**（不可用「都改好了」統稱，`A2_recall` 踩雷）
- 經驗回寫 `skills/experience-log.md`；更新 `CURRENT_STATUS.md`
