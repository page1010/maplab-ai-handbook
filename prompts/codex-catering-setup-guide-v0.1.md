# Codex Prompt — Catering Setup Guide v0.1

日期：2026-09-19  
母任務：GitHub Issue #26  
目標：讓全新的 Codex session 不靠舊對話即可直接接手。

## 第一輪：工程骨架

```text
你是 page1010/maplab-ai-handbook 的 Codex engineering executor。

先做 startup / preflight，不要直接寫碼。

必讀：
- CURRENT_STATUS.md
- AGENT_RULES.md
- AGENT_STARTUP_PROTOCOL.md
- skills/superpowers-guide.md
- skills/codex-offload-guide.md
- skills/catering-setup-guide.md
- projects/catering-setup-guide-v0.1.md
- skills/photo-asset-retrieval-guide.md
- skills/a4-fact-first-asset-matching.md
- skills/a4-photo-asset-skills.md
- skills/maplab-visual-spec.md
- GitHub Issue #26

先 audit：
1. repo 內是否已有 schema / renderer / fixture / HTML preview 可重用
2. A4 asset matching 哪些介面可讀
3. A5 master data 哪些資料只能 read-only 取用
4. 不重造已有能力

這一輪只做 bounded slice：
- input/output contracts
- deterministic layout engine
- SVG/HTML schematic renderer
- synthetic fixtures
- tests

硬規則：
- LLM 不得直接覆蓋 hard constraints
- 缺尺寸 / 器皿 / 庫存 → MISSING_INPUT
- 不寫 Google Sheets / Drive
- 不改 production runtime
- 不新增 scheduler
- 不接客戶資料
- 不生成假實拍食物案例
- concept visual 必須標 CONCEPT_PREVIEW
- 相同 input 必須得到相同 output
- 至少 12 tests
- 不自動 merge

預期檔案可以調整，但責任邊界要維持：
- catering_setup/contracts.py
- catering_setup/layout_engine.py
- catering_setup/render_svg.py
- fixtures/catering_setup/
- tests/test_catering_setup_*.py
- docs/catering_setup/README.md

fixture 至少包含：
- corporate 60p indoor 2 tables
- birthday 30p indoor 1 table
- opening 80p semi-outdoor 2 tables
- wedding 120p outdoor 3 tables

tests 至少覆蓋：
- deterministic repeatability
- missing table dimensions
- overcrowding detection
- guest/refill bottleneck
- beverage zone separation
- edge collision
- height layer rule
- outdoor wind flag
- semi-outdoor heat/sun flag
- flower obstruction
- one-table case
- three-table case

交付前一定要留下 receipt：
- files changed
- tests run + result
- sample command
- sample output
- assumptions
- unresolved data gaps
- next_bounded_action
- branch
- commit SHA

不要說「完成」除非 tests 與 sample output 有證據。
```

## 第二輪：Image-input advisor

只有第一輪通過後才做。

```text
延續 Issue #26，這一輪只做 image-input advisor。

目標：
讓 Codex 用 -i/--image 讀 1–3 張真實 reference 照，
抽取可驗證的 setup features，不能自由幻想場地尺寸。

允許抽取：
- 桌面相對比例
- zone 數量
- 低/中/高層次
- 視覺密度
- 食物與裝飾相對位置
- 可能的取餐瓶頸
- 可能的視線阻擋
- 是否有獨立飲品區
- 是否存在明顯 refill access

每個 feature 必須：
- evidence
- confidence
- observed / inferred 分離
- 無法判斷就 UNKNOWN

禁止：
- 從照片猜真實尺寸
- 猜器皿庫存
- 猜食材
- 猜客戶個資
- 把 reference photo 自動寫回任何系統

輸出結構化 JSON，必要時用 --output-schema。
建立 synthetic / known-reference tests。
最後留下 receipt，不自動 merge。
```

## 第三輪：One-page field guide + post-event loop

```text
延續 Issue #26，這一輪只做現場使用與回饋閉環。

輸入：
- setup-plan.json
- human edits
- optional reference features

輸出：
1. setup-guide.md
2. printable / mobile-friendly setup-guide.html
3. post-event-review template
4. rule-candidate schema

一頁式 guide 必須在現場 1–2 分鐘內看懂：
- 先放什麼
- 每區放什麼
- 高度
- 補餐入口
- 客人流向
- 風險
- 完成後 QA 角度

post-event 不得自動改正式規則。
rule candidate 必須有 source_event_id / evidence / confidence / human approval state。

補 tests，留 receipt，不自動 merge。
```

## 額度耗用策略

### 額度 > 50%
做工程：
- preflight audit
- contracts
- deterministic engine
- renderer
- tests
- fixtures

### 額度 20–50%
做可重用整合：
- image-input advisor
- reference matcher adapter
- field guide generator

### 額度 < 20%
只收斂：
- edge-case tests
- README
- receipts
- next_bounded_action
- 不開新大模組

## 不值得燒 Codex 額度
- IG 文案
- 一般翻譯
- 單次 prompt 美化
- 純視覺發想
- 生成擬真食物圖
- 手工資料整理

把稀缺工程額度留給：可測試、可複用、可版本化的東西。
