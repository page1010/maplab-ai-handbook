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

// ============================================================
// 語言切換（'zh' 中文 / 'en' 英文）
// ============================================================
var SLIDE_LANG = 'zh';

var SLIDE_TEXT = {
  zh: {
    menuTitle            : '餐點內容',
    quotationTitle       : '報價單',
    quotationSubtitle    : 'MAPLAB Kitchen — 精緻外燴',
    totalAmountLabel     : '報價總額',
    depositLabel         : '訂金 Deposit',
    notesLabel           : '備註',
    serviceIncludesLabel : '服務包含',
    serviceIncludesContent: '專業餐點製作 · 外場佈置服務 · 器具提供 · 活動當日全程服務',
    termsTitle           : '合約條款',
    termsSubtitle        : '簽約使用條款及細則',
    sigConfirmation      : '確認簽署 Confirmation',
    clientSignatureLabel : '客戶簽名 Client Signature',
    signDateField        : '日期 Date: _______________',
    eventDateLabel       : '活動日期',
    eventTypeLabel       : '活動類型',
    eventTimeLabel       : '活動時間',
    headcountLabel       : '預估人數',
    headcountUnit        : ' 人',
    menuItemsLabel       : '餐點件數',
    menuItemsUnit        : ' 件',
    venueLabel           : '活動地點'
  },
  en: {
    menuTitle            : 'Menu',
    quotationTitle       : 'Quotation',
    quotationSubtitle    : 'MAPLAB Kitchen — Private Catering',
    totalAmountLabel     : 'Total Amount',
    depositLabel         : 'Deposit',
    notesLabel           : 'Notes',
    serviceIncludesLabel : 'Service Includes',
    serviceIncludesContent: 'Professional food preparation · Setup & decor · Equipment supply · Full event-day service',
    termsTitle           : 'Terms & Conditions',
    termsSubtitle        : 'Please read carefully before signing',
    sigConfirmation      : 'Confirmation',
    clientSignatureLabel : 'Client Signature',
    signDateField        : 'Date: _______________',
    eventDateLabel       : 'Event Date',
    eventTypeLabel       : 'Event Type',
    eventTimeLabel       : 'Event Time',
    headcountLabel       : 'Headcount',
    headcountUnit        : '',
    menuItemsLabel       : 'Menu Items',
    menuItemsUnit        : '',
    venueLabel           : 'Venue'
  }
};
var T = SLIDE_TEXT[SLIDE_LANG];

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
  // 2026-04-08 依 live sheet 驗證更正：QUOTE_DRAFT 上半部 C/E 欄是 label，D/F 欄才是 value。
  // 原本讀 E2/E3 會讀到 label 字串 "\ndate" / "\n時間\n\n"，現改讀 F2/F3。
  var clientName  = String(qd.getRange('D2').getValue() || '客戶');
  var company     = String(qd.getRange('B3').getValue() || '').trim();
  var rawEventDate = qd.getRange('F2').getValue();  // 原 E2，04-08 改 F2
  var eventDate   = _formatDate(rawEventDate);
  // 檔名用 YYYYMMDD，來源有效日期 fallback 當日
  var eventDateForFile;
  if (rawEventDate instanceof Date && !isNaN(rawEventDate.getTime())) {
    eventDateForFile = Utilities.formatDate(rawEventDate, 'Asia/Taipei', 'yyyyMMdd');
  } else if (eventDate !== '-') {
    eventDateForFile = eventDate.replace(/-/g, '');
  } else {
    eventDateForFile = Utilities.formatDate(new Date(), 'Asia/Taipei', 'yyyyMMdd');
    Logger.log('[V2] ⚠️ F2 活動日期欄位為空，以今日日期代替 → 請補填 QUOTE_DRAFT F2');
  }
  var venue       = String(qd.getRange('D3').getValue() || '-');
  var eventType   = String(qd.getRange('D4').getValue() || '-');
  var eventTime   = String(qd.getRange('F3').getValue() || '-');  // 原 E3，04-08 改 F3
  var pax         = String(qd.getRange('F4').getValue() || '-');
  var totalItems  = String(qd.getRange('F5').getValue() || '-');
  // 2026-04-08 晚二修：live sheet 驗證 總金額 在 E30，不是 E29（E29 是額外成本行）
  var totalAmount = Number(qd.getRange('E30').getValue()) || 0;
  var notes       = '';  // 目前 master 沒有固定 notes cell，留空不讀避免拿到錯的

  Logger.log('[V2] 客戶=' + clientName + ' 日期=' + eventDate + ' 金額=' + totalAmount);

  // ── Step 2：讀品項 ──────────────────────────────────────
  // 2026-04-08 晚二修：依 live sheet 重新校正
  //   - 鹹食 appetizer = row 7-10（原本漏 row 7 比利時薯條）
  //   - 甜點 dessert  = row 12-14
  //   - 飲料 drinks   = row 15-16 **刻意排除**：Owner 明確說飲料不需要圖，不應放進 Slide
  //   - qty 欄位從 G 改 F：live sheet F 欄才是數量（G 欄是空的）
  var itemRanges = [
    {rows: [7, 8, 9, 10], label: '鹹食'},
    {rows: [12, 13, 14],  label: '甜點'}
  ];
  var selectedItems = [];
  itemRanges.forEach(function(range) {
    range.rows.forEach(function(r) {
      var name = String(qd.getRange('D' + r).getValue() || '').trim();
      var qty  = String(qd.getRange('F' + r).getValue() || '').trim();  // 原 G，改 F
      if (name) {
        selectedItems.push({ zh: name, qty: qty });
      }
    });
  });

  Logger.log('[V2] 品項數（未過濾圖片）=' + selectedItems.length + ': ' + selectedItems.map(function(x){return x.zh}).join(', '));

  // ── Step 3：從 Items 表比對 image_url，沒圖的直接從 Slide 排除 ──
  // 2026-04-08 晚二修：Owner 明確需求 — 沒圖的品項完全不進 Slide，不要顯示空名字或空圖。
  var imgMap = _buildImageMap(ss);
  var withImages = [];
  selectedItems.forEach(function(item) {
    item.imageUrl = _findImage(item.zh, imgMap);
    Logger.log('[V2] 圖片 ' + item.zh + ' → ' + (item.imageUrl ? 'found' : 'NONE (excluded from Slide)'));
    if (item.imageUrl) {
      withImages.push(item);
    }
  });
  selectedItems = withImages;
  Logger.log('[V2] 品項數（過濾後剩有圖的）=' + selectedItems.length);

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
    [T.eventDateLabel,  eventDate],
    [T.eventTypeLabel,  eventType],
    [T.eventTimeLabel,  eventTime],
    [T.headcountLabel,  pax + T.headcountUnit],
    [T.menuItemsLabel,  totalItems + T.menuItemsUnit],
    [T.venueLabel,      venue]
  ];
  _addQuotationSlide(pres, totalAmount, fields, notes);
  Logger.log('[V2] Quotation 頁完成');

  // ── Step 8：插入 Terms 頁 ────────────────────────────────
  _addTermsSlide(pres, clientName, eventDate);
  Logger.log('[V2] Terms 頁完成');

  // ── Step 9：Ready to Create 移到最後 ────────────────────
  // Bug 3 修正：結尾頁永遠在最後
  // 2026-04-08 修正：經過 Step 5 的多次 remove() 和 Step 6-8 的多次 insert()，
  // 原本 Step 5 抓的 readyToCreateSlide reference 裡存的內部 page id 已變 stale，
  // 直接呼叫 move() 會拋 "The page (SLIDES_API...) could not be found"。
  // 改為：從目前簡報 re-query 一次，用文字內容比對找到 Ready to Create 頁，
  // 拿新的 reference 再 move()。
  if (readyToCreateSlide) {
    var freshSlides = pres.getSlides();
    var freshReadyToCreate = null;
    for (var si = 0; si < freshSlides.length; si++) {
      var elements = freshSlides[si].getPageElements();
      for (var ei = 0; ei < elements.length; ei++) {
        try {
          var txt = elements[ei].asShape().getText().asString();
          if (txt.indexOf('Ready') >= 0 && txt.indexOf('Create') >= 0) {
            freshReadyToCreate = freshSlides[si];
            break;
          }
        } catch(e) {}
      }
      if (freshReadyToCreate) break;
    }
    if (freshReadyToCreate) {
      var finalCount = pres.getSlides().length;
      freshReadyToCreate.move(finalCount - 1);
      Logger.log('[V2] Ready to Create 已移至最後: P' + finalCount);
    } else {
      Logger.log('[V2] re-query 找不到 Ready to Create 頁，略過 move');
    }
  } else {
    Logger.log('[V2] 一開始就找不到 Ready to Create 頁，略過');
  }

  // ── 完成 ─────────────────────────────────────────────────
  pres.saveAndClose();
  var url = 'https://docs.google.com/presentation/d/' + newFile.getId() + '/edit';
  Logger.log('[V2] 完成！URL=' + url);
  // 2026-04-08 晚二修：alert 只能顯示純文字 URL，改用 HtmlService 彈出真正的可點擊超連結。
  try {
    var escapedName = fileName.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    var html =
      '<div style="font-family:sans-serif;padding:16px;line-height:1.6;">' +
        '<h3 style="margin:0 0 12px;color:#3A3A2E;">✅ 提案簡報已產生</h3>' +
        '<p style="margin:0 0 6px;color:#555;">' + escapedName + '</p>' +
        '<p style="margin:8px 0 0;">' +
          '<a href="' + url + '" target="_blank" rel="noopener"' +
          ' style="display:inline-block;padding:8px 14px;background:#7A5C3E;color:#fff;' +
          'text-decoration:none;border-radius:4px;font-size:14px;">' +
          '🔗 開啟提案簡報（新分頁）' +
          '</a>' +
        '</p>' +
        '<p style="margin-top:14px;color:#888;font-size:11px;word-break:break-all;">' + url + '</p>' +
      '</div>';
    var htmlOutput = HtmlService.createHtmlOutput(html).setWidth(460).setHeight(230);
    SpreadsheetApp.getUi().showModalDialog(htmlOutput, '提案簡報已產生');
  } catch(e) {
    Logger.log('[V2] 非試算表 context，略過彈窗：' + e.message);
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
  var titleBox = s.insertTextBox(T.menuTitle, 40, 10, 300, 32);
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

    // 品名標籤：中文品名 — 無圖時調整位置置中
    var label = pageItems[n].zh;
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
  var title = s.insertTextBox(T.quotationTitle, 40, 36, 320, 34);
  title.getText().setText(T.quotationTitle);
  title.getText().getTextStyle()
    .setFontSize(26).setFontFamily('Georgia')
    .setForegroundColor(BRAND.OLIVE).setBold(true);

  var sub = s.insertTextBox(T.quotationSubtitle, 40, 70, 400, 18);
  sub.getText().setText(T.quotationSubtitle);
  sub.getText().getTextStyle()
    .setFontSize(10).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);

  // 左欄：資訊表（白底圓角）
  var infoPanel = s.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE, 40, 100, 350, 190);
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
  var amtPanel = s.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE, 420, 100, 260, 190);
  amtPanel.getFill().setSolidFill(BRAND.BROWN);
  amtPanel.getBorder().setTransparent();

  var amtLbl = s.insertTextBox(T.totalAmountLabel, 420, 138, 260, 22);
  amtLbl.getText().setText(T.totalAmountLabel);
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

  var depLbl = s.insertTextBox(T.depositLabel, 420, 232, 260, 18);
  depLbl.getText().setText(T.depositLabel);
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

  // 備註（y 向上調整 24pt，讓服務包含區塊不超出頁面底部 405pt）
  var nTitle = s.insertTextBox(T.notesLabel, 40, 306, 200, 18);
  nTitle.getText().setText(T.notesLabel);
  nTitle.getText().getTextStyle()
    .setFontSize(10).setFontFamily('Georgia')
    .setForegroundColor(BRAND.BROWN).setBold(true);

  var nText = (notes && notes !== '-') ? notes : '無';
  var nBox = s.insertTextBox(nText, 40, 322, 640, 24);
  nBox.getText().setText(nText);
  nBox.getText().getTextStyle()
    .setFontSize(9).setFontFamily('Georgia').setForegroundColor(BRAND.OLIVE);

  // 服務包含（底邊 y=369+20=389，留 16pt margin）
  var iTitle = s.insertTextBox(T.serviceIncludesLabel, 40, 351, 350, 18);
  iTitle.getText().setText(T.serviceIncludesLabel);
  iTitle.getText().getTextStyle()
    .setFontSize(10).setFontFamily('Georgia')
    .setForegroundColor(BRAND.BROWN).setBold(true);

  var iBox = s.insertTextBox(T.serviceIncludesContent, 40, 369, 640, 20);
  iBox.getText().setText(T.serviceIncludesContent);
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

  var t2 = s.insertTextBox(T.termsTitle, 40, 36, 400, 28);
  t2.getText().setText(T.termsTitle);
  t2.getText().getTextStyle()
    .setFontSize(20).setFontFamily('Georgia')
    .setForegroundColor(BRAND.OLIVE).setBold(true);

  var sub2 = s.insertTextBox(T.termsSubtitle, 40, 64, 400, 16);
  sub2.getText().setText(T.termsSubtitle);
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

  // 各條款：每條 title(h=14, +14) + body(h=40, +42) = 56pt；4條 = 224pt
  // 起點 84pt，簽名區起始 ≈ 308pt，最末元素底邊 ≈ 392pt，留 13pt margin（頁高 405pt）
  var ty = 84;
  termsData.forEach(function(sec) {
    var secTitle = s.insertTextBox(sec[0], 40, ty, 660, 14);
    secTitle.getText().setText(sec[0]);
    secTitle.getText().getTextStyle()
      .setFontSize(8).setFontFamily('Georgia')
      .setForegroundColor(BRAND.BROWN).setBold(true);
    ty += 14;

    var secBody = s.insertTextBox(sec[1], 50, ty, 650, 40);
    secBody.getText().setText(sec[1]);
    secBody.getText().getTextStyle()
      .setFontSize(7).setFontFamily('Georgia').setForegroundColor(BRAND.CHARCOAL);
    ty += 42;
  });

  // 簽名區
  ty += 6;
  var sigLine = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 40, ty, 660, 1.5);
  sigLine.getFill().setSolidFill(BRAND.BROWN);
  sigLine.getBorder().setTransparent();
  ty += 10;

  var sigT = s.insertTextBox(T.sigConfirmation, 40, ty, 300, 16);
  sigT.getText().setText(T.sigConfirmation);
  sigT.getText().getTextStyle()
    .setFontSize(10).setFontFamily('Georgia')
    .setForegroundColor(BRAND.OLIVE).setBold(true);
  ty += 20;

  var cL = s.insertTextBox(T.clientSignatureLabel, 40, ty, 280, 14);
  cL.getText().setText(T.clientSignatureLabel);
  cL.getText().getTextStyle()
    .setFontSize(8).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);
  var cLine = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 40, ty + 28, 280, 1);
  cLine.getFill().setSolidFill(BRAND.OLIVE);
  cLine.getBorder().setTransparent();
  var cD = s.insertTextBox(T.signDateField, 40, ty + 34, 280, 12);
  cD.getText().setText(T.signDateField);
  cD.getText().getTextStyle()
    .setFontSize(8).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);

  var mL = s.insertTextBox('MAPLAB Kitchen', 400, ty, 280, 14);
  mL.getText().setText('MAPLAB Kitchen');
  mL.getText().getTextStyle()
    .setFontSize(8).setFontFamily('Georgia').setForegroundColor(BRAND.MID_GRAY);
  var mLine = s.insertShape(SlidesApp.ShapeType.RECTANGLE, 400, ty + 28, 280, 1);
  mLine.getFill().setSolidFill(BRAND.OLIVE);
  mLine.getBorder().setTransparent();
  var mD = s.insertTextBox(T.signDateField, 400, ty + 34, 280, 12);
  mD.getText().setText(T.signDateField);
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

// ============================================================
// Wrapper: English version of generateProposalV2
// ============================================================
function generateProposalV2_EN() {
  SLIDE_LANG = 'en';
  T = SLIDE_TEXT[SLIDE_LANG];
  return generateProposalV2();
}
