# Case-first WP／SEO／音樂系列修正收據

日期：2026-08-27

狀態：`INTAKE_PASS / WP_CASES_FAIL_CLOSED_UNTIL_PROOF`

## Owner 指出的缺陷

前一版 01–10 以 live WP 服務頁作為題目，沒有先從 Google Drive 真實案例、活動身分與原始素材進入 A2/A4 事實鏈；因此曲風雖有區分，WP 主題與 SEO 關鍵字仍是服務分類推演，不是案例研究。

## VERIFIED

- Drive 母夾：`2026maplab外燴紀錄`（folder id `1pKfGSOZXBpG7qXcJrW5T7aoHX4nqB1Tt`）。
- Google Drive connector 逐夾 inventory：
  - 邦尼兔畢業典禮：22 圖＋6 影片。
  - 美術館二館抓周：20 圖＋6 影片。
  - 國泰原美：17 圖＋1 影片。
  - All for Kids 音樂會：6 圖＋2 影片。
  - 建商美術館：48 圖＋6 影片。
  - 官田性別派對：15 圖＋7 影片。
  - 日照中心開幕：7 圖＋6 影片＋1 文件。
  - 訊聯細胞：15 圖＋2 影片。
  - 服飾店開幕茶會：19 圖＋3 影片＋3 A2 文件＋1 publish 子夾。
  - 派對空間抓周慶生：14 圖＋1 A2 文件＋1 publish 子夾，無影片。
- 已讀 Drive `【模板v3】A2 活動介紹文案-WordPress式` 與 repo `case-study-production-sop`、`a4-fact-first-asset-matching`、`seo-keyword-map`、`real-cases-to-seo-matrix`、`seo-publish-checklist`。
- 服飾店開幕案已有 v3 多來源查證與 SEO 草稿；實際分店仍待確認。
- 抓周慶生案已有 A2 v1 草稿；文件本身也註明尚未逐圖 preview。
- 日照中心案例夾的唯一文件與外燴案例無關且含私人資訊；本輪沒有摘錄或寫入任何內容，registry 已標 `excluded_from_case_facts`。
- canonical `MAPLAB_ASSET_LOG` id `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`，tab `工作表1`，本輪 metadata 為 40,293 rows × 26 columns。抽查新案例檔名多數未找到對應列；另有同名舊檔命中不同年代內容，故後續 join 必須用 Drive file ID，不能靠檔名。

## DECISION

1. 前一版十個服務頁規劃由本版 `case_first_registry.json` 與實例 01–10 取代。
2. 十個案例不自動變十個新文章：先判 existing post、pillar proof、new gap 或 social-only。
3. 關鍵字分 `final_verified`、`candidate_not_final`、`withheld_until_identity`；資料夾名不足以證明活動類型的三案，不先填主關鍵字或曲風。
4. 任一案例進 WP 前，必須通過 `scripts/maplab_case_first_gate.py --level wp --case-id ...`。

## PROOF

```text
python3 -m unittest -v tests.test_maplab_case_first_gate
Ran 7 tests ... OK

python3 scripts/maplab_case_first_gate.py \
  workbook/reviews/JOB-A8-MAPLAB-MUSIC-SERIES-20260827/case_first_registry.json \
  --level intake --json
ok=true
```

第 02 案（服飾店開幕）WP gate 試跑為預期 FAIL，缺：公開分店確認、報價／等價錨、ASSET_LOG、visual QA、live SEO collision check。這是健康擋下，不是交付失敗。

## CHANGES

- `skills/case-study-production-sop.md`：新增 case-first intake gate 與來源污染處置。
- `docs/seo-publish-checklist.md`：新增 G-1～G-5 真實案例／SEO 路由閘門。
- `scripts/maplab_case_first_gate.py`：deterministic intake/WP gate。
- `tests/test_maplab_case_first_gate.py`：7 個 regression tests。
- `case_first_registry.json`：10 個真實案例來源、素材數、SEO／音樂候選與缺證據狀態。
- `wp_music_series_01_10.md`：改為 Drive 實例，而非服務分類目錄。

## BOUNDARY

- Google Drive、Docs、Sheets 均只讀。
- 未改 ASSET_LOG、WordPress、Google Ads、社群平台或公開內容。
- 未生成音樂、未剪片、未消耗外部生成額度。

## NEXT

若繼續案例產線，首選第 02 案：先補分店／報價／ASSET_LOG／visual QA／live collision proof，直到單案 WP gate PASS；PASS 前不把候選關鍵字冒充 final，也不另開 slug。
