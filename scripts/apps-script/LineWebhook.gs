/**
 * MAPLAB LINE Webhook → CONVERSATION_LOG
 * 部署目標 Sheet：1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
 *
 * ⚠️ 實際 TOKEN 請填入 Apps Script 的 Script Properties，不要 hardcode
 *   Project settings > Script properties:
 *     LINE_CHANNEL_SECRET = <your secret>
 *     LINE_ACCESS_TOKEN   = <your token>
 *
 * 架構說明：
 *   doPost → LockService + message.id 去重 → 直接寫入 Sheet
 *   不使用 trigger queue（根除多觸發競爭條件）
 */

const SHEET_ID  = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg';
const LOG_SHEET = 'CONVERSATION_LOG';

function getConfig_() {
  const props = PropertiesService.getScriptProperties();
  return {
    channelSecret: props.getProperty('LINE_CHANNEL_SECRET'),
    accessToken:   props.getProperty('LINE_ACCESS_TOKEN')
  };
}

function getLineProfile(userId) {
  if (!userId) return '';
  try {
    const token = getConfig_().accessToken;
    if (!token) {
      Logger.log('getLineProfile: LINE_ACCESS_TOKEN not set');
      return userId;
    }
    const res = UrlFetchApp.fetch('https://api.line.me/v2/bot/profile/' + userId, {
      headers: { 'Authorization': 'Bearer ' + token },
      muteHttpExceptions: true
    });
    if (res.getResponseCode() !== 200) {
      Logger.log('getLineProfile HTTP ' + res.getResponseCode());
      return userId;
    }
    return JSON.parse(res.getContentText()).displayName || userId;
  } catch(err) {
    Logger.log('getLineProfile error: ' + err);
    return userId;
  }
}

function doPost(e) {
  // 先立即回 200，LINE 不會 retry
  const okResponse = ContentService
    .createTextOutput(JSON.stringify({ status: 'ok' }))
    .setMimeType(ContentService.MimeType.JSON);

  if (!e || !e.postData) return okResponse;

  // Lock 防止同一則訊息同時被兩個執行緒寫入
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
  } catch(err) {
    Logger.log('Lock timeout: ' + err);
    return okResponse;
  }

  try {
    const body = JSON.parse(e.postData.contents);
    const events = (body.events || []).filter(
      ev => ev.type === 'message' && ev.message && ev.message.type === 'text'
    );
    if (events.length === 0) return okResponse;

    const props = PropertiesService.getScriptProperties();
    const PROCESSED_KEY = 'processed_line_msg_ids';
    let processedIds = {};
    try { processedIds = JSON.parse(props.getProperty(PROCESSED_KEY) || '{}'); } catch(err) {}

    const ss = SpreadsheetApp.openById(SHEET_ID);
    let sheet = ss.getSheetByName(LOG_SHEET);
    if (!sheet) {
      sheet = ss.insertSheet(LOG_SHEET);
      sheet.appendRow(['msg_id','case_id','timestamp','speaker','message','source','line_user_id','reply_to_msg_id']);
    }

    let updated = false;
    events.forEach(event => {
      const lineMessageId = event.message.id;

      // message.id 去重
      if (lineMessageId && processedIds[lineMessageId]) {
        Logger.log('Duplicate skipped: ' + lineMessageId);
        return;
      }
      if (lineMessageId) {
        processedIds[lineMessageId] = true;
        updated = true;
      }

      const userId = (event.source && event.source.userId) || '';
      const displayName = getLineProfile(userId);

      sheet.appendRow([
        Utilities.getUuid(),                      // A: msg_id
        '',                                       // B: case_id（業務填入）
        new Date(event.timestamp),                // C: timestamp
        displayName,                              // D: speaker（LINE 顯示名稱）
        event.message.text || '',                 // E: message
        'LINE',                                   // F: source
        userId,                                   // G: line_user_id
        (event.message.quotedMessageId) || ''     // H: reply_to_msg_id
      ]);
    });

    // 持久化已處理 ID（最多保留 2000 筆）
    if (updated) {
      const idList = Object.keys(processedIds);
      if (idList.length > 2000) {
        const trimmed = {};
        idList.slice(-1000).forEach(id => trimmed[id] = true);
        props.setProperty(PROCESSED_KEY, JSON.stringify(trimmed));
      } else {
        props.setProperty(PROCESSED_KEY, JSON.stringify(processedIds));
      }
    }
  } catch(err) {
    Logger.log('doPost error: ' + err);
  } finally {
    lock.releaseLock();
  }

  return okResponse;
}
