/**
 * MAPLAB 報價系統 v2 — Phase 1
 * 功能：一鍵產出報價單、寫入 SALES_INTAKE
 *
 * 部署目標 Sheet：1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
 * 模板分頁：QUOTE_WORKBENCH
 * 寫入分頁：SALES_INTAKE
 */

var SPREADSHEET_ID = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg';
var TEMPLATE_SHEET_NAME = 'QUOTE_WORKBENCH';
var INTAKE_SHEET_NAME = 'SALES_INTAKE';
var DRIVE_ROOT_FOLDER = 'MAPLAB_報價單';

// ─────────────────────────────────────────
// 選單 & 入口
// ─────────────────────────────────────────

/**
 * 開啟 Spreadsheet 時自動掛載選單
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('MAPLAB')
    .addItem('產出報價單', 'showQuoteForm')
    .addToUi();
}

/**
 * 彈出報價單表單對話框
 */
function showQuoteForm() {
  var html = HtmlService.createHtmlOutputFromFile('QuoteForm')
    .setWidth(500)
    .setHeight(560)
    .setTitle('新建報價單');
  SpreadsheetApp.getUi().showModalDialog(html, '新建報價單');
}

// ─────────────────────────────────────────
// 主程式：createQuote()
// ─────────────────────────────────────────

/**
 * 由 HTML 表單呼叫，接收表單資料、產出報價單、回傳結果
 *
 * @param {Object} formData
 *   .clientName {string} 客戶名稱（必填）
 *   .company    {string} 公司名稱（選填，有 = 企業版條款）
 *   .phone      {string} 聯絡電話（選填）
 *   .eventType  {string} 活動類型（必填）
 *   .eventDate  {string} 活動日期 YYYY-MM-DD（必填）
 *   .location   {string} 活動地點（選填）
 *   .pax        {string} 預計人數（選填）
 *   .address    {string} 活動地址（選填）
 * @returns {Object} { success, caseId, sheetName, url }
 */
function createQuote(formData) {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);

  // ── 產生 case_id ──
  var now = new Date();
  var caseId = 'Q' + Utilities.formatDate(now, 'Asia/Taipei', 'yyyyMMddHHmmss');

  // ── 格式化活動日期 ──
  var eventDate = new Date(formData.eventDate + 'T00:00:00+08:00');
  var dateSuffix = Utilities.formatDate(eventDate, 'Asia/Taipei', 'yyyyMMdd');
  var newSheetName = '報價_' + formData.clientName + '_' + dateSuffix;

  // ── 複製 QUOTE_WORKBENCH 模板 ──
  var templateSheet = ss.getSheetByName(TEMPLATE_SHEET_NAME);
  if (!templateSheet) {
    throw new Error('找不到 QUOTE_WORKBENCH 模板分頁，請確認分頁名稱正確。');
  }
  var newSheet = templateSheet.copyTo(ss);
  newSheet.setName(newSheetName);

  // 移到最後一頁
  ss.setActiveSheet(newSheet);
  ss.moveActiveSheet(ss.getNumSheets());

  // ── 填入客戶資訊（對應 QUOTE_WORKBENCH 客戶區） ──
  // 假設模板 B 欄為填入欄，A 欄為標籤
  newSheet.getRange('B2').setValue(formData.clientName);
  newSheet.getRange('B3').setValue(formData.company || '');
  newSheet.getRange('B4').setValue(formData.phone || '');
  newSheet.getRange('B5').setValue(formData.address || '');
  newSheet.getRange('B6').setValue(formData.eventType);
  newSheet.getRange('B7').setValue(formData.eventDate);
  newSheet.getRange('B8').setValue(formData.pax || '');
  newSheet.getRange('B9').setValue(formData.location || '');

  // ── Case ID & 建立時間（右上角） ──
  newSheet.getRange('H1').setValue(caseId);
  newSheet.getRange('H2').setValue(Utilities.formatDate(now, 'Asia/Taipei', 'yyyy-MM-dd HH:mm'));

  // ── 條款自動帶入（個人版 / 企業版） ──
  var isCorporate = formData.company && formData.company.trim().length > 0;
  var terms = isCorporate
    ? getCorpTerms(eventDate)
    : getPersonalTerms();
  newSheet.getRange('A30').setValue('【合約條款】');
  newSheet.getRange('A31').setValue(terms);

  // ── 狀態區 ──
  newSheet.getRange('E2').setValue('報價中');   // 報價狀態
  newSheet.getRange('E3').setValue('');          // 成交金額（業務填）
  newSheet.getRange('E4').setValue('未匯');      // 匯款狀態
  newSheet.getRange('E5').setValue('系統');      // 最後修改者
  newSheet.getRange('E6').setValue('v1');        // 版本號

  // ── 建 Drive 資料夾（MAPLAB_報價單/[年份]/）──
  try {
    ensureDriveFolder_(eventDate.getFullYear().toString());
  } catch (e) {
    console.warn('Drive 資料夾建立失敗（不影響主流程）：' + e.message);
  }

  // ── 取得 Sheet URL ──
  var sheetUrl = ss.getUrl() + '#gid=' + newSheet.getSheetId();

  // ── 寫入 SALES_INTAKE ──
  writeToIntake_(ss, caseId, formData, sheetUrl, now);

  return {
    success: true,
    caseId: caseId,
    sheetName: newSheetName,
    url: sheetUrl
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
 * @param {string} year 例 '2026'
 * @returns {Folder} 年份子資料夾
 */
function ensureDriveFolder_(year) {
  var rootIter = DriveApp.getFoldersByName(DRIVE_ROOT_FOLDER);
  var rootFolder = rootIter.hasNext()
    ? rootIter.next()
    : DriveApp.createFolder(DRIVE_ROOT_FOLDER);

  var yearIter = rootFolder.getFoldersByName(year);
  return yearIter.hasNext()
    ? yearIter.next()
    : rootFolder.createFolder(year);
}

/**
 * 在 SALES_INTAKE 最後一行新增報價紀錄
 *
 * 欄位對應（依照現有表頭）：
 *   A: case_id
 *   B: created_at
 *   C: source
 *   D: client_name
 *   E: company
 *   F: phone
 *   G: event_type
 *   H: event_date
 *   I: location
 *   J: pax
 *   K: sheet_url
 *   L–N: （預留）
 *   O: notes
 */
function writeToIntake_(ss, caseId, formData, sheetUrl, now) {
  var intakeSheet = ss.getSheetByName(INTAKE_SHEET_NAME);
  if (!intakeSheet) {
    throw new Error('找不到 SALES_INTAKE 分頁，請確認分頁名稱正確。');
  }

  var createdAt = Utilities.formatDate(now, 'Asia/Taipei', 'yyyy-MM-dd HH:mm:ss');

  var row = [
    caseId,                                // A: case_id
    createdAt,                             // B: created_at
    'quote-system-v2',                     // C: source
    formData.clientName,                   // D: client_name
    formData.company    || '',             // E: company
    formData.phone      || '',             // F: phone
    formData.eventType,                    // G: event_type
    formData.eventDate,                    // H: event_date
    formData.location   || '',             // I: location
    formData.pax        || '',             // J: pax
    sheetUrl,                              // K: sheet_url
    '',                                    // L: （預留）
    '',                                    // M: （預留）
    '',                                    // N: （預留）
    ''                                     // O: notes
  ];

  intakeSheet.appendRow(row);
}
