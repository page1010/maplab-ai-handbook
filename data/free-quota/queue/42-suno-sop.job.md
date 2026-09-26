OUTPUT: data/free-quota/suno-sop/brief.md
FANOUT: lists/music_scenes.txt x lists/music_styles.txt
FANOUT_N: 100
DAILY: yes

你是 MAPLAB 音樂線的製作助理。本題只處理這一組「場景｜曲風骨架」:

{{ITEM}}

把它寫成一張可以直接照著燒的 Suno SOP 草稿。輸出格式(繁體中文):
1) `場景:` 與 `曲風:` 兩行,原字照抄上面那一組的左右兩半。
2) `SUNO_STYLE:` 一行英文 style prompt,120 字元內,包含曲風、樂器、質感詞。
3) `BPM:` 一個數字,必須落在上面曲風骨架給的區間內,並寫出區間本身。
4) `結構:` 用 intro / A / B / bridge / outro 標記,標出每段大約秒數,總長 90 到 150 秒。
5) `情緒曲線:` 三句話,說明開頭、中段、收尾各要讓現場的人感覺到什麼。
6) `避免:` 三條,寫這個場景絕對不能出現的音樂元素,並各給一句理由。
7) `驗收:` 兩條可以用耳朵判斷成敗的條件。

鐵律:
- 全 instrumental,不得寫歌詞、不得寫人聲指示、不得指定任何真實歌手或現有歌曲名。
- BPM 必須在給定區間內,不得自行改區間。
- 不得出現價格、客人姓名、店名。
- 全文 400 字內。
