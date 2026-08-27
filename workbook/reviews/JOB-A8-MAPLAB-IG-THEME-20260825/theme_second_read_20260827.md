# MAPLAB 主題曲第二讀與修正提案

狀態：`PROPOSAL_ONLY / OWNER_LYRICS_GATE`

日期：2026-08-27

## 結論

保留歌名《把相聚端上桌》。兩個獨立視角都認為它有動作、餐桌與人的關係，比抽象的「幸福／美好／滋味」更像 MAPLAB。這輪不改歌名，改三件事：

1. 把完整歌由 75–90 秒收斂為約 62–70 秒，先 Hook、再 Rap、再回 Hook。
2. 把主歌從單一家庭聚會擴成四個具體服務場景，讓廣告性來自真實能力，而不是促銷口號。
3. 讓 Hip-hop 真正進入節奏規格：8 小節女聲輕 Rap、拍點微後、每兩小節一個場景；副歌保留 City-pop 的旋律與留白。

## 保留與修正

### 保留

- 歌名與核心句：`把相聚端上桌`。
- 暖光、杯緣、碰杯、花與桌景的視覺語言。
- 女聲、清楚華語咬字、City-pop × 輕 Hip-hop。
- exact 15 秒 Hook 仍能單獨成立。

### 修正

- 現行 `孩子／長輩／好久不見` 太集中在家庭聚會，無法代表品牌活動、開幕、會議茶點與婚禮等服務範圍。
- 現行 prompt 有 City-pop 樂器與唱腔，卻沒有 Rap bars、flow、鼓點與 Hook-first 結構。
- `lyrics.txt`／`lyrics_review.md` 仍寫「檸檬和奶油」，Task Card 記錄 Google Doc 已是 `lemon and cream`；生成前須以 Google Doc 反讀結果鎖定唯一歌詞。
- 完整曲不再靠 75–90 秒堆段落；以 62–70 秒完成一次清楚的品牌敘事。

## 歌名候選

1. **《把相聚端上桌》** — 首選；情感、餐桌與動作最完整。
2. **《一桌成景》** — 服務辨識較高，情感較冷，適合作系列副標。
3. **《讓現場亮起來》** — 有開場能量，外燴指向較弱。

決策：主題曲保留《把相聚端上桌》；`一桌成景` 可作影音系列名稱，不替換歌名。

## 修正版結構提案（約 62–70 秒）

> 這是第二讀提案，不覆寫 Google Doc 或正式 `lyrics.txt`。

```text
[Cold Hook][Female Vocal]
把相聚端上桌
讓今天慢慢亮起來

[Verse][Female Vocal, Light Rap, 8 bars]
品牌開幕　看動線也看鏡頭
會議茶點　讓交談接著走
婚禮的花　週歲的笑
菜單和桌景　都跟著現場調

份量、器皿、取餐的節奏
讓來賓邊走邊聊　空間留得從容
我們沿著桌邊　把細節排好
等第一聲碰杯　讓故事開場

[Pre-Chorus][Female Vocal]
燈亮起來　人也靠近
杯子輕輕一碰　今晚有了聲音

[Chorus][Female Vocal, Warm Group Harmony]
把相聚端上桌
把心意留在每一口
光沿著杯緣走
讓笑聲坐到最後

[Final Tag][Soft Group Harmony]
MAPLAB　陪著笑聲到最後
```

### 為何這版比較像廣告、但不變硬廣

- `看動線也看鏡頭`：同時對應現場流動與品牌畫面。
- `菜單和桌景都跟著現場調`：把客製說成可見的工作，不用「專業客製」口號。
- `份量、器皿、取餐的節奏`：唱出外燴設計顧問的判斷層。
- Rap 承擔服務訊息，副歌承擔品牌記憶；不把服務清單塞進副歌。

## exact 15 秒 Hook 決策

建議音訊不額外唱品牌名，畫面最後 1.5 秒顯示 `MAPLAB Kitchen｜外燴設計顧問`。這能維持低壓銷售，也避免完整歌與短 Hook 重複喊品牌。

```text
把相聚端上桌
把心意留在每一口
光沿著杯緣走
讓笑聲坐到最後
```

若 Owner 希望 15 秒音訊離開畫面仍可辨識品牌，再另測一版短 tag：`MAPLAB，把相聚端上桌`；這會改動目前「品牌只在 Final Tag 出現一次」的 acceptance，須明確選擇。

## 修正版音樂 Prompt

```text
Taiwanese Mandarin city-pop × light hip-hop brand anthem, 102–104 BPM,
4/4, warm, polished, inviting and commercially memorable.
Open with a two-line sung hook in the first 8 seconds, followed by an
8-bar conversational female rap. Keep the rap slightly behind the beat,
with clear Mandarin consonants, 8–12 Chinese characters per bar, and one
concrete event-service scene every two bars. Sing service nouns on straight,
centered notes so every word stays intelligible.

Use Rhodes electric piano, clean muted guitar, melodic live bass,
syncopated kick, crisp hi-hat, dry brushed snare and restrained analog
synth glow. Let the bass and drums become more present during the rap,
then lift into warm stacked-third harmony for the chorus. Add a brief
stop-time accent before 「把相聚端上桌」 so the title lands like an audio logo.

Keep the chorus melodic and spacious. Hold 桌、口、走、後 for 1–1.5 beats,
add late vibrato only after pitch is centered, and use one small turn only
on the final 後. Mention MAPLAB once in the final tag. Keep the rhythm light,
the language concrete, the claims factual and the chorus spacious.
Target 62–70 seconds. Preserve exact bilingual diction for "lemon and cream"
only if that line remains in the Owner-approved Google Doc.
```

## Owner 需要決定的兩件事

1. Rap 採目前的「品牌／企業＋婚禮／家庭混合」；或只聚焦企業品牌活動。
2. exact 15 秒 Hook 只靠畫面 Logo；或新增一次 `MAPLAB` 音訊 tag。

## 證據與邊界

- 品牌與 IG brief：`ig_style_brief.md`。
- 現行歌詞：`lyrics_review.md`、`lyrics.txt`。
- 現行 prompt：`style_prompt.txt`。
- 英文發音證據：`theme_pronunciation_test_receipt.md`，只證明候選 B 的 `Lemon and Cream` 咬字，不代表完整歌核准。
- 本提案未送外部生成、未耗額度、未改 Google Doc、未渲染或發布影片。
