# Colab Resilience Guide — 防死機技能包
版本：v1.0 | 建立：2026-03-17 | 維護者：A4 Pipeline Agent

> 適用場景：Colab 長時間執行任務（解壓縮、批次處理、大量 API 呼叫）。
> 核心目標：任何時間點中斷都能從上次完成的地方繼續，不重做已完成的工作。

---

## 快速對照表

| 問題 | 解法 |
|------|------|
| Colab 斷線，不知道跑到哪 | 每個批次寫 checkpoint 檔 → 重連後讀取繼續 |
| Cell 跑了 3 小時沒輸出，不知道是否還活著 | 每 N 筆印一次進度 + 寫 timestamp |
| unzip 重跑會重複解壓 | 加 -n flag（skip existing）|
| API 呼叫卡住不回應 | 每個呼叫加 timeout + retry with backoff |
| Colab 12hr 上限到了，任務未完成 | 分批設計 + checkpoint → 下次 session 繼續 |
| 不確定 Cell 是否完成 | 最後一行印 === DONE === + timestamp |

---

## 規則 1 — Checkpoint 必須寫入 Drive

所有長時間任務，每完成一個單位就把進度寫入 Drive（不是 /content/，那是暫存）。

原則：
- Checkpoint 檔放在 /content/drive/MyDrive/MAPLAB/ 下
- 格式：JSON，包含 last_completed、total、timestamp
- 每 100 筆（或每個資料夾）寫一次，不要每筆寫（太慢）
- 重連後第一件事：讀 checkpoint，從 last_completed + 1 繼續

```bash
%%bash
CHECKPOINT=/content/drive/MyDrive/MAPLAB/checkpoint.json

# 寫入 checkpoint（bash）
python3 -c "
import json
from datetime import datetime, timezone
data = {'last_completed': '$FOLDER_NAME', 'count': $COUNT, 'ts': datetime.now(timezone.utc).isoformat()}
open('$CHECKPOINT', 'w').write(json.dumps(data))
print('[CHECKPOINT] saved:', data)
"

# 讀取 checkpoint
if [ -f $CHECKPOINT ]; then
  python3 -c "import json; d=json.load(open('$CHECKPOINT')); print('Resuming from:', d['last_completed'])"
fi
```

---

## 規則 2 — 未回應時間限制（Timeout）

所有 API 呼叫都必須加 timeout。沉默超過上限 = 強制失敗，記錄 + 繼續下一筆，不讓整個 batch 卡死。

```bash
%%bash
python3 << 'PYEOF'
import signal, time

class CallTimeoutError(Exception): pass

def _handler(signum, frame): raise CallTimeoutError('timed out')

def call_with_timeout(func, seconds=30):
    signal.signal(signal.SIGALRM, _handler)
    signal.alarm(seconds)
    try:
        result = func()
        signal.alarm(0)
        return result
    except CallTimeoutError:
        signal.alarm(0)
        raise

def retry_with_backoff(func, max_retries=3, base_delay=2, timeout_sec=30):
    for attempt in range(max_retries):
        try:
            return call_with_timeout(func, seconds=timeout_sec)
        except (CallTimeoutError, Exception) as e:
            print(f'[WARN] attempt {attempt+1}/{max_retries}: {e}')
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f'[RETRY] waiting {delay}s')
                time.sleep(delay)
    raise Exception(f'Failed after {max_retries} retries')

print('[OK] timeout + retry helpers loaded')
PYEOF
```

---

## 規則 3 — 進度輸出（防假死）

長時間沒輸出 = 無法確認是否活著。規定每個資料夾/每 100 筆印一行進度 + timestamp。

```bash
%%bash
COUNT=0
START=$(date +%s)

for FOLDER in /content/drive/MyDrive/MAPLAB/photos/Takeout/Google相簿/*/; do
  NAME=$(basename "$FOLDER")
  FILES=$(find "$FOLDER" -type f | wc -l)
  COUNT=$((COUNT + FILES))
  ELAPSED=$(( $(date +%s) - START ))
  echo "[$(date +%H:%M:%S)] $NAME: $FILES files | total=$COUNT | ${ELAPSED}s"
  # ... 實際處理邏輯 ...
done

echo "=== DONE === total=$COUNT elapsed=$(( $(date +%s) - START ))s"
```

---

## 規則 4 — unzip 防重複（-n flag）

所有 unzip 必須加 -n flag（skip existing files）。重跑或斷線重連後繼續都不會重複解壓。

```bash
# 正確：有 -n
unzip -n -q file.zip -d /output/

# 錯誤：沒有 -n，重跑會覆蓋
# unzip -q file.zip -d /output/
```

---

## 規則 5 — Colab Session 開頭 SOP

```
Cell 1: drive.mount('/content/drive')   # ValueError: mount failed = 正常，繼續
Cell 2: ls /content/drive/MyDrive/MAPLAB/   # 確認掛載
Cell 3: cat checkpoint.json              # 讀取上次進度
Cell 4: 執行主程式（有 -n / checkpoint 自動跳過已完成）
```

---

## 規則 6 — 斷線重連 SOP

1. 點「重新連線」
2. 跑 Cell 1（mount）
3. 讀 checkpoint.json → 確認 last_completed
4. 重跑處理 Cell → -n / checkpoint 自動跳過
5. 確認輸出底部有 === DONE === 才算完成

---

## Colab 時間上限參考

| 情況 | 上限 |
|----|------|
| 免費 idle timeout | ~90 分鐘 |
| 免費最大 session | ~12 小時 |
| Pro idle timeout | ~3 小時 |
| Pro 最大 session | ~24 小時 |

對策：把大任務切成 <2 小時批次，每批寫 checkpoint，跨 session 繼續。

---

## 本專案採用狀況

| Phase | 防死機措施 |
|-------|-----------|
| Phase 2 (unzip) | -n flag + 每個 ZIP 印完成訊息 ✅ |
| Phase 3+ (Drive collect / vision) | 需加 checkpoint.json + retry_with_backoff |

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-17 | 初始版本：checkpoint + timeout + retry + 進度輸出 | A4 Pipeline Agent |