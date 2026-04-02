/**
 * MAPLAB LINE Webhook → CONVERSATION_LOG
 * 部署目標 Sheet：1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
 *
 * ⚠️ 實際 TOKEN 請填入 Apps Script 的 Script Properties，不要 hardcode
 *   File > Project properties > Script properties:
 *     LINE_CHANNEL_SECRET = <your secret>
 *     LINE_ACCESS_TOKEN   = <your token>
 */

const SHEET_ID  = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg';
const LOG_SHEET = 'CONVERSATION_LOG';

function getConfig_() {
  const props = PropertiesService.getScriptProperties();
  return {
    channelSecret:  props.getProperty('LINE_CHANNEL_SECRET'),
    accessToken:    props.getProperty('LINE_ACCESS_TOKEN')
  };
}

function getLineProfile(userId) {
  if (!userId) return '';
  try {
    const token = getConfig_().accessToken;
    if (!token) {
      Logger.log('getLineProfile: LINE_ACCESS_TOKEN not set in Script Properties');
      return userId;
    }
    const res = UrlFetchApp.fetch('https://api.line.me/v2/bot/profile/' + userId, {
      headers: { 'Authorization': 'Bearer ' + token },
      muteHttpExceptions: true
    });
    const code = res.getResponseCode();
    if (code !== 200) {
      Logger.log('getLineProfile HTTP ' + code + ': ' + res.getContentText());
      return userId;
    }
    return JSON.parse(res.getContentText()).displayName || userId;
  } catch(err) {
    Logger.log('getLineProfile error: ' + err);
    return userId;
  }
}

function doPost(e) {
  if (!e || !e.postData) return ContentService.createTextOutput('no data');
  try {
    const props = PropertiesService.getScriptProperties();
    const key = 'pending_' + Date.now();
    props.setProperty(key, e.postData.contents);
    ScriptApp.newTrigger('processQueue').timeBased().after(1).create();
  } catch(err) {
    Logger.log('Queue error: ' + err);
  }
  return ContentService.createTextOutput(JSON.stringify({ status: 'ok' }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * 修正重複寫入 bug：加入 LockService 確保同一時間只有一個實例執行
 * 根本原因：每則訊息都會新建一個 processQueue trigger，
 * 多個 trigger 同時啟動時都會讀到相同的 pending_ keys，
 * props.deleteProperty 在並發情況下無法防止重複寫入。
 */
function processQueue() {
  // 取得 script lock，最多等 30 秒
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch(e) {
    Logger.log('Could not acquire lock: ' + e);
    return;
  }

  try {
    const props = PropertiesService.getScriptProperties();
    const allProps = props.getProperties();
    const pendingKeys = Object.keys(allProps).filter(k => k.startsWith('pending_'));
    if (pendingKeys.length === 0) return;

    const ss = SpreadsheetApp.openById(SHEET_ID);
    let sheet = ss.getSheetByName(LOG_SHEET);
    if (!sheet) {
      sheet = ss.insertSheet(LOG_SHEET);
      sheet.appendRow(['msg_id', 'case_id', 'timestamp', 'speaker', 'message', 'source', 'line_user_id', 'reply_to_msg_id']);
    }

    // 讀取已處理過的 LINE message ID，用於去重
    const PROCESSED_KEY = 'processed_line_msg_ids';
    let processedIds = {};
    try { processedIds = JSON.parse(props.getProperty(PROCESSED_KEY) || '{}'); } catch(e) {}

    pendingKeys.forEach(key => {
      const rawData = allProps[key];
      props.deleteProperty(key);  // 先刪，防重複
      try {
        const body = JSON.parse(rawData);
        const events = body.events || [];
        events.forEach(event => {
          if (event.type === 'message' && event.message.type === 'text') {
            const lineMessageId = event.message.id;
            // 已處理過的 message ID → 跳過，防止重複寫入
            if (lineMessageId && processedIds[lineMessageId]) {
              Logger.log('Skipping duplicate LINE message: ' + lineMessageId);
              return;
            }
            if (lineMessageId) processedIds[lineMessageId] = true;

            const userId = event.source.userId || '';
            const displayName = getLineProfile(userId);
            const replyToMsgId = (event.message.quotedMessageId) || '';
            sheet.appendRow([
              Utilities.getUuid(),             // A: msg_id
              '',                              // B: case_id（待業務填入）
              new Date(event.timestamp),       // C: timestamp
              displayName,                     // D: speaker（LINE 顯示名稱）
              event.message.text || '',        // E: message
              'LINE',                          // F: source
              userId,                          // G: line_user_id（原始 userId）
              replyToMsgId                     // H: reply_to_msg_id（長按回覆時才有值）
            ]);
          }
        });
      } catch(err) {
        Logger.log('processQueue error: ' + err);
      }
    });

    // 保存已處理 ID（最多保留最新 2000 筆，防止 Script Properties 過大）
    const idList = Object.keys(processedIds);
    if (idList.length > 2000) {
      const trimmed = {};
      idList.slice(-1000).forEach(id => trimmed[id] = true);
      props.setProperty(PROCESSED_KEY, JSON.stringify(trimmed));
    } else {
      props.setProperty(PROCESSED_KEY, JSON.stringify(processedIds));
    }

    // 清除本次觸發的所有 processQueue triggers
    ScriptApp.getProjectTriggers().forEach(t => {
      if (t.getHandlerFunction() === 'processQueue') ScriptApp.deleteTrigger(t);
    });
  } finally {
    lock.releaseLock();
  }
}
