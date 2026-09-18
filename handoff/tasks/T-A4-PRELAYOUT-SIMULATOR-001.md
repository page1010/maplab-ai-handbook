# T-A4-PRELAYOUT-SIMULATOR-001 — 外燴預擺照片、器具與桌面模擬

- **狀態**: 🔄 進行中 — FIRST_BATCH_VERIFIED / COLLECTION_INCOMPLETE / SIMULATOR_NOT_IMPLEMENTED
- Owner request: 2026-09-18，本 Codex thread。找 Mina 相簿預擺照片，從原始檔推敲年份，對照報價單人數與餐點；同類照片集中、核對命名與細節說明，為器具模擬系統建立可靠資料。
- Scope: historical + recent records; local private copies only. Do not rename/move/delete originals, modify Sheets, publish, send customer messages, or send private data to third-party models.
- Code/control root: canonical MAPLAB repo. Private photo/catalog root: `/Users/pagemacmini/Documents/MAPLAB_外燴預擺` (local, outside Git).

## Acceptance

### Owner scope correction — 2026-09-18 second turn

Goal (latest Owner correction): inventory ALL equipment and maximize feasible event count and service volume, subject to menu/service quality, safety, transport, labor and turnaround constraints. Four simultaneous events of differing headcounts is a test case, NOT a fixed upper bound. Morning equipment may serve an evening event only after return, cleaning/inspection and transport buffers. The intended product is a proportional drag-and-place table/equipment "paper-doll" planner, followed by menu/conversation-assisted, human-readable staff picking/return instructions. Owner asks to reuse prior A4/A5 recognition/renaming search, verify Mina login and include finished setup photos and alternative evidence. Annual 100–200 events and hundreds of historical cases are Owner estimates, not yet audited denominators.

First-principles review before execution:
1. Ideal: enter each event's time/site/table/menu/headcount once; derive compatible packing/layout plans against one shared equipment pool, maximizing feasible service and showing shortages, turnaround opportunities and eligible idle alternatives. Staff can identify the exact item, quantity, shelf, event, pick/return time and corresponding diagram.
2. Observed vs desired: previous 12-photo pack validated provenance only, not representative coverage or inventory completeness.
3. Real vs assumed limits: pre-layout-only is a removable method constraint. Finished setup/closeup/storage/packing/purchase evidence can help; present count, dimensions and availability need independent current evidence.
4. Minimal redesign: reuse current photo/quote indices, separate visual recognition from equipment identity/count/availability, then deterministic shared-resource constraints. No weight-training claim, new cloud provider or synthetic inventory promoted as real.
5. Live proof: query existing local index/schema and source counts, verify signed-in Mina Photos, copy selected real candidates with hashes and record unreviewed coverage. Independent reviewer tests counts/duplicates and four-event constraints.

This turn deliverables: expanded searchable/copyable candidate pool + documented coverage; corporate-culture rule for purpose-first alternate evidence; multi-event input/output and stop conditions. No production dispatch or purchasing.

1. Visually confirmed pre-layout photos copied into one discoverable folder with source URL/path, original filename, hash, date evidence, quote match confidence and missing fields.
2. Capture date and event date remain separate; dates from renamed year buckets are not EXIF proof. Ambiguous candidate quotes remain candidates.
3. Equipment catalog distinguishes photo-observed type, measured dimensions, stock count and dish capacity. Unknowns remain null, not invented.
4. Local table-size simulator: real catalog, proportional placement, collision/boundary checks, menu assignment, save/reopen; dimensional confidence displayed.
5. Tests, source coverage, remaining gaps, and Resume Prompt retained; no claim of complete collection without denominator.

## Current evidence

- Mina Google Photos account verified in Owner Chrome (2026-09-18).
- User reference photo found in live Mina Photos: `IMG_3327.JPG`, photo date 2026-09-15 12:28:32, 1587×1031, original-quality backup. Overlay says 9/16 B 下午茶敘 180.
- Candidate quote live readback: 2026/9/16 afternoon tea, at most 30 guests, 180 food pieces. Image-to-quote join still under cross-check; never call 180 guest count.
- Historical A4 index covers 2022–2025, not fresh 2026. Ten historical empty-layout/equipment-configuration photos and one close-up were visually reviewed and copied. Plus the Owner reference derivative: 11 layout/configuration photos + 1 equipment close-up, 12 primary photos total.
- Four historical files preserve EXIF capture dates (3 in 2023, 1 in 2025); seven remain unverified-year. H002/H004/H005 have explicitly labelled 2025 inferences supported by quote/date/event clues. N001 is dated by the live Photos UI, not downloaded-original EXIF.
- Live original download was blocked by client; local Takeout same-name IMG_3327.JPG is a different image. Only Owner attachment and separately labelled page rendition are saved for N001. Adjacent IMG_3326 is receipts, not menu-label evidence; excluded.
- Four live quote readbacks / 37 menu entries retained locally. Photo joins are all candidates, not confirmed identities. 180/240 food-piece sums verified; headcount vs servings, units and table count remain separate.
- Private entry: `/Users/pagemacmini/Documents/MAPLAB_外燴預擺/README.md`; each photo has same-name details; quotes, machine-readable catalog, hash evidence and measurement worksheet included.
- Receipt: `reviews/PRELAYOUT-20260918/receipt.md`. Six unit tests PASS; 12/12 source-copy hashes verified; idempotent report rerun PASS. Private data/photos are outside Git; only code and redacted handoff/receipt are committed.
- Equipment families are visual labels only (duplicates possible), zero measured inventory items. No simulator or scale/fit guarantee yet. Recent June–July backup 472 files is metadata-only, unreviewed/un-deduplicated, not claimed complete.

## Next Bounded Action

Review one bounded batch (up to 25 files) from the existing June–July 2026 event-backup folders for actual empty equipment pre-layouts. Preserve originals, use EXIF/Takeout sidecars for year evidence, add only visually confirmed copies by hash, and update the private source manifest plus report. Independently resolve the strongest H002/H004/H005 case match using original-photo metadata or order/event keys; do not rerun broad searches or treat all 472 files as relevant. Do not retry the rejected same-name N001 original or adjacent receipt photo. UI preference does not block data collection; no new simulator UI in this checkpoint.

## Resume Prompt

Read this card, CURRENT_STATUS.md, pitfalls.md, docs/a4/source-of-truth.md and skills/photo-asset-retrieval-guide.md.
Open `/Users/pagemacmini/Documents/MAPLAB_外燴預擺/README.md` and `資料/verification.json` first; 12 primary copies are already verified.
Do not re-download or re-label the same batch. Four EXIF dates are verified; seven historical years remain unknown; three have labelled 2025 inferences.
N001 is the Owner's 9/16 B afternoon-tea image. Photos displays IMG_3327.JPG and 2026-09-15 12:28:32 +08; original bytes remain missing.
Takeout same-name IMG_3327.JPG is a different picture. Adjacent IMG_3326 is not menu evidence. Exclusions are durable.
Candidate quote says at most 30 people / 180 food pieces; other cases also separate servings and guests. All four image joins are still candidate.
Use the next bounded batch above, not a new architecture or full-library download. Keep all private images and raw quote data local, no DeerFlow/OpenRouter.
Refresh private generated handoff with `rtk proxy python3 scripts/prelayout_collection_report.py --root /Users/pagemacmini/Documents/MAPLAB_外燴預擺` after curated source updates.
Run `rtk proxy python3 -m unittest discover -s tests -p test_prelayout_collection_report.py -v`, verify hashes and report idempotence, then update receipt.
Simulated fit requires measured equipment footprint, height, shelf area and current stock; none yet measured. Do not infer from perspective photos or a shopping screenshot.
No cloud publication, source-file mutation, customer messaging, or unapproved data egress. Continue this task, not stale SEO/LINE work.

## 收尾與接續備忘 — 2026-09-18 18:1x(Writer: Fable5 bot 窗代跑;Owner 5369 指示入卡)

Owner 原話(msg 5369, 2026-09-18T17:13:21):「當他寫紀錄讓他記得收尾與接續並注明你的意見與看法」。以下事實與意見分開標,codex 恢復額度後讀本節即接手,不需口頭交接。

### 事實(Fable5 已代跑,有憑證)

- 上節「Next Bounded Action」的 25 檔批次已由 Fable5 於 2026-09-18 執行完畢。報告:私有庫 資料/backup-batch-20260918-review.md;逐檔 sha256 與來源路徑:擴充候選/備份批次-20260918/staging-manifest.tsv。原檔零改動。
- 備份夾實際位置已定位:~/Library/CloudStorage/GoogleDrive-lb99104@gmail.com/我的雲端硬碟/MAPLAB/MAPLAB_ASSETS/備份-2026maplab外燴紀錄-20260720,遞迴實數 492 檔(帳面 472 過時)。
- 批次結果:24 張獨立影像全數人工目視,**0 張真空桌預擺照**;唯一入選 B15=0718 服飾店開幕「場地素桌 pre-setup」新類別(併桌未鋪巾)。19 張成品桌/食物、3 張無桌、1 張跨夾重複。
- 重複實證:0621說事實木地板開幕 與 20260621說事實木地板開幕 兩夾含相同檔案(IMG_1400.HEIC sha256 一致)→ 472/492 非獨立數,去重未做。
- 日期證據:24/25 檔 EXIF/HEIC creation 與夾名日期完全吻合(2026-06-12~07-19);B23 無 EXIF。
- H002/H004/H005 未推進:2025 標註案與本 2026 備份夾無交集,未硬湊。
- collection.json / verification.json 未動(保護 hash 鏈);本備忘與批次報告為新增檔,由 codex 決定如何併入 coverage。collection report 腳本與 unittest 未重跑(Fable5 bot 窗無 rtk proxy 通道)。

### 【Fable5 意見】(僅供裁定,主導權在 codex)

1. **本案瓶頸不是照片,是量尺。** 主庫多年 12 張+本批 0 張,證實團隊只拍成品桌;空桌預擺照存量趨近枯竭。模擬器需要的器具尺寸/庫存只能靠實測(器具量測清單.md 等 Owner/現場),照片降級為佈局參考即可,不建議再花大批檔次撈空桌照。
2. **下批抽樣改法**:每夾改抽「拍攝時間最早的 1 張」(比檔名排序更可能落在擺桌前)+ _根目錄散檔 夾(約 200 檔)抽查;動工前先做 0621/20260621 兩夾去重。
3. **收尾標準建議明訂進卡**:蒐集線可宣告階段性關閉(佈局參考已足量:本批另有 10 張成品桌全景可用),模擬器動工不必等 492 檔全審完;SIMULATOR_NOT_IMPLEMENTED 的解鎖條件建議寫成「首批 ≥N 件實測器具入冊」而非「照片蒐集完成」,避免無限期蒐集。

### 批次 2 補記 — 2026-09-18 晚(Owner 5370「幫他」,Fable5 代跑)

- 上節意見 2 的兩件事已代跑完畢,報告:私有庫 資料/backup-batch2-20260918-review.md。
- 去重實證:0621說事實木地板開幕 24 檔全數含於 20260621 夾(交集 24、獨有 0)→ 整夾冗餘,**真實獨立分母 = 492 − 24 = 468**。
- _根目錄散檔(201 檔)依序號分群抽 25 檔逐張目視:**再次 0 張空桌預擺**(兩批合計 49 張獨立影像 0/49),全為成品桌/食物特寫/外帶餐盒。空桌照存量枯竭雙重驗證,支持意見 1、3 的收斂主張。
- 新事實:散檔拍攝日 2026-03-06 ~ 06-13,早於命名夾區間(06-12 ~ 07-19)——散檔是 2026 年 3–5 月場次的唯一紀錄來源,建立全年案量分母時必須納入。C15/C16 無 EXIF,同場企業頒獎茶會,日期僅可由序號夾擠為 5 月上旬候選(非證據)。
- 暫存與 hash:擴充候選/備份批次2-散檔-20260918/(staging-manifest.tsv 雙驗)。原檔、collection.json、verification.json 一律未動;collection report / unittest 仍待 codex 以 rtk proxy 補跑。

## Owner 5380 指示 — training 素材庫 + 器皿尺寸新方法(2026-09-18)

Owner 原話(msg 5380, 2026-09-18T17:35:48):「用這個training 把路徑寫進這個案子 他可能不好核對場次人數 但器皿可以用淘寶以圖搜物 確認長寬高 並建檔備註報價與連結--https://drive.google.com/drive/folders/1W6XEQZso1IKKKRF9zw3vWteGdnuvcKLc」

1. **素材庫入冊**:Drive 資料夾「外燴照片(擺設)」= Owner 手選 training 集,140 檔無子夾(約 45 檔以場次命名)。清單已由 Fable5 以唯讀 Drive API 列冊:私有庫 資料/training-外燴照片擺設-manifest-20260918.md。注意:同名檔在 Drive 是不同檔案(長榮大學emba音樂會 ×9 等),下載須改名;多檔副檔名與實際 mime 不符,以 mime 為準。
2. **規則修訂(Owner 裁定,取代本卡先前禁令)**:器皿尺寸可用淘寶「以圖搜物」找同款商品頁,**長寬高抄商品頁規格**,逐件建檔並備註報價與連結。原「不得從商品截圖推尺寸」條款修訂為:商品頁規格=**候選證據層**,與現場實測分層並存,欄位標注來源;實測值仍為最高證據層,兩者不混寫。
3. **建檔格式建議**(codex 可改):資料/equipment-taobao-catalog.tsv,欄=器皿名/出現照片檔名/淘寶商品連結/長寬高mm(商品頁)/報價(幣別照頁面)/比對信心(同款確認|相似候選)/備註。淘寶報價僅作器材重置成本備註,**永不進客戶報價**(定價鐵律=台南行情×1.35)。
4. **優先序調整**:場次人數核對降優先(Owner 明示「他可能不好核對場次人數」);主線=器皿逐件辨識+尺寸建檔,直接餵 SIMULATOR 解鎖條件(首批 ≥N 件含尺寸器皿入冊)。
5. **外送邊界**:Owner 本指示=授權將「器皿」畫面送淘寶搜圖。上傳前裁切至器皿本體,**不得含客人/兒童/可識別人臉**(私照不外送規則對人像仍有效);整張含人照片不得直接上傳。
6. **執行分工**:淘寶以圖搜物需瀏覽器,由 codex(Owner Chrome)執行;Fable5 bot 窗無瀏覽器,已完成路徑入冊+清單列冊。
