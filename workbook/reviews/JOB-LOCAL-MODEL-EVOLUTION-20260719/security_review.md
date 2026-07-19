# Security Review — JOB-LOCAL-MODEL-EVOLUTION-20260719

## 紅線自查（LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md §三 + Owner 訊息「安全紅線」）

| 紅線 | 本輪狀態 |
|---|---|
| 不讀或輸出 secret（.env/password/token/cookie/OTP/API key value） | ✅ 未讀取任何 secret；`quota_sentinel.py` 只檢查指令是否存在，不讀取憑證內容 |
| 不真實下單 | ✅ Investment curriculum 全部合成 ticker，未接觸真實 Investment OS SQLite 或 broker |
| 不直接發布 SEO 內容或修改 Ads | ✅ 未呼叫任何 WordPress/Ads/GSC 寫入工具 |
| 不自動回覆客戶或送正式報價 | ✅ 未涉及 A5/A6/A7 runtime |
| 不讓模型自行升格 | ✅ `models/registry.json.candidates` 維持空陣列，無任何 promoted 條目 |
| 不因額度將重置就製造低價值資料 | ✅ 本輪未產生任何未經 eval 覆蓋的 synthetic bulk output；curricula 停在 24 題（20-50 範圍下段），未為了用量硬灌到 50 |
| 不將未經核准或權利不明的教師輸出加入訓練集 | ✅ `datasets/` 目錄為空；eval cases 全部標記 `usage_rights: approved`（因為是本輪自行合成，非第三方輸出） |
| 不直接 merge main | ✅ 本輪只在 `claude/local-model-evolution-orchestrator-puvj7d` 分支工作，額外 merge 進來的 `codex/system-directory-index-v0-1-20260718` 是 fast-forward 讀取冷啟動文件用，該分支本身尚未 merge 進 main（PR #20 仍是 open draft） |
| 客戶姓名/電話/LINE 原文/地址/家庭資料/金融帳戶秘密不得送外部模型 | ✅ 未讀取任何 Drive 客戶資料，兩個 curriculum 全部合成 |

## 新確認的治理發現（非紅線違反，是提前攔截的風險）

`docs/governance/model-tier-policy.md` §0 禁止按量 API key 這條規則，若本輪
沒有主動核對，`config/providers.yml` 很可能會照搬原始 prompt 假設「official
API」為次優先來源（仍會使用），而非「預設關閉」。已在 `providers.yml` /
`quota_source_matrix.md` 明確標記 `blocked_by_policy`，防止未來某一輪誤用
Owner 未核准的按量 API。

## 未觸碰事項（確認範圍未擴大）

未修改任何 production runtime、launchd/plist、GAS/clasp 專案、WordPress、
Ads、Telegram/LINE bot、Investment OS 的 SQLite 或 shioaji 相關程式碼。
Investment OS repo 僅唯讀 clone 用於讀冷啟動文件，未寫入任何 commit。
