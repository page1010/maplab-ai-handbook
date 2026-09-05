# 視窗匯流排（window bus）— bot 窗 ↔ 主視窗直接溝通，Owner 不當傳聲筒

依據：Owner 指正（2026-09-04）「這樣不是很本末倒置嗎 我要兩邊溝通誒」。
先前錯誤做法：bot 窗叫 Owner 開主視窗重新交代積壓工作。自本檔起廢止。

## 規則（兩邊都要遵守）

1. bot 窗（白名單自動制）遇到自己跑不了的工作 → 寫一筆進本檔「佇列」，狀態 QUEUED。不叫 Owner 轉述。
2. 主視窗每次開工（不論 Owner 為了什麼事打開、或 watchdog/續接喚醒）→ 第一步讀本檔，把可跑的 QUEUED 項直接接走：改 RUNNING → 跑完改 DONE 並附一行結果（或 BLOCKED 附卡點）。
3. bot 窗被問「進度」→ 直接讀本檔回報，不重跑工作。
4. Owner 只剩兩種被打擾：主視窗權限跳窗按一下；裝新東西（下載/安裝）的事前同意。其餘溝通一律走本檔。
5. 誠實規則照舊：狀態欄只寫實際發生的事，不准把 QUEUED 寫成 DONE。

## 佇列

| # | 工作 | 來源 | 前置 | 狀態 | 結果／卡點 |
|---|---|---|---|---|---|
| Q1 | 裝開源拆解工具＋抓 Owner 給的三支參考片＋跑第一份拆解報告 | 看板 T9（draft 4696 積壓） | Owner 派工 → 已同意安裝（msg 4756, 2026-09-04 18:43） | RUNNING(拆解) | 2026-09-05 15:45 工具鏈裝好：yt-dlp 2026.8.19＋ffmpeg 9.0.1＋whisper-cpp 1.9.2（log: data/install_logs/q1-teardown-20260905-153843.log）。剩下：抓三支片＋跑拆解報告（whisper 模型檔可能需另下載）。三支連結已找回（Owner msg 4681「對手拆解器」，09-04 13:26）：1. https://youtube.com/shorts/jaRAsqjCdFk 2. https://youtu.be/CY6QP4ofwx4 3. https://youtube.com/shorts/eZq1s-E2ugc 。主視窗裝工具（建議 yt-dlp＋whisper＋場景切分）後直接跑這三支的拆解報告；另有 msg 4725 Higgsfield reel 與 msg 4671 reel（接 A8）可排後 |
| Q2 | 把 win-01 複利系統卡推上 agent-hq bus | 132e098（draft 4696 積壓） | 無 | DONE | 2026-09-04 18:55 bot 窗完成：卡已上 bus inbox/win-01/win01-compounding-system-20260904.json（bus commit 71ddca1）。bot 窗本輪實測可用 Write+git 直推 bus，本項不再限主視窗。 |
| Q3 | 裝富途 OpenD（全程 Demo） | 看板 T6（draft 4696 積壓） | Owner 同意安裝 → 已同意（msg 4746＋4756 再確認） | DONE(裝機)→待 Owner 登入 | 2026-09-05 15:45 bot 窗裝完：/Applications/Futu_OpenD.app（GUI 版 10.10.7008，官方連結下載）＋futu-api SDK 10.8.6808（pip3 --user）＋版本戳 ~/.futu_skill_version（log: data/install_logs/q3-opend-20260905-153843.log）。剩 Owner 開 app GUI 登入（帳密只在 GUI 輸入），登入後任一窗跑 a0_sys_probe.sh port 11111 驗閘道＋SIMULATE 行情快照即全案 DONE。舊證據：investment-os worktree archive/scripts/test_futu_api.py（5 月）曾連過 11111。 |
| Q4 | 木地板案例草稿搬進 WP 建草稿（bus drafts/win-01/wp-case-woodfloor-opening-20260903.md → WP draft，供 Owner 後台檢查；SEO 標題/meta/快速索引照稿內註解設定；不發布） | Owner msg 4740＋4750 催辦 | WP 權限（主視窗）；先解 A0 審稿 R1（台南宣稱 vs UNVERIFIED 矛盾，見 bus drafts/win-01/wp-case-woodfloor-opening-20260903.review-a0.md） | QUEUED-P0 | Owner 已三度過問（4740/4750/4760）。**改文字先行**：不等 Q5 轉檔，主視窗開工第一件事先建純文字 WP 草稿（含 SEO 標題/meta/快速導覽，圖位留占位），Owner 即可後台檢查；webp 好了再補圖。R1 台南驗證若 Owner 未回，先照修法 b 中性措辭建稿。**2026-09-05 msg 4794 追加**：建稿前先照修稿鐵律刪虛構段（bus 卡 win01-seo-voice-revision-20260905：看圖說故事、不替客人定義、品牌口徑六條、Owner 審閱版純文字） |

| Q5 | A4 照片轉檔首發（木地板 17 張） | Owner msg 4751 | 無 | DONE | 2026-09-05 15:37 bot 窗自跑完成：兩夾去重 17 張、17 成功 0 失敗，輸出 handbook data/photo_convert/maplab-tainan-opening-tea/（NN.webp＋manifest.csv 一比一，同名覆蓋缺陷根治）。註：原派卡的 Drive 根路徑錯（lb99104/MAPLAB_ASSETS），實際=pagewu1010/我的雲端硬碟/2026maplab外燴紀錄，腳本已修。Q4 上圖直接照 manifest 上傳；alt 依 msg 4780 走自動閘，不等人眼 |

## 紀錄

- 2026-09-04 建檔（主視窗 session）。三筆佇列皆為登記，尚未開跑。
- 2026-09-04 19:10 Owner 拍板（msg 4738）：Antigravity 納入無額度值班輪替（skills/quota-duty-rotation.md v1.0），bus 已開 inbox/outbox/antigravity 通道；本階段完成，Fable5 接回主導。
