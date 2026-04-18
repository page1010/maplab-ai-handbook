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
 * addItem 需要：{ "action": "addItem", "standard_name", "category", "default_cost", "unit", "image_url"(選), "photo_urls"(選) }
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
      try {
        var result = addItemToDatabase_(body);
        return ContentService
          .createTextOutput(JSON.stringify(Object.assign({ success: true }, result)))
          .setMimeType(ContentService.MimeType.JSON);
      } catch (addErr) {
        return ContentService
          .createTextOutput(JSON.stringify({ success: false, error: addErr.message }))
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
 * 新增品項到 Items 分頁
 * @param {Object} body - {
 *   standard_name,   必填
 *   category,        必填（中文或英文，用來推斷 prefix）
 *   default_cost,    選填
 *   unit,            選填
 *   image_url,       選填 — 主圖 URL（Slide 用）
 *   photo_urls       選填 — 多張照片 URL，逗號分隔（例如 "url1,url2,url3"）
 * }
 * @returns {Object} { item_id, category, standard_name, default_cost, unit, image_url, photo_urls, message }
 */
function addItemToDatabase_(body) {
  var SS_ID = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg';
  var ss = SpreadsheetApp.openById(SS_ID);
  var sheet = ss.getSheetByName('Items');
  if (!sheet) throw new Error('Items 分頁不存在');

  var standardName = (body.standard_name || '').trim();
  var categoryStr  = (body.category || '').trim();
  var categoryRaw  = categoryStr.toUpperCase();
  var defaultCost  = Number(body.default_cost) || 0;
  var unit         = (body.unit || '').trim();
  var imageUrl     = (body.image_url || '').trim();
  var photoUrls    = (body.photo_urls || '').trim();

  if (!standardName) throw new Error('standard_name 為必填');

  // 從 category 字串推斷 source_tag prefix
  var prefix;
  if (categoryRaw.indexOf('DST') !== -1 || categoryRaw.indexOf('甜點') !== -1 || categoryRaw.indexOf('DESSERT') !== -1) {
    prefix = 'DST';
  } else if (categoryRaw.indexOf('BEV') !== -1 || categoryRaw.indexOf('飲品') !== -1 || categoryRaw.indexOf('BEVERAGE') !== -1) {
    prefix = 'BEV';
  } else if (categoryRaw.indexOf('MAIN') !== -1 || categoryRaw.indexOf('主食') !== -1) {
    prefix = 'MAIN';
  } else if (categoryRaw.indexOf('SOUP') !== -1 || categoryRaw.indexOf('湯品') !== -1) {
    prefix = 'SOUP';
  } else {
    prefix = 'APP';
  }

  // 找同 prefix 的最大編號
  var allData = sheet.getDataRange().getValues();
  var maxNum = 0;
  for (var i = 1; i < allData.length; i++) {
    var id = String(allData[i][0] || '');
    if (id.indexOf(prefix) === 0) {
      var num = parseInt(id.replace(prefix, ''), 10);
      if (!isNaN(num) && num > maxNum) maxNum = num;
    }
  }
  var nextNum = maxNum + 1;
  var itemId = prefix + (nextNum < 10 ? '00' : nextNum < 100 ? '0' : '') + nextNum;

  // A=item_id, B=category(全名), C=standard_name, D=default_price(空),
  // E=default_cost, F=unit, G=min_qty, H=is_active, I=note, J=source_tag,
  // K=image_url, L=photo_urls
  sheet.appendRow([
    itemId,       // A
    categoryStr,  // B category（全名，例如「湯品 Soup」）
    standardName, // C
    '',           // D default_price
    defaultCost,  // E
    unit,         // F
    '',           // G min_qty
    'TRUE',       // H is_active
    '',           // I note
    prefix,       // J source_tag
    imageUrl,     // K image_url（主圖，Slide 用）
    photoUrls     // L photo_urls（多圖，逗號分隔）
  ]);

  return {
    item_id:       itemId,
    category:      categoryStr,
    standard_name: standardName,
    default_cost:  defaultCost,
    unit:          unit,
    image_url:     imageUrl,
    photo_urls:    photoUrls,
    message:       '品項已新增：' + standardName + ' (' + itemId + ')'
  };
}
