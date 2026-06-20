# Lottie Motion JSON 技能書 — text-to-lottie / loading / icon 動效

版本：v1.0 | 建立：2026-06-14 | 維護：A2/A3/A8 + A0

---

## 何時使用

看到以下需求時使用本技能：

- text-to-lottie、Lottie JSON、loading 動畫、icon 動效、splash 短動畫。
- Owner 貼 AI 新工具截圖，問要不要擴充地端模型能力。
- A2/A3/A8 需要網站、IG、簡報、Telegram bot 的小型品牌動效。
- 地端模型要輸出結構化動畫 JSON，但不能把 raw model output 直接交付。

---

## 判斷

目前 repo 沒有已成形的 Lottie 技能。IG 截圖裡的 `DiffusionStudio text-to-lottie` 與 `Mac-1` 來源未核實前，不當成可直接安裝的 truth source。

但 Lottie 本身值得納入 MAPLAB 地端能力，原因：

- Lottie 是 JSON-based vector animation，適合 loading、icon、splash、網站微互動。
- 產物是文字檔，Codex / Claude / 地端模型都能生成草稿。
- 風險可用 validator 降低：不是模型說可以就交付，而是 JSON 結構、尺寸、幀率、layer、duration 都要過檢查。

不建議此階段直接訓練/換模型。先做：

1. Codex/Claude 產 Lottie JSON 草稿。
2. 地端模型做 prompt variation 或品牌語意草稿。
3. `tools/lottie_validate.py` 驗證。
4. 用瀏覽器或 LottieFiles 預覽。
5. 通過後再交給 A2/A3/A8 使用。

---

## 產出規格

### loading / icon 動效預設

- 尺寸：`512x512` 或 `1024x1024`。
- 幀率：`30` 或 `60`。
- 長度：1.2-3 秒，能 loop。
- 背景：透明，避免全版 raster image。
- 圖層：優先 shape layer，不依賴外部圖片。
- 色彩：先讀 `skills/maplab-visual-spec.md`，使用 MAPLAB 色票。

### 必備欄位

Lottie JSON 至少要有：

```json
{
  "v": "5.7.1",
  "fr": 30,
  "ip": 0,
  "op": 90,
  "w": 512,
  "h": 512,
  "layers": []
}
```

Shape layer 至少檢查：

- `ty: 4`
- `ks` transform 存在
- `shapes` 非空
- keyframes 的 `t` 不超出 `ip/op`

---

## 工作流程

### Step 1：定義短 prompt

先把需求壓成 4 行：

```text
用途：網站 loading / icon hover / proposal splash
品牌：MAPLAB 外燴，溫暖、乾淨、精緻
視覺：奶油白背景透明、橄欖綠線條、金棕點綴
動作：餐盤線條旋入，最後形成 M 字樣，2 秒 loop
```

### Step 2：產 JSON

Codex/Claude 可以直接產；地端模型只做草稿，不直接交付。

要求模型：

- 只輸出 JSON，不輸出 Thinking。
- 不使用 base64 圖片。
- 不依賴遠端 asset。
- 動畫層數少於 20。
- `op - ip <= 180`，避免太長。

### Step 3：驗證

```bash
rtk bot/venv/bin/python tools/lottie_validate.py path/to/animation.json
```

若 `ok=false`，先修 JSON，不要交付。

### Step 4：預覽

可選：

- 放到本機 HTML，用 `lottie-web` 或 LottieFiles web preview 檢視。
- 若沒有 renderer，至少用 validator + JSON readback + 截圖審查。

### Step 5：交付

交付至少包含：

- `.json` 檔案路徑。
- 用途與尺寸。
- 驗證結果。
- 若未預覽，明確說「尚未 render preview」。

---

## 地端模型擴充建議

先不新增「Mac-1 類」macOS 原生工具模型到正式路由，原因：

- 目前未找到可信原始來源。
- A6 已有 Telegram / Codex / Ollama / OpenClaw / osascript / Chrome 各自路由。
- macOS 原生工具自動化涉及權限、日曆、郵件、檔案系統，必須先做 sandbox 與 action confirmation。

可以擴充的是「Lottie JSON 生成能力」：

- 新增 A8/Lottie prompt profile。
- 建立 `workbook/reviews/LOTTIE-*` review bundle。
- 把地端模型定位成草稿生成器，validator/preview 才是完成標準。

---

## 禁止

- 不把 IG 截圖文案當作已安裝/已驗證工具。
- 不把地端模型 raw JSON 直接放進 WordPress/Canva/簡報。
- 不使用外部圖片 URL 或 base64 影像塞進 Lottie。
- 不產出沒有 validator 結果的動畫檔。
