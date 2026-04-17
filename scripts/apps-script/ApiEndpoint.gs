// ApiEndpoint.gs — HTTP doPost 路由
// 供 A6 Telegram bot 透過 HTTP POST 觸發報價/提案功能
// ⚠️ LineWebhook.gs 有自己的 doPost（LINE OA 用），必須透過 .claspignore 排除
//    否則 GAS 會有兩個 doPost 衝突

/**
 * HTTP POST 入口
 * Body: { "action": "createQuote" | "createSlide" | "addItem", ...params }
 *
 * createQuote 需要：clientName, company, phone, address, eventType, eventDate, location, pax
 * createQuote fromMaster：{ "action": "createQuote", "fromMaster": true } — 從 master QUOTE_DRAFT 讀資料
 * createSlide 不需要額外參數（讀 QUOTE_DRAFT Sheet）
 * addItem 需要：standard_name, category, default_cost, unit
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

    } else if (action === 'addItem') {
      return addItemToDatabase_(body);

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
 * 新增品項到 Items 工作表
 * 接受：standard_name (或 name), category, default_cost, unit
 * 自動生成 item_id（依 category 決定前綴，各前綴獨立計數）
 */
function addItemToDatabase_(data) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Items');
  if (!sheet) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: 'Items 工作表不存在' }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  var itemName = data.standard_name || data.name || '';
  if (!itemName) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: '品名（standard_name）不可為空' }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  // 依 category 決定前綴
  var category = data.category || '餐食小點';
  var prefix = 'APP';
  if (category === '湯品') prefix = 'SOUP';
  else if (category === '8L壺裝飲品') prefix = 'BEV';
  else if (category === '手作精緻甜點 Dessert') prefix = 'DES';

  // 讀取現有 item_id，找同前綴最大序號
  var lastRow = sheet.getLastRow();
  var maxNum = 0;
  if (lastRow >= 2) {
    var ids = sheet.getRange('A2:A' + lastRow).getValues().flat().filter(String);
    ids.forEach(function(id) {
      if (String(id).indexOf(prefix) === 0) {
        var match = String(id).match(/\d+$/);
        if (match) maxNum = Math.max(maxNum, parseInt(match[0], 10));
      }
    });
  }
  var newId = prefix + String(maxNum + 1).padStart(3, '0');

  // 寫入新行（欄位對應：A=item_id, B=category, C=name, E=default_cost, F=unit, H=is_active）
  var newRow = lastRow + 1;
  sheet.getRange(newRow, 1).setValue(newId);
  sheet.getRange(newRow, 2).setValue(category);
  sheet.getRange(newRow, 3).setValue(itemName);
  sheet.getRange(newRow, 5).setValue(Number(data.default_cost) || 0);
  sheet.getRange(newRow, 6).setValue(data.unit || '份');
  sheet.getRange(newRow, 8).setValue(true);  // is_active

  return ContentService
    .createTextOutput(JSON.stringify({
      success: true,
      item_id: newId,
      message: '品項已新增：' + itemName + '（' + newId + '）'
    }))
    .setMimeType(ContentService.MimeType.JSON);
}
