// ============================================================
// generateProposal_v2.gs
// 文學館標準模板 × 品牌色票 × QUOTE_DRAFT 自動讀取
// 修正版 2026-04-04：圖片比例、空白格、頁面順序、[photo] 文字
// ============================================================

var BRAND = {
  CREAM:    '#FAF7F2',  // 奶油白（主背景）
  SAND:     '#EDE5D8',  // 暖米（次背景）
  OLIVE:    '#3A3A2E',  // 深橄欖（主文字）
  BROWN:    '#7A5C3E',  // 棕褐（強調 / 右欄背景）
  SAGE:     '#8FA68E',  // 鼠尾草（輔助）
  BLUSH:    '#D9C4B8',  // 裸粉
  CHARCOAL: '#2C2C2C',  // 炭黑
  WHITE:    '#FFFFFF',
  MID_GRAY: '#888888'
};

var SLIDES_TEMPLATE_ID  = '1s4VJY3hIoIDd5gF_WcKVlTNzoAYr6YIq69oZ0lDnU5E';
var PROPOSALS_FOLDER_ID = '1uGBCSTLFRVm5ZPh6v10G-tImf2QB5deu';
var SPREADSHEET_ID      = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg';

// ============================================================
// 主函數 — 在 GAS 編輯器直接執行這個函數
// ============================================================
function generateProposalV2() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var qd = ss.getSheetByName('QUOTE_DRAFT');

  // ── Step 1：讀客戶資訊 ──────────────────────────────────
  var clientName  = String(qd.getRange('D2').getValue() || '客戶');
  var company     = String(qd.getRange('B3').getValue() || '').trim();
  var rawEventDate = qd.getRange('E2').getValue();
  var eventDate   = _formatDate(rawEventDate);
  // 檔名用 YYYYMMDD，來源有效日期 fallback 當日
  var eventDateForFile;
  if (rawEventDate instanceof Date && !isNaN(rawEventDate.getTime())) {
    eventDateForFile = Utilities.formatDate(rawEventDate, 'Asia/Taipei', 'yyyyMMdd');
  } else if (eventDate !== '-') {
    eventDateForFile = eventDate.replace(/-/g, '');
  } else {
    eventDateForFile = Utilities.formatDate(new Date(), 'Asia/Taipei', 'yyyyMMdd');
    Logger.log('[V2] ⚠️ E2 活動日期欄位為空，以今日日期代替 → 請補填 QUOTE_DRAFT E2');
  }
  var venue       = String(qd.getRange('D3').getValue() || '-');
  var eventType   = String(qd.getRange('D4').getValue() || '-');
  var eventTime   = String(qd.getRange('E3').getValue() || '-');
  var pax         = String(qd.getRange('F4').getValue() || '-');
  var totalItems  = String(qd.getRange('F5').getValue() || '-');
  var totalAmount = Number(qd.getRange('E29').getValue()) || 0;
  var notes       = String(qd.getRange('E30').getValue() || '-');

  Logger.log('[V2] 客戶=' + clientName + ' 日期=' + eventDate + ' 金額=' + totalAmount);

  // ── Step 2：讀品項 ──────────────────────────────────────
  var itemRanges = [
    {rows: [8, 9, 10],   label: '餐點'},
    {rows: [12, 13, 14], label: '餐點'},
    {rows: [15, 16],     label: '餐點'}
  ];
  var selectedItems = [];
  itemRanges.forEach(function(range) {
    range.rows.forEach(function(r) {
      var name = String(qd.getRange('D' + r).getValue() || '').trim();
      var qty  = String(qd.getRange('G' + r).getValue() || '').trim();
      if (name) {
        selectedItems.push({ zh: name, qty: qty });
      }
    });
  });

  Logger.log('[V2] 品項數=' + selectedItems.length + ': ' + selectedItems.map(function(x){return x.zh}).join(', '));

  // ── Step 3：從 Items 表比對 image_url ──────────────────
  var imgMap = _buildImageMap(ss);
  selectedItems.forEach(function(item) {
    item.imageUrl = _findImage(item.zh, imgMap);
    Logger.log('[V2] 圖片 ' + item.zh + ' → ' + (item.imageUrl ? 'found' : 'none'));
  });

  // ── Step 4：複製模板 ────────────────────────────────────
  var templateFile = DriveApp.getFileById(SLIDES_TEMPLATE_ID);
  var folder       = DriveApp.getFolderById(PROPOSALS_FOLDER_ID);
  var fileName     = eventDateForFile + '_' + clientName + (company ? '_' + company : '') + '_提案簡報';
  var newFile      = templateFile.makeCopy(fileName, folder);
  var pres         = SlidesApp.openById(newFile.getId());

  Logger.log('[V2] 已複製模板 → ' + fileName + ' id=' + newFile.getId());

  // ── Step 5：找到 Ready to Create 結尾頁，保留不刪 ──────
  // Bug 3 修正：結尾頁必須永遠在最後，先找到它、其他動態頁才刪
  var allSlides = pres.getSlides();
  var total     = allSlides.length;
  Logger.log('[V2] 模板頁數=' + total);

  var readyToCreateSlide = null;
  for (var si = 0; si < allSlides.length; si++) {
    var elements = allSlides[si].getPageElements();
    for (var ei = 0; ei < elements.length; ei++) {
      try {
        var txt = elements[ei].asShape().getText().asString();
        if (txt.indexOf('Ready') >= 0 && txt.indexOf('Create') >= 0) {
          readyToCreateSlide = allSlides[si];
          Logger.log('[V2] 找到 Ready to Create: P' + (si + 1));
          break;
        }
      } catch(e) {}
    }
    if (readyToCreateSlide) break;
  }

  // P8 以後的頁面全部刪掉，但跳過 Ready to Create（之後移到最後）
  allSlides = pres.getSlides();
  for (var si = allSlides.length - 1; si >= 7; si--) {
    if (allSlides[si] !== readyToCreateSlide) {
      allSlides[si].remove();
    }
  }
  Logger.log('[V2] 動態頁刪除完畢，剩餘頁數=' + pres.getSlides().length);

  // ── Step 6：插入 Menu Showcase 頁（3×2 格）──────────────
  var insertIdx     = 7; // P8 位置（0-indexed）
  var totalMenuPages = Math.ceil(selectedItems.length / 6) || 1;

  for (var p = 0; p < totalMenuPages; p++) {
    var pageItems = selectedItems.slice(p * 6, (p + 1) * 6);
    _addMenuSlide(pres, insertIdx + p, pageItems);
    Logger.log('[V2] Menu 頁 ' + (p + 1) + ' 完成');
  }

  // ── Step 7：插入 Quotation 頁 ───────────────────────────
  var fields = [
    ['活動日期', eventDate],
    ['活動類型', eventType],
    ['活動時間', eventTime],
    ['預估人數', pax + ' 人'],
    ['餐點件數', totalItems + ' 件'],
    ['活動地點', venue]
  ];
  _addQuotationSlide(pres, totalAmount, fields, notes);
  Logger.log('[V2] Quotation 頁完成');

  // ── Step 8：插入 Terms 頁 ────────────────────────────────
  _addTermsSlide(pres, clientName, eventDate);
  Logger.log('[V2] Terms 頁完成');

  // ── Step 9：Ready to Create 移到最後 ────────────────────
  // Bug 3 修正：結尾頁永遠在最後
  if (readyToCreateSlide) {
    var finalCount = pres.getSlides().length;
    readyToCreateSlide.move(finalCount - 1);
    Logger.log('[V2] Ready to Create 已移至最後: P' + finalCount);
  } else {
    Logger.log('[V2] 找不到 Ready to Create 頁，略過');
  }

  // ── 完成 ─────────────────────────────────────────────────
  pres.saveAndClose();
  var url = 'https://docs.google.com/presentation/d/' + newFile.getId() + '/edit';
  Logger.log('[V2] 完成！URL=' + url);
  try {
    SpreadsheetApp.getUi().alert('✅ 提案簡報已產生！\n\n' + fileName + '\n\n' + url);
  } catch(e) {
    Logger.log('[V2] 非試算表 context，略過 alert');
  }
  return { ok: true, url: url, name: fileName };
}

// ============================================================
// 輔助：Menu Showcase 頁（3×2 格）
// Bug 2 修正：只建立有品項的格子，不建立空格
// Bug 4 修正：無圖品項完全不放圖片區塊（不留 [photo]）
// ============================================================
function _addMenuSlide(pres, insertIdx, pageItems) {
  var s = pres.insertSlide(insertIdx, SlidesApp.PredefinedLayout.BLANK);
  s.getBackground().setSolidFill(BRAND.WHITE);

  // 標題列背景（奶油白 bar）
  var titleBar = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, 720, 52);
  titleBar.getFill().setSolidFill(BRAND.CREAM);
  titleBar.getBorder().setTransparent();

  // 標題文字
  var titleBox = s.insertTextBox('MENU', 40, 10, 300, 32);
  titleBox.getText().getTextStyle()
    .setFontSize(18).setFontFamily('Georgia')
    .setForegroundColor(BRAND.OLIVE).setBold(true);

  // 底線裝飾（棕褐）
  var deco = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 40, 44, 60, 2);
  deco.getFill().setSolidFill(BRAND.BROWN);
  deco.getBorder().setTransparent();

  // Bug 2 修正：只建立有品項的格子
  for (var n = 0; n < pageItems.length; n++) {
    if (!pageItems[n] || !pageItems[n].zh) continue;  // 跳過空品項

    var col = n % 3;
    var row = Math.floor(n / 3);
    var ix  = 40 + col * 213;  // 3 欄：40, 253, 466
    var iy  = 62 + row * 163;  // 2 列：62, 225

    // 圖片區 — Bug 4 修正：有圖才插入，無圖不放任何圖片元素
    var imgUrl = pageItems[n].imageUrl || '';
    if (imgUrl) {
      try {
        var blob = _fetchImageBlob(imgUrl, n);
        if (blob) {
          // Bug 1 修正：blob 已經由 weserv.nl 裁切成 800×420（比例 ~1.9:1）
          // 插入 210×110 不會拉伸（比例相同）
          var img = s.insertImage(blob, ix, iy, 210, 110);
          img.setLeft(ix).setTop(iy).setWidth(210).setHeight(110);
        }
      } catch(e) {
        Logger.log('[V2] 圖片載入失敗 ' + pageItems[n].zh + ': ' + e.message);
        // 圖片失敗時：不放任何佔位，只顯示品名
      }
    }
    // 無 imgUrl 或圖片載入失敗：完全不放圖片區塊，只有品名標籤

    // 品名標籤：中文品名 (數量) — 無圖時調整位置置中
    var label = pageItems[n].zh + (pageItems[n].qty ? ' (' + pageItems[n].qty + ')' : '');
    var labelY = imgUrl ? iy + 114 : iy + 50;  // 有圖放圖下方，無圖置中
    var nb = s.insertTextBox(label, ix, labelY, 210, 28);
    nb.getText().getTextStyle()
      .setFontSize(8).setFontFamily('Georgia').setForegroundColor(BRAND.OLIVE);
    nb.getText().getParagraphStyle()
      .setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);
  }
}

// ============================================================
// 輔助：Quotation 頁
// ============================================================
function _addQuotationSlide(pres, totalAmount, fields, notes) {
  var s = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s.getBackground().setSolidFill(BRAND.CREAM);

  // 頂部金線
  var topLine = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 40, 28, 100, 2.5);
  topLine.getFill().setSolidFill(BRAND.BROWN);
  topLine.getBorder().setTransparent();

  // 標題
  var title = s.insertTextBox('Quotation', 40, 36, 320, 34);
  title.getText().setText('Quotation');
  title.getText().getTextStyle()
    .setFontSize(26).setFontFamily('Georgia')
    .setForegroundColor(BRAND.OLIVE).setBold(true);

  var sub = s.insertTextBox('MAPLAB Kitchen — Private Catering', 40, 70, 400, 18);
  sub.getText().setText('MAPLAB Kitchen — Private Catering');
  sub.getText().getTextStyle()
    .setFontSize(10).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);

  // 左欄：資訊表（白底圓角）
  var infoPanel = s.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE, 40, 100, 350, 210);
  infoPanel.getFill().setSolidFill(BRAND.WHITE);
  infoPanel.getBorder().getLineFill().setSolidFill(BRAND.BLUSH);
  infoPanel.getBorder().setWeight(0.5);

  var infoY = 112;
  for (var i = 0; i < fields.length; i++) {
    var lbl = s.insertTextBox(fields[i][0], 55, infoY + i * 30, 140, 24);
    lbl.getText().setText(fields[i][0]);
    lbl.getText().getTextStyle()
      .setFontSize(9).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);

    var val = s.insertTextBox(String(fields[i][1] || '-'), 200, infoY + i * 30, 185, 24);
    val.getText().setText(String(fields[i][1] || '-'));
    val.getText().getTextStyle()
      .setFontSize(9).setFontFamily('Georgia')
      .setForegroundColor(BRAND.OLIVE).setBold(true);
  }

  // 右欄：金額（棕褐底）
  var amtPanel = s.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE, 420, 100, 260, 210);
  amtPanel.getFill().setSolidFill(BRAND.BROWN);
  amtPanel.getBorder().setTransparent();

  var amtLbl = s.insertTextBox('Total Amount', 420, 138, 260, 22);
  amtLbl.getText().setText('Total Amount');
  amtLbl.getText().getTextStyle()
    .setFontSize(11).setFontFamily('Georgia').setForegroundColor(BRAND.CREAM);
  amtLbl.getText().getParagraphStyle()
    .setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

  var amtStr = 'NT$ ' + totalAmount.toLocaleString();
  var amtVal = s.insertTextBox(amtStr, 420, 168, 260, 50);
  amtVal.getText().setText(amtStr);
  amtVal.getText().getTextStyle()
    .setFontSize(30).setFontFamily('Georgia')
    .setForegroundColor(BRAND.WHITE).setBold(true);
  amtVal.getText().getParagraphStyle()
    .setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

  var depLbl = s.insertTextBox('訂金 Deposit', 420, 232, 260, 18);
  depLbl.getText().setText('訂金 Deposit');
  depLbl.getText().getTextStyle()
    .setFontSize(9).setFontFamily('Georgia').setForegroundColor(BRAND.BLUSH);
  depLbl.getText().getParagraphStyle()
    .setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

  var depAmt = Math.round(totalAmount * 0.3 / 1000) * 1000;
  var depVal = s.insertTextBox('NT$ ' + depAmt.toLocaleString(), 420, 253, 260, 28);
  depVal.getText().setText('NT$ ' + depAmt.toLocaleString());
  depVal.getText().getTextStyle()
    .setFontSize(18).setFontFamily('Georgia')
    .setForegroundColor(BRAND.CREAM).setBold(true);
  depVal.getText().getParagraphStyle()
    .setParagraphAlignment(SlidesApp.ParagraphAlignment.CENTER);

  // 備註
  var nTitle = s.insertTextBox('備註', 40, 330, 200, 18);
  nTitle.getText().setText('備註');
  nTitle.getText().getTextStyle()
    .setFontSize(10).setFontFamily('Georgia')
    .setForegroundColor(BRAND.BROWN).setBold(true);

  var nText = (notes && notes !== '-') ? notes : '無';
  var nBox = s.insertTextBox(nText, 40, 352, 640, 28);
  nBox.getText().setText(nText);
  nBox.getText().getTextStyle()
    .setFontSize(9).setFontFamily('Georgia').setForegroundColor(BRAND.OLIVE);

  // 服務包含
  var iTitle = s.insertTextBox('服務包含 Included Services', 40, 390, 350, 18);
  iTitle.getText().setText('服務包含 Included Services');
  iTitle.getText().getTextStyle()
    .setFontSize(10).setFontFamily('Georgia')
    .setForegroundColor(BRAND.BROWN).setBold(true);

  var included = '專業餐點製作 · 外場佈置服務 · 器具提供 · 活動當日全程服務';
  var iBox = s.insertTextBox(included, 40, 412, 640, 22);
  iBox.getText().setText(included);
  iBox.getText().getTextStyle()
    .setFontSize(9).setFontFamily('Georgia').setForegroundColor(BRAND.OLIVE);
}

// ============================================================
// 輔助：Terms 頁
// ============================================================
function _addTermsSlide(pres, clientName, eventDate) {
  var s = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s.getBackground().setSolidFill(BRAND.CREAM);

  // 頂部金線
  var topLine = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 40, 28, 100, 2.5);
  topLine.getFill().setSolidFill(BRAND.BROWN);
  topLine.getBorder().setTransparent();

  var t2 = s.insertTextBox('Terms & Conditions', 40, 36, 400, 28);
  t2.getText().setText('Terms & Conditions');
  t2.getText().getTextStyle()
    .setFontSize(20).setFontFamily('Georgia')
    .setForegroundColor(BRAND.OLIVE).setBold(true);

  var sub2 = s.insertTextBox('簽約使用條款及細則', 40, 64, 400, 16);
  sub2.getText().setText('簽約使用條款及細則');
  sub2.getText().getTextStyle()
    .setFontSize(9).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);

  var termsData = [
    ['第一條｜訂單與付款',
      '訂金繳付後若客戶自行取消，訂金不予退還。\n' +
      '尾款須於活動日前完成，或活動當日佈置完畢後支付。\n' +
      '不可抗力因素可申請延期或轉讓一次（限 6 個月內）。\n' +
      '活動當日取消須支付總金額 80% 作為賠償。'],
    ['第二條｜現場服務',
      '超過 30 分鐘車程需另收車馬費。\n' +
      '2 樓無電梯加收 $800 搬運費，3 樓以上需自行搬運。\n' +
      '送達地點 50 公尺內需有停車位。\n' +
      '佈置器材活動結束後須完整歸還。'],
    ['第三條｜產品責任',
      '本公司已投保國泰產物產品責任險。\n' +
      '餐點需於 2–3 小時內食用完畢。\n' +
      '交付後因保存不當導致品質變化，恕不負責。'],
    ['第四條｜合約效力',
      '支付訂金後即視為同意本條款。\n' +
      '活動當日將於場地內拍攝紀錄照片。\n' +
      '爭議由本公司所在地法院管轄。']
  ];

  var ty = 88;
  termsData.forEach(function(sec) {
    var secTitle = s.insertTextBox(sec[0], 40, ty, 660, 16);
    secTitle.getText().setText(sec[0]);
    secTitle.getText().getTextStyle()
      .setFontSize(8).setFontFamily('Georgia')
      .setForegroundColor(BRAND.BROWN).setBold(true);
    ty += 16;

    var secBody = s.insertTextBox(sec[1], 50, ty, 650, 48);
    secBody.getText().setText(sec[1]);
    secBody.getText().getTextStyle()
      .setFontSize(7).setFontFamily('Georgia').setForegroundColor(BRAND.CHARCOAL);
    ty += 50;
  });

  // 簽名區
  ty += 8;
  var sigLine = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 40, ty, 660, 1.5);
  sigLine.getFill().setSolidFill(BRAND.BROWN);
  sigLine.getBorder().setTransparent();
  ty += 10;

  var sigT = s.insertTextBox('確認簽署 Confirmation', 40, ty, 300, 18);
  sigT.getText().setText('確認簽署 Confirmation');
  sigT.getText().getTextStyle()
    .setFontSize(10).setFontFamily('Georgia')
    .setForegroundColor(BRAND.OLIVE).setBold(true);
  ty += 22;

  var cL = s.insertTextBox('客戶簽名 Client Signature', 40, ty, 280, 14);
  cL.getText().setText('客戶簽名 Client Signature');
  cL.getText().getTextStyle()
    .setFontSize(8).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);
  var cLine = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 40, ty + 35, 280, 1);
  cLine.getFill().setSolidFill(BRAND.OLIVE);
  cLine.getBorder().setTransparent();
  var cD = s.insertTextBox('日期 Date: _______________', 40, ty + 42, 280, 14);
  cD.getText().setText('日期 Date: _______________');
  cD.getText().getTextStyle()
    .setFontSize(8).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);

  var mL = s.insertTextBox('MAPLAB Kitchen', 400, ty, 280, 14);
  mL.getText().setText('MAPLAB Kitchen');
  mL.getText().getTextStyle()
    .setFontSize(8).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);
  var mLine = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 400, ty + 35, 280, 1);
  mLine.getFill().setSolidFill(BRAND.OLIVE);
  mLine.getBorder().setTransparent();
  var mD = s.insertTextBox('日期 Date: _______________', 400, ty + 42, 280, 14);
  mD.getText().setText('日期 Date: _______________');
  mD.getText().getTextStyle()
    .setFontSize(8).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);
}

// ============================================================
// 輔助：建立 Items 表的 name→imageUrl 映射
// ============================================================
function _buildImageMap(ss) {
  var itemsSheet = ss.getSheetByName('Items');
  var data       = itemsSheet.getDataRange().getValues();
  var headers    = data[0];
  var colName    = headers.indexOf('standard_name');
  var colImgUrl  = headers.indexOf('image_url');
  var map = {};
  for (var i = 1; i < data.length; i++) {
    var name = String(data[i][colName] || '').trim();
    var url  = colImgUrl >= 0 ? String(data[i][colImgUrl] || '').trim() : '';
    if (name && url) map[name] = url;
  }
  return map;
}

// ============================================================
// 輔助：模糊匹配品名找圖片 URL
// ============================================================
function _findImage(zh, imgMap) {
  if (imgMap[zh]) return imgMap[zh];
  for (var key in imgMap) {
    if (zh.indexOf(key) >= 0 || key.indexOf(zh) >= 0) return imgMap[key];
  }
  for (var key in imgMap) {
    if (key.length >= 4 && zh.indexOf(key.substring(0, 4)) >= 0) return imgMap[key];
  }
  return '';
}

// ============================================================
// 輔助：取得圖片 blob — Bug 1 修正
// 所有圖片統一透過 weserv.nl 裁切成 800×420（比例 1.9:1）
// 再插入 210×110 框，比例吻合不拉伸
// ============================================================
function _fetchImageBlob(imageUrl, idx) {
  var driveId = _extractDriveId(imageUrl);

  // 決定 weserv.nl 的來源 URL
  var sourceUrl;
  if (driveId) {
    // Drive 檔案 → 使用直接下載 URL（需要檔案已公開或在同一 GCP 專案）
    sourceUrl = 'https://drive.google.com/uc?export=download&id=' + driveId;
  } else {
    sourceUrl = imageUrl;
  }

  // 統一裁切：800×420 = 210:110 × ~3.8 倍，fit=cover 置中裁切
  var proxyUrl = 'https://images.weserv.nl/?url=' + encodeURIComponent(sourceUrl) +
                 '&output=jpg&q=80&w=800&h=420&fit=cover';
  var response = UrlFetchApp.fetch(proxyUrl, { muteHttpExceptions: true });
  if (response.getResponseCode() === 200) {
    var blob = response.getBlob();
    blob.setName('img_' + idx + '.jpg');
    return blob;
  }

  // weserv.nl 失敗時，Drive 圖片改用 getBlob 直接取得（原圖，不裁切）
  if (driveId) {
    try {
      var file = DriveApp.getFileById(driveId);
      var blob = file.getBlob();
      blob.setName('img_' + idx + '.jpg');
      Logger.log('[V2] weserv 失敗，改用 DriveApp.getBlob: ' + driveId);
      return blob;
    } catch(e) {
      Logger.log('[V2] DriveApp.getBlob 失敗 id=' + driveId + ': ' + e.message);
    }
  }

  Logger.log('[V2] 圖片取得失敗 HTTP=' + response.getResponseCode() + ' url=' + sourceUrl);
  return null;
}

// ============================================================
// 輔助：從各種 Google Drive URL 格式提取 File ID
// ============================================================
function _extractDriveId(url) {
  if (!url) return null;
  var m1 = url.match(/\/file\/d\/([a-zA-Z0-9_-]+)/);
  if (m1) return m1[1];
  var m2 = url.match(/[?&]id=([a-zA-Z0-9_-]+)/);
  if (m2) return m2[1];
  return null;
}

// ============================================================
// 輔助：格式化日期（Date 物件 → yyyy-MM-dd 字串）
// ============================================================
function _formatDate(val) {
  if (!val) return '-';
  if (val instanceof Date) {
    return Utilities.formatDate(val, 'Asia/Taipei', 'yyyy-MM-dd');
  }
  return String(val);
}
