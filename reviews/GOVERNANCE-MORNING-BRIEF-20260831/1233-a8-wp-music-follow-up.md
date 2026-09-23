# MAPLAB A8／WordPress 現況跟進

- 時間：2026-08-31 12:33 Asia/Taipei
- 稽核範圍：2026-08-27 之後的 A8 主題曲、邦妮兔案例、WordPress 真實案例產線與平台草稿線路
- 角色：MAPLAB 內容產線治理／狀態稽核
- 總結：**AMBER — 有一個已公開案例成果與已核准歌詞，但核准後的 SSOT 同步、實際生成、平台草稿與後續 2–10 案均未形成可驗證閉環。**

## What｜實際發生了什麼

### 1. 已驗證成果

- 邦妮兔托嬰畢業典禮 WordPress 案例頁仍公開可讀，含主文、圖片、圖片替代文字與頁尾 CTA：
  - https://www.maplabkitchen.com/tainan-daycare-graduation-catering/
- 真實案例 gate 與 registry 仍可執行：
  - `python3 -m unittest -v tests.test_maplab_case_first_gate`：7/7 通過。
  - intake gate：`ok=true`。
- 2026-08-29 Owner 已核准主題曲歌詞；Task Card 頂部已記錄核准版本。
- 2026-08-30 Owner 已授權用邦妮兔案例測長／短版、平台 draft/private 上傳線路、平台文案與 SOP；公開發佈仍需另外核准。

### 2. 尚未完成的產品閉環

- 主題曲 Google Doc 與本機 `lyrics.txt` 仍是舊詞，尚未同步 8/29 核准版本。
- v2A／v2B prompt 仍保留舊規格（75–90 秒、偏亮女聲描述），尚未吸收 Owner 的「女聲太尖」回饋與新版 62–70 秒結構。
- prompt registry 仍為 `planned`；沒有 provider song ID、生成時間、音檔 hash 或權利收據。
- Owner 表示已聽到線外新版，但 repo 沒有該版本的 durable receipt；因此不能把它算成正式產出。
- YouTube 長版／Shorts、TikTok、Pinterest 尚無實際草稿上傳 ID、可點擊連結或平台 receipt。
- 真實案例 2–10 自 8/27 建立 gate 後沒有新增可驗證內容成果。

### 3. Clea 下一案 gate

`A8CASE-20260718-CLEA-OPENING` 的 WP gate 正確 fail-closed，目前缺五項：

1. 公開具名或匿名策略。
2. 可公開原話或等價引述。
3. ASSET_LOG。
4. 圖片視覺 QA。
5. 正式站 SEO collision check。

這表示系統沒有用模板猜資料，但也表示 Clea 尚未進入文章生產。

### 4. 治理與路由漂移

- repo 缺少規範要求的 `AGENT_CORE.md`；本輪以 `AGENT_RULES.md` 與 `AGENT_STARTUP_PROTOCOL.md` 補讀，但 canonical cold-start 檔仍缺。
- `CURRENT_STATUS.md` 沒有唯一 Active Task 指標；audit 得到 `active_task=null`、`next_bounded_action=""`、`resume_prompt_present=false`。
- `CURRENT_STATUS.md` 任務表只列 T-A8-001，未列正在承載主題曲真相的 T-A8-002。
- T-A8-002 內部同時存在「歌詞已核准待生成」與較舊的 `OWNER_LYRICS_GATE`／舊 Resume Prompt，會讓下一個 session 讀到互相衝突的指令。
- T-A8-001 上方舊 blocker 與下方後來的 draft/private 測試授權尚未收斂。
- Task Card 有分工紀錄，但目前沒有可驗證的 A8 active worker／automation 正在執行，因此不能稱為正在跑。

### 5. 畫面中的 Google 文件

- 目前瀏覽器文件 `1Xkx-2M1...` 是「裏府城｜Owner 最終需求藍圖 V1」，不是 MAPLAB A8 主題曲審稿文件，也不是這輪新增成果。
- A8 既有審稿文件仍是：
  - https://docs.google.com/document/d/1VicisMW7dVmwkr9wjL-l3hxlwJn3SLGH6-RcHtQHVKI/edit?tab=t.0

## So What｜為什麼重要

- 現在真正的瓶頸不是缺更多規劃，而是 **核准後沒有被同步成唯一可執行版本**。若直接再生成，會再次花額度在舊詞、舊長度或過尖女聲上。
- 邦妮兔 WP 頁證明案例內容可以上線；但一個公開頁不等於 10 案產線已跑起來。
- 平台測試已取得有限授權，但沒有上傳 receipt，故目前只有「可做」，沒有「已完成」。
- Clea 的五個缺口是正確的 fail-closed，不應用 AI 自動補造；要先從 Drive 真實案例資料補證據。

## Now What｜唯一優先下一步

**先做 T-A8-002 的 SSOT 收斂與兩版音源生成閉環，不同時展開第二篇 WP 或平台公開發佈。**

Bounded action：

1. 唯讀盤點 Suno 帳號／library，找出 Owner 已聽過的線外新版並補 provider ID、時間、權利與音檔 hash；找不到就明記 missing，不猜。
2. 將 8/29 核准歌詞同步到 A8 Google Doc、`lyrics.txt` 與 prompt registry。
3. 將 v2A／v2B 改為暖聲、較低音域、避免尖亮女聲；保留同詞，只測速度／律動差異。
4. 驗證 diff、hash 與 registry 後，只生成兩個候選並留下 receipt；交 Owner 聽選。

完成這一個閉環後，才進入邦妮兔長／短片與 YouTube／TikTok／Pinterest draft/private 上傳驗證。公開發佈仍維持 Owner gate。

## 本輪驗證證據

- commits：`11b4c1d`、`18c152d`、`3953ce5`、`f109dd0`、`52a3989`、`7e441bb`。
- tests：case-first gate 7/7 passed；intake gate `ok=true`。
- expected fail-closed：Clea WP gate 5 項缺證據。
- owner-facing runtime：邦妮兔 WordPress 公開頁可讀。
- Google Doc readback：A8 文件仍是舊版歌詞與舊生成規格。
- platform runtime：未找到任何 draft/private upload ID 或 receipt。

## 決策需求

本輪不需要 Owner 重複核准歌詞；8/29 核准已足夠。下一個真正需要 Owner 的節點是兩個新音源候選完成後的聽選。
