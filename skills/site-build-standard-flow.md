# 架站/改版標準流程 SOP v1.0（Owner 5130 指示建立,2026-09-11）

**為什麼有這份**:首頁改版兩次產出流程不一致——第一次提案有自選圖與對標,
第二次(2026-09-11 離線草稿)直接抄現站素材,結果「完全是本來的風格」且底圖切到字。
以後任何頁面(新站、改版、案例頁)都走同一條線,不再看窗口心情。

## 標準流程(每頁必走)

0. **續接檢查閘(任何 session/視窗動草稿前)**:先讀該任務資料夾的 TASK_BRIEF.md;
   不存在=先從歷史(telegram log 原話+裁定)建檔再動工,**不得只憑 session 摘要或衍生
   規劃檔開工**——摘要只帶結論不帶來源,是 9/11 重做一份的根因。
   **執法=決定論腳本,不靠 Owner 開口問(Owner 5144)**:
   - 動工前:bash scripts/task_gate.sh check <任務夾> → 列 R# 需求條目+落已讀收據
     (收據綁 TASK_BRIEF 當前 sha256,brief 一改舊收據即失效)。
   - 交付前:bash scripts/task_gate.sh verify <任務夾> → 驗收據版本+COVERAGE.md
     逐條對照(每個 R# 寫怎麼滿足+內含 brief 全 hash);任一缺=GATE FAIL 不得交付。
   - 防作弊:hash 只有跑 check 才拿得到;空跑產不出逐條對照;.gate 收據與 COVERAGE.md
     入 git 留痕,對照與成品不符=事後可稽核的造假證據。TASK_BRIEF 需求必用 R1. R2. 格式。
   **原話入檔規則**:Owner 的偏好/裁定在收到的當回合就抄進正典檔(含 msg id 來源),
   不只留在 telegram log;散檔=下個 session 讀不到。
1. **對標庫先讀**:handoff/benchmark-owner-marks-20260907.md(Owner 逐號標記的
   原始紀錄:喜歡哪些站、為什麼、出局原因)——並**實際打開 #2/#15/#21/#23 四站**
   對齊視覺層(大圖比例/留白/字級/排版密度),再讀 landing-revamp-plan-v2 §〇骨架
   +§二B 手機優先。結構對了不等於風格對了(5132 教訓);新頁風格對標記紀錄,不是對現站。
2. **企業色與字體**:棕 #8B5E3C/深棕 #5A3A1A/金褐 #C4A265(現站全域色)+LINE 綠 #06C755
   只給 CTA。背景/卡片/分區優先用企業色鋪,不靠圖片撐底。
3. **圖片來源優先序**:
   ① 348 真圖批次原檔(放行後)
   ② Canva 原檔副本匯出(無字版;主視窗 GUI 棒次,bot 不碰帳號)
   ③ 企業色設計版位(Canva 新做,無字)
   ④ 線上站現有素材=**只能過渡**,且**自帶文字的成品海報禁止裁切使用**
   (cover 硬裁必切字=Owner 5130 主訴;過渡期一律 contain+企業色底)。
4. **文案紅線**:不虛構見證/數字/場次(絕不編數);每區內文 ≤60 字;禁「對號入座」;
   TWD 不寫 NTD;定位語/副標題用 Owner 已圈版本(現行:P2+「台南外燴 派對統籌 企業茶會」)。
5. **離線 draft 落地**:handbook handoff/<案名>-YYYYMMDD/index.html,單檔可離線開。
6. **機器 QA 閘(playwright,借檔通道可跑)**:390px+1280px 全頁截圖;
   PASS 條件=無橫向捲動、無截斷、字級 ≥16px、CTA 三處(首屏/終末/懸浮)。
7. **交付**:截圖上 Drive(anyone-reader)發可點連結給 Owner——沒連結不算交付。
8. **Owner 圈選後**才進 WP draft;未圈選不發布;a0 不登 Canva/WP 帳號。

## 產出物命名

- 草稿:handoff/<案名>-YYYYMMDD/index.html(+canva-image-list.md 若有 GUI 棒次)
- 驗收圖:data/rwd-check/<案名>_draft390_YYYYMMDD.png / _draft1280_
- Drive 檔名:<案名>草稿_手機390px全頁_YYYYMMDD.png

## 版本紀錄

- v1.0(2026-09-11):首版,收斂自首頁改版兩輪教訓(Owner 5130)。
- v1.1(2026-09-11):步驟①改指 Owner 原始標記紀錄 benchmark-owner-marks-20260907.md,
  並要求實開四站對齊視覺層(Owner 5132:基準是「喜歡哪些、為什麼」的討論,非 30 條清單)。
- v1.2(2026-09-11):新增步驟〇續接檢查閘+原話入檔規則(Owner 5141 檢討:
  需求散檔+摘要只帶結論→跨 session 沒讀到需求又做一份;根治=任務級 TASK_BRIEF 必讀必建)。
- v1.3(2026-09-11):檢查閘改決定論執法 scripts/task_gate.sh(Owner 5144:自己問+防作弊,
  不靠 Owner 抽查);五案自測全過(check OK/無對照 FAIL/全對照 PASS/空條目 FAIL/改版舊收據 FAIL)。
