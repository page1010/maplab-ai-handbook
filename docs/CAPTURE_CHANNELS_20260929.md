# 取像通道架構圖(2026-09-29,依 Owner msg 6224「把路徑和架構釐清寫清楚」)

核心一句話:**macOS 螢幕錄製權限是「按程式」發的,不是按帳號或按 Claude 版本。**
一年前開的權限沒有消失,它掛在「chrome 側邊欄 computer use」那條通道的程式名下;
今天報「截圖失敗」的是另一條通道(Telegram bot 線),是另一個程式身分,從來沒拿過這張票。
兩件事同時為真:側邊欄一直看得到 ✅、bot 線照不到 ❌。差別在程式身分,不在模型新舊。

## 四條通道對照表

| # | 通道 | 程式身分(實查路徑) | 取像方式 | 需要的權限 | 現況 |
|---|---|---|---|---|---|
| ① | chrome 側邊欄子 session(computer use) | Owner 桌面那份 Chrome:`/Users/pagemacmini/Desktop/Google Chrome.app`(PID 422 實查在跑),Claude 擴充在它裡面 | Chrome 內部 API 截自己的分頁 | Chrome 自己的分頁不需 macOS 螢幕錄製;整個螢幕才需要,一年前已開 | ✅ 有眼睛。但它是獨立 session,不共用 bot 線的記憶、檔案與 Telegram 通道 |
| ② | Telegram bot 線(現在回話的這條) | launchd `com.maplab.telegrambot`(PID 78732)→ `/bin/bash run_daemon.sh` → `bot/venv/bin/python3 bot.py` → `claude` 指令列 | 呼叫系統 `screencapture` 抓整個螢幕 | 需要「螢幕錄製」清單裡勾 Python(bot 的程式) | ❌ 從未取得。9/29 07:4x 實測原文:`could not create image from display` |
| ③ | Owner Chrome AppleScript(bot 線借道) | 同①的 Chrome,但由②的 Python 發 Apple 事件 | 讀分頁標題 ✅ / 讀頁面文字 ❌ | 頁面文字需 Chrome 選單「檢視>開發人員>允許 Apple 事件的 JavaScript」 | 標題可讀(6210 輪即靠此驗登入);文字被關閉,實測原文:「透過 AppleScript 執行 JavaScript 的功能已關閉」 |
| ④ | openclaw 那份 Chrome | `/Applications/Google Chrome.app`(實查在跑),CDP 埠 18800 | CDP 截自己頁面 | 不需 macOS 權限(截自己) | ✅ 能截,但登的是 agent FB 帳號,看不到 Owner 分頁 |

## 標註(6066 紀律)

- **實查**:①②④ 兩份 Chrome 與 bot 行程路徑(pgrep/launchctl);②③ 的兩條失敗原文(9/29 07:4x 重測)。
- **推論**:一年前那張票確切開給哪個程式(側邊欄擴充所在的 Chrome、或桌面版 Claude app,其一)。TCC 資料庫需完整磁碟權限才能讀,無法直接查證;但「②的 Python 沒票」由錯誤原文直接成立,不依賴此推論。

## 解法(任選其一即可)

- **甲(給②開眼)**:系統設定 > 隱私權與安全性 > 螢幕錄製:清單裡勾 Python;沒有就按「+」加入 `/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python3`。勾完 bot 線直接能截整個螢幕。
- **乙(給③開文字)**:Owner Chrome 選單列 檢視 > 開發人員 > 允許 Apple 事件的 JavaScript 打勾。bot 線即可逐字讀頁面內容,多數指路場景不需截圖。
- **丙(用①現成的眼)**:直接在側邊欄子 session 下指令看畫面與點按;bot 線負責 API、payload 與收尾。①與②是兩個 session,結果要用檔案或 Telegram 對接。

## 邊界(不變)

截圖只存 `~/.maplab/screenshots/`,不進版控、不進 Telegram;分頁網址一律砍 `?` 之後;owner-open 只開頁不代填帳密。
