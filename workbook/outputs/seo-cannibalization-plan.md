## 決策矩陣（每頁一列）

| Slug | 現有角色推論 | 建議行動 | 目標 pillar | 備註 |
|---|---|---|---|---|
| `tainan-party-venue`（page ID 15） | 派對流程、場地、餐點、預算的泛用 page；搜尋意圖比純外燴場地更寬 | 保留為「派對流程規劃」頁，弱化 venue 主詞，轉向流程、預算、家庭與派對規劃 | `tainan-catering-venue-guide` | Page 權重可能較高，先不要直接 301；需 REST / GSC 確認是否吃到「台南外燴場地」query |
| `tainan-catering-venue-7` | 場地清單型文章，可能承接「7個場地推薦」與比較型搜尋 | 改成 supporting list：保留清單價值，H1/H2 聚焦「7種場地情境」，文首導向 pillar | `tainan-catering-venue-guide` | 內容若薄或過時，再評估合併；內鏈前需標記 [INTERNAL_LINK_RECHECK_REQUIRED: tainan-catering-venue-guide] |
| `tainan-catering-venue-selection-2026` | 年份型場地選擇指南，可能承接 2026 新鮮度與 checklist 意圖 | 改成年度 checklist / 更新紀錄頁，避免和 evergreen pillar 搶同一 H1 | `tainan-catering-venue-guide` | 可保留「2026 選場注意事項」子意圖；年份過期後需更新或合併 |
| `tainan-catering-venue-guide` | evergreen 場地指南，較適合承接「台南外燴場地」主意圖 | 推薦升級為 pillar；補完整場地分類、選場流程、FAQ、案例與 supporting links | `tainan-catering-venue-guide` | 需 REST 確認 title、現有內容長度、流量與是否 indexable |
| `tainan-waihui-changdi-tuijian` | 中文拼音 slug，主題推論為「台南外燴場地推薦」 | 若有流量或 backlinks，暫列 legacy candidate；最終建議 canonical 到 pillar | `tainan-catering-venue-guide` | 與另一拼音 slug 近重複；不要在新文章內鏈直接引用 |
| `tai-nan-wai-hui-chang-di-tui-jian` | 另一版本拼音 slug，疑似同主題重複頁 | 高優先確認；若無明顯流量或獨立內容，301 到最終 pillar 或勝出的拼音頁 | `tainan-catering-venue-guide` | 需避免 redirect chain：不要先轉到另一拼音頁、再轉 pillar |

## Pillar 化方案（推薦首選）

推薦以 `tainan-catering-venue-guide` 作為場地群 pillar。理由是它的 slug 最接近 evergreen guide 意圖，可承接「台南外燴場地」「台南外燴場地推薦」「外燴場地怎麼選」等主題，不會像 `tainan-party-venue` 一樣同時混入派對流程與預算，也比年份頁更耐用。

需要強化方向：

1. H1 與首段聚焦「台南外燴場地指南 / 場地推薦」主意圖。
2. H2 拆成場地類型：飯店會議、品牌開幕、展覽 VIP、企業內訓、家庭派對、文化場館。
3. 增加選場 checklist：人數、動線、電源、備餐區、停車、進撤場時間、雨備。
4. 放入案例支援，但不過度堆案例；案例內鏈全部先用 [INTERNAL_LINK_RECHECK_REQUIRED] 標記。
5. Supporting pages 改成子意圖，文首或結尾回鏈 pillar。

## 301 方案（若 pillar 化難度高）

若 REST / GSC 確認多數頁內容薄、排名分散，才進 301 合併。建議先決定最終 canonical，再一次設 redirect，避免 chain。

建議路徑：

1. `tai-nan-wai-hui-chang-di-tui-jian` → `tainan-catering-venue-guide`，除非 GSC 顯示它明顯高於其他頁。
2. `tainan-waihui-changdi-tuijian` → `tainan-catering-venue-guide`，若它沒有獨立內容或有效流量。
3. `tainan-catering-venue-selection-2026` → `tainan-catering-venue-guide`，僅在 2026 年份頁無法維護或內容重複時執行。
4. `tainan-catering-venue-7` 先不急著 301，可改成清單型 supporting page；若內容與 pillar 重疊超過 70%，再合併。
5. `tainan-party-venue` 先保留，不做 301；它是 page ID 15，且角色可轉為派對規劃。

Redirect 注意事項：

- 只做一跳到最終 pillar，不建立 A → B → C。
- Redirect 前先匯出原 slug 的 title、status、canonical、top query、clicks、impressions、backlinks。
- 若某頁已有外部連結或穩定流量，優先改寫成子意圖，不直接合併。

## 內鏈收斂建議

現有文章若引用場地群 slug，建議統一收斂到：

- 主場地 pillar：[INTERNAL_LINK_RECHECK_REQUIRED: tainan-catering-venue-guide]
- 場地清單 supporting：[INTERNAL_LINK_RECHECK_REQUIRED: tainan-catering-venue-7]
- 派對流程 supporting：[INTERNAL_LINK_RECHECK_REQUIRED: tainan-party-venue]

改法：

1. 泛稱「台南外燴場地推薦」「外燴場地怎麼選」統一指向 [INTERNAL_LINK_RECHECK_REQUIRED: tainan-catering-venue-guide]。
2. 文中談「7個場地」「場地清單」「快速比較」才指向 [INTERNAL_LINK_RECHECK_REQUIRED: tainan-catering-venue-7]。
3. 文中談「派對流程、預算、餐點安排」才指向 [INTERNAL_LINK_RECHECK_REQUIRED: tainan-party-venue]。
4. 不再新增指向 [INTERNAL_LINK_RECHECK_REQUIRED: tainan-waihui-changdi-tuijian] 或 [INTERNAL_LINK_RECHECK_REQUIRED: tai-nan-wai-hui-chang-di-tui-jian] 的內鏈，除非 REST / GSC 確認其中一頁是正式 canonical。

## 執行優先序

1. 最優先（立即可做，低風險）

   匯出六頁的 REST 狀態、title、canonical、modified、indexability，先不改站。新文章內鏈先全部收斂為 [INTERNAL_LINK_RECHECK_REQUIRED: tainan-catering-venue-guide]，避免再擴大互搶。

2. 次優先（需 REST 確認後）

   決定 `tainan-catering-venue-guide` 是否可當 pillar；若可，改寫其 H1、導言、H2 架構與內鏈入口。同步把 `tainan-catering-venue-7`、`tainan-catering-venue-selection-2026`、`tainan-party-venue` 改為清楚子意圖。

3. 保留觀察

   拼音重複 slug 先只列入 redirect 候選。等 GSC / REST / backlinks 確認後，再決定 301 到 pillar 或保留一頁作 legacy landing。

## 注意事項

- REST 查無前，不能宣稱任一頁是 live、indexable 或應立即刪除。
- GSC query 重疊未確認前，本文只屬於 cannibalization plan，尚未進入執行命令。
- 301、canonical 修改、正式頁改寫與 WordPress 發布都需要 Owner approval。
- 若 Rank Math 設定仍凍結，先改內容與內鏈草案，不碰付費設定或 schema。
- 新增文章時不要直接連任何 slug；先使用 [INTERNAL_LINK_RECHECK_REQUIRED: slug]，由 checker 或 A2 盤點後再換成正式 URL。
