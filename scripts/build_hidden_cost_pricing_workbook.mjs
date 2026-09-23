import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "/Users/pagemacmini/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";


const outputDir = process.argv[2];
if (!outputDir) throw new Error("usage: build_hidden_cost_pricing_workbook.mjs OUTPUT_DIR");
await fs.mkdir(outputDir, { recursive: true });

const generatedAt = "2026-08-28";
const workbook = Workbook.create();
const dashboard = workbook.worksheets.add("毛利機會總覽");
const catalog = workbook.worksheets.add("加價服務矩陣");
const signals = workbook.worksheets.add("對話訊號彙總");
const audit = workbook.worksheets.add("案件稽核表");
const params = workbook.worksheets.add("計價參數");
const sources = workbook.worksheets.add("來源與邊界");

const colors = {
  green: "#234E3F",
  green2: "#3D6B59",
  beige: "#F3E9DC",
  beige2: "#FBF7F1",
  terracotta: "#C76D45",
  amber: "#F4C95D",
  red: "#B84A45",
  gray: "#667085",
  lightGray: "#E7E5E4",
  white: "#FFFFFF",
};

function titleBand(sheet, range, title, subtitle) {
  sheet.getRange(range).merge();
  const topLeft = range.split(":")[0];
  sheet.getRange(topLeft).values = [[title]];
  sheet.getRange(range).format = {
    fill: colors.green,
    font: { bold: true, color: colors.white, size: 18 },
    verticalAlignment: "center",
  };
  const row = Number(topLeft.match(/\d+/)[0]) + 1;
  const startCol = topLeft.match(/[A-Z]+/)[0];
  const endCol = range.split(":")[1].match(/[A-Z]+/)[0];
  sheet.getRange(`${startCol}${row}:${endCol}${row}`).merge();
  sheet.getRange(`${startCol}${row}`).values = [[subtitle]];
  sheet.getRange(`${startCol}${row}:${endCol}${row}`).format = {
    fill: colors.beige,
    font: { color: colors.green, italic: true, size: 10 },
    wrapText: true,
    verticalAlignment: "center",
  };
}

function styleHeader(range) {
  range.format = {
    fill: colors.green2,
    font: { bold: true, color: colors.white },
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: colors.green },
  };
}

function styleBody(range) {
  range.format = {
    fill: colors.beige2,
    font: { color: "#252525", size: 10 },
    verticalAlignment: "top",
    wrapText: true,
    borders: {
      insideHorizontal: { style: "thin", color: colors.lightGray },
      bottom: { style: "thin", color: colors.lightGray },
    },
  };
}

const conversationSignals = [
  ["custom_scope", "客製／主題／品牌細節", 1419, 972, "造型、花藝、Logo、試作等；候選訊號，不等於可收費"],
  ["third_party_turnkey", "統包／第三方協調", 838, 686, "場地、花藝、音響、行政代辦等；vendor 字詞可能有誤報"],
  ["logistics_access", "搬運／樓層／卸貨", 561, 455, "樓梯、無電梯、停車、偏遠或多點"],
  ["revision_change_order", "追加／變更／修改", 589, 363, "需核對是否超過合約內含 2 次修改"],
  ["equipment_consumables", "設備／桌椅／器皿", 602, 348, "需先定義標準內含量，避免重複收費"],
  ["time_rush", "急件／等待／特殊時段", 477, 269, "急件字詞占多數；需核對真正 lead time"],
  ["dietary_separation", "特殊飲食分流", 154, 104, "只在獨立製作、包裝、標示產生額外成本時列費"],
  ["onsite_service", "駐場／巡場服務", 110, 75, "服務人員、補餐、倒酒、Tray-passed"],
  ["cleanup_waste", "垃圾／清潔／復原", 56, 44, "垃圾帶走與場地復原必須拆成兩項"],
];

const addonRows = [
  ["SVC-ONSITE-DAY", "onsite_service", "現場服務人員（日間）", "送達與基本陳列；是否含撤場須以個案合約為準", "駐場補餐、巡場遞送、倒酒或接待", "人／2小時", "1,200–2,000／人／2–3小時", "1,500／人／2小時；續時 600／人／小時", 1500, 1500, 2000, "HIGH", "PILOT_OWNER_REVIEW", "https://www.papagofood.com.tw/faq.php?cate=1&cid= ; https://www.centuryfood.com.tw/about.php?CNo=10", "IG 已公開展示四場一致 Tray-passed service，證明是可獨立交付服務"],
  ["SVC-OVERTIME", "time_rush", "等待／延遲撤場／超時", "報價核准時段內的進撤場", "場地未開、流程延誤、要求待命或延長服務", "人／30分鐘", "約 125–300／人／30分鐘", "250–500／人／30分鐘；每次最低 500", 500, 250, 500, "HIGH", "PILOT_OWNER_REVIEW", "https://missfaithsbakery.mystrikingly.com/ordering ; https://www.papagofood.com.tw/faq.php?cate=1&cid= ; https://yamiyami.com.tw/menu/", "MAPLAB 內部已有 500／30分鐘錨點，需統一合約"],
  ["LOG-STAIRS", "logistics_access", "無電梯樓層搬運", "平面或有可用電梯的正常卸貨動線", "無電梯、狹窄樓梯、跨樓層搬運", "每層／每批", "300–1,000／層", "事前告知 800／層；當日才告知 1,000／層", 800, 800, 1000, "HIGH", "SCOPE_RECONCILE", "https://missfaithsbakery.mystrikingly.com/ordering", "目前程式、合約與歷史案例有 500／800／1,000 三種版本，先統一再上線"],
  ["LOG-UNLOAD", "logistics_access", "困難卸貨／停車／遠距搬運", "可臨停並在合理距離卸貨", "無卸貨區、付費停車、需人力長距離搬運", "實支＋人時", "公開業者多採另報或實支", "停車實支＋搬運工時；行政最低 300", 300, 300, 800, "MEDIUM", "PILOT_OWNER_REVIEW", "https://www.pro360.com.tw/price/catering ; https://www.paultaiwan.com/party", "保留停車收據；不可把一般停車一律灌成固定費"],
  ["LOG-OUTZONE", "logistics_access", "跨區／跨縣市運送", "台南市或合約載明免費區域", "超過 30 分鐘、跨縣市、冷藏車或需往返回收", "每車次／公里", "100／km、2,000 來回、非核心區 8,000 等不同樣本", "沿用成本公式並設最低 1,000；遠距 1,000–3,000 起另報", 1000, 1000, 3000, "MEDIUM", "SCOPE_RECONCILE", "https://yamiyami.com.tw/menu/ ; https://www.paultaiwan.com/party ; https://www.hotelroyal.com.tw/Files/Documents/IJb20250207010604972.pdf", "現行內部公式與公開市場差距大，須以車次、回收與人時校正"],
  ["LOG-MULTISTOP", "logistics_access", "多地址／分批配送", "單一地址、單一時段", "追加地址、分批到貨或二次進撤場", "每追加地址／車次", "一般配送樣本 150–350／址，非完整外燴", "每追加地址 800–1,500，再加實際運送", 800, 800, 1500, "LOW", "PILOT_OWNER_REVIEW", "https://www.bestoilrice.com.tw/fare/", "公開來源不是南部完整外燴，只支持多點不等於一次配送"],
  ["CLN-WASTE", "cleanup_waste", "垃圾／廚餘打包與載走", "餐飲區基本收整；是否含垃圾須寫清楚", "要求分類、打包、搬運並載離現場", "訂單比例／車次", "訂單總額 10% 的公開樣本", "訂單 8–10%；每案最低 1,500", 1500, 1500, 5000, "HIGH", "PILOT_OWNER_REVIEW", "https://www.papagofood.com.tw/faq.php?cate=1&cid=", "垃圾載走與場地清潔復原不可混成同一承諾"],
  ["CLN-RESTORE", "cleanup_waste", "場地清潔／復原", "僅餐檯與我方作業區正常撤場", "清掃地面、油污處理、移動復原非我方物件", "人時／區域", "多數業者另報，未找到南部固定價", "完全負擔人時回推；最低 2,500", 2500, 2500, 6000, "LOW", "PILOT_OWNER_REVIEW", "https://www.papagofood.com.tw/faq.php?cate=1&cid=", "先定義責任區域與完成標準"],
  ["TIM-RUSH", "time_rush", "急件處理費", "正常 lead time 內確認", "活動前三天內才確認，或已排程後重大變更", "每案／提前天數", "前三天 1,000、前兩天 2,000、前一天 3,000", "1,000／2,000／3,000 分級", 1000, 1000, 3000, "MEDIUM", "PILOT_OWNER_REVIEW", "https://missfaithsbakery.mystrikingly.com/ordering", "單一北部樣本，結構可採、金額需用 MAPLAB 加班成本校正"],
  ["TIM-NIGHT", "time_rush", "夜間／清晨／假日附加", "一般工作時段", "夜間、清晨、國定假日或連假服務", "固定附加／人力倍率", "小額假日 1,000；夜間多採另報", "基本 1,000，或人力 1.25 倍，取高者", 1000, 1000, 3000, "LOW", "PILOT_OWNER_REVIEW", "https://missfaithsbakery.mystrikingly.com/ordering ; https://www.paultaiwan.com/party", "不得把同一夜間成本同時收固定費與重複人力加成"],
  ["EQP-TABLE", "equipment_consumables", "外燴長桌租借", "歷史部分方案曾含基本桌數，須明列標準內含量", "超出內含量或場地完全不供桌", "張／場", "200–1,000／張", "400–450／張；運回另計", 400, 400, 450, "HIGH", "SCOPE_RECONCILE", "https://www.papagofood.com.tw/tableware.php?cate=188&cid=4 ; https://yamiyami.com.tw/menu/", "現行 GAS 350、歷史標準 400；先定唯一價格"],
  ["EQP-CLOTH", "equipment_consumables", "桌巾超量／特殊色", "基本餐檯桌巾若方案已含", "超出內含張數、特殊色或額外清洗", "條／場", "100／條的公開樣本", "100–150／條", 100, 100, 150, "MEDIUM", "SCOPE_RECONCILE", "https://yamiyami.com.tw/menu/", "若基本桌巾已含，不得重複收"],
  ["EQP-CHAIR", "equipment_consumables", "椅子／圓凳租借", "一般外燴不含賓客座椅", "客戶要求我方代辦座椅", "張／場", "椅 60–100、圓凳 30", "椅 80–100；運送另計", 80, 80, 100, "HIGH", "PILOT_OWNER_REVIEW", "https://www.papagofood.com.tw/tableware.php?cate=188&cid=4 ; https://www.hotelroyal.com.tw/Files/Documents/IJb20250207010604972.pdf", "大型數量先走 vendor 報價"],
  ["EQP-PREMIUM", "equipment_consumables", "陶瓷／玻璃精品餐具升級", "合約內含的一次性餐具數量", "改用可回收精品器皿、需清洗與破損管理", "人／場", "30–50／人", "40–60／人；最低 1,200，破損另計", 1200, 40, 60, "HIGH", "PILOT_OWNER_REVIEW", "https://www.shop2000.com.tw/%E7%86%8A%E6%84%9B%E7%9A%84%E8%8A%B1%E8%8B%91/product/p4011850 ; https://www.hotelroyal.com.tw/Files/Documents/IJb20250207010604972.pdf", "加押金或破損條款，不以模糊『高級餐具』帶過"],
  ["CUS-LOGO", "custom_scope", "企業 Logo 插旗／印刷物", "標準無品牌印刷物", "指定 Logo、版型、打樣與印刷", "批／版", "未找到可信南部固定價", "第三方實支＋15–20% 協調費；最低 800", 800, 800, 3000, "LOW", "PILOT_OWNER_REVIEW", "https://www.instagram.com/maplabkitchen/", "IG AMD 案例明載『客製企業 Logo 食物小插旗』，應成為正式品項"],
  ["CUS-FLORAL", "custom_scope", "鮮花／花藝加購", "歷史基本乾燥花或簡易陳列若方案已含", "指定鮮花、色系或超量造景", "案／組", "多數業者依花材與設計另報", "第三方實支＋15–20% 協調費；最低 1,200", 1200, 1200, 8000, "LOW", "SCOPE_RECONCILE", "https://www.instagram.com/maplabkitchen/", "IG AMD 案例明載加購小鮮花；基本陳列與花藝升級要切清楚"],
  ["CUS-BRAND-DESIGN", "custom_scope", "品牌調性菜單／陳列設計", "從既有品項選配與標準餐檯", "需依品牌、空間、色系重做菜單與器皿陳列", "設計案／工時", "市場多採場勘後另報", "設計與專案工時回推；最低 3,000，常見建議 3,000–8,000", 3000, 3000, 8000, "LOW", "PILOT_OWNER_REVIEW", "https://www.instagram.com/maplabkitchen/", "IG Cléa 案例公開描述依品牌調性調整餐點、器皿與整體呈現"],
  ["PM-SITE", "third_party_turnkey", "額外場勘／動線規劃", "一次基本線上需求確認", "第二次以上場勘、圖面、流程表或多方會議", "次／工時", "公開業者多為場勘後報價，無一致固定價", "1,500–3,000／次＋交通；成交可選擇折抵", 1500, 1500, 3000, "LOW", "PILOT_OWNER_REVIEW", "https://www.pro360.com.tw/price/catering", "把可折抵規則寫進報價，避免口頭免費承諾"],
  ["PM-REVISION", "revision_change_order", "超過內含次數的修改", "合約 v4 內含 2 次修改", "第 3 次起或已確認後重大變更", "次／變更單", "內部條款允許另報；未找到公開一致價", "1,000–2,000／次，或增量成本回推取高者", 1000, 1000, 2000, "MEDIUM", "PILOT_OWNER_REVIEW", "internal://data/contract-terms-v4.md", "先區分我方錯誤修正，後者不可收費"],
  ["PM-TURNKEY", "third_party_turnkey", "第三方統包／供應商協調", "只交付 MAPLAB 餐飲範圍", "代找場地、花藝、攝影、主持、音響或行政登記", "第三方實支＋管理", "多數業者另報，無可信南部固定率", "第三方實支＋15–20% 管理費；最低 1,500", 1500, 1500, 10000, "LOW", "PILOT_OWNER_REVIEW", "https://www.pro360.com.tw/price/catering", "報價中分列 vendor 實支與我方管理責任"],
  ["DIE-SEPARATE", "dietary_separation", "特殊飲食獨立製作／標示", "一般菜單偏好調整", "需獨立製程、包裝、器皿、標示或專人分流", "批／份", "無可信全台固定價", "增量成本回推；每批最低 800，不使用『過敏加價』用語", 800, 800, 3000, "LOW", "PILOT_OWNER_REVIEW", "https://www.papagofood.com.tw/faq.php?cate=1&cid= ; https://www.cateringking.com.tw/vegan-friendly/", "不得保證零交叉接觸；只有實際分流成本才收"],
  ["EQP-POWER", "equipment_consumables", "發電／保冷／特殊設備", "正常室內電力與一般運輸", "戶外無電、長時間保冷保溫、特殊設備操作", "設備日租＋運送", "發電機約 700–3,000／日，規格差異大", "實際租金＋運送燃料＋20% 管理；最低 1,000", 1000, 1000, 5000, "MEDIUM", "PILOT_OWNER_REVIEW", "https://www.championpower.com.tw/rental-service ; https://www.cool-wow.com/power-generator", "設備型號、功率、燃料與操作責任必須寫清楚"],
  ["CUS-TASTING", "custom_scope", "試吃／打樣／樣品", "正式訂單餐點製作", "成交前指定試作、打樣、照片或多版本樣品", "次／組", "未找到南部一致公開價", "直接成本＋行政工時回推；1,500–5,000，可設定成交折抵", 1500, 1500, 5000, "LOW", "PILOT_OWNER_REVIEW", "internal://margin-formula", "折抵條件要書面化，避免無限試作"],
  ["CO-CHANGE", "revision_change_order", "確認後變更單", "核准報價範圍", "確認後追加菜色、人數、時段、地點、設備或責任", "每張變更單", "法規要求成交前明列免費與另計項目，不可事後任意加價", "max(最低 1,000，增量完全成本／(1-目標毛利))", 1000, 1000, 20000, "HIGH", "PILOT_OWNER_REVIEW", "https://www.fda.gov.tw/tc/sitecontent.aspx?sid=2519", "必須在執行前取得書面確認；我方錯誤補救不可列變更單"],
];

const sourceRows = [
  ["LIVE", "MAPLAB 主報價系統", "SALES_INTAKE、REVISION_LOG、CONVERSATION_LOG live headers；REVISION_LOG 無工時、成本、加價與豁免欄", "https://docs.google.com/spreadsheets/d/1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg/edit", generatedAt, "HIGH", "系統缺口"],
  ["LIVE", "MAPLAB IG", "公開展示企業 Logo 插旗、鮮花、Tray-passed、品牌調性菜單與陳列，證明可拆成獨立交付", "https://www.instagram.com/maplabkitchen/", generatedAt, "HIGH", "產品化證據"],
  ["LIVE", "MAPLAB_ASSET_LOG", "live header 以 file_id 為主鍵，首列可見 40,292；尚未與 case_id／quote_id／IG permalink 串接", "https://docs.google.com/spreadsheets/d/1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI/edit", generatedAt, "HIGH", "素材 join 缺口"],
  ["LIVE", "2026 MAPLAB 外燴照片根目錄", "抽取頁回傳 100 項：41 folders、39 HEIF、4 MOV、3 JPEG 等；活動資料夾與報價仍缺穩定 join", "https://drive.google.com/drive/folders/1pKfGSOZXBpG7qXcJrW5T7aoHX4nqB1Tt", generatedAt, "MEDIUM", "素材流程"],
  ["PRIVATE_LOCAL", "LINE 初步訊號掃描", "20,256 rows、2,491 conversations；只輸出 aggregate，不含原文與識別碼", "/Users/pagemacmini/.maplab/margin-leak-audit/20260828-initial-aggregate.json", generatedAt, "MEDIUM", "候選排序；不是已確認漏收"],
  ["PUBLIC", "食藥署定型化契約", "免費與另行計費項目應預先列明；不得訂約後變相任意加價", "https://www.fda.gov.tw/tc/sitecontent.aspx?sid=2519", generatedAt, "HIGH", "治理邊界"],
  ["PUBLIC", "好田外燴", "台南公開最低消費樣本：20 人 8,000 起", "https://www.howtian.com/catering", generatedAt, "MEDIUM", "南部最低消費錨點"],
  ["PUBLIC", "原味好食", "高雄公開最低消費樣本：精緻型 8,000、大型客製 15,000 起", "https://originalmeal2016.com.tw/home", generatedAt, "MEDIUM", "南部最低消費錨點"],
  ["PUBLIC", "Papago", "人員、超時、垃圾廚餘、租借品拆項收費樣本", "https://www.papagofood.com.tw/faq.php?cate=1&cid=", generatedAt, "MEDIUM", "服務拆項"],
  ["PUBLIC", "YAMI", "距離、服務人員、桌巾與桌具公開價樣本", "https://yamiyami.com.tw/menu/", generatedAt, "MEDIUM", "物流／設備"],
  ["PUBLIC", "費小姐", "樓層、超時、急件、假日分級收費樣本", "https://missfaithsbakery.mystrikingly.com/ordering", generatedAt, "MEDIUM", "規則結構"],
  ["PUBLIC", "新竹老爺", "人員、廚師、桌椅杯皿與非核心區運送公開價樣本", "https://www.hotelroyal.com.tw/Files/Documents/IJb20250207010604972.pdf", generatedAt, "MEDIUM", "飯店級上緣"],
  ["PUBLIC", "OpenAI eval practice", "先人工檢視輸出、建立 failure taxonomy，再選改善槓桿", "https://openai.com/index/evals-drive-next-chapter-of-ai/", generatedAt, "HIGH", "訓練 SOP"],
  ["PUBLIC", "Anthropic eval guide", "開發集與 held-out data 分離；同案例比較 baseline/candidate", "https://www-cdn.anthropic.com/38a1fb9db81446402a70bc45d104327aab12f3fe.pdf", generatedAt, "HIGH", "訓練 SOP"],
  ["PUBLIC", "Anthropic agent evals", "低分先讀 transcript／grader；安全 gate 與能力分數分離", "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents", generatedAt, "HIGH", "訓練 SOP"],
];

// Parameters
params.showGridLines = false;
titleBand(params, "A1:F1", "MAPLAB 加價計價參數", "黃色儲存格為 Owner 可調整假設；尚未核准前不得寫回正式報價系統。所有金額為 NT$。 ");
params.getRange("A4:C10").values = [
  ["參數", "目前假設", "使用說明"],
  ["完全負擔現場人員時薪", 300, "薪資＋勞健保／餐費／準備與交通分攤，請 A5 以真實成本覆蓋"],
  ["完全負擔行政／設計時薪", 400, "報價、改稿、會議、採購與供應商協調"],
  ["目標加價毛利率", 0.5, "與餐點毛利分開；正式值由 Owner/A5 核准"],
  ["第三方管理費率", 0.18, "只對確有管理責任的第三方實支計算"],
  ["急件人力倍率", 1.25, "不與同一成本的固定急件費重複收"],
  ["夜間／假日人力倍率", 1.25, "只套額外人力成本"],
];
styleHeader(params.getRange("A4:C4"));
styleBody(params.getRange("A5:C10"));
params.getRange("B5:B10").format.fill = "#FFF2B2";
params.getRange("B5:B6").format.numberFormat = "NT$#,##0";
params.getRange("B7:B10").format.numberFormat = "0%";
params.getRange("A:A").format.columnWidth = 30;
params.getRange("B:B").format.columnWidth = 18;
params.getRange("C:C").format.columnWidth = 72;
params.freezePanes.freezeRows(4);

// Catalog
catalog.showGridLines = false;
titleBand(catalog, "A1:N1", "MAPLAB 隱藏成本／加價服務矩陣", "市場價是公開樣本，不是正式售價。先核對合約內含範圍，再以完全成本與目標毛利回推；Owner status 非 APPROVED 一律不可對客。 ");
const catalogHeaders = ["addon_id", "對話分類", "對客品名", "標準內含範圍", "可計費觸發", "單位", "公開市場樣本", "MAPLAB 建議模型", "最低收費", "建議低", "建議高", "信心", "Owner status", "來源與備註"];
catalog.getRange("A5:N5").values = [catalogHeaders];
catalog.getRange(`A6:N${5 + addonRows.length}`).values = addonRows.map(row => [
  row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], `${row[13]}\n${row[14]}`,
]);
styleHeader(catalog.getRange("A5:N5"));
styleBody(catalog.getRange(`A6:N${5 + addonRows.length}`));
catalog.getRange(`I6:K${5 + addonRows.length}`).format.numberFormat = "NT$#,##0";
catalog.getRange(`L6:L${5 + addonRows.length}`).dataValidation = { rule: { type: "list", values: ["HIGH", "MEDIUM", "LOW"] } };
catalog.getRange(`M6:M${5 + addonRows.length}`).dataValidation = { rule: { type: "list", values: ["PILOT_OWNER_REVIEW", "SCOPE_RECONCILE", "APPROVED", "REJECTED"] } };
catalog.getRange(`M6:M${5 + addonRows.length}`).conditionalFormats.add("containsText", { text: "APPROVED", format: { fill: "#D9EAD3", font: { color: colors.green, bold: true } } });
catalog.getRange(`M6:M${5 + addonRows.length}`).conditionalFormats.add("containsText", { text: "RECONCILE", format: { fill: "#FCE8B2", font: { color: "#7A4E00", bold: true } } });
catalog.getRange("A:A").format.columnWidth = 20;
catalog.getRange("B:B").format.columnWidth = 22;
catalog.getRange("C:C").format.columnWidth = 28;
catalog.getRange("D:E").format.columnWidth = 42;
catalog.getRange("F:F").format.columnWidth = 18;
catalog.getRange("G:H").format.columnWidth = 40;
catalog.getRange("I:K").format.columnWidth = 15;
catalog.getRange("L:M").format.columnWidth = 22;
catalog.getRange("N:N").format.columnWidth = 62;
catalog.freezePanes.freezeRows(5);
catalog.freezePanes.freezeColumns(3);
catalog.tables.add(`A5:N${5 + addonRows.length}`, true, "AddonCatalogTable");

// Signals
signals.showGridLines = false;
titleBand(signals, "A1:E1", "LINE 對話隱藏成本訊號（初篩）", "本機 deterministic 掃描：20,256 rows／2,491 conversations。類別會重疊，且關鍵字命中不是漏收證明；必須回到合約、實際交付與已收費資料確認。 ");
signals.getRange("A5:E5").values = [["category", "人話分類", "matched_rows", "unique_conversations", "解讀邊界"]];
signals.getRange("A6:E14").values = conversationSignals;
styleHeader(signals.getRange("A5:E5"));
styleBody(signals.getRange("A6:E14"));
signals.getRange("C6:D14").format.numberFormat = "#,##0";
signals.getRange("A:B").format.columnWidth = 30;
signals.getRange("C:D").format.columnWidth = 20;
signals.getRange("E:E").format.columnWidth = 66;
signals.freezePanes.freezeRows(5);
signals.tables.add("A5:E14", true, "ConversationSignalsTable");

// Audit template
audit.showGridLines = false;
titleBand(audit, "A1:AF1", "案件漏收費稽核表", "只在本機填入 hash／evidence path，不貼客戶原文。先判定 INCLUDED／BILLABLE／CHANGE_ORDER／PASS_THROUGH／DECLINE_OR_RISK／OWNER_WAIVER，再計算。 ");
const auditHeaders = [
  "leak_id", "case_id_hash", "quote_id", "日期", "來源", "category", "addon_id", "baseline_scope", "requested_scope", "evidence_hash/path",
  "staff_count", "labor_hours", "admin_hours", "material_cost", "vendor_cost", "equipment_cost", "transport_cost", "parking_tolls", "waste_cost", "risk_reserve",
  "target_margin", "fully_loaded_cost", "price_floor", "minimum_charge", "recommended_fee", "charged_fee", "unbilled_leakage", "decision_status", "waiver_reason", "review_owner", "reviewed_at", "notes",
];
audit.getRange("A5:AF5").values = [auditHeaders];
styleHeader(audit.getRange("A5:AF5"));
styleBody(audit.getRange("A6:AF205"));
audit.getRange("U6").formulas = [["='計價參數'!$B$7"]];
audit.getRange("U6:U205").fillDown();
audit.getRange("V6").formulas = [["=IF(COUNTA(A6:T6)=0,\"\",K6*L6*'計價參數'!$B$5+M6*'計價參數'!$B$6+SUM(N6:T6))"]];
audit.getRange("V6:V205").fillDown();
audit.getRange("W6").formulas = [["=IF(V6=\"\",\"\",IF(U6>=1,\"\",V6/(1-U6)))"]];
audit.getRange("W6:W205").fillDown();
audit.getRange("X6").formulas = [["=IF(G6=\"\",\"\",IFERROR(INDEX('加價服務矩陣'!$I$6:$I$29,MATCH(G6,'加價服務矩陣'!$A$6:$A$29,0)),0))"]];
audit.getRange("X6:X205").fillDown();
audit.getRange("Y6").formulas = [["=IF(W6=\"\",\"\",MAX(W6,X6))"]];
audit.getRange("Y6:Y205").fillDown();
audit.getRange("AA6").formulas = [["=IF(Y6=\"\",\"\",MAX(0,Y6-Z6))"]];
audit.getRange("AA6:AA205").fillDown();
audit.getRange("F6:F205").dataValidation = { rule: { type: "list", values: conversationSignals.map(row => row[0]) } };
audit.getRange("AB6:AB205").dataValidation = { rule: { type: "list", values: ["NEEDS_REVIEW", "INCLUDED", "BILLABLE", "CHANGE_ORDER", "PASS_THROUGH", "DECLINE_OR_RISK", "OWNER_WAIVER", "CHARGED"] } };
audit.getRange("U6:U205").format.numberFormat = "0%";
audit.getRange("N6:T205").format.numberFormat = "NT$#,##0";
audit.getRange("V6:AA205").format.numberFormat = "NT$#,##0";
audit.getRange("AA6:AA205").conditionalFormats.add("cellIs", { operator: "greaterThan", formula: 0, format: { fill: "#F8D7DA", font: { color: colors.red, bold: true } } });
audit.getRange("A:J").format.columnWidth = 22;
audit.getRange("H:I").format.columnWidth = 40;
audit.getRange("J:J").format.columnWidth = 34;
audit.getRange("K:U").format.columnWidth = 15;
audit.getRange("V:AA").format.columnWidth = 18;
audit.getRange("AB:AF").format.columnWidth = 24;
audit.freezePanes.freezeRows(5);
audit.freezePanes.freezeColumns(3);
audit.tables.add("A5:AF205", true, "MarginLeakAuditTable");

// Sources
sources.showGridLines = false;
titleBand(sources, "A1:G1", "來源、證據與使用邊界", "LIVE 是本輪 readback；PUBLIC 是公開價格樣本；PRIVATE_LOCAL 僅能在本機使用。公開價不能直接覆蓋 MAPLAB 正式售價。 ");
sources.getRange("A5:G5").values = [["類型", "來源", "支持的事實", "URL／路徑", "查核日", "可靠度", "用途"]];
sources.getRange(`A6:G${5 + sourceRows.length}`).values = sourceRows;
styleHeader(sources.getRange("A5:G5"));
styleBody(sources.getRange(`A6:G${5 + sourceRows.length}`));
sources.getRange("A:A").format.columnWidth = 18;
sources.getRange("B:B").format.columnWidth = 30;
sources.getRange("C:C").format.columnWidth = 66;
sources.getRange("D:D").format.columnWidth = 66;
sources.getRange("E:G").format.columnWidth = 18;
sources.freezePanes.freezeRows(5);
sources.tables.add(`A5:G${5 + sourceRows.length}`, true, "SourceEvidenceTable");

// Dashboard
dashboard.showGridLines = false;
titleBand(dashboard, "A1:N1", "MAPLAB 毛利機會總覽", "先把做得到、實際做過、但尚未產品化計價的服務變成 catalog；不把每個客戶要求都當成可收費。 ");
dashboard.getRange("A4:D4").values = [["指標", "數值", "狀態", "解讀"]];
dashboard.getRange("A5:D9").values = [
  ["初篩 LINE 對話數", 2491, "CANDIDATE", "類別重疊；不是漏收案件數"],
  ["候選加價服務", addonRows.length, "OWNER_REVIEW", "正式價目上線前需 scope reconcile"],
  ["已核准正式價目", 0, "NOT_LIVE", "本表未修改正式 Sheets／GAS"],
  ["高信心市場錨點", addonRows.filter(row => row[11] === "HIGH").length, "EVIDENCE", "有多個公開拆項價或內外證據交叉"],
  ["目前已確認漏收金額", 0, "NOT_YET_AUDITED", "需把對話、報價、實際交付與付款 join 後才能計算"],
];
styleHeader(dashboard.getRange("A4:D4"));
styleBody(dashboard.getRange("A5:D9"));
dashboard.getRange("B5:B9").format.numberFormat = "#,##0";
dashboard.getRange("A:A").format.columnWidth = 30;
dashboard.getRange("B:B").format.columnWidth = 18;
dashboard.getRange("C:C").format.columnWidth = 22;
dashboard.getRange("D:D").format.columnWidth = 64;
dashboard.getRange("A12:D12").values = [["第一批應產品化", "為什麼", "建議先做", "不得做"]];
dashboard.getRange("A13:D17").values = [
  ["駐場／Tray-passed", "IG 已公開展示且市場普遍拆項", "人數×時數×人力規則", "默認免費駐場"],
  ["樓層／搬運／等候", "對話訊號高、內部價格漂移", "統一 500／800／1000 衝突", "事後臨時加價"],
  ["Logo／鮮花／品牌陳列", "已實際交付但未成 catalog", "第三方實支＋明示管理費", "把基本陳列重複收費"],
  ["垃圾與場地復原", "責任最易膨脹", "分成『載走』與『清潔復原』", "用一句『撤場』包全部"],
  ["超過 2 次修改／確認後變更", "合約已允許另報", "變更單＋書面確認", "我方錯誤也收費"],
];
styleHeader(dashboard.getRange("A12:D12"));
styleBody(dashboard.getRange("A13:D17"));
dashboard.getRange("A:D").format.wrapText = true;
dashboard.getRange("F4:J4").values = [["對話候選分類", "unique conversations", "matched rows", "注意", "狀態"]];
dashboard.getRange("F5:J13").values = conversationSignals.map(row => [row[1], row[3], row[2], row[4], "NEEDS_REVIEW"]);
styleHeader(dashboard.getRange("F4:J4"));
styleBody(dashboard.getRange("F5:J13"));
dashboard.getRange("F:F").format.columnWidth = 28;
dashboard.getRange("G:H").format.columnWidth = 20;
dashboard.getRange("I:I").format.columnWidth = 44;
dashboard.getRange("J:J").format.columnWidth = 20;
const chart = dashboard.charts.add("bar", dashboard.getRange("F4:G13"));
chart.title = "對話中可計價服務候選（類別可重疊）";
chart.hasLegend = false;
chart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
chart.yAxis = { numberFormatCode: "#,##0" };
chart.setPosition("F16", "N34");
dashboard.freezePanes.freezeRows(4);

for (const sheet of [dashboard, catalog, signals, audit, params, sources]) {
  sheet.getRange("1:2").format.rowHeight = 28;
}

const formulaInspection = await workbook.inspect({
  kind: "formula",
  sheetId: "案件稽核表",
  range: "U5:AA12",
  maxChars: 8000,
  options: { maxResults: 60 },
});
const preview = await workbook.render({
  sheetName: "毛利機會總覽",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(path.join(outputDir, "maplab_hidden_cost_pricing_matrix_20260828_preview.png"), new Uint8Array(await preview.arrayBuffer()));
for (const [sheetName, fileName] of [
  ["加價服務矩陣", "maplab_hidden_cost_pricing_matrix_20260828_catalog_preview.png"],
  ["對話訊號彙總", "maplab_hidden_cost_pricing_matrix_20260828_signals_preview.png"],
]) {
  const sheetPreview = await workbook.render({ sheetName, autoCrop: "all", scale: 0.8, format: "png" });
  await fs.writeFile(path.join(outputDir, fileName), new Uint8Array(await sheetPreview.arrayBuffer()));
}
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
const xlsxPath = path.join(outputDir, "maplab_hidden_cost_pricing_matrix_20260828.xlsx");
await xlsx.save(xlsxPath);
await fs.writeFile(
  path.join(outputDir, "maplab_hidden_cost_pricing_matrix_20260828_validation.json"),
  JSON.stringify(
    {
      generated_at: generatedAt,
      xlsx: xlsxPath,
      sheets: ["毛利機會總覽", "加價服務矩陣", "對話訊號彙總", "案件稽核表", "計價參數", "來源與邊界"],
      addon_rows: addonRows.length,
      conversation_categories: conversationSignals.length,
      formula_inspection: formulaInspection,
      warnings: [
        "No MAPLAB live price was changed.",
        "All proposed fees remain Owner review until approved.",
        "Conversation counts are overlapping candidate signals, not confirmed leakage cases.",
      ],
    },
    null,
    2,
  ) + "\n",
  "utf8",
);
console.log(JSON.stringify({ status: "ok", xlsx: xlsxPath, addon_rows: addonRows.length, signal_categories: conversationSignals.length }));
