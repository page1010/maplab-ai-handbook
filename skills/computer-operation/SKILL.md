# 電腦操作技能書（Computer Operation）

> 這份是給需要操作電腦（滑鼠、鍵盤、GUI）的 agent 的召喚必讀。
> 觸發條件：任何需要用 `computer-use` / `Claude in Chrome` MCP、操作原生 App、
> 截圖驗證、表單輸入的任務，開工前先讀這份清單。

---

## 可檢核清單（每次操作前逐項確認）

- [ ] **打字前確認輸入框已聚焦**：截圖看游標/邊框閃爍，不盲打；懷疑時先 `left_click` 輸入框再 `type`。
- [ ] **長文字用剪貼簿貼上**：超過 20 字用 `write_clipboard` → `key("cmd+v")`，不逐字 `type`，避免中途失焦遺失。
- [ ] **操作前先關掉擋路的選單/下拉**：`key("Escape")` 或點空白處收選單，再執行目標操作。
- [ ] **關鍵動作後截圖驗證**：每個「送出 / 確認 / 儲存」後 `screenshot`，不要假設成功。
- [ ] **精準座標點擊**：小目標（按鈕 < 40px）先 `zoom`/放大再點；對準中心，不要點邊緣。
- [ ] **一次只帶一個 App 到前景**：`open_application` 帶目標 App，確認 menu bar 顯示正確 App 再操作；疊窗時先截圖確認 frontmost。
- [ ] **受限 Tier 要換工具**：
  - 瀏覽器（Safari/Chrome/Arc…）→ `mcp__Claude_in_Chrome__*`，不用 `computer-use` 點擊/打字。
  - 終端機/IDE（Terminal/iTerm/VS Code/JetBrains…）→ Bash tool，不用 `computer-use` 打字。
  - 其他原生 App → `computer-use` 全功能可用。

---

## Mac mini 快速操作參考

| 動作 | 方法 |
|------|------|
| 帶 App 到前景 | `open_application("App 名稱")` |
| 複製文字到剪貼簿 | `write_clipboard("內容")` |
| 貼上 | `key("cmd+v")` |
| 截圖驗證 | `screenshot()` |
| 確認游標位置 | `cursor_position()` |
| 全螢幕滾動 | `scroll(x, y, direction, amount)` |
| 右鍵選單 | `right_click(x, y)`（受限 Tier 無效） |

---

## 常見踩坑（實戰教訓）

1. **輸入框未聚焦就打字** → 字打到背景或觸發快捷鍵。修正：先點輸入框截圖確認聚焦再打。
2. **選單還開著就點下一層** → 觸發錯誤動作。修正：Escape 收選單後再點。
3. **長文字 type 到一半失焦** → 文字截斷或插入別處。修正：剪貼簿貼上。
4. **多視窗疊加點到背景 App** → 操作到錯誤視窗。修正：`open_application` 確認前景後截圖再操作。
5. **只說「點了」沒截圖** → 無法判斷是否真的成功。修正：送出後一定截圖。
