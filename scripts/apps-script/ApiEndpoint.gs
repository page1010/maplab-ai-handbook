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
