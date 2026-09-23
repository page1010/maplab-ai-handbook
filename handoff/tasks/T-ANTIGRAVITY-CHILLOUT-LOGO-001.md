# 工作單 T-ANTIGRAVITY-CHILLOUT-LOGO-001｜音樂頻道 logo 與封面一致性系統（提案）

> 來源：Owner Telegram msg **5881**（inbox ts `2026-09-22T18:41:01`）
> 原話（SSOT，不改寫）：**「發給antigravity 留存 對標我們音樂頻道要有logo 叫台南chill out」**
> 對標素材：Owner 同批三張截圖（ts 18:40:36／18:40:38／18:40:39），存
> `data/telegram-photos/20260922_184035_*.jpg`、`_184037_*.jpg`、`_184039_*.jpg`
> 執行者：antigravity（派工走 `agent-bus/inbox/antigravity/`）
> 建立：2026-09-22，Writer=Fable5 本人・同 session 續接
>
> 派工前必跑：`python3 scripts/check_work_order.py handoff/tasks/T-ANTIGRAVITY-CHILLOUT-LOGO-001.md`

---

## 對標對象拆解（我已逐張看過，不是靠檔名猜）

素材是 **We Are Diamond** 的 **Chillout 2026** 播放清單（218 首）。真正造成一致性的不是美術，是三件死規矩：

1. **同一個單線連續字母標**壓在每張不同照片的正中央，約佔封面寬六成，半透明讓照片透過去。
2. **右上角固定小徽章**壓母品牌名（WE ARE DIAMOND），每張同位置同尺寸。
3. **左下角固定兩行字**：上行藝人全大寫較粗、下行曲名較細，顏色從照片取色。

**關鍵證據（第三張截圖）**：同一個標在日落照是橘色、在草地照是金綠色——造型不變、顏色跟著照片走。能這樣做是因為它是**單色線條標**。這是「必須是單線標」的技術理由，不是審美偏好。

## 頻道名分層：未定，不得自行處置

我們現行頻道名是 **MAP TABLE RADIO**（`style_registry.jsonl` 17 首中 16 首的 SEO 標題結尾、`STYLE_REGISTRY.md` 標題格式皆是）。Owner 說「叫台南chill out」有兩個讀法，已上呈並附建議（見 ts 18:40:36 回覆）：

- 讀法一：改名，台南 chill out 取代 MAP TABLE RADIO（連帶 16 首標題與 MTR 代號體系）。
- 讀法二（**我建議、且未定案前照此做**）：MAP TABLE RADIO 為母品牌，台南 chill out 為系列／清單名——對標對象自己就是這樣分層的，且不動已發布標題＝可逆。

**對 antigravity 的硬性要求：徽章文字出兩版（MAP TABLE RADIO 版、台南 chill out 版），不得自行選定，也不得修改任何已發布影片的標題或說明。**

---

## 派工欄位（五欄硬性 ＋ 可逆性）

- **結果**: `data/music-style-db/logo-proposals/` 底下有一份 `PROPOSAL.md` 與三個 logo 方向的完整檔案，每個方向都是單色單線字母標（台南 chill out 字首，線條可取台南意象如運河水波、屋簷曲線入字形），附純黑與純白版本、實際套在既有封面照上的模擬圖、以及一份可照著做下一首的版位規格；Owner 圈選其中一個之後，任何人拿一張台南照片就能產出風格一致的封面，不必每次找美術
- **指標**: 三個方向各交齊六項且可逐項驗：①單色單線、無漸層無陰影 ②純黑與純白兩版 ③至少兩張套用模擬（一張亮底照、一張暗底照），證明同一標換色可用 ④縮到 96px 的縮圖仍能辨識（附該縮圖，這是手機清單的真實尺寸） ⑤徽章文字兩版（MAP TABLE RADIO／台南 chill out） ⑥版位規格寫成數字（標佔封面寬百分比、徽章位置與尺寸、左下兩行的字級與位置）。另：三案皆不得出現 We Are Diamond 的字母造型；提案檔不含任何歌詞
- **期限**: 2026-09-26 12:00
- **權限**: 只能新增 `data/music-style-db/logo-proposals/` 底下的檔案；**不得修改** `style_registry.jsonl`、`STYLE_REGISTRY.md`、既有 `covers/`、任何已發布影片的標題或說明；**不得上傳到 YouTube 或任何平台**；不得 commit 到 main（自己的分支或提案夾即可）；不碰金鑰、真倉
- **回報點**: 交件時回寫 `agent-bus/outbox/antigravity/` 的同名卡片終態，並在 `PROPOSAL.md` 底部補「執行紀錄」一節。done = 指標六項對三個方向都成立且 PROPOSAL.md 已落檔；blocked = 卡在素材不足或字形做不出可辨識的 96px 版時，寫下卡在哪一案的哪一項、已試過什麼，**不准靜默結束、不准自標 PASS、不准自己選定方案**
- **動作可逆性**: 可逆（只新增提案檔，不動既有資產，不發布；錯了刪掉重做即可）

---

## 硬規則（違反即退件）

1. **不得仿 We Are Diamond 的標。** 對標的是版位制度，不是那個圖形——那是人家的商標，不是靈感素材。
2. **提案即提案。** logo 是對外品牌，**發布與否由 Owner 圈選**；antigravity 不得自行啟用、不得上傳、不得改既有頻道識別。
3. **頻道名分層未定**（見上節），徽章兩版並存，不得代 Owner 決定。
4. 不得虛構曲目或代號；引用不到實體的檔名不得寫進提案（「357 模板」教訓）。
5. 歌詞不進提案檔（歌詞另存獨立檔由 Owner 定稿）。
6. 自己跑完不得自標 PASS。

## 接續狀態

- **狀態**: 🔄 IN_PROGRESS（工作單已成形並驗過，卡片待寫入 bus）
- **最後活動**: 2026-09-22
- **動作可逆性**: 可逆
- **接續點**: 看 `agent-bus/inbox/antigravity/antigravity-chillout-logo-20260922.json` 是否已被撿走、`data/music-style-db/logo-proposals/` 是否已有 PROPOSAL.md

## 執行紀錄

（executor 回寫處。**終態未寫＝未完工**，不論成敗都要留一行。）
