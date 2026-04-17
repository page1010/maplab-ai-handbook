// ApiEndpoint.gs — HTTP doPost 路由
// 供 A6 Telegram bot 透過 HTTP POST 觸發報價/提案功能
// ⚠️ LineWebhook.gs 有自己的 doPost（LINE OA 用），必須透過 .claspignore 排除
//    否則 GAS 會有兩個 doPost 衝突

/**
 * HTTP POST 入口
 * Body: { "action": "createQuote" | "createSlide", ...params }
 *
 * createQuote 需要：clientName, company, phone, address, eventType, eventDate, location, pax
 * createQuote fromMaster：{ "action": "createQuote", "fromMaster": true } — 從 master QUOTE_DRAFT 讀資料
 * createSlide 不需要額外參數（讀 QUOTE_DRAFT Sheet）
 */
function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var action = body.action || '';

    if (action === 'createQuote') {
      if (body.fromMaster === true || body.fromMaster === 'true') {
        return createQuoteFromMaster_();
      }
      // handleQuoteRequest_ 已自行回傳 ContentService JSON，直接 return
      return handleQuoteRequest_(body);

    } else if (action === 'createSlide') {
      try {
        var result = generateProposalV2();
        return ContentService
          .createTextOutput(JSON.stringify({ success: true, url: result.url, name: result.name }))
          .setMimeType(ContentService.MimeType.JSON);
      } catch (slideErr) {
        return ContentService
          .createTextOutput(JSON.stringify({ success: false, error: slideErr.message }))
          .setMimeType(ContentService.MimeType.JSON);
      }

    } else if (action === 'addItem') {
      return addItemToDatabase_(body);

    } else {
      return ContentService
        .createTextOutput(JSON.stringify({ success: false, error: 'Unknown action: ' + action }))
        .setMimeType(ContentService.MimeType.JSON);
    }

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * 新增品項到 Items 資料庫
 * Body: { action: "addItem", standard_name, category, default_cost, unit }
 */
function addItemToDatabase_(data) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Items');
  if (!sheet) {
    return ContentService.createTextOutput(
      JSON.stringify({ success: false, error: 'Items sheet not found' })
    ).setMimeType(ContentService.MimeType.JSON);
  }

  var lastRow = sheet.getLastRow();
  var ids = sheet.getRange('A2:A' + Math.max(lastRow, 2)).getValues().flat().filter(String);

  // 依 category 決定前綴，各前綴獨立計數
  var prefix = 'APP';
  var cat = (data.category || '').trim();
  if (cat === '湯品') prefix = 'SOUP';
  else if (cat === '8L壺裝飲品' || cat.indexOf('飲品') >= 0) prefix = 'BEV';
  else if (cat === '手作精緻甜點 Dessert' || cat.indexOf('甜點') >= 0) prefix = 'DES';

  var maxNum = 0;
  ids.forEach(function(id) {
    if (typeof id === 'string' && id.startsWith(prefix)) {
      var num = parseInt(id.replace(prefix, ''), 10);
      if (!isNaN(num) && num > maxNum) maxNum = num;
    }
  });
  var newId = prefix + ('000' + (maxNum + 1)).slice(-3);

  var newRow = lastRow + 1;
  sheet.getRange(newRow, 1).setValue(newId);
  sheet.getRange(newRow, 2).setValue(cat);
  sheet.getRange(newRow, 3).setValue(data.standard_name || '');
  sheet.getRange(newRow, 5).setValue(Number(data.default_cost) || 0);
  sheet.getRange(newRow, 6).setValue(data.unit || '份');

  return ContentService.createTextOutput(
    JSON.stringify({
      success: true,
      item_id: newId,
      category: cat,
      standard_name: data.standard_name,
      default_cost: data.default_cost,
      unit: data.unit,
      message: '品項已新增：' + data.standard_name + ' (' + newId + ')'
    })
  ).setMimeType(ContentService.MimeType.JSON);
}
