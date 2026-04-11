/**
 * QUOTE_DRAFT 模板一次性設定 — T-A5-003
 * 執行完後可刪除此檔案
 *
 * 修改項目：
 * 1. E2/E4 統計欄位清空（移到列印範圍外 K 欄）
 * 2. K 欄加入業務內部欄位標籤
 * 3. I 欄加入業務備註欄
 * 4. D21 加入熟客招待顯示/隱藏下拉
 * 5. E28 長桌改為大張/小張下拉
 * 6. J28 外包標記下拉
 */

function setupQuoteDraftTemplate() {
  var ss = SpreadsheetApp.openById('1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg');
  var sheet = ss.getSheetByName('QUOTE_DRAFT');
  if (!sheet) {
    throw new Error('找不到 QUOTE_DRAFT');
  }

  // ═══════════════════════════════════════
  // 1. 列印範圍外的業務內部資訊區（K欄）
  // ═══════════════════════════════════════

  // K 欄標題
  sheet.getRange('K1').setValue('【內部資訊 — 列印範圍外】');
  sheet.getRange('K1').setFontWeight('bold').setFontColor('#999999');

  // 系統欄位標籤
  sheet.getRange('K2').setValue('Case ID');
  sheet.getRange('K3').setValue('建立時間');
  sheet.getRange('K4').setValue('報價狀態');
  sheet.getRange('K5').setValue('成交金額');
  sheet.getRange('K6').setValue('匯款狀態');
  sheet.getRange('K7').setValue('最後修改');
  sheet.getRange('K8').setValue('版本');

  // 設定 K 欄字色為灰色
  sheet.getRange('K2:K8').setFontColor('#999999');

  // L 欄放對應的值（預設）
  sheet.getRange('L4').setValue('尚未報價');
  sheet.getRange('L6').setValue('未匯');
  sheet.getRange('L8').setValue('v0');

  // ═══════════════════════════════════════
  // 2. E2/E4 統計欄位處理
  // ═══════════════════════════════════════
  //
  // 注意：E4 目前是電話（0910-589263），E2 可能有統計資料
  // Owner 說 E2 和 E4 是統計欄位，不要在列印範圍內
  // 但電話需要保留在某處給客人看
  //
  // 方案：把 E2 的統計資料移到 K 欄，E2 保持空或放客戶可見資訊
  // E4 電話保留（客人需要看到聯絡方式），但確認列印範圍
  //
  // 先把 E2 值移到 K10（如果有值的話）
  var e2Val = sheet.getRange('E2').getValue();
  if (e2Val && e2Val !== '') {
    sheet.getRange('K10').setValue('原E2統計: ' + e2Val);
  }

  // ═══════════════════════════════════════
  // 3. I 欄：業務備註
  // ═══════════════════════════════════════
  sheet.getRange('I1').setValue('業務備註');
  sheet.getRange('I1').setFontWeight('bold').setFontColor('#999999');
  // I6 起可以讓業務對每個品項寫備註
  sheet.getRange('I6').setValue('備註');
  sheet.getRange('I6').setFontWeight('bold').setFontColor('#999999');

  // ═══════════════════════════════════════
  // 4. 熟客招待 — D21 加下拉控制
  // ═══════════════════════════════════════
  var complimentControl = sheet.getRange('D21');
  var rule1 = SpreadsheetApp.newDataValidation()
    .requireValueInList(['顯示', '隱藏'], true)
    .setAllowInvalid(false)
    .build();
  complimentControl.setDataValidation(rule1);
  complimentControl.setValue('顯示');
  complimentControl.setNote('選「隱藏」則產出報價單時不含熟客招待區');

  // ═══════════════════════════════════════
  // 5. E28 長桌 — 改為大張/小張下拉
  // ═══════════════════════════════════════
  // 目前 D28="租借長桌", E28=0
  // 改為：D28="長桌規格", E28=下拉(無/大張$350/小張$100)
  sheet.getRange('D28').setValue('長桌規格');

  var tableRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(['無', '大張($350/張)', '小張($100/張)'], true)
    .setAllowInvalid(false)
    .build();
  sheet.getRange('E28').setDataValidation(tableRule);
  sheet.getRange('E28').setValue('無');

  // F28 = 長桌數量
  sheet.getRange('F28').setValue(0);
  sheet.getRange('F28').setNote('長桌數量');

  // ═══════════════════════════════════════
  // 6. J28 外包標記（僅大張可選）
  // ═══════════════════════════════════════
  sheet.getRange('J28').setValue('自有');
  var outsourceRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(['自有', '外包租借'], true)
    .setAllowInvalid(false)
    .build();
  sheet.getRange('J28').setDataValidation(outsourceRule);
  sheet.getRange('J28').setFontColor('#999999');
  sheet.getRange('J28').setNote('外包租借僅適用大張長桌');

  // J 欄標題
  sheet.getRange('J1').setValue('外包/標記');
  sheet.getRange('J1').setFontWeight('bold').setFontColor('#999999');

  // ═══════════════════════════════════════
  // 7. Row 36+ 預留條款區
  // ═══════════════════════════════════════
  sheet.getRange('B36').setValue('【合約條款】');
  sheet.getRange('B36').setFontWeight('bold');
  sheet.getRange('B37').setValue('（條款將由系統自動帶入）');
  sheet.getRange('B37').setFontColor('#999999');

  // ═══════════════════════════════════════
  // Done
  // ═══════════════════════════════════════
  Logger.log('QUOTE_DRAFT 模板設定完成：K欄系統資訊 / I欄備註 / D21熟客下拉 / E28長桌下拉 / J28外包標記 / B36條款預留');
}
