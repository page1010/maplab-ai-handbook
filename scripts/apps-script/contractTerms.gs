/**
 * contractTerms.gs — MAPLAB 合約條款 v4.0 動態生成模組
 * 唯一真相來源：data/contract-terms-v4.md（2026-04-08 Owner 親口提供）
 *
 * 四個版本：
 *   to_c           - 個人版｜有訂金
 *   to_b_deposit   - 企業版｜有訂金
 *   to_b_full      - 企業版｜無訂金
 *   to_b_marketing - 行銷/公關公司版｜高變動專案型（4 條 → 6 條）
 *
 * 對外主要入口：
 *   resolveContractVersion(formData)                            → 'to_c' | 'to_b_*'
 *   getContractTermsV4(version, eventDate, depositAmount)        → 完整條款 + 匯款資訊 + 訂金說明
 *   isCorporateEventType(eventType)                              → boolean
 *   getBankInfoBlock(version)                                    → 匯款資訊字串（個人或公司帳戶）
 *   _getDepositClause_(version, depositAmount)                   → 訂金金額說明（內部）
 */

// ─────────────────────────────────────────
// 常數區：Owner 可調整預設值
// ─────────────────────────────────────────
var CONTRACT_CONFIG = {
  CONFIRM_DAYS: 14,                  // 活動日前＿日為最終人數確認日
  QUOTE_VALID_DAYS: 14,              // 本報價單自提供日起＿日內有效
  REVISION_LIMIT: 2,                 // 本報價內容提供＿次內調整（Owner 2026-04-08: 2 次）
  MARKETING_CHANGE_CUTOFF_DAYS: 14   // 行銷版：活動前＿日內之變更視為急件
};

var CORPORATE_EVENT_KEYWORDS = ['尾牙', '春酒', '企業', '公司', '記者會', '開幕', '酒會'];

// ─────────────────────────────────────────
// 決策輔助
// ─────────────────────────────────────────

/**
 * 判斷活動類型是否屬於企業類（含 7 個關鍵字之一）
 */
function isCorporateEventType(eventType) {
  if (!eventType) return false;
  var et = String(eventType);
  for (var i = 0; i < CORPORATE_EVENT_KEYWORDS.length; i++) {
    if (et.indexOf(CORPORATE_EVENT_KEYWORDS[i]) >= 0) return true;
  }
  return false;
}

/**
 * 解析 formData 決定合約版本
 * 決策樹（Owner 2026-04-08：預設有訂金，不收訂金才是例外）：
 *   if (isCorporate) {
 *     if (isMarketingAgency)  → to_b_marketing   // 行銷公關優先
 *     else if (noDeposit)     → to_b_full        // 例外：勾「不收訂金」
 *     else                    → to_b_deposit     // 預設：有訂金
 *   } else {
 *     → to_c                                     // 個人一律有訂金
 *   }
 * isCorporate = (公司名有填) OR (活動類型含企業關鍵字)
 *
 * formData 相容舊欄位：
 *   - noDeposit  (新、主要)
 *   - hasDeposit (舊，true=有訂金，false=無訂金)
 */
function resolveContractVersion(formData) {
  var hasCompany = formData.company && String(formData.company).trim().length > 0;
  var isCorpEvent = isCorporateEventType(formData.eventType);
  var isCorporate = hasCompany || isCorpEvent;

  if (!isCorporate) return 'to_c';

  var isMarketing = _asBool_(formData.isMarketingAgency);
  if (isMarketing) return 'to_b_marketing';

  // 不收訂金判定（優先用新欄位 noDeposit，舊欄位 hasDeposit=false 等價）
  var noDeposit;
  if (formData.noDeposit !== undefined) {
    noDeposit = _asBool_(formData.noDeposit);
  } else if (formData.hasDeposit !== undefined) {
    noDeposit = !_asBool_(formData.hasDeposit);
  } else {
    noDeposit = false; // 預設：收訂金
  }

  if (noDeposit) return 'to_b_full';    // 例外
  return 'to_b_deposit';                // 預設
}

/**
 * 把各種 truthy 值都視為 true：true / 'true' / 'on' / 'yes' / '1'
 */
function _asBool_(v) {
  if (v === true) return true;
  if (v === false || v == null) return false;
  var s = String(v).toLowerCase();
  return s === 'true' || s === 'on' || s === 'yes' || s === '1';
}

// ─────────────────────────────────────────
// 匯款資訊（依 version 切換個人/公司帳戶）
// ─────────────────────────────────────────
function getBankInfoBlock(version) {
  if (version === 'to_c') {
    return [
      '▶匯款資訊',
      '中國信託 822 / 西台南分行',
      '戶名：[收款資訊另提供]'  // 請由 Owner 設定於 GAS PropertiesService，不寫死於 public repo,
      '帳號：[收款資訊另提供]'  // 請由 Owner 設定於 GAS PropertiesService，不寫死於 public repo,
      '匯款後，請提供後五碼對帳。'
    ].join('\n');
  }
  // to_b_deposit / to_b_full / to_b_marketing 全部用公司帳戶
  return [
    '▶匯款資訊',
    '中國信託 822 / 西台南分行',
    '戶名：圖蕾實業社',
    '帳號：222540645172',
    '匯款後，請提供後五碼對帳。'
  ].join('\n');
}

// ─────────────────────────────────────────
// 共用條款段落（第二、三、四條的共通文字）
// ─────────────────────────────────────────

/**
 * 現場服務（to_c 第二條 / to_b_deposit 第二條 / to_b_full 第二條 / to_b_marketing 第四條）
 */
function _article_siteService_(articleLabel) {
  var lines = [];
  lines.push(articleLabel + '｜現場服務');
  lines.push('若活動指定地點距離門市超過30分鐘車程，需額外收取車馬費，具體費用依公里數報價。');
  lines.push('餐點放置地點若位於2樓無電梯，本公司將收取 $800 人員搬運費，3樓以上無電梯則需由客戶自行搬運。');
  lines.push('若當日電梯臨時無法使用，則現場加收 $800 為樓層搬運費（現金支付）。');
  lines.push('因前置作業較費時、器具易碎又繁多，送達地點臨近50公尺內必需要有停車位、或無違規被開單風險的停車空間（可接受收費或卸貨車位），並可臨停1小時，也避免找不到車位耽誤活動開始時間。');
  lines.push('本公司之服務限於餐點擺設，不協助佈置私人道具' + (articleLabel === '第四條' ? '，亦不負責其他廠商之整合或場控責任' : '') + '。');
  lines.push('若因場地尚未開放、前場活動未結束或其他非本公司因素，導致無法依約定時間進場，超過約定時間每30分鐘酌收 $500 等待費（未滿30分鐘以30分鐘計）。');
  lines.push('本公司將依雙方約定之時間進行撤場與整理，若因客戶方或現場因素導致延誤撤場，超過約定時間每30分鐘酌收 $500 等待費（未滿30分鐘以30分鐘計）。');
  lines.push('本公司服務不包含垃圾清運與場地清潔，如需相關服務須另行報價。');
  lines.push('');
  lines.push('佈置器材責任：');
  lines.push('本公司提供之佈置器材（如桌巾、盤器、裝飾品等）限於活動期間使用，活動結束後須完整歸還。');
  lines.push('本公司撤場時將清點設備，如有遺失、損壞或人為因素導致無法使用，客戶須依原價或修繕費用賠償，會於24小時內確認賠償事宜。');
  return lines.join('\n');
}

/**
 * 產品責任與保證（to_c 第三條 / to_b_* 第三條 / to_b_marketing 第五條）
 */
function _article_productResponsibility_(articleLabel) {
  var lines = [];
  lines.push(articleLabel + '｜產品責任與保證');
  lines.push('本公司產品每年皆有投保『國泰產物產品責任險』。');
  lines.push('餐點需於 2-3 小時內食用完畢，以確保食品安全。');
  lines.push('本公司提供符合衛生標準之餐點，餐點於完成擺設並交付後，相關保管責任即由客戶承擔。');
  lines.push('交付客戶後如因天候或保存不當導致品質變化，恕不負責。');
  lines.push('如有外帶打包，不宜於室溫下久置，打包風險歸屬於客戶，恕不負責。');
  return lines.join('\n');
}

/**
 * 合約效力（有訂金版本用：to_c 第四條 / to_b_deposit 第四條）
 */
function _article_contractValidity_withDeposit_(articleLabel) {
  var lines = [];
  lines.push(articleLabel + '｜合約效力');
  lines.push('本合約自雙方確認內容無誤，支付訂金款項後即視為同意本條款，並具法律效力，活動結束且物品檢查無誤後自動失效。');
  lines.push('本公司會於活動當日於場地內拍攝紀錄照片，作為品牌與行銷使用，若不同意須事先通知。');
  lines.push('任何合約爭議，雙方應以誠信協商解決，若無法達成共識，則由本公司所在地法院管轄。');
  return lines.join('\n');
}

/**
 * 合約效力（無訂金版本用：to_b_full 第四條 / to_b_marketing 第六條）
 */
function _article_contractValidity_noDeposit_(articleLabel) {
  var lines = [];
  lines.push(articleLabel + '｜合約效力');
  lines.push('本合約自雙方確認內容無誤後即視為同意本條款，並具法律效力，活動結束且物品檢查無誤後自動失效。');
  lines.push('本公司會於活動當日於場地內拍攝紀錄照片，作為品牌與行銷使用，若不同意須事先通知。');
  lines.push('任何合約爭議，雙方應以誠信協商解決，若無法達成共識，則由本公司所在地法院管轄。');
  return lines.join('\n');
}

// ─────────────────────────────────────────
// 第一條生成器（四版各自不同）
// ─────────────────────────────────────────

function _article1_toC_() {
  var c = CONTRACT_CONFIG;
  var lines = [];
  lines.push('第一條｜訂單與付款');
  lines.push('訂金繳付後，若客戶自行取消服務，訂金不予退還。');
  lines.push('客戶須支付尾款於活動日前完成匯款，或於活動當日擺設完畢後以現金或匯款方式支付尾款。');
  lines.push('若因不可抗力因素（如天災、重大疫情、本人或直系親屬重大傷病，需附醫療或官方證明），請於活動前7日內主動提出證明，可申請延期或轉讓一次（限6個月內使用）。');
  lines.push('活動當日取消或更動者，須支付總金額80%作為食材與人力成本賠償，恕不退還任何已付金額。');
  lines.push('活動日前 ' + c.CONFIRM_DAYS + ' 日為最終人數與餐點確認日，其後之增減，本公司將依實際狀況評估是否調整，並保留加收費用或無法調整之權利。');
  lines.push('本報價單自提供日起 ' + c.QUOTE_VALID_DAYS + ' 日內有效，逾期將依當時食材成本與檔期重新報價。');
  lines.push('本報價內容提供 ' + c.REVISION_LIMIT + ' 次內調整（包含餐點、份量、擺設形式等），超過次數之修改，將酌收專案調整費或重新報價。');
  lines.push('若報價經多次調整後仍未確認，或超過報價有效期限未完成訂單確認，本公司得暫停後續調整與保留檔期之義務。');
  lines.push('付款方式以現金或匯款為主，匯款金額須為實收金額，不得扣除手續費後轉帳。');
  lines.push('因本公司為小型團隊營運，帳務流程以簡化為主，付款方式以現金或匯款為主，暫不提供支票付款方式，敬請見諒。');
  return lines.join('\n');
}

function _article1_toBDeposit_() {
  var c = CONTRACT_CONFIG;
  var lines = [];
  lines.push('第一條｜訂單與付款');
  lines.push('訂金繳付後，若客戶自行取消服務，訂金不予退還。');
  lines.push('尾款須依雙方約定之「最晚入帳日期」完成付款。');
  lines.push('若付款方式為匯款，客戶應於活動前主動告知預計入帳日期，以利雙方確認帳務流程。');
  lines.push('若因不可抗力因素（如天災、重大疫情、本人或直系親屬重大傷病，需附醫療或官方證明），請於活動前7日內主動提出證明，可申請延期或轉讓一次（限6個月內使用）。');
  lines.push('活動當日取消或更動者，須支付總金額80%作為食材與人力成本賠償，恕不退還任何已付金額。');
  lines.push('活動日前 ' + c.CONFIRM_DAYS + ' 日為最終人數與餐點確認日，其後之增減，本公司將依實際狀況評估是否調整，並保留加收費用或無法調整之權利。');
  lines.push('本報價單自提供日起 ' + c.QUOTE_VALID_DAYS + ' 日內有效，逾期將依當時食材成本與檔期重新報價。');
  lines.push('本報價內容提供 ' + c.REVISION_LIMIT + ' 次內調整（包含餐點、份量、擺設形式等），超過次數之修改，將酌收專案調整費或重新報價。');
  lines.push('若報價經多次調整後仍未確認，或超過報價有效期限未完成訂單確認，本公司得暫停後續調整與保留檔期之義務。');
  lines.push('付款方式以現金或匯款為主，匯款金額須為實收金額，不得扣除手續費後轉帳。');
  lines.push('因本公司為小型團隊營運，帳務流程以簡化為主，付款方式以現金或匯款為主，暫不提供支票付款方式，敬請見諒。');
  return lines.join('\n');
}

function _article1_toBFull_() {
  var c = CONTRACT_CONFIG;
  var lines = [];
  lines.push('第一條｜訂單與付款');
  lines.push('本訂單採一次性付款制，不收取訂金。');
  lines.push('客戶須於雙方約定之「最晚入帳日期」前完成付款，或於活動當日擺設完畢後完成付款。');
  lines.push('若付款方式為匯款，客戶應於活動前主動告知預計入帳日期，以利雙方確認帳務流程。');
  lines.push('若因不可抗力因素（如天災、重大疫情、本人或直系親屬重大傷病，需附醫療或官方證明），請於活動前7日內主動提出證明，可申請延期或轉讓一次（限6個月內使用）。');
  lines.push('活動當日取消或更動者，須支付總金額80%作為食材與人力成本費用。');
  lines.push('活動日前 ' + c.CONFIRM_DAYS + ' 日為最終人數與餐點確認日，其後之增減，本公司將依實際狀況評估是否調整，並保留加收費用或無法調整之權利。');
  lines.push('本報價單自提供日起 ' + c.QUOTE_VALID_DAYS + ' 日內有效，逾期將依當時食材成本與檔期重新報價。');
  lines.push('本報價內容提供 ' + c.REVISION_LIMIT + ' 次內調整（包含餐點、份量、擺設形式等），超過次數之修改，將酌收專案調整費或重新報價。');
  lines.push('若報價經多次調整後仍未確認，或超過報價有效期限未完成訂單確認，本公司得暫停後續調整與保留檔期之義務。');
  lines.push('付款方式以現金或匯款為主，匯款金額須為實收金額，不得扣除手續費後轉帳。');
  lines.push('若無法以現金支付，需事先告知並改以匯款完成付款。');
  lines.push('因本公司為小型團隊營運，帳務流程以簡化為主，付款方式以現金或匯款為主，暫不提供支票付款方式，敬請見諒。');
  return lines.join('\n');
}

function _article1_toBMarketing_() {
  var c = CONTRACT_CONFIG;
  var lines = [];
  lines.push('第一條｜訂單與付款');
  lines.push('本訂單採一次性付款制或依雙方約定方式執行。');
  lines.push('客戶須於雙方約定之「最晚入帳日期」完成付款。');
  lines.push('若付款方式為匯款，客戶應於活動前主動告知預計入帳日期，以利雙方確認帳務流程。');
  lines.push('若因不可抗力因素（如天災、重大疫情、本人或直系親屬重大傷病，需附醫療或官方證明），請於活動前7日內主動提出證明，可申請延期或轉讓一次（限6個月內使用）。');
  lines.push('活動當日取消或更動者，須支付總金額80%作為食材與人力成本費用。');
  lines.push('活動日前 ' + c.CONFIRM_DAYS + ' 日為最終人數與餐點確認日，其後之增減或調整，將視為追加需求處理。');
  lines.push('本報價單自提供日起 ' + c.QUOTE_VALID_DAYS + ' 日內有效，逾期將依當時食材成本、檔期與專案需求重新報價。');
  lines.push('本報價內容提供 ' + c.REVISION_LIMIT + ' 次內調整（包含餐點、份量、擺設形式、進場時間、動線安排等），超過次數之修改，將酌收專案調整費或重新報價。');
  lines.push('若報價經多次調整後仍未確認，或超過報價有效期限未完成訂單確認，本公司得暫停後續調整與保留檔期之義務。');
  lines.push('付款方式以現金或匯款為主，匯款金額須為實收金額，不得扣除手續費後轉帳。');
  lines.push('因本公司為小型團隊營運，帳務流程以簡化為主，付款方式以現金或匯款為主，暫不提供支票付款方式，敬請見諒。');
  return lines.join('\n');
}

// ─────────────────────────────────────────
// 行銷版專屬第二、三條
// ─────────────────────────────────────────

function _article2_marketing_projectComm_() {
  var c = CONTRACT_CONFIG;
  var lines = [];
  lines.push('第二條｜專案溝通與變更管理');
  lines.push('本專案以單一窗口為主要聯繫對象，若窗口更動或多方指示導致資訊重複確認，本公司得依實際溝通成本酌收專案管理費。');
  lines.push('報價確認後之內容（包含餐點、擺設形式、進場時間、動線安排等）若有調整，視為專案變更，將依變更內容另行報價。');
  lines.push('活動前 ' + c.MARKETING_CHANGE_CUTOFF_DAYS + ' 日內之變更，將視實際狀況收取急件處理費或無法調整。');
  lines.push('溝通次數與修改次數超出一般合理範圍時，本公司得視專案複雜度酌收額外專案服務費。');
  return lines.join('\n');
}

function _article3_marketing_onsiteAddon_() {
  var lines = [];
  lines.push('第三條｜現場執行與追加需求');
  lines.push('本公司依雙方確認內容進行現場執行，未列於報價內之需求，視為現場追加。');
  lines.push('活動當日如有臨時增加餐點、調整擺設形式或新增服務需求，將依現場人力與物料狀況評估可行性，並另行報價。');
  lines.push('若因客戶或現場單位臨時要求調整動線、位置或服務內容，導致作業時間增加或人力負擔提高，將酌收現場調整費。');
  return lines.join('\n');
}

// ─────────────────────────────────────────
// 四個完整版本的組裝器
// ─────────────────────────────────────────

function _buildToC_() {
  return [
    '『簽約使用條款及細則』',
    '',
    _article1_toC_(),
    '',
    _article_siteService_('第二條'),
    '',
    _article_productResponsibility_('第三條'),
    '',
    _article_contractValidity_withDeposit_('第四條')
  ].join('\n');
}

function _buildToBDeposit_() {
  return [
    '『簽約使用條款及細則』',
    '',
    _article1_toBDeposit_(),
    '',
    _article_siteService_('第二條'),
    '',
    _article_productResponsibility_('第三條'),
    '',
    _article_contractValidity_withDeposit_('第四條')
  ].join('\n');
}

function _buildToBFull_() {
  return [
    '『簽約使用條款及細則』',
    '',
    _article1_toBFull_(),
    '',
    _article_siteService_('第二條'),
    '',
    _article_productResponsibility_('第三條'),
    '',
    _article_contractValidity_noDeposit_('第四條')
  ].join('\n');
}

function _buildToBMarketing_() {
  return [
    '『簽約使用條款及細則』',
    '',
    _article1_toBMarketing_(),
    '',
    _article2_marketing_projectComm_(),
    '',
    _article3_marketing_onsiteAddon_(),
    '',
    _article_siteService_('第四條'),
    '',
    _article_productResponsibility_('第五條'),
    '',
    _article_contractValidity_noDeposit_('第六條')
  ].join('\n');
}

// ─────────────────────────────────────────
// 主入口
// ─────────────────────────────────────────

/**
 * 完整條款輸出（匯款資訊 + 分隔線 + 四版條款之一 + 訂金金額說明）
 * @param {string} version - 'to_c' | 'to_b_deposit' | 'to_b_full' | 'to_b_marketing'
 * @param {Date}   eventDate - 活動日期（保留給未來動態帶入日期用）
 * @param {number} depositAmount - 訂金金額（個人 baseline 3000，業務可調）
 * @returns {string} 完整條款文字
 */
function getContractTermsV4(version, eventDate, depositAmount) {
  var termsText;
  switch (version) {
    case 'to_c':           termsText = _buildToC_();           break;
    case 'to_b_deposit':   termsText = _buildToBDeposit_();    break;
    case 'to_b_full':      termsText = _buildToBFull_();       break;
    case 'to_b_marketing': termsText = _buildToBMarketing_();  break;
    default:
      Logger.log('[contractTerms] 未知 version=' + version + '，fallback to_c');
      termsText = _buildToC_();
  }
  var bankInfo = getBankInfoBlock(version);
  var depositClause = _getDepositClause_(version, depositAmount);
  var separator = '\n\n───────────────────────────\n\n';
  return bankInfo + '\n\n' + depositClause + separator + termsText;
}

/**
 * 依合約版本產生訂金金額說明（2026-04-09 Owner 決策：個人 baseline 3000，業務可調）
 */
function _getDepositClause_(version, depositAmount) {
  var amt = Number(depositAmount) || 3000;
  var amtStr = 'NT$' + amt.toLocaleString();
  if (version === 'to_b_full') {
    return '▶付款安排（一次性後付）：本案採活動結束後一次請款制，不收取訂金。';
  }
  if (version === 'to_b_marketing') {
    return '▶付款安排（行銷/公關專案）：本案訂金 ' + amtStr + '，尾款依請款流程與專案約定日期匯款完成。';
  }
  if (version === 'to_b_deposit') {
    return '▶付款安排（企業版）：本案訂金 ' + amtStr + '，尾款依雙方約定之最晚入帳日期完成付款。';
  }
  // to_c
  return '▶付款安排：本案訂金 ' + amtStr + '（業務依案件規模評估），尾款請於活動日前完成匯款，或於活動當日擺設完畢後以現金或匯款方式支付。';
}

/**
 * 給 Apps Script 編輯器裡手動測試用
 * 執行後會在 Logger 輸出四版本各自前 500 字
 */
function _testContractTermsV4_() {
  var versions = ['to_c', 'to_b_deposit', 'to_b_full', 'to_b_marketing'];
  var today = new Date();
  for (var i = 0; i < versions.length; i++) {
    var text = getContractTermsV4(versions[i], today, 3000);
    Logger.log('=== ' + versions[i] + ' (' + text.length + ' chars) ===');
    Logger.log(text.slice(0, 500));
  }
}
