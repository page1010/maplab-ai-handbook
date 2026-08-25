# A6 Hermes Telegram 啟動收據

日期：2026-08-25 12:27（Asia/Taipei）
狀態：`live_roundtrip_pass`

## 已完成

- `scripts/a6_hermes_activate.sh` 以 fail-closed 模式執行成功；舊 A6 bot polling 已退場。
- launchd `com.maplab.a6bot` 正在運行 `bot_a6/hermes_telegram_gateway.py`。
- Telegram Web 在 `@maplab_a6_bot` 送出 `/start`，讀回一則 `【hermes】值班中` final。
- 回覆明確區分 Hermes 與 Fable5，未宣稱自己是 Claude／Fable5。

## 安全邊界

- 本收據不含 token、Owner 原文、gateway log 或免費 provider 的私密 payload。
- A6 只處理允許的公開／低敏感工作；客戶素材、持股、券商、密鑰與個資不得送免費端點。
- 本輪只證明入口與基本身份回覆可用，未證明任意投資研究品質。

## 下一步

用一題公開資訊做 bounded QA：檢查來源、事實／推論分離、研究判斷標籤與答不了時的升級路徑；不改模型鏈、不增加權限。
