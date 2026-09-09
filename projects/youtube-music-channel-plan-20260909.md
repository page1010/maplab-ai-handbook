# MAPLAB 音樂頻道企劃 v1.1（Suno + hermes 音樂風格資料庫 → YouTube 全自動日更）
建立：2026-09-09 | 開案：Owner msg 5045 | 維護：A0(Fable5) | 執行線：A8(音樂影音專屬)+hermes
狀態：v1.1——Owner msg 5048 全權授權 Fable5（含開頻道與命名）；每日晨會機制已上線，首場已跑

## ○、v1.1 裁定紀錄（Owner 5048 全權授權後，Fable5 依 a0-decision-autonomy-rule 自裁並留檔）

1. **頻道名裁定：MAP TABLE RADIO**（副標 by maplabkitchen）。理由：保留 map 字根扣品牌、TABLE 直指餐桌 BGM 定位、RADIO 給日更電台感；搜尋 maplab 可同時撈到頻道與外燴站。Owner 若記起原「map什麼」提案可隨時翻案改名（頻道未建立前零成本）。
2. **引流心機裁定（Owner 5048「埋下一個心機,設法引流到我的外燴站」）**——三層：
   - 表層：每支影片描述前兩行固定格式=「一句真實派對場景故事」+「這樣的派對真實存在——台南外燴 maplabkitchen：外燴站連結」。聽歌的人裡會辦活動的那群自然點進去。
   - 中層：**曲名一律用台南真實派對場景命名**（例：赤崁樓新人誓約的第一支舞）——搜尋「台南 開幕 音樂」「婚禮 BGM」的長尾流量=正在籌辦派對的人=外燴潛在客群，頻道本身就是獲客漏斗。
   - 深層：封面微動畫的餐桌道具對應真實案例；日後案例文章上線後，描述加一行「這場派對的完整紀錄」連到 WP 案例頁，形成 頻道→案例→詢價 的閉環。
3. **每日晨會機制（Owner 5048「每天早上跟hermes開會並執行」）**：scripts/yt_daily_hermes_meeting.sh——Fable5 主持、hermes(免費鏈,日耗1-2次)出當日曲目 brief（Suno prompt/曲名/含心機描述/封面道具/明日備忘），冪等（同日重跑自動跳過），產出落 data/music-style-db/daily/brief_YYYYMMDD.md 並自動 commit push。觸發雙保險：①每日第一輪 bot resume 開場必跑（已寫入 handoff RESUME 區）②launchd 定時（com.maplab.mtr-daily-meeting 07:2x）待主視窗一次性安裝。首場 2026-09-09 已跑成：nemotron-3-super 出「赤崁樓新人誓約的第一支舞」（B5 婚宴基底,118BPM）。
4. **開頻道技術事實**：YouTube API 無建頻道端點，channel 建立本身必須 Google 帳號 GUI 一次；建成後 uploads 走 token 現有 youtube.upload scope 全自動。故「開頻道」一步=Owner 手機點一次或授權主視窗 GUI 操作，其餘 Fable5 全包。

## 一、對標（三個成功模型，各取一塊）

| 對標 | 模型重點 | 我們取什麼 |
|---|---|---|
| Lofi Girl（youtube.com/@LofiGirl） | 單一角色微動畫 loop+固定曲風，日更/長直播，訂閱千萬級 | **微動畫封面模型**：一個固定場景小幅循環動畫（爐火、蒸氣、吊燈微晃） |
| Chillhop Music（@ChillhopMusic） | 浣熊 IP+季節合輯+廠牌化（幫獨立音樂人發行） | **風格資料庫→廠牌化**：每首歌掛曲風標籤，累積成可檢索的 style DB |
| Cafe Music BGM channel（@cafemusicbgmchannel） | 日本餐飲公司開的 BGM 頻道：爵士/bossa 配咖啡店場景，反過來幫本業導流 | **本業連動**：餐飲品牌開 BGM 頻道的先例，maplabkitchen 完全同構 |

定位一句話：**台南外燴品牌的餐桌 BGM 廠牌**——派對前的備餐、茶會中的背景、收工後的夜歌，全 instrumental（純音樂：繞開歌詞定稿閘與人聲版權面，日更才自動化得起來）。

## 二、頻道識別（等 Owner 圈選）

- Owner 記憶中有個「map 什麼」的舊提案，本窗把 handbook/agent-bus/cdo 全文搜過找不到落檔（可能只在當時對話裡沒沉澱）。候選三個，Owner 圈一個或糾正：
  1. **MAP TABLE RADIO**（地圖×餐桌×電台，扣 maplab 字根）
  2. **MAPLAB TAPES**（廠牌感，合輯化好命名 vol.1/2/3）
  3. **MAP & LADLE**（地圖與湯勺，廚房味最重）
- 視覺：微動畫封面固定場景=「台南騎樓下的派對餐桌」——長桌、吊燈、蒸氣、遠處霓虹；配色抓 maplabkitchen IG 的暖橘＋深綠；每首歌只換「桌上的一樣道具」（蛋糕/香檳杯/抓周物/花藝）呼應曲風，品牌味藏在場景不打 logo。
- 紅線：頻道視覺不用客戶照片、不出現客戶資訊；lyrics 不進任何公開描述（instrumental 無此問題）。

## 三、全自動日更管線（設計；分四段，每段可獨立驗收）

```
[1] hermes 每日 style brief（免費鏈,cron 1次/日）
    讀 style DB → 產出：曲風/BPM/氛圍/樂器/封面道具 + YouTube 標題與描述
[2] Suno 生成（A8 線,燒 Suno 額度）
    brief → 2 個 take → 自動選時長合格者（>2:30）落 WAV+SHA-256
[3] 封面微動畫（本機,零額度）
    固定場景母圖 + 道具圖層置換 → ffmpeg loop（zoompan/淡入淡出/粒子蒸氣,15-30s 循環）
    → 與音檔 mux 成 1080p 影片
[4] 上傳（token 已有 youtube.upload scope,REST 通道同款手動 refresh 可用）
    每日定時上傳+標題描述標籤自動帶入;首月建議 unlisted 積 20-30 支後轉公開排播
```

- 額度帳：hermes 免費鏈 1000/日只用 1-2 次；Suno 是唯一真消耗（日更=每天 2 take）；[3][4] 零額度。
- 每段驗收點：brief JSON 格式閘 → 音檔時長+hash → 影片可播+loop 無縫 → 上傳回 videoId。
- 風險：Suno 商用權與 YouTube 內容識別（先查 Suno 方案的商用授權條款再開公開化）；頻道建立本身要 Owner GUI 點（action-time confirmation，同健身頻道前例）。

## 四、20 首試聽批次（風格資料庫種子，先於頻道，Owner 5045「弄個20首歌來聽聽」）

四主題×5 首，全 instrumental。曲風根基取自 JOB-A8-MAPLAB-MUSIC-SERIES 十案已核的曲風向量（kawaii future-bass 124-126 / nu-disco city-pop 112 等），擴成頻道四時段：

| 主題（時段） | 曲風帶 | BPM | 5 首變化軸 |
|---|---|---|---|
| A 備餐晨光 morning prep | acoustic bossa × jazzhop | 85-95 | 吉他主導→鋼琴主導→手風琴→口哨→弦樂 |
| B 派對進行 party time | nu-disco × city-pop | 108-118 | 開幕迎賓→性別派對→抓周慶生→企業茶會→婚宴 |
| C 午後茶會 tea break | kawaii future-bass(去人聲) × chill EDM | 100-124 | 甜點桌→兒童場→戶外場→雨天室內→黃昏場 |
| D 收工夜歌 after hours | lofi jazz × 台味那卡西慢版 | 70-82 | 收桌→夜市遠聲→騎樓雨→老屋木地板→打烊熄燈 |

每首落格式：`style_id | 主題 | Suno prompt(英文) | BPM | 封面道具 | 案例對應(若有)`
→ 存 data/music-style-db/style-seeds-20260909.csv（A8 執行時逐列生成，兩 take 取優）。
20 首交付=一個雲端資料夾連結（音檔照 style_id 命名），Owner 手機點開就能聽。

## 五、執行順序與分工

1. A8 卡（handoff/tasks/T-A8-YT-MUSIC-CHANNEL-001.md）：先跑 20 首試聽（Suno 額度=唯一消耗，卡內附額度上限）。
2. Owner：聽 20 首圈方向＋圈頻道名＋Suno 商用權方案確認。
3. A0+A8：管線 [1][3] 先建好乾跑（不用 Suno 也能測 brief→封面→mux）。
4. Owner GUI 建頻道（一次性）→ [4] 上傳線接通 → unlisted 養庫 → 公開日更。
