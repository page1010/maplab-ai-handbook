# Skill:Firecrawl 網頁抓取(爬站→乾淨 markdown)

- 建立:2026-08-25|作者:A0/Fable5|狀態:**待接鑰匙(未整合)**|Owner 指示:msg 3992
- 用途:把任意網站爬成乾淨 markdown/結構化 JSON,給 SEO 研究、競品分析、資料入庫用;比自己寫 scraper 穩(處理 JS 渲染、反爬、分頁)。

## 現況(2026-08-25 盤點)

- repo 內沒有任何 Firecrawl 整合;這是新能力,不是撿回舊的。
- 接入方式二選一:①官方 MCP server(agent 直接用 scrape/crawl/search 工具)②REST API(scripts 排程用)。免費層約 500 credits,夠先試。
- 鑰匙管理照 OpenRouter 模式:金鑰存 repo 外 env 檔(~/.maplab/ 下,chmod 600),不進對話、不進 git;由 Owner 註冊帳號後貼入(涉及註冊帳號=Owner 的事,涉及付費升級=Owner 的錢)。

## 邊界(先寫死)

- 只爬公開網頁(L2);不碰需登入的頁面、不碰客戶後台。
- robots/ToS 尊重:大量爬站前先看目標站條款;競品站只做人類也能看的公開頁研究。
- 爬回來的內容入庫要標來源 URL + 抓取日期(配合查價 SOP 同一原則:數字必標日期)。

## 啟用步驟(額度回來後執行,或派 Codex)

1. Owner 或有權限窗口註冊 firecrawl.dev 取 API key → 存 ~/.maplab/firecrawl.env。
2. 把官方 MCP server 加進 Claude Code user scope(照 claude-design 同款 user-scope 共用模式)。
3. 第一個試用案例:SEO 線競品頁抓取(配 docs/seo-keyword-map.md),產出回 git 驗收。
