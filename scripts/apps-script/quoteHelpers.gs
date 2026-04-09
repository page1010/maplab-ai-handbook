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
 * ⚠️ Owner 2026-04-09：此處為暫用值，實際門市地址確認後請更新
 * 來源：LINE OA 自動回應提到「台南和緯店」
 */
var MAPLAB_ORIGIN_ADDRESS = '台南市北區和緯路二段';

/**
 * 車馬費規則（Owner 2026-04-09 定義）
 */
var TRANSPORT_FREE_THRESHOLD_MINUTES = 30;  // 導航時間 < 30 min → 免費
var TRANSPORT_FEE_PER_KM              = 6;  // ≥ 30 min → 每公里 NT$6

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
    var note = '';
    if (driveMin < TRANSPORT_FREE_THRESHOLD_MINUTES) {
      fee = 0;
      note = 'Maps 導航 ' + driveMin + ' 分 / ' + distanceKm + ' km，未達 30 分鐘免收';
    } else {
      fee = distanceKm * TRANSPORT_FEE_PER_KM;
      note = 'Maps 導航 ' + driveMin + ' 分 / ' + distanceKm + ' km × $' + TRANSPORT_FEE_PER_KM + ' = $' + fee;
    }

    return {
      fee: fee,
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
