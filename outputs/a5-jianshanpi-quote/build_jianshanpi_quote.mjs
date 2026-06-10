import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "/Users/pagemacmini/maplab-ai-handbook/outputs/a5-jianshanpi-quote";
const outputPath = `${outputDir}/A5_尖山埤三版報價毛利試算_20260519.xlsx`;

const plans = [
  {
    code: "A",
    title: "A 小點補給版",
    positioning: "活動後快速補給，主打小點、好拿取、總件數充足",
    salesNote: "A 方案要講總件數：以小點與甜點為主，約 1,000+ 件/份量，適合健行後墊胃與交流。",
    foodRevenue: 60000,
    softDrinkRevenue: 22000,
    alcoholRevenue: 38000,
    staffRevenue: 10000,
    decorRevenue: 18000,
    softDrinkCost: 7000,
    alcoholCost: 30000,
    staffCost: 10000,
    decorCost: 7000,
    menu: [
      ["APP019", "日式醬蛋沙拉小漢堡", "小點", 100, "份", 30, "好拿取、可補件數"],
      ["APP021", "澳式手拍漢堡排起司小漢堡_豬肉", "小點", 100, "個", 30, "提高飽足感"],
      ["APP004", "明太子可頌", "小點", 100, "個", 15, "小點視覺差異"],
      ["APP014", "澳式雞球迷你鬆餅", "小點", 100, "份", 20, "活動後補給"],
      ["APP008", "普羅旺斯香料烤澳洲白玉薯塊", "鹹點", 120, "份", 20, "戶外派對安全品項"],
      ["APP001", "起酥皮捲腸", "鹹點", 100, "份", 10, "孩子友善"],
      ["DES001", "焦糖千層酥", "甜點", 200, "個", 4.5, "甜點件數"],
      ["DST034", "奶油餅乾", "甜點", 5, "組(40片)", 100, "約 200 片"],
    ],
  },
  {
    code: "B",
    title: "B 精緻特色小點版",
    positioning: "主推版本，精緻小點加特色熱食，餐檯比較有企業家庭日質感",
    salesNote: "B 方案要講特色：有手工普切塔、小漢堡、沙拉、主食熱食與甜點，兼顧拍照感與飽足感。",
    foodRevenue: 100000,
    softDrinkRevenue: 28000,
    alcoholRevenue: 48000,
    staffRevenue: 10000,
    decorRevenue: 26000,
    softDrinkCost: 8500,
    alcoholCost: 33000,
    staffCost: 10000,
    decorCost: 10000,
    menu: [
      ["APP019", "日式醬蛋沙拉小漢堡", "小點", 100, "份", 30, "穩定受眾"],
      ["APP020", "澳式手拍漢堡排起司小漢堡_蝦排", "小點", 100, "個", 30, "特色小漢堡"],
      ["APP026", "尼斯鮪魚奶油乳酪可頌", "小點", 120, "份", 35, "精緻冷食"],
      ["APP024", "義式 BBQ 燻煙手撕豬普切塔", "小點", 120, "份", 35, "特色鹹點"],
      ["APP035", "普羅旺斯田園鮮果核桃沙拉", "沙拉", 6, "大盆", 500, "餐檯顏色與清爽感"],
      ["MAIN005", "義式經典拿波里肉醬義大利麵", "主食", 5, "鍋", 500, "提升飽足"],
      ["MAIN008", "慢烤美式雞翅", "熱食", 4, "份", 800, "戶外派對感"],
      ["APP008", "普羅旺斯香料烤澳洲白玉薯塊", "熱食", 120, "份", 20, "補熱食量"],
      ["DST041", "季節水果香緹糖小鬆餅", "甜點", 5, "包", 300, "親子友善"],
      ["DST040", "黃金虎皮蛋糕捲", "甜點", 5, "組(36片)", 300, "切片甜點"],
    ],
  },
  {
    code: "C",
    title: "C 正餐派對版",
    positioning: "完整晚宴正餐，主食、主菜、特色小點、甜點與佈置感一起拉高",
    salesNote: "C 方案要講正餐：不是只有點心，適合正式晚宴 Party，餐點層次與主菜份量完整。",
    foodRevenue: 160000,
    softDrinkRevenue: 35000,
    alcoholRevenue: 60000,
    staffRevenue: 10000,
    decorRevenue: 35000,
    softDrinkCost: 10000,
    alcoholCost: 40000,
    staffCost: 10000,
    decorCost: 14000,
    menu: [
      ["APP021", "澳式手拍漢堡排起司小漢堡_豬肉", "小點", 120, "個", 30, "高接受度"],
      ["APP020", "澳式手拍漢堡排起司小漢堡_蝦排", "小點", 120, "個", 30, "雙口味"],
      ["APP025", "義式舒肥牛小排佐蒜香奶油醬手工普切塔", "特色小點", 120, "份", 35, "升級肉類特色"],
      ["APP029", "義式蒜味鮮蝦手工醬切塔", "特色小點", 120, "份", 40, "海鮮特色"],
      ["APP028", "法式燻燻鵝胸葡萄小串", "特色小點", 100, "份", 40, "派對感"],
      ["APP036", "季節水果小農溫室水耕沙拉盆", "沙拉", 8, "大盆", 600, "正餐蔬食平衡"],
      ["MAIN009", "鍋炒台南七股虱目魚香腸炒飯", "主食", 6, "鍋", 800, "在地感"],
      ["MAIN008", "慢烤美式雞翅", "主菜", 6, "份", 800, "主菜熱食"],
      ["MAIN007", "招牌義式炸雞腿", "主菜", 4, "方格", 800, "主菜份量"],
      ["APP012", "法式黑松露野菇烤薄餅", "特色小點", 120, "份", 20, "素食友善感"],
      ["DST045", "馬卡龍派對4.5", "甜點", 5, "組(20個)", 800, "高質感甜點"],
      ["DST041", "季節水果香緹糖小鬆餅", "甜點", 4, "包", 300, "水果甜點"],
    ],
  },
];

function money(n) {
  return Math.round(n);
}

function foodCost(plan) {
  return plan.menu.reduce((sum, row) => sum + Number(row[3]) * Number(row[5]), 0);
}

function totalRevenue(plan) {
  return plan.foodRevenue + plan.softDrinkRevenue + plan.alcoholRevenue + plan.staffRevenue + plan.decorRevenue;
}

function totalCost(plan) {
  return foodCost(plan) + plan.softDrinkCost + plan.alcoholCost + plan.staffCost + plan.decorCost;
}

function margin(revenue, cost) {
  return revenue === 0 ? 0 : (revenue - cost) / revenue;
}

function writeSection(sheet, startRow, title, rows) {
  sheet.getRange(`A${startRow}:H${startRow}`).merge();
  sheet.getRange(`A${startRow}`).values = [[title]];
  sheet.getRange(`A${startRow}`).format.fill.color = "#173F35";
  sheet.getRange(`A${startRow}`).format.font.color = "#FFFFFF";
  sheet.getRange(`A${startRow}`).format.font.bold = true;
  sheet.getRange(`A${startRow}`).format.font.size = 12;
  sheet.getRange(`A${startRow + 1}:H${startRow + rows.length}`).values = rows;
}

const workbook = Workbook.create();
const overview = workbook.worksheets.add("一頁總覽");
overview.showGridLines = false;

overview.getRange("A1:H1").merge();
overview.getRange("A1").values = [["MAPLAB A5｜尖山埤企業家庭日 200 人｜三版報價與毛利試算"]];
overview.getRange("A1").format.fill.color = "#173F35";
overview.getRange("A1").format.font.color = "#FFFFFF";
overview.getRange("A1").format.font.bold = true;
overview.getRange("A1").format.font.size = 16;

overview.getRange("A3:H3").values = [[
  "方案",
  "銷售定位",
  "餐點收入",
  "額外服務",
  "總報價",
  "餐點毛利",
  "整體毛利",
  "對客戶一句話",
]];
overview.getRange("A3:H3").format.fill.color = "#D9E6DA";
overview.getRange("A3:H3").format.font.bold = true;

const overviewRows = plans.map((plan) => {
  const fc = foodCost(plan);
  const tr = totalRevenue(plan);
  const tc = totalCost(plan);
  const addon = tr - plan.foodRevenue;
  return [
    plan.title,
    plan.positioning,
    plan.foodRevenue,
    addon,
    tr,
    margin(plan.foodRevenue, fc),
    margin(tr, tc),
    plan.salesNote,
  ];
});
overview.getRange("A4:H6").values = overviewRows;

overview.getRange("A8:H8").values = [["額外服務報價", "A", "B", "C", "說明", "", "", ""]];
overview.getRange("A8:H8").format.fill.color = "#D9E6DA";
overview.getRange("A8:H8").format.font.bold = true;
overview.getRange("A9:H12").values = [
  ["軟性飲料自助區", plans[0].softDrinkRevenue, plans[1].softDrinkRevenue, plans[2].softDrinkRevenue, "已往上調整；依品項、冰塊、杯具、現場補量微調", "", "", ""],
  ["酒精 / 行動調酒吧台", plans[0].alcoholRevenue, plans[1].alcoholRevenue, plans[2].alcoholRevenue, "先報吧台服務，不承諾車體進場；車體/啤酒車另詢廠商與場地規範", "", "", ""],
  ["服務人員", plans[0].staffRevenue, plans[1].staffRevenue, plans[2].staffRevenue, "最多 5 位；夜間 18:00-22:00，以每位每 2 小時 2,000 計", "", "", ""],
  ["叢林風餐檯佈置", plans[0].decorRevenue, plans[1].decorRevenue, plans[2].decorRevenue, "先限餐檯桌面/餐飲區；拍照區、背板、舞台另估", "", "", ""],
];

overview.getRange("A14:H14").merge();
overview.getRange("A14").values = [["報價保護說明"]];
overview.getRange("A14").format.fill.color = "#F4E3B2";
overview.getRange("A14").format.font.bold = true;
overview.getRange("A15:H18").values = [
  ["本試算使用 Items 成本欄位回推餐點毛利；主系統 Sheet 與 Apps Script 未修改。", "", "", "", "", "", "", ""],
  ["A/B/C 皆不含大型硬體、帳篷、桌椅、電力、車體進場、舞台延伸佈置與交通運送；台南尖山埤戶外動線需二次確認。", "", "", "", "", "", "", ""],
  ["酒水價格已較原 30,000 調高；若客戶指定金車 / Kavalan / 啤酒車車體，需另詢供應商與場地方規範。", "", "", "", "", "", "", ""],
  ["服務人員最多先報 5 位，需搭配自助式 Buffet 動線與餐檯集中；若要更高服務密度，需外部支援另估。", "", "", "", "", "", "", ""],
];

overview.getRange("A20:H20").values = [["外部參考連結", "用途", "連結", "", "", "", "", ""]];
overview.getRange("A20:H20").format.fill.color = "#D9E6DA";
overview.getRange("A20:H20").format.font.bold = true;
overview.getRange("A21:H29").values = [
  ["音樂行動啤酒車", "啤酒車型態參考", "https://www.musicbeercar.com/", "", "", "", "", ""],
  ["酒樂網台啤 30L", "啤酒桶 / 設備費參考", "https://chiule.com/products/%E5%8F%B0%E5%95%A4%E3%80%9030%E5%85%AC%E5%8D%87%E3%80%91/", "", "", "", "", ""],
  ["X1 行動調酒", "行動調酒公開單價參考", "https://www.x1-club.com.tw/bar.php", "", "", "", "", ""],
  ["啤酒頭膠囊生啤機", "設備租賃參考", "https://headbrewers.com.tw/beerdispenser/", "", "", "", "", ""],
  ["金車 Kavalan Whisky Bar", "品牌案例參考，非行動車報價", "https://www.kingcar.com.tw/tw/news-press-detail.aspx?serno=116", "", "", "", "", ""],
  ["蝦皮叢林風葉材", "基礎佈置採購參考", "https://shopee.tw/search?keyword=%E5%8F%A2%E6%9E%97%20%E4%BD%88%E7%BD%AE%20%E8%91%89%E5%AD%90", "", "", "", "", ""],
  ["蝦皮藤蔓", "基礎佈置採購參考", "https://shopee.tw/search?keyword=%E4%BB%BF%E7%9C%9F%20%E8%97%A4%E8%94%93%20%E4%BD%88%E7%BD%AE", "", "", "", "", ""],
  ["蝦皮木箱層架", "餐檯高低層次參考", "https://shopee.tw/search?keyword=%E6%9C%A8%E7%AE%B1%20%E5%B1%A4%E6%9E%B6%20%E4%BD%88%E7%BD%AE", "", "", "", "", ""],
  ["蝦皮草皮", "桌面 / 地面局部參考", "https://shopee.tw/search?keyword=%E4%BA%BA%E9%80%A0%E8%8D%89%E7%9A%AE%20%E4%BD%88%E7%BD%AE", "", "", "", "", ""],
];

for (const plan of plans) {
  const sheet = workbook.worksheets.add(`${plan.code}_${plan.title.replace(/^[ABC] /, "")}`);
  sheet.showGridLines = false;
  sheet.getRange("A1:H1").merge();
  sheet.getRange("A1").values = [[`${plan.title}｜餐點明細與毛利`]];
  sheet.getRange("A1").format.fill.color = "#173F35";
  sheet.getRange("A1").format.font.color = "#FFFFFF";
  sheet.getRange("A1").format.font.bold = true;
  sheet.getRange("A1").format.font.size = 15;

  sheet.getRange("A3:B8").values = [
    ["銷售定位", plan.positioning],
    ["對客戶一句話", plan.salesNote],
    ["餐點報價", plan.foodRevenue],
    ["餐點成本", foodCost(plan)],
    ["餐點毛利率", margin(plan.foodRevenue, foodCost(plan))],
    ["整體報價", totalRevenue(plan)],
  ];
  sheet.getRange("D3:E8").values = [
    ["整體成本", totalCost(plan)],
    ["整體毛利率", margin(totalRevenue(plan), totalCost(plan))],
    ["軟性飲料", plan.softDrinkRevenue],
    ["酒精/行動吧", plan.alcoholRevenue],
    ["服務人員", plan.staffRevenue],
    ["叢林風佈置", plan.decorRevenue],
  ];

  sheet.getRange("A10:H10").values = [["品項編碼", "品項", "類型", "數量", "單位", "單位成本", "成本小計", "備註"]];
  sheet.getRange("A10:H10").format.fill.color = "#D9E6DA";
  sheet.getRange("A10:H10").format.font.bold = true;
  const rows = plan.menu.map((row) => [...row.slice(0, 6), row[3] * row[5], row[6]]);
  sheet.getRange(`A11:H${10 + rows.length}`).values = rows;

  const addOnRows = [
    ["軟性飲料自助區", plan.softDrinkRevenue, plan.softDrinkCost, margin(plan.softDrinkRevenue, plan.softDrinkCost), "含杯具、冰塊、補量，實際依品項調整"],
    ["酒精 / 行動調酒吧台", plan.alcoholRevenue, plan.alcoholCost, margin(plan.alcoholRevenue, plan.alcoholCost), "先報吧台服務，不承諾車體進場"],
    ["服務人員", plan.staffRevenue, plan.staffCost, margin(plan.staffRevenue, plan.staffCost), "最多 5 位，每位每 2 小時 2,000"],
    ["叢林風餐檯佈置", plan.decorRevenue, plan.decorCost, margin(plan.decorRevenue, plan.decorCost), "餐檯/餐飲區，不含大型背板與舞台"],
  ];
  const start = 13 + rows.length;
  writeSection(sheet, start, "額外服務", [["項目", "報價", "估成本", "毛利率", "說明", "", "", ""], ...addOnRows.map((r) => [r[0], r[1], r[2], r[3], r[4], "", "", ""])]);
  sheet.getRange(`A${start + 1}:H${start + 1}`).format.fill.color = "#D9E6DA";
  sheet.getRange(`A${start + 1}:H${start + 1}`).format.font.bold = true;

  sheet.getRange("A:A").format.columnWidthPx = 110;
  sheet.getRange("B:B").format.columnWidthPx = 280;
  sheet.getRange("C:D").format.columnWidthPx = 90;
  sheet.getRange("E:H").format.columnWidthPx = 120;
  sheet.getRange("A1:H40").format.wrapText = true;
  sheet.getRange("B5:B8").format.numberFormat = "#,##0";
  sheet.getRange("E3:E8").format.numberFormat = "#,##0";
  sheet.getRange("B7").format.numberFormat = "0.0%";
  sheet.getRange("E4").format.numberFormat = "0.0%";
}

overview.getRange("C4:E12").format.numberFormat = "#,##0";
overview.getRange("F4:G6").format.numberFormat = "0.0%";
overview.getRange("A:H").format.wrapText = true;
overview.getRange("A:A").format.columnWidthPx = 180;
overview.getRange("B:B").format.columnWidthPx = 300;
overview.getRange("C:G").format.columnWidthPx = 115;
overview.getRange("H:H").format.columnWidthPx = 360;
overview.freezePanes.freezeRows(3);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);

const tableCheck = await workbook.inspect({
  kind: "table",
  range: "一頁總覽!A1:H18",
  include: "values,formulas",
  tableMaxRows: 18,
  tableMaxCols: 8,
});
console.log(tableCheck.ndjson);

await fs.mkdir(outputDir, { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);
console.log(`saved ${outputPath}`);
