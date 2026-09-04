# A8 發布操作手冊：YouTube＋Pinterest（Owner 版）

- 建檔：2026-09-04，Fable5 應 Owner msg 4655（「寫成操作手冊，需要我做什麼我晚點補」）
- 依據：skills/a8-produce-to-publish-sop.md、handoff/tasks/T-A8-001、T-A8-FITNESS-MVP-001、
  workbook/reviews/JOB-A8-BUNNY-EDM-WP-20260825/final/multiplatform_handoff_20260826.md、CURRENT_STATUS.md
- 原則：**你只做需要人手/授權的那幾下，其餘欄位填寫、metadata、記錄由我（A0/A8）接手。**
  任何 public 發布都要 action-time 你點頭，我不代按。

## 〇、30 秒看懂現況

| 案子 | 素材狀態 | YouTube | Pinterest |
|---|---|---|---|
| 樂齡健身 MVP（跟著動） | ✅ 已渲染（107.5s 合輯＋5 支短片） | 🔴 頻道還沒建（表單已填好，差你按「建立」）→ 之後手選檔案上傳 | 無此案素材 |
| 邦尼兔（畢業外燴） | 🔴 現有剪輯版你已退件（AUDIO_REGEN_REQUIRED），**不可上傳** | 等音訊重製＋你驗片後才進上傳 | 兩張 Pin 圖＋文案備妥，帳號已登入，等你看圖點頭 |

技術背景（為什麼需要你）：
1. 受控 Chrome 的檔案選擇器對本機 MP4 回 Not allowed → **檔案要你手選**，其餘我填。
2. 現有 Google OAuth token 沒有 youtube.upload scope → 沒有 API 自動上傳這條路（要不要補 scope 是待決策，見第四節）。
3. Pinterest 是瀏覽器登入態（maplabkitchen 商業帳號，已登入、可見「建立 Pin」），不需要任何 token 檔。

## 一、最快能上的：樂齡健身 YouTube（你的動作約 7 分鐘）

**Step 1（你，約 3 分鐘）建立頻道**
1. 開 YouTube（Google 帳號同 maplabkitchen 那組登入態）。
2. 建立頻道表單已預填：頻道名「跟著動｜華語樂齡節拍」、handle「@跟著動樂齡節拍」（系統已顯示可用）。
3. 確認名稱無誤 → 按「建立頻道」。（目前卡在這一下，final Create 尚未點。）

**Step 2（你，約 2 分鐘）手選檔案**
1. 進 YouTube Studio → 建立 → 上傳影片。
2. 檔案選這支（合輯版先上）：
   workbook/reviews/JOB-A8-SENIOR-FITNESS-MVP-20260901/render/a8-fitness-mvp-compilation-107.5s.mp4
3. 選完檔就可以離手。

**Step 3（我）填欄位**
標題／說明／章節／關鍵字用 platform/platform_copy.md 既定文案（107 秒跟著動｜5 個扶椅＋坐姿低衝擊動作）。
一律先存 **私人（Private）**，不直接公開。

**Step 4（你，10 秒）驗收裁決**
私人連結你看過 → 回「可公開」或「改」。公開那一下也由你按或明確授權我按。

**待補三小項（我先擬好給你選）**：觀眾設定（是否兒童內容→選「否，非兒童內容」）、AI 內容揭露（有 AI 生成成分→勾「是」）、縮圖（我出 2 版你挑）。
5 支單動作短片：合輯流程走通後，同 Step 2 手選逐支上（或攢一次上），每支 15 秒內可完成。

## 二、邦尼兔案：先修內容，再談上傳（你的動作＝兩個裁決）

紅線重申：final/ 與 correction 資料夾裡現有的長片、短片都是**你退過件的版本，禁止上傳**。
狀態機：AUDIO_SELECTED → TIMING_LOCKED → EDIT_READY → RENDERED_UNVERIFIED → QA_PASS → OWNER_VIDEO_GATE → APPROVED_FOR_UPLOAD，a8_video_acceptance 要 ok=true 才准進平台。

**你的動作 1（裁決）**：確認 Google Doc 裡最終版歌詞是哪一份（回訊息指認即可），我才能鎖詞重製音訊母帶。
**你的動作 2（驗收）**：重製版過 ASR＋人耳 QA 後我交你聽/看，你點頭才進 OWNER_VIDEO_GATE。
之後上傳流程與第一節相同（手選檔案那一下還是你）。

## 三、Pinterest：兩張圖等你點頭（你的動作約 1 分鐘）

帳號已登入（maplabkitchen 商業帳號）、「建立 Pin」入口可用，titles／descriptions／alt／連結全部備妥（platform_metadata.md）。

**你的動作**：看這兩張圖，回「兩張都上」「只上第 N 張」或「不上」：
1. workbook/reviews/JOB-A8-BUNNY-EDM-WP-20260825/final/pinterest/maplab-tainan-graduation-catering-menu-pin.jpg（台南托嬰畢業典禮外燴｜一口點心甜點桌）
2. 同資料夾 maplab-tainan-graduation-dessert-table-pin.jpg（台南畢業典禮甜點桌｜花藝與層架陳列）

你點頭後：發 Pin 時檔案手選那一下若同樣被瀏覽器擋，比照 YouTube 由你手選、我填欄位；沒擋就我全程處理，發完回報 Pin 連結。
（備註：Pin 是靜態圖，跟被退件的影片音訊問題無關，可先於影片單獨發。）

## 四、待你決策的一項：要不要開 API 自動上傳

- 現況：上傳走瀏覽器 Studio，每支影片都需要你手選檔案那一下。
- 若要全自動：需在 GCP 專案 maplab-ai 的 OAuth 加 youtube.upload scope＋做一次授權，之後我可 API 上傳（未驗證專案可能限私人影片，正好符合「先私人再驗收」流程）。Pinterest 同理有官方 api-quickstart 可建最小上傳器。
- 我的建議：先用手動流程把樂齡第一支走通、確認頻道方向，再決定要不要投工程做 API。**此項不急，你晚點補資訊時順帶說一聲要或不要即可。**

## 五、你晚點回來時，最小回覆格式

一則訊息含四樣就能全部推進：
1. 「頻道已建」（或卡在哪一步）
2. 「合輯已選檔」（或約時間我把 Studio 頁面備好）
3. 邦尼兔最終歌詞＝哪一份
4. Pinterest：兩張都上／只上N／不上（＋要不要研究 API 自動上傳）
