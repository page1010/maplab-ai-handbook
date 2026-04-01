/**
 * MAPLAB 報價系統 v2 — Phase 1
 * 功能：一鍵產出報價單（獨立 Spreadsheet 檔案）、寫入 SALES_INTAKE
 *
 * 部署目標 Sheet：1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
 * 模板分頁：QUOTE_DRAFT
 * 寫入分頁：SALES_INTAKE
 */

var SPREADSHEET_ID = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg';
var TEMPLATE_SHEET_NAME = 'QUOTE_DRAFT';
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
 * 由 HTML 表單呼叫，接收表單資料、產出獨立報價單 Spreadsheet、回傳結果
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

  // ── 取模板分頁 QUOTE_DRAFT ──
  var templateSheet = ss.getSheetByName(TEMPLATE_SHEET_NAME);
  if (!templateSheet) {
    throw new Error('找不到 QUOTE_DRAFT 模板分頁，請確認分頁名稱正確。');
  }

  // ── 建立獨立新 Spreadsheet ──
  var newSs = SpreadsheetApp.create(newFileName);

  // ── 複製 QUOTE_DRAFT 到新檔案 ──
  templateSheet.copyTo(newSs);

  // ── 找到複製的分頁（非預設 Sheet1）──
  var copiedSheet = null;
  var allSheets = newSs.getSheets();
  for (var i = 0; i < allSheets.length; i++) {
    if (allSheets[i].getName() !== 'Sheet1') {
      copiedSheet = allSheets[i];
      break;
    }
  }
  if (!copiedSheet) {
    // 若模板複製後沒有非 Sheet1 的分頁（極少數情況），取第一個
    copiedSheet = allSheets[0];
  }

  // ── 改名為「報價單」──
  copiedSheet.setName('報價單');

  // ── 刪預設空白頁 Sheet1 ──
  var defaultSheet = newSs.getSheetByName('Sheet1');
  if (defaultSheet) {
    newSs.deleteSheet(defaultSheet);
  }

  // ── 填入客戶資訊（對應 QUOTE_DRAFT 客戶區） ──
  // B 欄為填入欄，A 欄為標籤
  copiedSheet.getRange('B2').setValue(formData.clientName);
  copiedSheet.getRange('B3').setValue(formData.company || '');
  copiedSheet.getRange('B4').setValue(formData.phone || '');
  copiedSheet.getRange('B5').setValue(formData.address || '');
  copiedSheet.getRange('B6').setValue(formData.eventType);
  copiedSheet.getRange('B7').setValue(formData.eventDate);
  copiedSheet.getRange('B8').setValue(formData.pax || '');
  copiedSheet.getRange('B9').setValue(formData.location || '');

  // ── Case ID & 建立時間（右上角） ──
  copiedSheet.getRange('H1').setValue(caseId);
  copiedSheet.getRange('H2').setValue(Utilities.formatDate(now, 'Asia/Taipei', 'yyyy-MM-dd HH:mm'));

  // ── 條款自動帶入（個人版 / 企業版） ──
  var isCorporate = formData.company && formData.company.trim().length > 0;
  var terms = isCorporate
    ? getCorpTerms(eventDate)
    : getPersonalTerms();
  copiedSheet.getRange('A30').setValue('【合約條款】');
  copiedSheet.getRange('A31').setValue(terms);

  // ── 狀態區 ──
  copiedSheet.getRange('E2').setValue('報價中');   // 報價狀態
  copiedSheet.getRange('E3').setValue('');          // 成交金額（業務填）
  copiedSheet.getRange('E4').setValue('未匯');      // 匯款狀態
  copiedSheet.getRange('E5').setValue('系統');      // 最後修改者
  copiedSheet.getRange('E6').setValue('v1');        // 版本號

  // ── 移到 Drive 資料夾 MAPLAB_報價單/[年份]/ ──
  try {
    var yearFolder = ensureDriveFolder_(eventDate.getFullYear().toString());
    var fileId = newSs.getId();
    var file = DriveApp.getFileById(fileId);
    yearFolder.addFile(file);
    // 移除根目錄的預設位置
    DriveApp.getRootFolder().removeFile(file);
  } catch (e) {
    console.warn('Drive 資料夾移動失敗（不影響主流程）：' + e.message);
  }

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
 *   K: sheet_url（新獨立 Spreadsheet URL）
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
    sheetUrl,                              // K: sheet_url（獨立 Spreadsheet URL）
    '',                                    // L: （預留）
    '',                                    // M: （預留）
    '',                                    // N: （預留）
    ''                                     // O: notes
  ];

  intakeSheet.appendRow(row);
}
