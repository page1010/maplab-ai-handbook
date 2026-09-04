# video-autopilot-kit 研究紀錄：把用得上的接給 A8（2026-09-04）

- 來源：Owner msg 4671 轉的 IG reel（@ai_note_101，講台灣創作者 Hao 開源自動剪片流程被罵割韭菜的事件）
- 專案本體：https://github.com/Hao0321/video-autopilot-kit （作者 Threads @hao0321_studio）
- 授權：MIT（免費、可商用、可改）。作者官網無付費商品，開源動機單純。
- 狀態：**只做了線上研究，尚未下載任何程式碼**（等 Owner 回「接」才 clone）。

## 為什麼跟 A8 合拍

技術棧完全同款：Python 3.9+、ffmpeg/ffprobe、Pillow/numpy/opencv——就是 `tools/ai_workbook/a8_senior_fitness_mvp.py` 現在用的東西。跨平台（含 macOS），**不需要裝 CapCut**（CapCut JSON 只是它的中介格式之一，我們用不到）。設計哲學也對頻：不內建別人的數據、閾值要用自己的 3–5 支參考影片校準、私有設定 gitignore 不外流——跟我們「決定性渲染＋不編造」的紅線一致。

## 接得上的四塊（優先序）

| 優先 | 模組 | 功能 | 接到 A8 哪裡 |
|---|---|---|---|
| P1 | `src/media_delivery_qa.py` | 檢查閃爍、音畫同步漂移、字幕對齊、**音量位準** | 接在渲染完成後、Owner 驗收前。music_volume=0.11 聽不到那次，這種檢查器會自動抓到 |
| P2 | `src/longform_maker/shorts_gate.py` | 直式短片九條結構規則，分 YT Shorts / IG 兩套 | 樂齡短片發布前守門（現在 5 支短片＋合輯都是直式 1080×1920） |
| P3 | `src/teardown.py` | 拆解對手短片：剪輯頻率、節奏分布、每句話對應剪點比、響度 | Hermes 音樂健身房教材＋校準工具；決定性腳本、跑起來不燒 LLM 額度，符合「Hermes 免費鏈」原則 |
| P4 | `knowledge/` 知識庫 | shorts-mastery-2026、留存型腳本寫法、AI 內容合規 53 條（附出處） | 進 Hermes gym SOP／gold set 教材 |

加分項（之後再說）：`src/channel_tracker.py` 做 D2/D7/D28 成效快照——頻道真的開起來、有影片上線後才有用。

## 不接的

- CapCut JSON／Editkin 剪輯執行層：我們是 Pillow 逐幀＋ffmpeg 直渲，不經任何剪輯軟體，接了是繞遠路。
- 訪談節目整條線（interview_autopilot／interview_gate／templates）：A8 沒有訪談內容。
- 它的 script_gate 語言校驗：調校對象是它自己的受眾語言，我們的樂齡口白標準要自己定（可參考方法，不搬閾值）。

## 等 Owner 回「接」之後的執行順序

1. clone 到本機（研究區，不進生產路徑），跑 `examples/` 自帶測試確認在這台 Mac 跑得動。
2. 先接 P1：用 media_delivery_qa 跑現有樂齡 MVP 全部渲染輸出，產一份檢查報告給 Owner 看（音量 0.22 夠不夠，讓檢查器說話）。
3. P2 短片守門員跑 5 支短片，把它的九條規則跟我們現有安全審核清單合併成 A8 發布前 checklist。
4. P3/P4 打包進 Hermes gym 任務卡（教材＋工具），配合週四額度重置前的燒額度窗口。

## Owner 指定的拆解參考集（msg 4681，2026-09-04 13:26）

Owner 傳 3 支片給對手拆解器＝視同放行「接」。校準集（工具建議 3–5 支）：

| # | 連結 | 頻道 | 內容 | 對應我方 |
|---|---|---|---|---|
| 1 | youtube.com/shorts/jaRAsqjCdFk | Yoga with Sanjeev | 半鴿式開髖教學 short | 單動作短片 |
| 2 | youtu.be/CY6QP4ofwx4 | Mady Morrison | 30 分鐘全身溫和伸展長片 | 107s 合輯／未來長片 |
| 3 | youtube.com/shorts/eZq1s-E2ugc | FIT CHINESE | 懶人 5 分鐘無跳躍全身操 short | 低衝擊居家短片 |

執行順序（已告知 Owner，預設先短後長）：主視窗 clone 工具包 → 下載 3 支影片（Owner 傳連結＝同意抓這三支分析用）→ 先拆 1、3 出第一份報告 → 長片 2 排後。報告欄位：剪輯頻率／節奏分布／字幕密度／響度＋與我方樂齡影片的差距清單。

## 附註

reel 本身的故事（開源被罵割韭菜、「終於懂台灣為什麼沒有人想開源」）＝我們用它時記得：出處標清楚、回報 issue 友善、如果改出有用的東西考慮回饋 upstream——這也是企業文化的事。
