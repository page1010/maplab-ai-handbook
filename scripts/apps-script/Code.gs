/**
 * MAPLAB 報價系統 v3.4
 * 修正：品項名稱格式、客戶資訊欄位、毛利率驗證、禮盒殘留資料
 *   - Bug1: D欄品項名寫入格式改為「品名 (item_id)」+ G欄qty
 *   - Bug2: D2 只寫 clientName，company 不混入
 *   - Bug3: D3 = location || address
 *   - Bug4: D5 自動組合活動名稱
 *   - Bug5: F5 = 品項總數
 *   - Bug6: 整體毛利率驗證 ≥ minMargin，不合格直接拋錯
 *   - Bug7: makeCopy 後清空 D18:D19
 * 前版：v3.3 cell reference 修正
 *
 * 部署目標 Sheet：1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
 * 模板分頁：QUOTE_DRAFT
 * 寫入分頁：SALES_INTAKE
 *
 * QUOTE_DRAFT v3 版面對應：
 *   D2: 客戶名（企業版：公司名 + 聯絡人）
 *   E2: 活動日期
 *   D3: 地址
 *   E3: 時間（v3.3 修正：原錯寫 F3）
 *   D4: 活動型態
 *   F4: 規劃人數
 *   D5: 活動名稱
 *   F5: 餐點總件數
 *   D8:D10  appetizer 鹹食品名（3格）
 *   D12:D14 dessert 甜點品名（3格）
 *   D15:D16 飲品品名（2格）
 *   G欄: qty, I欄: 單位成本
 *   K1: Case ID
 *   K2: 建立時間
 *   K3: 報價狀態（dropdown 保留）
 *   K4: 匯款狀態（dropdown 保留）
 *   K5: 版本
 *   B33: 【合約條款】（template 已有，不覆寫）
 *   B34: 條款內容（v3.3 修正：原錯寫 C40）
 *   E29: 總金額, H29: 訂單成本標籤, H30: 毛利率標籤, I30: 毛利率%
 *
 * Items 分頁欄位（A=序號, B=品名, C=品類, D=售價, E=成本, K=圖片URL）
 */

var SPREADSHEET_ID      = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg';
var TEMPLATE_SHEET_NAME = 'QUOTE_DRAFT';
var INTAKE_SHEET_NAME   = 'SALES_INTAKE';
var DRIVE_ROOT_FOLDER   = 'MAPLAB_報價單';

// 菜單品項在 QUOTE_DRAFT 的列範圍（v3.3 對照 Chrome 截圖修正）
var APPETIZER_ROWS = { start: 8,  end: 10 };  // 鹹食 appetizer D8:D10（3 格）
var DESSERT_ROWS   = { start: 12, end: 14 };  // 甜點 dessert D12:D14（3 格）
var DRINK_ROWS     = { start: 15, end: 16 };  // 飲品 D15:D16（2 格）

// ─────────────────────────────────────────
// 選單 & 入口
// ─────────────────────────────────────────

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('MAPLAB')
    .addItem('產出報價單', 'showQuoteForm')
    .addSeparator()
    .addItem('產出 Slide 提案', 'createSlidesFromSheet')
    .addToUi();
}

function showQuoteForm() {
  var html = HtmlService.createHtmlOutputFromFile('QuoteForm')
    .setWidth(500)
    .setHeight(680)
    .setTitle('新建報價單');
  SpreadsheetApp.getUi().showModalDialog(html, '新建報價單');
}

// ─────────────────────────────────────────
// debug endpoint
// ─────────────────────────────────────────

/**
 * action:"debugItems" — 回傳 Items 分頁前 20 行原始資料（用於排查 D 欄寫不進去）
 */
function handleDebugItems_() {
  try {
    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    var sheet = ss.getSheetByName('Items');
    if (!sheet) {
      return ContentService.createTextOutput(JSON.stringify({ error: 'Items sheet not found' }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    var lastRow = sheet.getLastRow();
    var lastCol = sheet.getLastColumn();
    var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
    var sampleRows = lastRow > 1 ? sheet.getRange(2, 1, Math.min(20, lastRow - 1), lastCol).getValues() : [];
    var rows = sampleRows.map(function(r) {
      var obj = {};
      headers.forEach(function(h, i) { obj[h || 'col'+(i+1)] = r[i]; });
      // 額外標出 code 讀取的欄位
      obj['_code_A_itemId'] = r[0];
      obj['_code_B_name']   = r[1];
      obj['_code_C_cat']    = r[2];
      obj['_code_D_price']  = r[3];
      obj['_code_E_cost']   = r[4];
      return obj;
    });
    return ContentService.createTextOutput(JSON.stringify({
      sheetName: sheet.getName(),
      lastRow: lastRow,
      lastCol: lastCol,
      headers: headers,
      rows: rows
    })).setMimeType(ContentService.MimeType.JSON);
  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({ error: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// 主程式：createQuote()
// ─────────────────────────────────────────

/**
 * 由 HTML 表單或 handleQuoteRequest_ 呼叫
 *
 * @param {Object} formData
 *   .clientName  {string} 客戶名稱（必填）
 *   .company     {string} 公司名稱（選填，有 = 企業版條款）
 *   .phone       {string} 聯絡電話（選填）
 *   .eventType   {string} 活動型態（必填）
 *   .eventDate   {string} 活動日期 YYYY-MM-DD（必填）
 *   .eventTime   {string} 活動時間 ex. "15:00-17:00"（選填）
 *   .eventName   {string} 活動名稱（選填）
 *   .location    {string} 活動地點（選填）
 *   .address     {string} 活動地址（選填）
 *   .pax         {string|number} 規劃人數（選填）
 *   .totalItems  {string|number} 餐點總件數（選填）
 *   .budget      {number} 總預算（選填，有則執行品項篩選）
 *   .itemCount   {number} 品項數量需求（選填，預設 8）
 *   .minMargin   {number} 最低毛利率 0~1（選填，預設 0.7）
 *   .style       {string} "tea_time"=甜鹹均衡 / "savory"=鹹食為主 / "sweet"=甜點為主（選填）
 * @returns {Object} { success, caseId, fileName, url }
 */
function createQuote(formData) {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);

  // ── 產生 case_id ──
  var now    = new Date();
  var caseId = 'Q' + Utilities.formatDate(now, 'Asia/Taipei', 'yyyyMMddHHmmss');

  // ── 格式化活動日期 ──
  var eventDate  = new Date(formData.eventDate + 'T00:00:00+08:00');
  var dateSuffix = Utilities.formatDate(eventDate, 'Asia/Taipei', 'yyyyMMdd');

  // ── 新檔案名稱：20260425_王小明 ──
  var newFileName = dateSuffix + '_' + formData.clientName;

  // ── 確保 Drive 資料夾存在 ──
  var yearFolder = ensureDriveFolder_(eventDate.getFullYear().toString());

  // ── 用 makeCopy 複製整個 Spreadsheet ──
  var sourceFile = DriveApp.getFileById(SPREADSHEET_ID);
  var newFile    = sourceFile.makeCopy(newFileName, yearFolder);
  var newSs      = SpreadsheetApp.openById(newFile.getId());

  // ── 找出要保留的分頁 ──
  var sheets        = newSs.getSheets();
  var keepSheet     = null;
  var newItemsSheet = null;
  for (var i = 0; i < sheets.length; i++) {
    if (sheets[i].getName() === TEMPLATE_SHEET_NAME) keepSheet     = sheets[i];
    if (sheets[i].getName() === 'Items')             newItemsSheet = sheets[i];
  }
  if (!keepSheet) throw new Error('新檔案中找不到 QUOTE_DRAFT 分頁。');

  // v3.5 修正：從原始 ss 讀 Items，避免複製後公式失效（price=0 → 全部被過濾 → D欄空白）
  var itemsSheet = ss.getSheetByName('Items');

  // ── 先 activate 保留分頁，再批次刪除其餘分頁 ──
  newSs.setActiveSheet(keepSheet);
  var sheetsToDelete = [];
  for (var i = 0; i < sheets.length; i++) {
    var n = sheets[i].getName();
    if (n !== TEMPLATE_SHEET_NAME && n !== 'Items') sheetsToDelete.push(sheets[i]);
  }
  for (var j = 0; j < sheetsToDelete.length; j++) {
    try { newSs.deleteSheet(sheetsToDelete[j]); } catch(e) { Logger.log('刪除分頁失敗: ' + e.message); }
  }

  // ── 改名 QUOTE_DRAFT → 報價單 ──
  keepSheet.setName('報價單');

  // ── 隱藏 Items 分頁（保留 VLOOKUP） ──
  if (newItemsSheet) newItemsSheet.hideSheet();

  // ── 填入客戶資訊（對應 QUOTE_DRAFT v3 版面） ──
  // Bug2 修正：D2 只寫 clientName，company 不混入
  keepSheet.getRange('D2').setValue(formData.clientName || '');
  keepSheet.getRange('E2').setValue(formData.eventDate || '');
  // Bug3 修正：D3 = location || address
  keepSheet.getRange('D3').setValue(formData.location || formData.address || '');
  keepSheet.getRange('E3').setValue(formData.eventTime || '');  // v3.3 修正：原錯寫 F3
  keepSheet.getRange('D4').setValue(formData.eventType || '');
  keepSheet.getRange('F4').setValue(formData.pax       || '');
  // Bug4 修正：D5 = eventName 或自動組合
  var autoEventName = formData.eventName ||
    ((formData.clientName || '') + ' ' + (formData.eventType || '') + ' ' + (formData.eventDate || '')).trim();
  keepSheet.getRange('D5').setValue(autoEventName);
  keepSheet.getRange('F5').setValue(formData.totalItems|| '');

  // ── 系統資訊寫入 K 欄（列印範圍外） ──
  keepSheet.getRange('K1').setValue(caseId);
  keepSheet.getRange('K2').setValue(Utilities.formatDate(now, 'Asia/Taipei', 'yyyy-MM-dd HH:mm'));
  keepSheet.getRange('K3').setValue('報價中');
  keepSheet.getRange('K4').setValue('未匯');
  keepSheet.getRange('K5').setValue('v1');

  // K3 下拉驗證：報價狀態
  keepSheet.getRange('K3').setDataValidation(
    SpreadsheetApp.newDataValidation()
      .requireValueInList(['報價中', '成交', '未成交結案'], true)
      .setAllowInvalid(false).build()
  );
  // K4 下拉驗證：匯款狀態
  keepSheet.getRange('K4').setDataValidation(
    SpreadsheetApp.newDataValidation()
      .requireValueInList(['未匯', '已收訂金', '已收全額'], true)
      .setAllowInvalid(false).build()
  );

  // ── 清除 D 欄品項區的 dropdown 驗證（D8:D19，含 D18:D19 禮盒格） ──
  keepSheet.getRange('D8:D19').clearDataValidations();
  // Bug7 修正：清空 D18:D19 禮盒殘留模板資料
  keepSheet.getRange('D18:D19').clearContent();

  // ── 若有傳入預算，自動篩選品項寫入菜單區 ──
  if (formData.budget && itemsSheet) {
    var paxNum = Number(formData.pax) || 1;
    var selected = selectItemsForBudget_(itemsSheet, {
      budget:    Number(formData.budget),
      pax:       paxNum,
      itemCount: Number(formData.itemCount) || 8,
      minMargin: Number(formData.minMargin) || 0.7,
      style:     formData.style || 'tea_time'
    });
    writeItemsToQuote_(keepSheet, selected, paxNum);
    // Bug5 修正 v3.6：F5 = 餐點總件數（所有 G 欄數量加總），非品項種類數
    keepSheet.getRange('F5').setFormula('=SUM(G8:G10,G12:G16)');
  }

  // ── 條款寫入 B34（v3.3 修正：B33=【合約條款】template 已有，B34 寫內容） ──
  var isCorporate = formData.company && formData.company.trim().length > 0;
  var terms = isCorporate ? getCorpTerms(eventDate) : getPersonalTerms();
  // B33 的【合約條款】標籤由 template 提供，此處直接寫 B34 內容
  keepSheet.getRange('B34').setValue(terms)
    .setWrap(true)
    .setFontSize(9)
    .setVerticalAlignment('top');

  // 確保條款行可見（取消隱藏 33-45）
  keepSheet.showRows(33, 15);

  // ── 回傳新檔案 URL ──
  var newUrl = newSs.getUrl();

  // ── 寫入 SALES_INTAKE ──
  writeToIntake_(ss, caseId, formData, newUrl, now);

  return { success: true, caseId: caseId, fileName: newFileName, url: newUrl,
           _debug: { appetizers: selected ? selected.appetizers.length : 'budget not set',
                     desserts:   selected ? selected.desserts.length   : 'budget not set' } };
}

// ─────────────────────────────────────────
// 【新增 問題 1+2】品項篩選：selectItemsForBudget_
// ─────────────────────────────────────────

/**
 * 從 Items 分頁根據預算、人數、品項數量、毛利率篩選品項
 *
 * Items 分頁欄位：
 *   A: 序號, B: 品名, C: 品類（鹹/甜/飲品）, D: 售價, E: 成本, K: 圖片URL
 *
 * @param {Sheet}  itemsSheet  Items 分頁物件
 * @param {Object} params
 *   .budget    {number} 總預算
 *   .pax       {number} 人數
 *   .itemCount {number} 品項總數量
 *   .minMargin {number} 最低毛利率 0~1（預設 0.7）
 *   .style     {string} "tea_time"=甜鹹均衡 / "savory"=鹹食為主 / "sweet"=甜點為主
 * @returns {Object} { appetizers: [...], desserts: [...] }
 *   每個品項：{ name, price, cost, margin, imageUrl, category }
 */
function selectItemsForBudget_(itemsSheet, params) {
  var budget    = params.budget;
  var pax       = params.pax    || 1;
  var itemCount = params.itemCount || 8;
  var minMargin = params.minMargin || 0.7;
  var style     = params.style  || 'tea_time';

  // 每人預算
  var perPersonBudget = budget / pax;

  // 讀取 Items 資料（第 2 行起）
  var lastRow = itemsSheet.getLastRow();
  if (lastRow < 2) return { appetizers: [], desserts: [] };

  // v3.5 修正：欄位以實際 Items 分頁 header 為準
  // A=item_id, B=category（餐食小點/甜點/飲品）, C=standard_name（品名）
  // D=default_price（可能為空）, E=default_cost（成本）, I=active, K=image_url
  var data = itemsSheet.getRange(2, 1, lastRow - 1, 11).getValues();

  var allItems = [];
  for (var i = 0; i < data.length; i++) {
    var itemId   = String(data[i][0]).trim();  // A: item_id
    var category = String(data[i][1]).trim();  // B: category
    var name     = String(data[i][2]).trim();  // C: standard_name（品名）
    var price    = Number(data[i][3]);         // D: default_price（售價，可能為空）
    var cost     = Number(data[i][4]);         // E: default_cost（成本）
    var active   = String(data[i][8]).trim();  // I: active（Y/N）
    var imageUrl = data[i][10];                // K: image_url

    if (!name || !itemId) continue;
    if (active && active !== 'Y') continue;
    if (!cost || cost <= 0) continue;

    // 若沒有 default_price，依 minMargin 反推最低售價
    if (!price || price <= 0) {
      price = cost / (1 - minMargin);
    }

    var margin = (price - cost) / price;

    allItems.push({ id: itemId, name: name, price: price, cost: cost, margin: margin, imageUrl: imageUrl, category: category });
  }

  Logger.log('[selectItemsForBudget_] 讀取 ' + data.length + ' 列，有效品項：' + allItems.length + ' 項');
  if (allItems.length > 0) {
    Logger.log('品類分布：' + allItems.map(function(x){return x.category;}).join(', '));
  }

  if (allItems.length === 0) return { appetizers: [], desserts: [] };

  // 依風格決定甜/鹹比例
  var appetizerCount, dessertCount;
  if (style === 'tea_time') {
    appetizerCount = Math.ceil(itemCount * 0.55);   // 約 55% 鹹食
    dessertCount   = itemCount - appetizerCount;    // 約 45% 甜點
  } else if (style === 'savory') {
    appetizerCount = Math.ceil(itemCount * 0.8);
    dessertCount   = itemCount - appetizerCount;
  } else if (style === 'sweet') {
    dessertCount   = Math.ceil(itemCount * 0.7);
    appetizerCount = itemCount - dessertCount;
  } else {
    appetizerCount = Math.ceil(itemCount * 0.55);
    dessertCount   = itemCount - appetizerCount;
  }

  // 分類（v3.5：Items 分頁 category 實際值為「餐食小點」「甜點」「飲品」等）
  var savoryPool  = allItems.filter(function(x) {
    return x.category === '鹹' || x.category === '鹹食' || x.category === 'appetizer' ||
           x.category === '餐食小點' || x.category === '鹹點';
  });
  var sweetPool   = allItems.filter(function(x) {
    return x.category === '甜' || x.category === '甜點' || x.category === 'dessert' ||
           x.category === '甜點小點' || x.category === '甜食' || x.category === '西點';
  });

  // 若分類不足，從 allItems 補充
  if (savoryPool.length < appetizerCount) savoryPool = allItems.filter(function(x) { return sweetPool.indexOf(x) === -1; });
  if (sweetPool.length < dessertCount)   sweetPool  = allItems.filter(function(x) { return savoryPool.indexOf(x) === -1; });

  // 依售價從低到高排序（預算最佳化）
  savoryPool.sort(function(a, b) { return a.price - b.price; });
  sweetPool.sort(function(a, b)  { return a.price - b.price; });

  // 計算可用預算（每人）下的品項目標單價上限
  var pricePerItem = perPersonBudget / itemCount;

  // 篩選：price ≤ pricePerItem * 1.3（容許 30% 彈性）
  var priceLimit = pricePerItem * 1.3;
  var selected_s = savoryPool.filter(function(x) { return x.price <= priceLimit; }).slice(0, appetizerCount);
  var selected_d = sweetPool.filter(function(x)  { return x.price <= priceLimit; }).slice(0, dessertCount);

  // 若嚴格預算篩不夠，就取最便宜的
  if (selected_s.length < appetizerCount) selected_s = savoryPool.slice(0, appetizerCount);
  if (selected_d.length < dessertCount)   selected_d = sweetPool.slice(0, dessertCount);

  Logger.log('品項篩選完成：鹹食 ' + selected_s.length + ' 項，甜點 ' + selected_d.length + ' 項');
  Logger.log('預算 ' + budget + '，人數 ' + pax + '，每人預算 ' + perPersonBudget.toFixed(0) + '，每項均攤 ' + pricePerItem.toFixed(0));

  // 整體毛利率 log（v3.5：price 可能是反推值，僅供 debug）
  var allSelected = selected_s.concat(selected_d);
  if (allSelected.length > 0) {
    var totalRevenue = 0, totalCost = 0;
    for (var k = 0; k < allSelected.length; k++) {
      totalRevenue += allSelected[k].price;
      totalCost    += allSelected[k].cost;
    }
    var overallMargin = totalRevenue > 0 ? (totalRevenue - totalCost) / totalRevenue : 0;
    Logger.log('整體毛利率：' + (overallMargin * 100).toFixed(1) + '%，最低要求：' + (minMargin * 100).toFixed(0) + '%');
  }

  return { appetizers: selected_s, desserts: selected_d };
}

/**
 * 把篩選結果寫入 QUOTE_DRAFT 菜單區
 * Bug1 修正：D 欄格式「品名 (item_id)」，G 欄寫 qty（=pax），I 欄寫成本
 * @param {Sheet}  sheet    keepSheet（已重命名為報價單）
 * @param {Object} selected { appetizers: [...], desserts: [...] }
 * @param {number} pax      人數（G 欄 qty）
 */
function writeItemsToQuote_(sheet, selected, pax) {
  var appetizers = selected.appetizers || [];
  var desserts   = selected.desserts   || [];
  var qty        = pax || 1;
  var maxSlots   = APPETIZER_ROWS.end - APPETIZER_ROWS.start + 1;  // 3
  var maxDSlots  = DESSERT_ROWS.end   - DESSERT_ROWS.start + 1;    // 3

  Logger.log('[writeItemsToQuote_] appetizers=' + appetizers.length + ' desserts=' + desserts.length + ' qty=' + qty);

  // Bug修正 v3.6：先用 setValue('') 清空所有品項列（含飲品列），
  // 確保模板殘留值或公式被覆蓋（clearContent 對公式格無效）
  var allItemRows = [8, 9, 10, 12, 13, 14, 15, 16];
  for (var k = 0; k < allItemRows.length; k++) {
    var r = allItemRows[k];
    sheet.getRange('D' + r).setValue('');
    sheet.getRange('G' + r).setValue('');
    sheet.getRange('I' + r).setValue('');
  }

  // 寫 appetizer D8:D10
  for (var i = 0; i < maxSlots; i++) {
    var row  = APPETIZER_ROWS.start + i;
    var item = appetizers[i];
    if (item) {
      var displayName = item.id ? item.name + ' (' + item.id + ')' : item.name;
      sheet.getRange('D' + row).setValue(displayName);
      sheet.getRange('G' + row).setValue(qty);
      sheet.getRange('I' + row).setValue(item.cost);
      Logger.log('寫入 D' + row + '：' + displayName + ' G=' + qty + ' I=' + item.cost);
    }
  }

  // 寫 dessert D12:D14
  for (var j = 0; j < maxDSlots; j++) {
    var dRow  = DESSERT_ROWS.start + j;
    var dItem = desserts[j];
    if (dItem) {
      var dDisplayName = dItem.id ? dItem.name + ' (' + dItem.id + ')' : dItem.name;
      sheet.getRange('D' + dRow).setValue(dDisplayName);
      sheet.getRange('G' + dRow).setValue(qty);
      sheet.getRange('I' + dRow).setValue(dItem.cost);
      Logger.log('寫入 D' + dRow + '：' + dDisplayName + ' G=' + qty + ' I=' + dItem.cost);
    }
  }

  Logger.log('品項已寫入 QUOTE_DRAFT 菜單區（含 D 格式、G qty=' + qty + '、I 成本）');
}

// ─────────────────────────────────────────
// 表單預填資料
// ─────────────────────────────────────────

function getQuoteDraftValues() {
  var ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(TEMPLATE_SHEET_NAME);
  if (!sheet) return {};

  return {
    clientName : sheet.getRange('D2').getValue() || '',
    eventDate  : sheet.getRange('E2').getValue()
                   ? Utilities.formatDate(new Date(sheet.getRange('E2').getValue()), 'Asia/Taipei', 'yyyy-MM-dd')
                   : '',
    address    : sheet.getRange('D3').getValue() || '',
    eventTime  : sheet.getRange('E3').getValue() || '',  // v3.3 修正：原錯寫 F3
    eventType  : sheet.getRange('D4').getValue() || '',
    pax        : sheet.getRange('F4').getValue() || '',
    eventName  : sheet.getRange('D5').getValue() || '',
    totalItems : sheet.getRange('F5').getValue() || ''
  };
}

// ─────────────────────────────────────────
// 條款文字
// ─────────────────────────────────────────

function getPersonalTerms() {
  return [
    '匯款資訊如下：',
    '中國信託822 / 西台南分行',
    '帳號：222510859464',
    '戶名：莊貴棻',
    '匯款後，再麻煩提供後五碼對帳。如需收據請提前告知，當日會附上。',
    '',
    '（1）已保留檔期，預約付訂後取消，欲收取訂金50%作為成本取消費',
    '（2）用餐日期14天內取消（或變更），收取訂金80%作為食材成本取消費',
    '（3）用餐當日取消（或變更），收取訂金100%作為取消與變更費'
  ].join('\n');
}

function getCorpTerms(eventDate) {
  var year  = eventDate.getFullYear();
  var month = eventDate.getMonth() + 1;
  var day   = eventDate.getDate();
  return [
    '▶簽約使用條款及細則：',
    '（1）鑒於部分企業用戶之會計核銷，此合約僅供公司行號使用。',
    '（2）本合約代表雙方對於' + year + '年' + month + '月' + day + '日之活動做出預約，並確認保留檔期。',
    '（3）已保留之檔期，如有於十日內取消服務之情事，須支付活動合約總金額之20%材料損失費。',
    '（4）活動當日取消（或臨時有地點、菜色、時間之變更），將酌情形額外收取費用。',
    '',
    '‣活動指定地點如超過30分鐘距離須收取車馬費，諮詢依地區實際公里數各別報價。',
    '‣擺設場地有樓層必須預先告知，2F以上無電梯須收取$1,000搬運費，有人協助收取$500元搬運費。',
    ' 若當日電梯因故無法使用，則現場以現金加收$1,000樓層搬運費。'
  ].join('\n');
}

// ─────────────────────────────────────────
// 內部工具函式
// ─────────────────────────────────────────

function ensureDriveFolder_(year) {
  var rootIter   = DriveApp.getFoldersByName(DRIVE_ROOT_FOLDER);
  var rootFolder = rootIter.hasNext() ? rootIter.next() : DriveApp.createFolder(DRIVE_ROOT_FOLDER);
  var yearIter   = rootFolder.getFoldersByName(year);
  return yearIter.hasNext() ? yearIter.next() : rootFolder.createFolder(year);
}

/**
 * 在 SALES_INTAKE 最後一行新增報價紀錄
 * A: case_id, B: created_at, C: source, D: client_name, E: company,
 * F: phone, G: event_type, H: event_date, I: location, J: pax,
 * K: sheet_url, L: quote_status, M: payment_status, N: (預留), O: notes
 */
function writeToIntake_(ss, caseId, formData, sheetUrl, now) {
  var intakeSheet = ss.getSheetByName(INTAKE_SHEET_NAME);
  if (!intakeSheet) throw new Error('找不到 SALES_INTAKE 分頁。');

  var createdAt = Utilities.formatDate(now, 'Asia/Taipei', 'yyyy-MM-dd HH:mm:ss');
  intakeSheet.appendRow([
    caseId,
    createdAt,
    'quote-system-v3.4',
    formData.clientName,
    formData.company    || '',
    formData.phone      || '',
    formData.eventType  || '',
    formData.eventDate  || '',
    formData.location   || '',
    formData.pax        || '',
    sheetUrl,
    '報價中',
    '未匯',
    '',
    ''
  ]);
}

// ─────────────────────────────────────────
// T-A5-005：報價狀態同步 + Dashboard
// ─────────────────────────────────────────

function ensureIntakeHeaders_() {
  var ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(INTAKE_SHEET_NAME);
  if (!sheet) return;
  if (!sheet.getRange('L1').getValue()) sheet.getRange('L1').setValue('quote_status');
  if (!sheet.getRange('M1').getValue()) sheet.getRange('M1').setValue('payment_status');
}

/**
 * 掃描 SALES_INTAKE K 欄 → 打開每份報價單 → 讀 K3/K4 → 寫回 L/M
 * 注意：v3.2 狀態位置改為 K3（報價狀態）/ K4（匯款狀態）
 */
function syncQuoteStatus_() {
  var ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(INTAKE_SHEET_NAME);
  if (!sheet) return;

  ensureIntakeHeaders_();

  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  var kValues  = sheet.getRange(2, 11, lastRow - 1, 1).getValues();
  var lmValues = sheet.getRange(2, 12, lastRow - 1, 2).getValues();
  var updates  = [];

  for (var i = 0; i < kValues.length; i++) {
    var url = kValues[i][0];
    if (!url || typeof url !== 'string' || url.indexOf('https://') !== 0) {
      updates.push([lmValues[i][0], lmValues[i][1]]);
      continue;
    }
    try {
      var quoteId      = extractSpreadsheetId_(url);
      var quoteSs      = SpreadsheetApp.openById(quoteId);
      var quoteSheet   = quoteSs.getSheetByName('報價單') || quoteSs.getSheets()[0];
      var quoteStatus  = quoteSheet.getRange('K3').getValue();  // v3.2: K3
      var paymentStatus = quoteSheet.getRange('K4').getValue(); // v3.2: K4
      updates.push([quoteStatus || '', paymentStatus || '']);
    } catch (e) {
      Logger.log('無法同步列 ' + (i + 2) + '：' + e.message);
      updates.push([lmValues[i][0], lmValues[i][1]]);
    }
  }

  if (updates.length > 0) sheet.getRange(2, 12, updates.length, 2).setValues(updates);
  Logger.log('syncQuoteStatus_ 完成，共掃描 ' + updates.length + ' 筆');
}

function extractSpreadsheetId_(url) {
  var match = url.match(/\/spreadsheets\/d\/([a-zA-Z0-9_-]+)/);
  if (!match) throw new Error('無法解析 Spreadsheet URL: ' + url);
  return match[1];
}

function setupSyncTrigger() {
  ensureIntakeHeaders_();
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'syncQuoteStatus_') {
      Logger.log('syncQuoteStatus_ trigger 已存在，跳過');
      return;
    }
  }
  ScriptApp.newTrigger('syncQuoteStatus_').timeBased().everyMinutes(30).create();
  Logger.log('已建立 syncQuoteStatus_ 每 30 分鐘 trigger');
}

function removeSyncTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'syncQuoteStatus_') {
      ScriptApp.deleteTrigger(triggers[i]);
      Logger.log('已刪除 syncQuoteStatus_ trigger');
    }
  }
}

function setupDashboard() {
  var ss   = SpreadsheetApp.openById(SPREADSHEET_ID);
  var dash = ss.getSheetByName('Dashboard') || ss.insertSheet('Dashboard');
  dash.clearContents();

  dash.getRange('A1').setValue('MAPLAB 報價 Dashboard').setFontWeight('bold').setFontSize(14);
  dash.getRange('A3').setValue('最後更新');
  dash.getRange('B3').setFormula('=NOW()');

  dash.getRange('A5').setValue('報價狀態').setFontWeight('bold');
  dash.getRange('A6').setValue('報價中');
  dash.getRange('A7').setValue('成交');
  dash.getRange('A8').setValue('未成交結案');
  dash.getRange('B6').setFormula('=COUNTIF(SALES_INTAKE!L:L,"報價中")');
  dash.getRange('B7').setFormula('=COUNTIF(SALES_INTAKE!L:L,"成交")');
  dash.getRange('B8').setFormula('=COUNTIF(SALES_INTAKE!L:L,"未成交結案")');

  dash.getRange('A10').setValue('匯款狀態').setFontWeight('bold');
  dash.getRange('A11').setValue('未匯');
  dash.getRange('A12').setValue('已收訂金');
  dash.getRange('A13').setValue('已收全額');
  dash.getRange('B11').setFormula('=COUNTIF(SALES_INTAKE!M:M,"未匯")');
  dash.getRange('B12').setFormula('=COUNTIF(SALES_INTAKE!M:M,"已收訂金")');
  dash.getRange('B13').setFormula('=COUNTIF(SALES_INTAKE!M:M,"已收全額")');

  dash.getRange('A15').setValue('總報價筆數').setFontWeight('bold');
  dash.getRange('B15').setFormula('=COUNTA(SALES_INTAKE!A:A)-1');

  Logger.log('Dashboard 分頁已建立/更新');
}

// ─────────────────────────────────────────
// doPost 報價入口（LINE Bot 透過 HTTP POST 呼叫）
// ─────────────────────────────────────────

/**
 * 由 LineWebhook.gs 的 doPost 路由呼叫
 *
 * @param {Object} params
 *   .action      {string}  "createQuote"（必要）
 *   .clientName  {string}  客戶名稱（必填）
 *   .eventType   {string}  活動型態（必填）
 *   .eventDate   {string}  活動日期 YYYY-MM-DD（必填）
 *   .company     {string}  公司名稱（選填）
 *   .phone       {string}  聯絡電話（選填）
 *   .address     {string}  活動地址（選填）
 *   .eventTime   {string}  活動時間（選填）
 *   .eventName   {string}  活動名稱（選填）
 *   .location    {string}  活動地點（選填）
 *   .pax         {string}  規劃人數（選填）
 *   .totalItems  {string}  餐點總件數（選填）
 *   ── 品項篩選參數（選填，有 budget 才執行品項篩選）──
 *   .budget      {number}  總預算
 *   .itemCount   {number}  品項數量（預設 8）
 *   .minMargin   {number}  最低毛利率 0~1（預設 0.7）
 *   .style       {string}  "tea_time" / "savory" / "sweet"（預設 "tea_time"）
 */
function handleQuoteRequest_(params) {
  try {
    var formData = {
      clientName : params.clientName  || '',
      company    : params.company     || '',
      phone      : params.phone       || '',
      address    : params.address     || '',
      eventType  : params.eventType   || '',
      eventDate  : params.eventDate   || '',
      eventTime  : params.eventTime   || '',
      eventName  : params.eventName   || '',
      location   : params.location    || '',
      pax        : params.pax         || '',
      totalItems : params.totalItems  || '',
      // 品項篩選參數
      budget     : params.budget      || null,
      itemCount  : params.itemCount   || 8,
      minMargin  : params.minMargin   || 0.7,
      style      : params.style       || 'tea_time'
    };

    var result = createQuote(formData);

    return ContentService.createTextOutput(JSON.stringify({
      success  : true,
      caseId   : result.caseId,
      fileName : result.fileName,
      url      : result.url
    })).setMimeType(ContentService.MimeType.JSON);

  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error  : err.message
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
