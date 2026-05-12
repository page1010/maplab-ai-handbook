# A4 影像資產整理部 — 核心技能書

版本：v1.0 | 建立：2026-03-26 | 維護：A1 Claude Code

> 80/20 原則：只寫最影響素材可用性的 2 個技能 + 最容易卡住的點
> 注意：A4 已有豐富技能書（photo-pipeline-toolkit-guide 等），此文件聚焦新增的實用技能

---

## 技能 1：品牌素材風格統一

**場景**：任何角色（A2/A3/A6）要用圖片時，確保符合 MAPLAB 品牌規範

**MAPLAB 品牌圖片規範**：
- ✅ 使用：食物特寫、場景佈置、無人場景、品牌 Logo 牆
- ❌ 禁止：人臉（含兒童）、非 MAPLAB logo、酒類廣告圖、模糊/低解析度
- 命名格式：`maplab-{場景關鍵字}-{內容描述}.png`
- Alt text：`MAPLAB Kitchen {場景}｜{具體描述含長尾關鍵字}`
- 圖片尺寸建議：
  - WordPress 精選圖：1200×630px
  - IG 貼文：1080×1080px
  - FB 貼文：1200×630px
  - 提案簡報：1920×1080px

**做法**：
1. 從 Google Drive 相簿或已分類素材庫選圖
2. 檢查是否符合上述規範
3. 必要時裁切/調整尺寸
4. SEO 命名 + alt text

**容易卡住的點**：
- Google Drive 相簿量大（6 萬+），用 Gemini 分類結果（C/T/D）篩選
- 已分類結果：C=4,593（可用）、T=254（待確認）、D=55,737（不用）
- 上傳到 WordPress 用 Clipboard API 跨 Tab 法（見 gdrive-to-wordpress-upload-guide.md）

**必讀**：skills/photo-pipeline-toolkit-guide.md、skills/a4-fact-first-asset-matching.md、skills/gdrive-to-wordpress-upload-guide.md

---

## 技能 1.5：事實鏈找圖

**場景**：A2/A3/A6 要用真實外燴案例照片，尤其是要對應報價單、SEO 頁、廣告素材或案例段落。

**規則**：
1. 先用 `a4-fact-first-asset-matching.md` 建立日期、報價單、TimeTree、ASSET_LOG、Drive source file 的證據鏈。
2. 圖片辨識只能當最後 QA，不可當第一索引鍵。
3. 任何 public draft 不得帶價格、電話、地址、內部日期或本機路徑。

**CLI**：
```bash
python3 tools/ai_workbook/cli.py asset-case-match --year 2025 --limit 120
```

---

## 技能 2：數位菜單卡製作

**場景**：客戶詢問菜單 → 產出漂亮的數位菜單卡

**做法**：
1. 從 A5 的 Items 表拉品項名稱 + 描述
2. 從素材庫選對應餐點照片
3. 依活動類型組合：
   - 週歲派對菜單（甜點比重高）
   - 婚禮外燴菜單（全餐式）
   - 企業茶會菜單（輕食為主）
   - 餐盒菜單（個人份）
4. 排版成可分享的圖片或 PDF
5. 自動標註：份量依人數調整（50 人 vs 200 人的量不同）

**容易卡住的點**：
- 品項名稱要用客戶看得懂的中文，不是內部編碼
- 照片要跟實際出餐一致，不要用網路素材
- 價格不放在菜單卡上（菜單卡是引起興趣用的，報價單另外給）

**依賴**：A5 品項資料 + 素材庫照片

---

### Gemini Flash 整合（2026-04-18 新增）

A4 pipeline 擴充，同一次 API call 產出多個結果：

| 輸出 | 用途 | 目的地 |
|------|------|--------|
| 分類 category/keywords | 照片管理 | ASSET_LOG |
| alt_text | SEO | WordPress 圖片 alt 欄位 |
| caption | 讀者描述 | WordPress 圖片下方 |
| quality_score (1-5) | Slide 選圖 | ASSET_LOG → A5 報價 |
| crop_suggestion | 排版 | Slide 裁切方向 |
| story_caption | InnerFlowLab | 文章配圖描述 |

優先順序：
1. alt text 生成（最快見效，改幾行 Colab 就能跑）
2. 品質評分（Slide 母版選圖自動化）
3. 旅遊照片分組 + caption（等 InnerFlowLab 啟動）

---

## 不需要做的

- ❌ 食譜卡（外燴不對外公開食譜）
- ❌ AI 自動生成食物照片（用真實照片，假圖會失去信任）
- ❌ 影片處理（交給 A8）
