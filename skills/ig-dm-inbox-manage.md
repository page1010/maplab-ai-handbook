# IG/FB 私訊收件匣管理（統整問題→Owner 一次回→照表貼回）

狀態：【未驗證草案】依 Owner 規矩（msg 4967），實跑成功一次前不得稱為已驗證 skill。
建立：2026-09-08（Owner msg 4980/4981 指示方向）。執行者：a0/Fable5 或接派工的 agent。
姊妹篇：skills/ig-vendor-inquiry-send.md（已驗證的發送流程，本 skill 沿用其瀏覽器操作與踩雷）。

## 目的
官方帳號發出詢價後，廠商回覆會散在收件匣。本 skill 把回覆裡的「問題」集中成一張表，
Owner 一次回覆全部，agent 再照表逐家貼回。讀取廠商回覆僅限抄錄問題，不代答、不聊天。

## 前置條件（缺一即停）
1. Owner 已在 Chrome 登入官方帳號（IG：instagram.com；FB 粉專：messenger.com 或粉專收件匣）。
2. Claude-in-Chrome 擴充已連上本 session（mcp__claude-in-chrome__* 可用）。
3. 集中表已建立（現行：data/vendor-db/vendor-replies-qa-20260908.md）。

## 流程
A. 抄錄階段
1. 開 https://www.instagram.com/direct/inbox/ ，截圖確認登入態＝官方帳號。
2. 逐一點開名單內廠商的對話，截圖辨識回覆內容。
3. 問題原文抄進集中表；沒回的記「尚未回覆」；只致意無問題的記「無問題，僅致意」。
4. 抄完 commit 集中表，Telegram 發 Owner：已回X家、各家問題編號列表。
B. 回填階段（等 Owner 一則訊息回覆全部）
5. 把 Owner 回覆按編號填進集中表的「Owner 回覆」欄，不改寫語意。
C. 貼回階段
6. 逐家開對話，貼上該家對應的 Owner 回覆，發送前截圖核對對象與內容，送出後記「貼回狀態＝已貼」。
7. 全部貼完 commit＋回報。之後任何後續對話一律歸 Owner。

## 鐵則
- 只抄問題、只貼 Owner 核可的回覆；agent 不代答、不追問、不臨場改稿。
- 一家一則；貼回後廠商再回覆，不讀不回，歸 Owner。
- 不透露預算報價；不碰帳號設定/追蹤/按讚/留言；不輸入任何帳密/驗證碼，登入態掉了就停。
- 廠商聯絡內容留在本 repo 集中表，不外送第三方服務。

## FB 粉專私訊
同一套流程理論上適用（messenger.com 網頁版介面），但未實測過，首次執行時比照 IG 逐步截圖驗證。

## 裁決（Owner msg 4986，2026-09-08）
走免費自家流程，不接外部服務。外部方案只吸收做法，不引入依賴。

## 從外部方案吸收的做法（Chatwoot／Meta API 研究後留下的）
- 對話狀態機（學 Chatwoot 的 open/resolved）：集中表每家標一個狀態
  「尚未回覆／待Owner答／待貼回／已貼回／已結案」，一眼看出卡在誰手上。
- 類別標籤（學 Chatwoot 的 labels）：廠商編號本身就是標籤（攝/花/主/擴），
  貼回與統計都按類別分組進行。
- 24小時回覆窗（學 Meta 官方政策精神）：廠商回覆後盡量在 24 小時內完成
  抄錄→Owner答→貼回一輪；抄錄完成當下就提醒 Owner，不積壓。
- 節流（學 Meta 200則/小時上限精神）：逐家慢速操作、每家之間留間隔，
  行為貼近人工，不做批量連發。
- 罐頭回覆庫（學 Chatwoot 的 canned responses）：Owner 重複用到的回覆句
  沉淀到 data/vendor-db/ 下的模板檔，下次同類問題直接引用 Owner 已核可版本。

## 外部方案備考（2026-09-08 查證，僅存檔參考）
- 量大時的正規解：Chatwoot（開源自架，IG/FB 走 Meta 官方 API 進統一收件匣，含 REST API/webhook 可接 agent）github.com/chatwoot/chatwoot
- 其底層：Meta Instagram Messaging API，需專業帳號綁 FB 粉專＋App Review（數週）、200則/小時上限。
- 非官方庫（instagrapi 等）動官方帳號有封號風險，否決不用。
