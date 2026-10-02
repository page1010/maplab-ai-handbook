# Hermes 守門設計可移植一頁(給 win-01 hermes_tg_bridge 沿用)

> 出處:Owner 6595(2026-10-02)「給他權限看,可以拿相片與資料,但是不動程式碼或是只寫自己用的」。
> 血證:A6H-20261002-133830 — Owner 貼進來的 Codex 計畫書因文中出現「發布/修改…排程」字樣被整則 fail closed,文件連讀都不准讀。
> macmini a6 實作:bot_a6/hermes_task_executor.py(commit 9162b11),214 條測試全綠。

## 核心原則:紅線放在「能力層」與「檔案層」,不放在「字面層」

關鍵字掃全文=把「說到」當「要做」。hermes 收到的長文多半是 Owner 貼進來給他讀的材料,
不是指令。真正的安全保證是:executor 根本沒有發布/下單/刪除這些動作可配(能力層),
以及檔案路徑解析時硬擋紅線目錄(檔案層)。字面掃描只留給「短指令句式」。

## classify 判定順序(照抄即可)

1. 明確白名單動作(狀態查詢、自我測試等固定 argv)→ 直接配對。
2. 讀寫三能力的句式(見下)→ 配對。
3. **長度閘:>600 字 → 一律走 CHAT**(讓模型讀完回話,不做任何工具動作)。
   理由:長文=貼入的文件;文件提到敏感詞 ≠ 下令做敏感事。
4. 短句命中「排程/服務變更」句式(例:修改.{0,20}排程)→ 硬拒 fail closed。
   這類是真指令句式,保留字面層。
5. 短句命中其他敏感詞(發布/下單/刪除…)→ 走 CHAT(executor 無對應能力,回話無害)。
6. 其餘白名單別名、報價收件 → 照舊。
7. 都不中 → CHAT。

## 三個「看/寫」能力(參數與紅線)

| 能力 | 句式 | 行為 | 上限 |
|---|---|---|---|
| repo-read | 看檔/讀檔/read-file <repo 相對路徑> | 只讀文字副檔名(.md .txt .json .csv .py .sh .html .log…) | 8,000 字/次,截斷標明 |
| asset-list | 素材清單/看素材/相片清單 [目錄] | os.walk 列 metadata(檔名/大小/mtime),**像素永不送模型** | 120 筆/次 |
| hermes-note | 寫筆記 <內容> | 只寫 workbook/hermes-notes/<task_id>.md,收據式格式(標題+建立+來源+sha256) | 筆記夾外零寫入 |

句式正則注意:冒號後不強制空白 — `(?:\s*[:：]\s*|\s+)`,否則「寫筆記:內容」會漏接
(macmini 實測踩過:漏接後落進報價收件匣)。

## 檔案層紅線(_safe_repo_path,一字不差照搬)

- 路徑先 resolve(吃掉 symlink 與 ../),再驗 relative_to(REPO_ROOT),出界即拒。
- 目錄黑名單:.git / telegram-photos(兒童照) / mcp-keys / cookies / venv / __pycache__。
- 檔名黑名單:路徑任一段含 .env|token|secret|cookie|credential|.key$|.pem$ 即拒。
- 非文字副檔名(圖片等)拒讀,指回 asset-list(只給 metadata)。
- win-01 對應調整:REPO_ROOT 換成該機工作根;兒童照對應目錄名要查當機實況再填。

## 不變式(改任何一條都要 Owner 裁)

1. hermes 無寫程式碼能力 — 不是「擋住」,是「沒有這個動作」。
2. 相片像素不進任何雲端模型(Owner 常設紅線,與 5743 客資解封不同層)。
3. 金鑰/憑證類檔案拒讀,連檔名帶字樣的都擋。
4. 排程/服務變更短指令硬拒,不因 6595 鬆綁。
5. 每次動作留收據(receipt.json / 筆記含 request_sha256),Hermes 自報不可信,配第二方驗證。

## 驗收探針(bridge 上線前至少跑這八發)

1. 貼一篇 >600 字含「發布/修改排程」字樣的計畫書 → 應走 CHAT 讀後回話,不得 fail closed。
2. 看檔 docs/OPERATING_CULTURE.md → completed,截斷標示正確。
3. 看檔 bot/.env → rejected(金鑰字樣)。
4. 看檔 ../<repo 外路徑> → rejected(出界)。
5. 看檔 <兒童照目錄>/x.jpg → rejected(紅線目錄)。
6. 素材清單 <相片目錄> → completed,只有 metadata。
7. 寫筆記:<含「報價」字樣的內容> → hermes-note(不得被報價收件匣搶走)。
8. 修改排程 → rejected fail closed。
