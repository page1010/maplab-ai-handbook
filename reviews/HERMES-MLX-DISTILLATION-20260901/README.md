# Hermes MLX installation receipt

狀態：`INFRASTRUCTURE_SMOKE_PASS / QUALITY_NOT_PROVEN / LIVE_ROUTE_DISABLED`

2026-09-01 已在 Apple M4／24GB 上完成隔離式 MLX-LM QLoRA 安裝與真實權重更新煙霧測試：

- Python 3.12.13、MLX 0.32.2、MLX-LM 0.31.3。
- Qwen3-4B-Instruct-2507 4-bit 公開基模固定 revision 與 SHA，放外接碟。
- Runtime、dataset、adapter、receipt 私有根目錄為 `0700`；adapter 檔為 `0600`。
- 8 train／2 validation／1 test 的純合成資料，在 deny-network sandbox 跑 3 steps。
- Adapter 可重新載入，與 base 對同 prompt 產生不同輸出；peak memory 2.697GB。
- Adapter 只把回覆縮短，仍漏掉「先承接單一窗口價值」，所以不能宣稱品質改善。
- 沒有使用 LINE 原文、沒有第三方外送、沒有 customer send、沒有接 live Hermes route。

正式下一步不是增加推論次數，而是 20 案具名真人 rubric labels、scorer 校正、DLP，再建立 30–50 組 Owner 親改 gold 做第一個可證偽 QLoRA。
