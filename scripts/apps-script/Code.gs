/**
 * MAPLAB 報價系統 v3.8
 * 修正：createQuote 客戶區 cell reference 回到接手前版本（B2:B9 / H1-H2 / M/N 欄 / A30-A31 條款）
 * 保留：doPost 路由（LineWebhook.gs）/ handleQuoteRequest_ / selectItemsForBudget_ / writeItemsToQuote_
 *
 * 部署目標 Sheet：1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
 * 模板分頁：QUOTE_DRAFT
 * 寫入分頁：SALES_INTAKE
 *
 * QUOTE_DRAFT v3.1 版面對應（接手前版本）：
 *   B2: 客戶名稱
 *   B3: 公司名稱
 *   B4: 聯絡電話
 *   B5: 活動地址
 *   B6: 活動型態
 *   B7: 活動日期
 *   B8: 預計人數
 *   B9: 活動地點
 *   H1: Case ID
 *   H2: 建立時間
 *   M2/N2: CaseID
 *   M3/N3: 建立時間
 *   M5/N5: 報價狀態（dropdown）
 *   M7/N7: 匯款狀態（dropdown）
 *   M9/N9: 版本
 *   A30: 【合約條款】
 *   A31: 條款內容
 *
 * Items 分頁欄位（A=item_id, B=category, C=standard_name, D=default_price, E=default_cost, K=image_url）
 * 菜單品項寫入位置：D8:D10（鹹食）/ D12:D14（甜點） + G欄（qty）
 */

var SPREADSHEET_ID      = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg';
var TEMPLATE_SHEET_NAME = 'QUOTE_DRAFT';
var INTAKE_SHEET_NAME   = 'SALES_INTAKE';
var DRIVE_ROOT_FOLDER   = 'MAPLAB_報價單';

// 菜單品項在 QUOTE_DRAFT 的列範圍（接手前版本對照）
var APPETIZER_ROWS = { start: 8,  end: 10 };  // 鹹食 D8:D10（3 格）
var DESSERT_ROWS   = { start: 12, end: 14 };  // 甜點 D12:D14（3 格）
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
 * action:"debugItems" — 回傳 Items 分頁前 20 行原始資料
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

// ─────────────────────────────────────────
// 主程式：createQuote()
// ─────────────────────────────────────────

/**
 * 由 HTML 表單或 handleQuoteRequest_ 呼叫，產出獨立報價單 Spreadsheet
 *
 * @param {Object} formData
 *   .clientName  {string} 客戶名稱（必填）
 *   .company     {string} 公司名稱（選填，有 = 企業版條款）
 *   .phone       {string} 聯絡電話（選填）
 *   .eventType   {string} 活動型態（必填）
 *   .eventDate   {string} 活動日期 YYYY-MM-DD（必填）
 *   .location    {string} 活動地點（選填）
 *   .address     {string} 活動地址（選填）
 *   .pax         {string|number} 預計人數（選填）
 *   .budget      {number} 總預算（選填，有則執行品項篩選）
 *   .itemCount   {number} 品項數量需求（選填，預設 8）
 *   .minMargin   {number} 最低毛利率 0~1（選填，預設 0.7）
 *   .style       {string} "tea_time" / "savory" / "sweet"（選填）
 * @returns {Object} { success, caseId, fileName, url }
 */
function createQuote(formData) {
  // ── 打開主系統 Sheet ──
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);

  // ── 產生 case_id ──
  var now = new Date();
  var caseId = 'Q' + Utilities.formatDate(now, 'Asia/Taipei', 'yyyyMMddHHmmss');

  // ── 格式化活動日期 ──
  var eventDate = new Date(formData.eventDate + 'T00:00:00+08:00');
  var dateSuffix = Utilities.formatDate(eventDate, 'Asia/Taipei', 'yyyyMMdd');

  // ── 新檔案名稱：20260425_王小明 ──
  var newFileName = dateSuffix + '_' + formData.clientName;

  // ── 確保 Drive 資料夾存在 ──
  var yearFolder = ensureDriveFolder_(eventDate.getFullYear().toString());

  // ── 用 makeCopy 複製整個 Spreadsheet（保留所有分頁與公式） ──
  var sourceFile = DriveApp.getFileById(SPREADSHEET_ID);
  var newFile = sourceFile.makeCopy(newFileName, yearFolder);
  var newSs = SpreadsheetApp.openById(newFile.getId());

  // ── 保留 QUOTE_DRAFT 與 Items，刪除其餘分頁 ──
  var sheets = newSs.getSheets();
  var keepSheet = null;
  var itemsSheet = null;
  for (var i = 0; i < sheets.length; i++) {
    if (sheets[i].getName() === TEMPLATE_SHEET_NAME) {
      keepSheet = sheets[i];
    } else if (sheets[i].getName() === 'Items') {
      itemsSheet = sheets[i];
    }
  }
  if (!keepSheet) {
    throw new Error('新檔案中找不到 QUOTE_DRAFT 分頁。');
  }

  // 先 activate 要保留的分頁，避免刪最後一個 sheet 報錯
  newSs.setActiveSheet(keepSheet);

  // 批次刪除非 QUOTE_DRAFT、非 Items 的分頁
  var sheetsToDelete = [];
  for (var i = 0; i < sheets.length; i++) {
    var name = sheets[i].getName();
    if (name !== TEMPLATE_SHEET_NAME && name !== 'Items') {
      sheetsToDelete.push(sheets[i]);
    }
  }
  for (var j = 0; j < sheetsToDelete.length; j++) {
    try { newSs.deleteSheet(sheetsToDelete[j]); } catch(e) { Logger.log('刪除分頁失敗: ' + e.message); }
  }

  // ── 改名 QUOTE_DRAFT → 報價單 ──
  keepSheet.setName('報價單');

  // ── 隱藏 Items 分頁（保留 VLOOKUP 正常運作） ──
  if (itemsSheet) {
    itemsSheet.hideSheet();
  }

  // ── 填入客戶資訊（對應 QUOTE_DRAFT 客戶區，B 欄填入） ──
  keepSheet.getRange('B2').setValue(formData.clientName);
  keepSheet.getRange('B3').setValue(formData.company   || '');
  keepSheet.getRange('B4').setValue(formData.phone     || '');
  keepSheet.getRange('B5').setValue(formData.address   || '');
  keepSheet.getRange('B6').setValue(formData.eventType);
  keepSheet.getRange('B7').setValue(formData.eventDate);
  keepSheet.getRange('B8').setValue(formData.pax       || '');
  keepSheet.getRange('B9').setValue(formData.location  || '');

  // ── Case ID & 建立時間（右上角） ──
  keepSheet.getRange('H1').setValue(caseId);
  keepSheet.getRange('H2').setValue(Utilities.formatDate(now, 'Asia/Taipei', 'yyyy-MM-dd HH:mm'));

  // ── 系統資訊寫入 N 欄（標籤在 M 欄） ──
  keepSheet.getRange('M2').setValue('CaseID');
  keepSheet.getRange('N2').setValue(caseId);
  keepSheet.getRange('M3').setValue('建立時間');
  keepSheet.getRange('N3').setValue(Utilities.formatDate(now, 'Asia/Taipei', 'yyyy-MM-dd HH:mm'));
  keepSheet.getRange('M5').setValue('報價狀態');
  keepSheet.getRange('N5').setValue('報價中');
  keepSheet.getRange('M7').setValue('匯款狀態');
  keepSheet.getRange('N7').setValue('未匯');
  keepSheet.getRange('M9').setValue('版本');
  keepSheet.getRange('N9').setValue('v3.8');

  // N5 下拉驗證：報價狀態
  var quoteStatusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(['報價中', '成交', '未成交結案'], true)
    .setAllowInvalid(false)
    .build();
  keepSheet.getRange('N5').setDataValidation(quoteStatusRule);

  // N7 下拉驗證：匯款狀態
  var paymentStatusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(['未匯', '已收訂金', '已收全額'], true)
    .setAllowInvalid(false)
    .build();
  keepSheet.getRange('N7').setDataValidation(paymentStatusRule);

  // ── 條款自動帶入（個人版 / 企業版） ──
  var isCorporate = formData.company && formData.company.trim().length > 0;
  var terms = isCorporate
    ? getCorpTerms(eventDate)
    : getPersonalTerms();
  keepSheet.getRange('A30').setValue('【合約條款】');
  keepSheet.getRange('A31').setValue(terms);

  // ── 返回新檔案 URL ──
  var newUrl = newSs.getUrl();

  // ── 寫入 SALES_INTAKE ──
  writeToIntake_(ss, caseId, formData, newUrl, now);

  return {
    success: true,
    caseId: caseId,
    fileName: newFileName,
    url: newUrl
  };
}

// ─────────────────────────────────────────
// 品項篩選：selectItemsForBudget_
// ─────────────────────────────────────────

/**
 * 從 Items 分頁根據預算、人數、品項數量、毛利率篩選品項
 *
 * Items 分頁欄位：
 *   A: item_id, B: category, C: standard_name（品名）
 *   D: default_price（售價）, E: default_cost（成本）, I: active, K: image_url
 *
 * @param {Sheet}  itemsSheet  Items 分頁物件
 * @param {Object} params
 *   .budget    {number} 總預算
 *   .pax       {number} 人數
 *   .itemCount {number} 品項總數量
 *   .minMargin {number} 最低毛利率 0~1（預設 0.7）
 *   .style     {string} "tea_time" / "savory" / "sweet"
 * @returns {Object} { appetizers: [...], desserts: [...] }
 */
function selectItemsForBudget_(itemsSheet, params) {
  var budget    = params.budget;
  var pax       = params.pax    || 1;
  var itemCount = params.itemCount || 8;
  var minMargin = params.minMargin || 0.7;
  var style     = params.style  || 'tea_time';

  var perPersonBudget = budget / pax;

  var lastRow = itemsSheet.getLastRow();
  if (lastRow < 2) return { appetizers: [], desserts: [] };

  // A=item_id, B=category, C=standard_name, D=default_price, E=default_cost, I=active, K=image_url
  var data = itemsSheet.getRange(2, 1, lastRow - 1, 11).getValues();

  var allItems = [];
  for (var i = 0; i < data.length; i++) {
    var itemId   = String(data[i][0]).trim();  // A: item_id
    var category = String(data[i][1]).trim();  // B: category
    var name     = String(data[i][2]).trim();  // C: standard_name
    var price    = Number(data[i][3]);         // D: default_price
    var cost     = Number(data[i][4]);         // E: default_cost
    var active   = String(data[i][8]).trim();  // I: active
    var imageUrl = data[i][10];                // K: image_url

    if (!name || !itemId) continue;
    if (active && active !== 'Y') continue;
    if (!cost || cost <= 0) continue;

    if (!price || price <= 0) {
      price = cost / (1 - minMargin);
    }

    var margin = (price - cost) / price;
    allItems.push({ id: itemId, name: name, price: price, cost: cost, margin: margin, imageUrl: imageUrl, category: category });
  }

  Logger.log('[selectItemsForBudget_] 讀取 ' + data.length + ' 列，有效品項：' + allItems.length + ' 項');

  if (allItems.length === 0) return { appetizers: [], desserts: [] };

  var appetizerCount, dessertCount;
  if (style === 'tea_time') {
    appetizerCount = Math.ceil(itemCount * 0.55);
    dessertCount   = itemCount - appetizerCount;
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

  var savoryPool = allItems.filter(function(x) {
    return x.category === '鹹' || x.category === '鹹食' || x.category === 'appetizer' ||
           x.category === '餐食小點' || x.category === '鹹點';
  });
  var sweetPool = allItems.filter(function(x) {
    return x.category === '甜' || x.category === '甜點' || x.category === 'dessert' ||
           x.category === '甜點小點' || x.category === '甜食' || x.category === '西點';
  });

  if (savoryPool.length < appetizerCount) savoryPool = allItems.filter(function(x) { return sweetPool.indexOf(x) === -1; });
  if (sweetPool.length < dessertCount)   sweetPool  = allItems.filter(function(x) { return savoryPool.indexOf(x) === -1; });

  savoryPool.sort(function(a, b) { return a.price - b.price; });
  sweetPool.sort(function(a, b)  { return a.price - b.price; });

  var pricePerItem = perPersonBudget / itemCount;
  var priceLimit   = pricePerItem * 1.3;

  var selected_s = savoryPool.filter(function(x) { return x.price <= priceLimit; }).slice(0, appetizerCount);
  var selected_d = sweetPool.filter(function(x)  { return x.price <= priceLimit; }).slice(0, dessertCount);

  if (selected_s.length < appetizerCount) selected_s = savoryPool.slice(0, appetizerCount);
  if (selected_d.length < dessertCount)   selected_d = sweetPool.slice(0, dessertCount);

  Logger.log('品項篩選完成：鹹食 ' + selected_s.length + ' 項，甜點 ' + selected_d.length + ' 項');

  return { appetizers: selected_s, desserts: selected_d };
}

/**
 * 把篩選結果寫入 QUOTE_DRAFT 菜單區
 * 只寫 D 欄（品名）和 G 欄（數量），不碰 I/J 欄公式
 * I 欄 = VLOOKUP 公式自動帶成本，J 欄 = G×I 公式自動算小計
 *
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

  // 先清空 D 欄和 G 欄（不碰 I/J 欄，保留 VLOOKUP 和小計公式）
  var allItemRows = [8, 9, 10, 12, 13, 14, 15, 16];
  for (var k = 0; k < allItemRows.length; k++) {
    var r = allItemRows[k];
    sheet.getRange('D' + r).setValue('');
    sheet.getRange('G' + r).setValue('');
  }

  // 寫 appetizer D8:D10
  for (var i = 0; i < maxSlots; i++) {
    var row  = APPETIZER_ROWS.start + i;
    var item = appetizers[i];
    if (item) {
      var displayName = item.id ? item.name + ' (' + item.id + ')' : item.name;
      sheet.getRange('D' + row).setValue(displayName);
      sheet.getRange('G' + row).setValue(qty);
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
    }
  }

  Logger.log('品項已寫入菜單區（D 品名 + G 數量，I/J 公式保留）');
}

// ─────────────────────────────────────────
// 表單預填資料
// ─────────────────────────────────────────

/**
 * 從 QUOTE_DRAFT 讀取預填資料供表單使用（對應 v3.1 B 欄版面）
 */
function getQuoteDraftValues() {
  var ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(TEMPLATE_SHEET_NAME);
  if (!sheet) return {};

  return {
    clientName : sheet.getRange('B2').getValue() || '',
    company    : sheet.getRange('B3').getValue() || '',
    phone      : sheet.getRange('B4').getValue() || '',
    address    : sheet.getRange('B5').getValue() || '',
    eventType  : sheet.getRange('B6').getValue() || '',
    eventDate  : sheet.getRange('B7').getValue()
                  ? Utilities.formatDate(new Date(sheet.getRange('B7').getValue()), 'Asia/Taipei', 'yyyy-MM-dd')
                  : '',
    headcount  : sheet.getRange('B8').getValue() || '',
    eventName  : sheet.getRange('B9').getValue() || '',
    totalItems : sheet.getRange('B10').getValue() || ''
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

/**
 * 確保 MAPLAB_報價單/[year]/ 資料夾存在
 */
function ensureDriveFolder_(year) {
  var rootIter   = DriveApp.getFoldersByName(DRIVE_ROOT_FOLDER);
  var rootFolder = rootIter.hasNext() ? rootIter.next() : DriveApp.createFolder(DRIVE_ROOT_FOLDER);
  var yearIter   = rootFolder.getFoldersByName(year);
  return yearIter.hasNext() ? yearIter.next() : rootFolder.createFolder(year);
}

/**
 * 在 SALES_INTAKE 最後一行新增報價紀錄
 *
 * 欄位對應：
 *   A: case_id, B: created_at, C: source, D: client_name, E: company,
 *   F: phone, G: event_type, H: event_date, I: location, J: pax,
 *   K: sheet_url, L–N: （預留）, O: notes
 */
function writeToIntake_(ss, caseId, formData, sheetUrl, now) {
  var intakeSheet = ss.getSheetByName(INTAKE_SHEET_NAME);
  if (!intakeSheet) {
    throw new Error('找不到 SALES_INTAKE 分頁，請確認分頁名稱正確。');
  }

  var createdAt = Utilities.formatDate(now, 'Asia/Taipei', 'yyyy-MM-dd HH:mm:ss');

  var row = [
    caseId,                      // A: case_id
    createdAt,                   // B: created_at
    'quote-system-v3.8',         // C: source
    formData.clientName,         // D: client_name
    formData.company    || '',   // E: company
    formData.phone      || '',   // F: phone
    formData.eventType  || '',   // G: event_type
    formData.eventDate  || '',   // H: event_date
    formData.location   || '',   // I: location
    formData.pax        || '',   // J: pax
    sheetUrl,                    // K: sheet_url
    '',                          // L: （預留）
    '',                          // M: （預留）
    '',                          // N: （預留）
    ''                           // O: notes
  ];

  intakeSheet.appendRow(row);
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
 * 掃描 SALES_INTAKE K 欄 → 打開每份報價單 → 讀 N5/N7 → 寫回 L/M
 * v3.8：狀態位置 = N5（報價狀態）/ N7（匯款狀態）
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
      var quoteStatus  = quoteSheet.getRange('N5').getValue();  // v3.8: N5
      var paymentStatus = quoteSheet.getRange('N7').getValue(); // v3.8: N7
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
// HTTP 入口：handleQuoteRequest_（由 LineWebhook.gs doPost 呼叫）
// ─────────────────────────────────────────

/**
 * @param {Object} params  來自 doPost 解析後的 JSON
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
      location   : params.location    || '',
      pax        : params.pax         || '',
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
