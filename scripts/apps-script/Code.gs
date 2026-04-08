/**
 * MAPLAB 報價系統 v3.8
 * 修正：createQuote 客戶區 cell reference 回到接手前版本（B2:B9 / H1-H2 / M/N 欄 / A30-A31 條款）
 * 保留：doPost 路由（LineWebhook.gs）/ handleQuoteRequest_
 *
 * 部署目標 Sheet：1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
 * 模板分頁：QUOTE_DRAFT
 * 寫入分頁：SALES_INTAKE
 *
 * QUOTE_DRAFT 版面對應（2026-04-08 修正：對齊 C1:F61 列印範圍）：
 *   D2: 客戶名稱（框線內，列印範圍 C1:F61）
 *   B3: 公司名稱（generateProposalV2 相容暫留）
 *   E2: 活動日期（框線內）
 *   D3: 活動地點（框線內，location || address）
 *   D4: 活動型態（框線內）
 *   F4: 預計人數（框線內）
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
 * 對齊決策（2026-04-08 A0）：B 欄在 C1:F61 框線外（labels），主體資料對齊框線內 D/E/F。
 * 改前：B2:B9（接手前版本，v3.8 回滾後狀態）
 * 改後：D2/E2/D3/D4/F4（與 generateProposalV2 讀取位置統一，避免業務填兩次）
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
    .addItem('產出 Slide 提案', 'generateProposalV2')
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
 * @returns {Object} { success, caseId, fileName, url }
 */
function createQuote(formData) {
  // ── 欄位名稱相容層（QuoteForm 新名 + doPost/舊版舊名都吃）──
  // QuoteForm.html (2026-04-02+): customer / date / time / headcount / eventName / totalItems
  // 舊版 createQuote 期待:      clientName / eventDate / -     / pax       / eventName / totalItems
  var _clientName  = formData.clientName || formData.customer  || '';
  var _eventDateStr= formData.eventDate  || formData.date      || '';
  var _eventTime   = formData.time       || '';
  var _address     = formData.location   || formData.address   || '';
  var _eventType   = formData.eventType  || '';
  var _pax         = formData.pax        || formData.headcount || '';
  var _eventName   = formData.eventName  || '';
  var _totalItems  = formData.totalItems || '';
  var _company     = formData.company    || '';
  // 寫回 formData 讓下游（writeToIntake_ 等）也拿到正規化後的值
  formData.clientName = _clientName;
  formData.eventDate  = _eventDateStr;
  formData.pax        = _pax;
  formData.eventName  = _eventName;
  formData.totalItems = _totalItems;

  // ── 打開主系統 Sheet ──
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);

  // ── 產生 case_id ──
  var now = new Date();
  var caseId = 'Q' + Utilities.formatDate(now, 'Asia/Taipei', 'yyyyMMddHHmmss');

  // ── 格式化活動日期 ──
  if (!_eventDateStr) {
    throw new Error('活動日期為空（表單 date / eventDate 欄位都沒值）');
  }
  var eventDate = new Date(_eventDateStr + 'T00:00:00+08:00');
  if (isNaN(eventDate.getTime())) {
    throw new Error('活動日期格式無法解析：' + _eventDateStr);
  }
  var dateSuffix = Utilities.formatDate(eventDate, 'Asia/Taipei', 'yyyyMMdd');

  // ── 新檔案名稱：20260425_王小明 ──
  var newFileName = dateSuffix + '_' + _clientName;

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

  // ── 填入客戶資訊 ──
  // 2026-04-08 依 live sheet 驗證：QUOTE_DRAFT 上半部 C/E 整欄是 label，D/F 整欄是 value。
  // 原 commit 4301369 誤把 E2 當日期值寫入，結果覆蓋模板的 "date" 標籤。
  keepSheet.getRange('D2').setValue(_clientName);  // C2="客戶" label
  keepSheet.getRange('B3').setValue(_company);     // generateProposalV2 讀 B3 公司名（框線外，保留）
  keepSheet.getRange('F2').setValue(_eventDateStr);// E2="date" label，F2 才是活動日期值
  keepSheet.getRange('D3').setValue(_address);     // C3="地址" label
  keepSheet.getRange('F3').setValue(_eventTime);   // E3="時間" label，F3 才是活動時間值
  keepSheet.getRange('D4').setValue(_eventType);   // C4="活動型態" label
  keepSheet.getRange('F4').setValue(_pax);         // E4="規劃人數" label
  keepSheet.getRange('D5').setValue(_eventName);   // C5="活動名稱" label
  keepSheet.getRange('F5').setValue(_totalItems);  // E5="餐點總件數" label

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
  var isCorporate = _company && _company.trim().length > 0;
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
// 表單預填資料
// ─────────────────────────────────────────

/**
 * 從 QUOTE_DRAFT 讀取預填資料供表單使用（對應 C1:F61 框線內版面，2026-04-08 修正）
 */
function getQuoteDraftValues() {
  var ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(TEMPLATE_SHEET_NAME);
  if (!sheet) return {};

  var rawDate = sheet.getRange('F2').getValue();  // 2026-04-08: E2 是 label，活動日期值在 F2
  var rawTime = sheet.getRange('F3').getValue();  // 2026-04-08: E3 是 label，活動時間值在 F3
  return {
    clientName : sheet.getRange('D2').getValue() || '',
    company    : sheet.getRange('B3').getValue() || '',
    phone      : sheet.getRange('B4').getValue() || '',
    address    : sheet.getRange('D3').getValue() || '',
    eventType  : sheet.getRange('D4').getValue() || '',
    eventDate  : rawDate instanceof Date
                  ? Utilities.formatDate(rawDate, 'Asia/Taipei', 'yyyy-MM-dd')
                  : (rawDate ? String(rawDate) : ''),
    time       : rawTime instanceof Date
                  ? Utilities.formatDate(rawTime, 'Asia/Taipei', 'HH:mm')
                  : (rawTime ? String(rawTime) : ''),
    headcount  : sheet.getRange('F4').getValue() || '',
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
      pax        : params.pax         || ''
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
