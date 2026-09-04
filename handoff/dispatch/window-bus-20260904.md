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
| Q1 | 裝開源拆解工具＋抓 Owner 給的三支參考片＋跑第一份拆解報告 | 看板 T9（draft 4696 積壓） | Owner 一句派工（涉及安裝） | QUEUED | — |
| Q2 | 把 win-01 複利系統卡推上 agent-hq bus | 132e098（draft 4696 積壓） | 無 | DONE | 2026-09-04 18:55 bot 窗完成：卡已上 bus inbox/win-01/win01-compounding-system-20260904.json（bus commit 71ddca1）。bot 窗本輪實測可用 Write+git 直推 bus，本項不再限主視窗。 |
| Q3 | 裝富途 OpenD（全程 Demo） | 看板 T6（draft 4696 積壓） | Owner 同意安裝 | QUEUED | — |
| Q4 | 木地板案例草稿搬進 WP 建草稿（bus drafts/win-01/wp-case-woodfloor-opening-20260903.md → WP draft，供 Owner 後台檢查；SEO 標題/meta/快速索引照稿內註解設定；不發布） | Owner msg 4740 | WP 權限（主視窗） | QUEUED | 注意:上圖前先修照片索引重複計數+同名覆蓋兩缺陷（outbox 回執 defect 1、2） |

## 紀錄

- 2026-09-04 建檔（主視窗 session）。三筆佇列皆為登記，尚未開跑。
- 2026-09-04 19:10 Owner 拍板（msg 4738）：Antigravity 納入無額度值班輪替（skills/quota-duty-rotation.md v1.0），bus 已開 inbox/outbox/antigravity 通道；本階段完成，Fable5 接回主導。
