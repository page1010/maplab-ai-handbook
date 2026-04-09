/**
 * quoteHelpers.gs — MAPLAB 報價系統 可重用計算工具
 * 2026-04-09 新建 (Owner 決策 S6 + S9)
 *
 * 這個模組收集「可程式化的跨案件工具」（企業價值第二層 / docs/company-values.md）
 * — 業務判斷不進這裡，這裡只放「input X 一定產出 output Y」的確定性公式。
 *
 * 對外 API：
 *   calcTransportFee(destinationAddress)  → { fee: Number, distanceKm, driveMin, method, note }
 *   calcFloorFee(mode)                    → Number  (0 / 500 / 1000)
 *   MAPLAB_ORIGIN_ADDRESS                 → String (門市地址常數，Owner 可調)
 */

// ─────────────────────────────────────────
// 常數（Owner 可調）
// ─────────────────────────────────────────

/**
 * MAPLAB 門市起點地址（Google Maps 導航基準點）
 * 2026-04-09 Owner 確認：台南市北區和緯路2段450號
 */
var MAPLAB_ORIGIN_ADDRESS = '台南市北區和緯路2段450號';

/**
 * 車馬費規則（Owner 2026-04-09 兩次調整後定版）
 * 三要素：
 *   (a) 30 分鐘內免費
 *   (b) 30 分鐘以上取「每公里 $6」與「每分鐘 $50」兩者的較高值
 *       （Owner 指示：用高的算好了 讓業務談）
 *   (c) 驗證樣本：嘉義案 60 min 65 km → max(390, 3000) = $3000 ✓ 跟歷史 sample 對齊
 */
var TRANSPORT_FREE_THRESHOLD_MINUTES = 30;  // 導航時間 < 30 min → 免費
var TRANSPORT_FEE_PER_KM              = 6;  // 每公里 NT$6
var TRANSPORT_FEE_PER_MIN             = 50; // 每分鐘 NT$50

/**
 * 搬運費規則（2F 無電梯，SOP 確認 + sample 驗證）
 */
var FLOOR_FEE_WITH_HELP = 500;   // 有人協助：$500
var FLOOR_FEE_NO_HELP   = 1000;  // 無人協助：$1000

// ─────────────────────────────────────────
// 車馬費：calcTransportFee
// ─────────────────────────────────────────

/**
 * 依 Google Maps 導航距離與時間計算車馬費
 * 公式（Owner 2026-04-09）：
 *   driveMin < 30 min       → 車馬費 = 0
 *   driveMin >= 30 min      → 車馬費 = ceil(distanceKm) × NT$6
 *
 * @param {string} destinationAddress 活動地點地址
 * @returns {Object} { fee, distanceKm, driveMin, method, note }
 *   - fee: 計算出的車馬費（NT$）
 *   - distanceKm: 單程公里數（取整）
 *   - driveMin: 導航預估分鐘數
 *   - method: 'maps_auto' | 'no_address' | 'maps_error'
 *   - note: 說明字串（寫進備註方便業務檢視）
 */
function calcTransportFee(destinationAddress) {
  if (!destinationAddress || String(destinationAddress).trim().length < 4) {
    return {
      fee: 0, distanceKm: 0, driveMin: 0,
      method: 'no_address',
      note: '地址未填 / 太短，車馬費預設 0，業務可手動修正'
    };
  }

  try {
    var directions = Maps.newDirectionFinder()
      .setOrigin(MAPLAB_ORIGIN_ADDRESS)
      .setDestination(destinationAddress)
      .setMode(Maps.DirectionFinder.Mode.DRIVING)
      .getDirections();

    if (!directions || !directions.routes || directions.routes.length === 0) {
      return {
        fee: 0, distanceKm: 0, driveMin: 0,
        method: 'maps_error',
        note: 'Google Maps 找不到路線，車馬費預設 0'
      };
    }

    var leg = directions.routes[0].legs[0];
    var distanceMeters = leg.distance.value;       // 公尺
    var durationSec    = leg.duration.value;       // 秒
    var distanceKm     = Math.ceil(distanceMeters / 1000);
    var driveMin       = Math.round(durationSec / 60);

    var fee = 0;
    var feeByKm = 0;
    var feeByMin = 0;
    var note = '';
    if (driveMin < TRANSPORT_FREE_THRESHOLD_MINUTES) {
      fee = 0;
      note = 'Maps 導航 ' + driveMin + ' 分 / ' + distanceKm + ' km，未達 30 分鐘免收';
    } else {
      feeByKm  = distanceKm * TRANSPORT_FEE_PER_KM;   // 公里制
      feeByMin = driveMin   * TRANSPORT_FEE_PER_MIN;  // 分鐘制
      fee = Math.max(feeByKm, feeByMin);               // Owner：用高的算好了 讓業務談
      note = 'Maps 導航 ' + driveMin + ' 分 / ' + distanceKm + ' km | ' +
             'km 制 $' + feeByKm + ' vs min 制 $' + feeByMin + ' → 取高 $' + fee;
    }

    return {
      fee: fee,
      feeByKm: feeByKm,
      feeByMin: feeByMin,
      distanceKm: distanceKm,
      driveMin: driveMin,
      method: 'maps_auto',
      note: note
    };
  } catch (e) {
    Logger.log('[calcTransportFee] error: ' + e.message);
    return {
      fee: 0, distanceKm: 0, driveMin: 0,
      method: 'maps_error',
      note: 'Maps service 錯誤: ' + e.message + '，車馬費預設 0'
    };
  }
}

// ─────────────────────────────────────────
// 搬運費：calcFloorFee
// ─────────────────────────────────────────

/**
 * 2F 無電梯搬運費計算
 * Owner 2026-04-09 + 真實 sample 驗證（陳瀅如 2F + 1000）:
 *   mode = 'none'         → 0（電梯可用 / 一樓 / 戶外平面）
 *   mode = 'with_help'    → 500（客戶提供人力協助）
 *   mode = 'no_help'      → 1000（MAPLAB 獨力搬運）
 *
 * @param {string} mode  'none' | 'with_help' | 'no_help'
 * @returns {Number}
 */
function calcFloorFee(mode) {
  switch (String(mode || '').toLowerCase()) {
    case 'with_help': return FLOOR_FEE_WITH_HELP;
    case 'no_help':   return FLOOR_FEE_NO_HELP;
    case 'none':
    case '':
    default:          return 0;
  }
}

// ─────────────────────────────────────────
// 手動測試函式（Apps Script 編輯器執行）
// ─────────────────────────────────────────

function _testCalcTransportFee_() {
  var tests = [
    '台南市東區大學路',                  // 市內近
    '台南市安南區安佃七街176號',          // 市內遠
    '嘉義市西區新榮路',                   // 外縣市
    '高雄市左營區',                        // 外縣市
    '',                                     // 空地址
  ];
  for (var i = 0; i < tests.length; i++) {
    var r = calcTransportFee(tests[i]);
    Logger.log((tests[i] || '[empty]') + ' → ' + JSON.stringify(r));
  }
}

function _testCalcFloorFee_() {
  Logger.log('none      → ' + calcFloorFee('none'));       // 0
  Logger.log('with_help → ' + calcFloorFee('with_help'));  // 500
  Logger.log('no_help   → ' + calcFloorFee('no_help'));    // 1000
  Logger.log('(empty)   → ' + calcFloorFee(''));           // 0
}

// ─────────────────────────────────────────
// 情境測試函式（Apps Script 編輯器直接跑）
// ─────────────────────────────────────────

/**
 * 情境 A 測試：個人週歲 20 人 K 輕食 A
 * 在 Apps Script 編輯器選這個函式 → 點 Run
 * 會產出一份真正的報價單 copy 到 Drive，回傳 URL
 */
function test_scenarioA_週歲20人() {
  var result = createQuote({
    customer: '測試_李晴宜',
    date: '2026-05-15',
    time: '11:00',
    address: '台南市安南區安和路三段190巷71弄17號',
    eventType: '生日派對',
    headcount: '20',
    eventName: '抓周派對測試',
    totalItems: '',
    depositAmount: '3000',
    dietaryNotes: '不要羊 部分長輩不吃牛 串燒可以',
    floorFeeMode: 'none',
    noDeposit: false,
    isMarketingAgency: false
  });
  Logger.log('scenarioA result: ' + JSON.stringify(result));
  return result;
}

/**
 * 情境 B 測試：個人入厝 30 人 K 主食 B
 */
function test_scenarioB_入厝30人() {
  var result = createQuote({
    customer: '測試_洪炳輝',
    date: '2026-06-20',
    time: '17:30',
    address: '台南市安南區安興街351巷60號',
    eventType: '外燴到府',
    headcount: '30',
    eventName: '新居入厝測試',
    totalItems: '',
    depositAmount: '3000',
    dietaryNotes: '',
    floorFeeMode: 'none',
    noDeposit: false,
    isMarketingAgency: false
  });
  Logger.log('scenarioB result: ' + JSON.stringify(result));
  return result;
}

/**
 * 情境 C 測試：企業開幕 30 人 K
 */
function test_scenarioC_企業開幕() {
  var result = createQuote({
    customer: '測試_Gina浥慧',
    company: '測試開幕公司',
    date: '2026-07-10',
    time: '10:00',
    address: '台南市安平區慶平路440號',
    eventType: '企業聚會',
    headcount: '30',
    eventName: '開幕茶會測試',
    totalItems: '',
    depositAmount: '5000',
    dietaryNotes: '',
    floorFeeMode: 'none',
    noDeposit: false,
    isMarketingAgency: false
  });
  Logger.log('scenarioC result: ' + JSON.stringify(result));
  return result;
}
