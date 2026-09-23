# T-BUS-UNPICKED-CARDS-20260923 — 有卡沒撿:antigravity 七張零回執、pillar1205 掛 13 天

來源:Owner msg 6050(2026-09-23T21:56:13)「有卡沒撿？」
開卡者:mac-a0 / Claude
狀態:open

## 派工六欄(gate 可解析的一行式,細節見下方各節)

- **結果**: 產出一份 agent-bus 投遞通道診斷 handoff/reports/bus_channel_audit_20260923.md,明確判定 antigravity 的收件匣到回執匣這條路是「程式壞了」「席位沒在跑」還是「從來沒接上」三者之一並附證據;同時讓 win-01 的 pillar1205-line-canonical-fix-20260910 從 assigned 走到 done 或 blocked,不准繼續留在 assigned。
- **指標**: antigravity 7 張卡每一張都有一行判定與證據路徑;診斷後至少有一張 antigravity 卡產生第一份 outbox 回執檔,或寫明無法產生回執的實體原因(席位不存在/程式不存在/授權不在本端);pillar1205 的 state 欄位不再是 assigned。
- **期限**: 2026-09-24 當日內完成診斷段;pillar1205 改態不設死線但每日回報一次進度,連續三日無進展即改判 blocked 並寫明擋點。
- **權限**: 可讀寫 agent-bus 的 inbox/outbox/drafts 與 handoff/reports;可讀四個 repo 的腳本與 log;不得改寫他人已寫入的 outbox 回執內容,只能另寫 reconcile 欄位;不碰任何帳密、授權碼、cookie。
- **回報點**: 回報診斷檔路徑、七張卡的判定分佈、pillar1205 的新狀態。三項齊備記 done;診斷完成但無法產生回執記 partial 並寫明實體原因;查不到 antigravity 席位對應的執行程式記 blocked。
- **動作可逆性**: 全部可逆。只做讀取、產檔、以及在自己開的卡上寫狀態欄位;不刪卡、不刪回執、不改他人回執。

## 1. 事實(2026-09-23 實查)

- inbox/antigravity 有 7 張卡,最舊 2026-09-06,最新 2026-09-23(專輯全量上傳)。
- outbox/antigravity 目錄裡只有 README.md,零回執,從開站到今天沒有過任何一份。
- drafts/ 底下沒有 antigravity 的目錄。
- inbox/invest 5 張卡,outbox/invest 1 份回執,席位心跳停 33 天。
- inbox/win-01 3 張卡,outbox/win-01 約 60 份回執——唯一真的在動的席位。
- win-01 的 pillar1205-line-canonical-fix-20260910 state 欄自 2026-09-10 起是 assigned,至今 13 天。

## 2. 為什麼這張卡比「催一下」重要

回執是零,不是少。少代表撿得慢,零代表這條路可能從來沒有人走過。
派卡的那端一直以為卡發出去了,收卡的那端可能根本沒有程式在讀。
在證明通道會動之前,往 antigravity 再派任何一張卡都是把事情丟進沒有底的地方。

## 3. 判定分類(三選一,必須選一個並附證據)

1. 通道沒接:找不到任何程式會去讀 inbox/antigravity —— 那 7 張卡等於沒派過,要嘛接通,要嘛全部改派到會動的席位。
2. 席位沒跑:程式存在但機器或排程沒在跑 —— 附最後一次執行時間。
3. 程式壞了:有跑但寫不出回執 —— 附錯誤訊息。

## 4. 不做什麼

不刪那 7 張卡。卡是痕跡,判定寫在卡上或診斷檔裡,過期的封存不刪除。
