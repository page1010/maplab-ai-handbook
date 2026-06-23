/**
 * MAPLAB 報價系統 v3.8
 * 修正：createQuote 客戶區 cell reference 回到接手前版本（B2:B9 / H1-H2 / M/N 欄 / A30-A31 條款）
 * 保留：doPost 路由（LineWebhook.gs）/ handleQuoteRequest_
 *
 * 部署目標 Sheet：1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
 * 模板分頁：QUOTE_DRAFT
 * 寫入分頁：SALES_INTAKE
 *
 * QUOTE_DRAFT 版面對應（2026-04-08 修正：對齊 C1:F55 列印範圍）：
 *   列印範圍 = C1:F55（Owner 用實體框線劃的客人可見區）
 *   框線外（B/G/H/I/J/K/L/M/N 欄 + row 56 以下）= 業務內部
 *   完整規則：docs/business-requirements/quote-sheet-print-range.md
 *
 *   D2: 客戶名稱（框線內）
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
 * 對齊決策（2026-04-08 A0）：B 欄在 C1:F55 框線外（labels），主體資料對齊框線內 D/E/F。
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
    .addItem('產出 Slide 提案（英文版）', 'generateProposalV2_EN')
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
  var _clientName   = formData.clientName || formData.customer  || '';
  var _eventDateStr = formData.eventDate  || formData.date      || '';
  var _eventTime    = formData.time       || '';
  var _address      = formData.location   || formData.address   || '';
  var _eventType    = formData.eventType  || '';
  var _pax          = formData.pax        || formData.headcount || '';
  var _eventName    = formData.eventName  || '';
  var _totalItems   = formData.totalItems || '';
  var _company      = formData.company    || '';
  // 2026-04-09 新增：訂金金額（個人 baseline 3000，業務可調）+ 飲食禁忌
  var _depositAmount = Number(formData.depositAmount) || 3000;
  var _dietaryNotes  = formData.dietaryNotes || '';
  // 2026-04-09 新增：樓層搬運費 mode (none / with_help / no_help)
  var _floorFeeMode  = formData.floorFeeMode || 'none';
  // 寫回 formData 讓下游（writeToIntake_ / resolveContractVersion 等）也拿到正規化後的值
  formData.clientName    = _clientName;
  formData.eventDate     = _eventDateStr;
  formData.pax           = _pax;
  formData.eventName     = _eventName;
  formData.totalItems    = _totalItems;
  formData.depositAmount = _depositAmount;
  formData.dietaryNotes  = _dietaryNotes;
  // noDeposit / isMarketingAgency 由 resolveContractVersion 自己從 formData 讀

  // ── 決議合約版本（四版 v4.0：to_c / to_b_deposit / to_b_full / to_b_marketing）──
  // 由 contractTerms.gs 的 resolveContractVersion 依決策樹判斷：
  //   企業類（公司名有填 or 活動類型含企業關鍵字）→ 行銷公關 > 不收訂金 > 有訂金
  //   個人類 → to_c
  var _contractVersion = resolveContractVersion(formData);
  // isCorporate 保留給 SALES_INTAKE 紀錄用
  var isCorporate = _contractVersion !== 'to_c';

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
  keepSheet.getRange('M7').setValue('付款狀態');
  // N7 下拉維持單一組（2026-04-08 Owner 最終指示：付款狀態和契約類型解耦，
  // 這三個狀態對 to_c / to_b_* 全部適用，業務自己依合約判斷）
  var defaultPaymentStatus = '未匯款';
  var paymentOptions       = ['未匯款', '已收訂金', '已收全額'];
  keepSheet.getRange('N7').setValue(defaultPaymentStatus);
  keepSheet.getRange('M9').setValue('版本');
  keepSheet.getRange('N9').setValue('v3.8-verified-2026-04-08');

  // N5 下拉驗證：報價狀態（B2B/B2C 共用）
  var quoteStatusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(['報價中', '成交', '未成交結案'], true)
    .setAllowInvalid(false)
    .build();
  keepSheet.getRange('N5').setDataValidation(quoteStatusRule);

  // N7 下拉驗證：付款狀態（2026-04-08 拆分 B2B/B2C）
  // 原本的 ['未匯','已收訂金','已收全額'] 對 B2B 不準，B2B 不收訂金。
  var paymentStatusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(paymentOptions, true)
    .setAllowInvalid(false)
    .build();
  keepSheet.getRange('N7').setDataValidation(paymentStatusRule);

  // ── 隱藏熱客招待整塊（Row 17 label + Row 18-19 兩個內部品項）──
  // Owner 2026-04-08 指示：客人不應看到熱客招待的內部品項與標籤。
  // 2026-04-08 依 live sheet 重新定位：label 在 row 17、item 在 row 18-19，
  // 所以隱藏 row 17-19 三列；row 20 是「項目」header（費用區開始），必須保留可見。
  keepSheet.hideRows(17, 3);

  // ── 還原 E25 租借長桌公式 ──
  // 原本 master 有 =G25*350+H25*100 的公式（大桌 $350 x 大桌數 + 小桌 $100 x 小桌數），
  // 歷次 setValue 覆蓋過程中被清掉了。generated copy 必須恢復這條公式，
  // 否則業務填 G25/H25 數量後 E25 不會自動算金額。
  keepSheet.getRange('E25').setFormula('=IF(OR(G25>0,H25>0),G25*350+H25*100,"")');

  // ── 條款自動帶入 C32/C33（列印範圍 C1:F55 框線內） ──
  // 2026-04-08 v4.0：四版動態選擇，contractTerms.gs 負責文字生成。
  // getContractTermsV4 會把匯款資訊（個人或公司帳戶）+ 分隔線 + 完整條款合成一段。
  // 2026-04-09：傳入 depositAmount 讓條款裡的訂金金額可由業務調整（baseline 3000）
  var terms = getContractTermsV4(_contractVersion, eventDate, _depositAmount);
  keepSheet.getRange('C32').setValue('【合約條款】（' + _contractVersion + '）');
  keepSheet.getRange('C33').setValue(terms).setWrapStrategy(SpreadsheetApp.WrapStrategy.WRAP);
  // 合約條款會很長，確保 C33 儲存格有足夠高度顯示多行文字
  keepSheet.setRowHeight(33, 600);

  // ── 飲食禁忌 / 客戶偏好寫進框線外備註區（K10 附近，看得到但不印出）──
  // 2026-04-09 依 Owner 需求：業務接洽時抄下的禁忌提醒
  if (_dietaryNotes) {
    keepSheet.getRange('K10').setValue('客戶禁忌/偏好');
    keepSheet.getRange('L10').setValue(_dietaryNotes);
  }

  // ── 車馬費自動計算（S6：30 分鐘內免費 / 以上取 km 制與 min 制較高值）──
  // 2026-04-09 Owner 定版：用高的算好了 讓業務談
  try {
    var transport = calcTransportFee(_address);
    if (transport.fee > 0) {
      keepSheet.getRange('E27').setValue(transport.fee);
    }
    // 框線外備註寫 3 列：計算結果 + 距離時間 + 公式拆解，業務一眼看清楚
    keepSheet.getRange('K11').setValue('車馬費計算');
    keepSheet.getRange('L11').setValue(transport.note);
    keepSheet.getRange('K12').setValue('距離 / 時間');
    keepSheet.getRange('L12').setValue(
      transport.distanceKm + ' km｜約 ' + transport.driveMin + ' 分鐘｜' +
      'km 制 $' + (transport.feeByKm || 0) + ' / min 制 $' + (transport.feeByMin || 0) +
      ' → 取高 $' + transport.fee
    );
  } catch (e) {
    Logger.log('[createQuote] calcTransportFee 失敗: ' + e.message);
    keepSheet.getRange('K11').setValue('車馬費計算');
    keepSheet.getRange('L11').setValue('計算失敗 (' + e.message + ')，業務手動填 E27');
  }

  // ── 搬運費自動計算（S9：2F 無電梯 $500/$1000）──
  var floorFee = calcFloorFee(_floorFeeMode);
  if (floorFee > 0) {
    keepSheet.getRange('E28').setValue(floorFee);
  }
  keepSheet.getRange('K13').setValue('搬運費模式');
  keepSheet.getRange('L13').setValue(_floorFeeMode + ' → NT$' + floorFee);

  // ── 返回新檔案 URL ──
  var newUrl = newSs.getUrl();

  // ── 寫入 SALES_INTAKE ──
  writeToIntake_(ss, caseId, formData, newUrl, now);

  return {
    success: true,
    caseId: caseId,
    fileName: newFileName,
    spreadsheetId: newFile.getId(),
    url: newUrl
  };
}

// ─────────────────────────────────────────
// A5 adapter: 一次產出多版報價副本
// ─────────────────────────────────────────

/**
 * 由 A6 / Codex runtime 呼叫的安全批次接口。
 * 不寫 master QUOTE_DRAFT 的品項、公式或欄位結構；只呼叫 createQuote()
 * 產出獨立副本，再把 A/B/C 菜單與毛利試算填到各自副本。
 */
function createQuoteVariants_(body) {
  var base = body.base || body.formData || {};
  var variants = body.variants || [];
  if (!variants || variants.length === 0) {
    throw new Error('createQuoteVariants 需要 variants 陣列。');
  }

  var results = [];
  for (var i = 0; i < variants.length; i++) {
    var variant = variants[i] || {};
    var label = variant.label || variant.code || String.fromCharCode(65 + i);
    var formData = clonePlainObject_(base);
    var baseClientName = base.clientName || base.customer || 'MAPLAB';

    // 檔名需要區分 A/B/C；副本內 D2 會在 applyQuoteVariantToCopy_ 還原成原客戶名。
    formData.clientName = baseClientName + '_' + label;
    formData.customer = formData.clientName;
    formData.eventName = variant.title || variant.name || base.eventName || '';
    formData.totalItems = variant.totalItems || calcVariantTotalItems_(variant);
    formData.dietaryNotes = joinNonEmpty_([
      base.dietaryNotes,
      variant.positioning,
      variant.internalNote
    ], '｜');

    var created = createQuote(formData);
    applyQuoteVariantToCopy_(created.spreadsheetId, base, variant, label);

    results.push({
      label: label,
      title: variant.title || variant.name || '',
      caseId: created.caseId,
      fileName: created.fileName,
      spreadsheetId: created.spreadsheetId,
      url: created.url,
      foodRevenue: toNumber_(variant.foodRevenue),
      foodCost: toNumber_(variant.foodCost),
      foodCostRatio: calcRatioDecimal_(variant.foodCost, variant.foodRevenue),
      foodMargin: calcMarginDecimal_(variant.foodRevenue, variant.foodCost, variant.foodMargin),
      totalRevenue: toNumber_(variant.totalRevenue),
      overallMargin: calcMarginDecimal_(variant.totalRevenue, variant.totalCost, variant.overallMargin)
    });
  }

  return {
    generatedAt: Utilities.formatDate(new Date(), 'Asia/Taipei', 'yyyy-MM-dd HH:mm:ss'),
    count: results.length,
    quotes: results
  };
}

function applyQuoteVariantToCopy_(spreadsheetId, base, variant, label) {
  if (!spreadsheetId) throw new Error('缺少 spreadsheetId，無法填入方案副本。');
  var ss = SpreadsheetApp.openById(spreadsheetId);
  var sheet = ss.getSheetByName('報價單') || ss.getSheetByName(TEMPLATE_SHEET_NAME) || ss.getSheets()[0];
  var menu = variant.menu || [];
  var maxMenuRows = 12;
  var rowsToWrite = Math.min(menu.length, maxMenuRows);

  try { sheet.showRows(7, 13); } catch (e) { Logger.log('showRows skipped: ' + e.message); }

  sheet.getRange('D2').setValue(base.clientName || base.customer || '');
  sheet.getRange('B3').setValue(base.company || '');
  sheet.getRange('D5').setValue(variant.title || variant.name || base.eventName || '');
  sheet.getRange('F5').setValue(variant.totalItems || calcVariantTotalItems_(variant));

  sheet.getRange('D7:D20').clearContent();
  sheet.getRange('F7:F20').clearContent();
  sheet.getRange('I7:J20').clearContent();

  if (rowsToWrite > 0) {
    var names = [];
    var qtys = [];
    var costs = [];
    for (var i = 0; i < rowsToWrite; i++) {
      var item = menu[i] || {};
      var qtyText = item.qtyText || joinNonEmpty_([item.qty, item.unit], ' ');
      var unitCost = toNumber_(item.unitCost || item.cost);
      var subtotal = item.subtotal !== undefined && item.subtotal !== null && item.subtotal !== ''
        ? toNumber_(item.subtotal)
        : toNumber_(item.qty) * unitCost;

      names.push([item.name || item.standardName || item.itemName || '']);
      qtys.push([qtyText]);
      costs.push([unitCost || '', subtotal || '']);
    }
    sheet.getRange(7, 4, rowsToWrite, 1).setValues(names);
    sheet.getRange(7, 6, rowsToWrite, 1).setValues(qtys);
    sheet.getRange(7, 9, rowsToWrite, 2).setValues(costs);
  }

  var extra = variant.extraServices || {};
  var foodRevenue = variantAmount_(variant, extra, ['foodRevenue', 'food', 'mealRevenue'], 0);
  var softDrinkRevenue = variantAmount_(variant, extra, ['softDrinkRevenue', 'softDrinks', 'beverageRevenue'], 0);
  var alcoholRevenue = variantAmount_(variant, extra, ['alcoholRevenue', 'alcohol', 'barRevenue'], 0);
  var staffRevenue = variantAmount_(variant, extra, ['staffRevenue', 'staff', 'serviceStaff'], 0);
  var decorRevenue = variantAmount_(variant, extra, ['decorRevenue', 'decor', 'decorationRevenue'], 0);
  var transportRevenue = variantAmount_(variant, extra, ['transportRevenue', 'transport', 'equipmentRevenue'], '');
  var otherRevenue = variantAmount_(variant, extra, ['otherRevenue', 'other'], '');
  var totalRevenue = variantAmount_(variant, extra, ['totalRevenue', 'total'], 0);
  var totalCost = variantAmount_(variant, extra, ['totalCost', 'cost'], 0);
  var foodCost = variantAmount_(variant, extra, ['foodCost'], '');
  var overallMargin = calcMarginDecimal_(totalRevenue, totalCost, variant.overallMargin);

  sheet.getRange('C22:H28').clearContent();
  sheet.getRange('C22:F28').setValues([
    ['餐點', '', foodRevenue || '', variant.foodNote || ''],
    ['軟性飲料自助區', '', softDrinkRevenue || '', '含品項、杯具、冰塊、補量估算'],
    ['酒精／行動調酒吧台', '', alcoholRevenue || '', '現場吧台服務；車體進場另確認'],
    ['服務人員（最多5位）', '', staffRevenue || '', '夜間 2 小時，每位 2,000'],
    ['叢林風餐檯佈置', '', decorRevenue || '', '限餐檯桌面與餐飲區'],
    ['運送／特殊設備', '', transportRevenue || '', '依場地動線另確認'],
    ['其他', '', otherRevenue || '', variant.otherNote || '']
  ]);

  sheet.getRange('C30').setValue('總金額');
  sheet.getRange('E30').setValue(totalRevenue || '');
  sheet.getRange('I29').setValue('估成本小計');
  sheet.getRange('J29').setValue(totalCost || '');
  sheet.getRange('I30').setValue('訂單成本');
  sheet.getRange('J30').setValue(totalCost || '');
  sheet.getRange('I31').setValue('毛利率');
  sheet.getRange('J31').setValue(overallMargin || '');
  sheet.getRange('E22:E30').setNumberFormat('$#,##0');
  sheet.getRange('I7:J31').setNumberFormat('$#,##0');
  sheet.getRange('J31').setNumberFormat('0.0%');

  sheet.getRange('K10').setValue('方案定位');
  sheet.getRange('L10').setValue(variant.positioning || '');
  sheet.getRange('K11').setValue('酒水備註');
  sheet.getRange('L11').setValue(variant.alcoholNote || '行動調酒吧台先報，不承諾車體進場。');
  sheet.getRange('K12').setValue('人員備註');
  sheet.getRange('L12').setValue(variant.staffNote || '最多 5 位服務人員；更高服務密度需另行安排外部人力。');
  sheet.getRange('K13').setValue('佈置備註');
  sheet.getRange('L13').setValue(variant.decorNote || '叢林風範圍限餐檯桌面與餐飲區，大型背板/舞台另估。');
  sheet.getRange('K14').setValue('餐點成本');
  sheet.getRange('L14').setValue(foodCost === '' ? '' : 'NT$' + foodCost);
  sheet.getRange('K15').setValue('產出接口');
  sheet.getRange('L15').setValue('createQuoteVariants adapter 2026-05-19；master 表格/公式未改');

  SpreadsheetApp.flush();
}

function clonePlainObject_(obj) {
  var out = {};
  obj = obj || {};
  for (var key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) out[key] = obj[key];
  }
  return out;
}

function joinNonEmpty_(parts, sep) {
  var kept = [];
  for (var i = 0; i < parts.length; i++) {
    if (parts[i] !== undefined && parts[i] !== null && String(parts[i]).trim() !== '') {
      kept.push(String(parts[i]).trim());
    }
  }
  return kept.join(sep);
}

function toNumber_(value) {
  if (value === undefined || value === null || value === '') return 0;
  var num = Number(String(value).replace(/[$,％%]/g, ''));
  return isNaN(num) ? 0 : num;
}

function variantAmount_(variant, extra, keys, fallback) {
  for (var i = 0; i < keys.length; i++) {
    if (variant[keys[i]] !== undefined && variant[keys[i]] !== null && variant[keys[i]] !== '') {
      return toNumber_(variant[keys[i]]);
    }
  }
  for (var j = 0; j < keys.length; j++) {
    if (extra[keys[j]] !== undefined && extra[keys[j]] !== null && extra[keys[j]] !== '') {
      return toNumber_(extra[keys[j]]);
    }
  }
  return fallback;
}

function calcMarginDecimal_(revenue, cost, preset) {
  if (preset !== undefined && preset !== null && preset !== '') {
    var presetNum = toNumber_(preset);
    return presetNum > 1 ? presetNum / 100 : presetNum;
  }
  var rev = toNumber_(revenue);
  if (!rev) return 0;
  return (rev - toNumber_(cost)) / rev;
}

function calcRatioDecimal_(numerator, denominator) {
  var denom = toNumber_(denominator);
  if (!denom) return 0;
  return toNumber_(numerator) / denom;
}

function calcVariantTotalItems_(variant) {
  var menu = variant.menu || [];
  var total = 0;
  for (var i = 0; i < menu.length; i++) total += toNumber_(menu[i].qty);
  return total || '';
}

// ─────────────────────────────────────────
// 表單預填資料
// ─────────────────────────────────────────

/**
 * 從 QUOTE_DRAFT 讀取預填資料供表單使用（對應 C1:F55 框線內版面，2026-04-08 修正）
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

// ─────────────────────────────────────────
// 條款函式已移到 contractTerms.gs（v4.0 四版）
// getContractTermsV4 / resolveContractVersion / isCorporateEventType / getBankInfoBlock
// 舊的 getDepositStandardTerms / getLumpSumAfterTerms 已於 2026-04-08 晚三修移除
// ─────────────────────────────────────────

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

  // 從 sheetUrl 抽出 spreadsheet id 給 IMPORTRANGE 用
  var quoteIdMatch = sheetUrl.match(/\/d\/([a-zA-Z0-9_-]+)/);
  var quoteId      = quoteIdMatch ? quoteIdMatch[1] : '';

  // L/M 欄使用 IMPORTRANGE 形成動態連結（2026-04-08 Owner 需求）
  // 原本是靜態字串 + 手動 syncQuoteStatus_ 拉取，改為 live formula。
  // 首次使用時 SALES_INTAKE 會彈出 #REF! → 需點「允許存取」授權一次這個 source sheet。
  var quoteStatusFormula   = quoteId
    ? '=IFERROR(IMPORTRANGE("' + quoteId + '","報價單!N5"),"報價中")'
    : '';
  var paymentStatusFormula = quoteId
    ? '=IFERROR(IMPORTRANGE("' + quoteId + '","報價單!N7"),"未匯")'
    : '';

  var row = [
    caseId,                      // A: case_id
    createdAt,                   // B: created_at
    'quote-system-v3.8-verified',// C: source
    formData.clientName,         // D: client_name
    formData.company    || '',   // E: company
    formData.phone      || '',   // F: phone
    formData.eventType  || '',   // G: event_type
    formData.eventDate  || '',   // H: event_date
    formData.location   || '',   // I: location
    formData.pax        || '',   // J: pax
    sheetUrl,                    // K: sheet_url
    quoteStatusFormula,          // L: quote_status (IMPORTRANGE live link)
    paymentStatusFormula,        // M: payment_status (IMPORTRANGE live link)
    '',                          // N: （預留）
    ''                           // O: notes
  ];

  // 用 setValues 寫入一整列（含 = 開頭的 IMPORTRANGE 字串會被解析為 formula）
  var lastRow = intakeSheet.getLastRow() + 1;
  intakeSheet.getRange(lastRow, 1, 1, row.length).setValues([row]);
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
// T-A5-002 一次性修復：品項名稱對齊 + 重複行清除
// ─────────────────────────────────────────

/**
 * 修復 master QUOTE_DRAFT 中的兩個品項名稱問題（T-A5-002 Owner 決策 2026-06-23）：
 * 1. 「日式章魚燒明太子可頌」→「明太子可頌」（符合 Items standard_name，G 欄可自動帶成本）
 * 2. 「府城冰梅醬蝦棗」→「台南古早味蝦棗」（符合 Items standard_name，G 欄可自動帶成本）
 * 3. D7:D20 若有重複品項，保留第一個、清除後出現的同名列（含 F 欄數量）
 *
 * 冪等：可重複執行；已正確則跳過。
 * 可逆：只改 D 欄字串值，不刪列、不改公式結構。若需還原，手動改回原名即可。
 */
function fixMasterTemplate() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(TEMPLATE_SHEET_NAME);
  if (!sheet) throw new Error('找不到 QUOTE_DRAFT 分頁');

  var ITEM_ROW_START = 7;   // D7 開始
  var ITEM_ROW_END   = 20;  // D20 結束
  var rows = ITEM_ROW_END - ITEM_ROW_START + 1;

  var nameRename = [
    { from: '日式章魚燒明太子可頌', to: '明太子可頌' },
    { from: '府城冰梅醬蝦棗',      to: '台南古早味蝦棗' }
  ];

  var changeLog = [];

  // Step 1：名稱替換（長名 → 與 Items 表一致的短名）
  var dRange  = sheet.getRange(ITEM_ROW_START, 4, rows, 1);
  var dValues = dRange.getValues();
  for (var r = 0; r < rows; r++) {
    var cell = String(dValues[r][0] || '').trim();
    for (var m = 0; m < nameRename.length; m++) {
      if (cell === nameRename[m].from) {
        dValues[r][0] = nameRename[m].to;
        changeLog.push('D' + (ITEM_ROW_START + r) + '：' + nameRename[m].from + ' → ' + nameRename[m].to);
      }
    }
  }
  dRange.setValues(dValues);

  // Step 2：重複品項清除（保留第一次出現的列，清除後續同名列的 D 與 F 欄）
  var seen = {};
  dValues = sheet.getRange(ITEM_ROW_START, 4, rows, 1).getValues();
  for (var r = 0; r < rows; r++) {
    var name = String(dValues[r][0] || '').trim();
    if (!name) continue;
    if (seen[name]) {
      sheet.getRange(ITEM_ROW_START + r, 4).clearContent();
      sheet.getRange(ITEM_ROW_START + r, 6).clearContent();
      changeLog.push('D' + (ITEM_ROW_START + r) + '：重複品項「' + name + '」清除（D + F 欄）');
    } else {
      seen[name] = true;
    }
  }

  if (changeLog.length === 0) {
    Logger.log('fixMasterTemplate: 無需修改，master QUOTE_DRAFT 已是正確狀態。');
  } else {
    changeLog.forEach(function(line) { Logger.log(line); });
    Logger.log('fixMasterTemplate 完成，共修改 ' + changeLog.length + ' 處。');
  }
}

// ─────────────────────────────────────────
// fromMaster 模式：從 master QUOTE_DRAFT 讀取已有資料，組 formData 後走正常流程
// ─────────────────────────────────────────

/**
 * 當 bot_a6 已將資料寫入 master QUOTE_DRAFT sheet，
 * 傳 {action:"createQuote", fromMaster:true} 時呼叫此函數。
 * 反向讀取 sheet cells → 組 formData → 呼叫 createQuote()。
 */
function createQuoteFromMaster_() {
  try {
    var ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
    var sheet = ss.getSheetByName(TEMPLATE_SHEET_NAME);
    if (!sheet) throw new Error('找不到 QUOTE_DRAFT sheet');

    var rawDate = sheet.getRange('F2').getValue();
    var rawTime = sheet.getRange('F3').getValue();

    var formData = {
      clientName : sheet.getRange('D2').getValue() || '',
      company    : sheet.getRange('B3').getValue() || '',
      phone      : sheet.getRange('B4').getValue() || '',
      address    : sheet.getRange('D3').getValue() || '',
      eventType  : sheet.getRange('D4').getValue() || '',
      pax        : String(sheet.getRange('F4').getValue() || ''),
      eventName  : sheet.getRange('D5').getValue() || '',
      totalItems : sheet.getRange('F5').getValue() || '',
      eventDate  : rawDate instanceof Date
                    ? Utilities.formatDate(rawDate, 'Asia/Taipei', 'yyyy-MM-dd')
                    : (rawDate ? String(rawDate) : ''),
      time       : rawTime instanceof Date
                    ? Utilities.formatDate(rawTime, 'Asia/Taipei', 'HH:mm')
                    : (rawTime ? String(rawTime) : '')
    };

    var result = createQuote(formData);

    return ContentService.createTextOutput(JSON.stringify({
      success  : true,
      caseId   : result.caseId,
      fileName : result.fileName,
      spreadsheetId: result.spreadsheetId,
      url      : result.url
    })).setMimeType(ContentService.MimeType.JSON);

  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error  : err.message
    })).setMimeType(ContentService.MimeType.JSON);
  }
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
      clientName    : params.clientName    || '',
      company       : params.company       || '',
      phone         : params.phone         || '',
      address       : params.address       || '',
      eventType     : params.eventType     || '',
      eventDate     : params.eventDate     || '',
      location      : params.location      || '',
      pax           : params.pax           || '',
      depositAmount : params.depositAmount || '3000',
      dietaryNotes  : params.dietaryNotes  || '',
      floorFeeMode  : params.floorFeeMode  || 'none'
    };

    var result = createQuote(formData);

    return ContentService.createTextOutput(JSON.stringify({
      success  : true,
      caseId   : result.caseId,
      fileName : result.fileName,
      spreadsheetId: result.spreadsheetId,
      url      : result.url
    })).setMimeType(ContentService.MimeType.JSON);

  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error  : err.message
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
