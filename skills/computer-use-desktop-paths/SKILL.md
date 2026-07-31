---
name: computer-use-desktop-paths
description: 用截圖辨識定位、可靠處理 Mac 桌面操作卡點的 SOP —— 特別是授權彈窗（cowork 資料夾授權、request_access 應用授權）與 UI 導覽找不到目標。觸發：任何 computer-use 桌面任務卡在「授權彈窗動不了 / UI 找不到按鈕 / request_access 等不到回應 / Finder/Google Drive/TextEdit 設定畫面」。核心原則：先截圖辨識再動作、動作前後各截一張、能用 Desktop Commander 就別走 GUI 彈窗。
status: DRAFT (2026-07-31 建立，待實戰截圖補圖庫後轉正)
---

# Computer-Use 桌面路徑辨識 SOP（截圖辨識為核心）

> 觸發條件：任何需要 `computer-use` 操作原生桌面的任務，尤其**卡在授權彈窗或 UI 找不到目標**時，開工前先讀這份。
> 姊妹技能：`skills/computer-operation/SKILL.md`（操作前檢核清單）、`skills/mac-local-tool-routing/SKILL.md`（工具路由階梯）。本篇不重複那兩份，專攻「**看畫面認畫面 → 走對路徑**」。

## 為什麼有這份（根因，不只補症狀）

協作任務反覆卡在同一批畫面：cowork 資料夾授權彈窗、`request_access` 等不到回應、Google Drive/Finder 桌面設定找不到入口。每次都重新摸索＝重工。根因是「**這些畫面的辨識特徵與正確路徑沒有被固化**」。這份把它變成可照做的辨識表，呼應 `docs/OPERATING_CULTURE.md` 原則 5（最短路徑）與原則 6（解決根因）。

---

## 一、通用流程：眼見為憑，動作前後各截一張

固定五步，不要跳步、不要盲點：

1. **先截圖看現況**：`screenshot`。看不清小字/小按鈕就 `zoom(region)` 放大辨識（zoom 只用來看，點擊座標仍以全螢幕截圖為準）。
2. **辨識目標**：從截圖找出目標按鈕/彈窗/欄位的**視覺特徵**（文字、圖示、顏色、位置），對照本篇「畫面辨識表」。辨識不到就往下滾或換視窗，不要亂猜座標。
3. **確認前景 App 對**：menu bar 顯示的是不是目標 App？疊窗時先 `open_application` 帶對的 App 到前景再操作。
4. **動作**：`left_click` / `type`（長文字改 `write_clipboard`＋`cmd+v`）。小按鈕先對準中心。
5. **再截圖確認結果**：每個「送出/確認/儲存/允許」後一定 `screenshot`，比對畫面是否如預期變化。沒截圖＝不算完成。

> 鐵律：**沒有截圖證據，就不宣稱「已完成／已點到」**（呼應 pitfalls「只說點了沒截圖」）。

---

## 二、畫面辨識表（每格：長怎樣／關鍵字／該點哪／fallback）

### 2.1 cowork 資料夾授權彈窗（最常卡）

- **畫面長怎樣**：Claude 桌面 App 內彈出的模態視窗，要你選一個資料夾授權給 Claude 讀寫。通常有資料夾選擇器 + 「允許／Allow」「取消／Cancel」按鈕。
- **辨識關鍵字**：「允許存取／Allow access」「選擇資料夾／Choose folder」「Grant access」，標題常含資料夾名或 `cowork`。
- **正確路徑（治本）**：**能用 Desktop Commander 就別走這個 GUI 彈窗**。要讀/寫本機 repo（例如 `~/maplab-ai-handbook`）時，直接用 `mcp__Desktop_Commander__read_file / write_file / list_directory / start_process`，不需要開整個家目錄授權。GUI 資料夾授權只在「Claude 必須透過 cowork 檔案卡呈現檔案給 Owner」時才需要。
- **真的要授權時該點哪**：截圖確認彈窗聚焦 → 點「允許/Allow」；若要換資料夾先點資料夾選擇器選對路徑再允許。
- **fallback（卡住時）**：① 先問自己這步能不能改用 Desktop Commander 免掉彈窗；② 不行就 `request_cowork_directory` 帶明確 `path`（例如 `~/Downloads`）觸發乾淨的授權流程，而不是硬點一個半開的彈窗；③ 仍卡就回報 Owner「請你按一下允許」，附截圖，不要空等。

### 2.2 request_access / 應用授權（tiered app）

- **畫面長怎樣**：`request_access` 呼叫後，Owner 螢幕跳出一個列出所有請求 App 的核准對話框，Owner 整組允許或整組拒絕。
- **關鍵字**：對話框列出 App 名稱 + 你填的 `reason`。
- **Tier 限制與對策（記死）**：
  - **瀏覽器**（Safari/Chrome/Arc…）= tier **read**：截圖看得到，但**不能點/不能打字**。導頁/點擊/填表改用 `mcp__claude-in-chrome__*`。
  - **終端機/IDE**（Terminal/iTerm/VS Code/JetBrains…）= tier **click**：可點（例如按 Run），但**不能打字/不能右鍵/不能組合鍵**。要跑指令改用 Bash 或 `mcp__Desktop_Commander__start_process`。
  - **其他原生 App** = tier **full**：滑鼠鍵盤全可用。
- **正確路徑**：開工前一次把需要的 App 都填進 `request_access`（少來回）；中途發現要多一個 App 再補呼叫，已授權的會保留。
- **fallback（等不到回應／逾時）**：`request_access` 會等 Owner 核准，逾時代表 Owner 沒按。**不要反覆重打空等**。改判斷這步能不能用非 GUI 路徑完成（Desktop Commander 讀檔、Chrome MCP 操作網頁、connector/MCP 直接打 API）；真的非桌面 GUI 不可，才回報 Owner「請核准這個授權」附上要做什麼。用 `list_granted_applications` 確認目前到底授權了哪些，再決定下一步。

### 2.3 Google Drive 桌面 App 設定（新增帳號／離線／位置）

- **畫面長怎樣**：Google Drive 是 **menu bar App**（右上選單列的三角/雲朵圖示），不在 Dock。點圖示先出小面板（顯示同步狀態），面板右上角**齒輪 ⚙︎** 才是設定入口。
- **關鍵字**：menu bar 的 Drive 圖示；面板內「偏好設定/Preferences」「設定/Settings」；設定視窗分頁「我的 Mac 電腦/我的 Google 雲端硬碟」「帳戶/Account」。
- **該點哪**：
  - 新增帳號：齒輪 ⚙︎ →「偏好設定」→ 左下/帳戶區「新增其他帳戶/Add account」→ 走瀏覽器 OAuth（**登入交給 Owner，不要代打帳密**）。
  - 離線/串流：偏好設定 →「Google 雲端硬碟」分頁 → 選「串流檔案/Stream」或「鏡像檔案/Mirror」。
  - 資料夾位置：鏡像模式下同分頁可改本機資料夾位置。
- **辨識陷阱**：Google Drive 沒被 `request_access` 授權時，menu bar 圖示與其下拉面板在 computer-use 截圖裡會被**合成層過濾掉（看不到）**。先確認它有在授權清單（`list_granted_applications`）；索引抓不到「Google Drive」名稱時，請 Owner 開 App 後在輸入框打 `@Google Drive` 直接指定。
- **fallback**：只是要讀/放檔到 Drive 內容 → 優先用 Google Drive connector（`mcp__…__read_file_content / create_file`）或 `gdrive-to-wordpress-upload-guide.md` 的路徑，別去戳桌面 App 設定。桌面 App 設定只在「改同步行為」時才需要 GUI。

### 2.4 Finder（選檔／選資料夾對話框、路徑跳轉）

- **畫面長怎樣**：Finder 視窗或系統「開啟/儲存/選擇資料夾」對話框，左側 Sidebar（喜好項目/iCloud/位置），上方路徑列，右側檔案清單。
- **關鍵字**：「打開/Open」「儲存/Save」「選擇/Choose」按鈕；標題列資料夾名。
- **該點哪／最短路徑**：與其一層層點資料夾，**按 `cmd+shift+g` 叫出「前往資料夾」輸入框**，貼上絕對路徑（`write_clipboard`＋`cmd+v`）→ Return，直接跳到目標，最省步。
- **fallback**：純檔案搬移/改名/查檔 → 用 `mcp__Desktop_Commander__move_file / list_directory / get_file_info`，不要開 Finder 手點。Finder GUI 只在「App 的檔案選擇對話框逼你用 GUI」時才走。

### 2.5 TextEdit / 文字編輯（純文字 vs 富文字陷阱）

- **畫面長怎樣**：白底文件視窗。富文字模式有格式工具列；純文字模式沒有、字體等寬。
- **關鍵字**：選單「格式/Format」→「製作純文字/Make Plain Text」或「製作 RTF/Make Rich Text」。
- **該點哪**：要存 `.md`/`.txt`/程式碼 → 先「格式 → 製作純文字」，否則會被存成 `.rtf` 帶格式碼污染。
- **fallback**：要產生/編輯本機文字檔，**優先 `mcp__Desktop_Commander__write_file / edit_block`**，完全免開 TextEdit，也沒有 RTF 陷阱。TextEdit GUI 只在 Owner 要看/當場改時才用。

---

## 三、反模式（別這樣做）

1. **Desktop Commander 能解卻硬走 GUI 彈窗**：讀寫本機 repo/檔案、跑指令，優先 Desktop Commander / Bash / connector；GUI 授權彈窗是最後手段，不是預設。
2. **沒截圖就盲點座標**：憑記憶或猜測點按鈕 → 點到背景視窗/錯按鈕。永遠先 `screenshot` 辨識再點。
3. **授權彈窗卡住還反覆重打**：`request_access` / `request_cowork_directory` 逾時＝Owner 沒按，重打只會再等一輪空轉。改路徑或回報 Owner 按，附截圖。
4. **在 tier 受限的 App 上硬打字/點擊**：瀏覽器上用 computer-use 點擊、終端機裡用 computer-use 打字，一定失敗。先分辨 tier 再選對工具。
5. **長文字逐字 type**：中途失焦會截斷。>20 字一律 `write_clipboard`＋`cmd+v`。
6. **只更新一個工具沒收口**：完成後要留可接續狀態（見姊妹技能與 handoff 規範）。

## 四、授權卡住的 Fallback 階梯（照順序試）

1. **改工具免掉彈窗**：這步能不能改用 Desktop Commander（本機檔案/指令）、Chrome MCP（網頁）、connector/MCP（帳號動作）完成？能就走，跳過 GUI。
2. **乾淨重觸發**：真的需要授權，就用帶明確參數的正規呼叫（`request_cowork_directory` 帶 `path`、`request_access` 帶完整 App 清單＋清楚 reason），不要對半開彈窗硬點。
3. **確認現況**：`list_granted_applications` 看實際授權了什麼，避免在沒授權的前提下空轉。
4. **回報 Owner 按一下**：附截圖、說明要做什麼、按哪顆。這是最後手段，但比無限等待好——呼應 AGENT_RULES SECTION 21「卡在等 input 等於做白工」。

## 五、圖庫（辨識範本）

代表性截圖存在同層 `images/`，命名 `畫面代號-情境-YYYYMMDD.png`（如 `cowork-folder-auth-popup-20260731.png`）。取用時對照本篇 2.x 的「畫面長怎樣／關鍵字」定位。缺圖時先照文字特徵辨識，補到圖後回填此節與 `images/README.md`。

> 建立時（2026-07-31）因 `request_access` 授權未獲回應，未能截到即時範本——這本身就是本篇 §2.2 / §四 描述的「授權等不到回應」實況。`images/` 已備好結構與拍攝清單，待下次桌面任務順手補齊。
