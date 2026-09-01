/**
 * Isolated Hermes -> Google Sheets bridge.
 *
 * This project deliberately has no dependency on the legacy quote project or
 * its master spreadsheet. It accepts two signed, non-commercial write routes.
 */

var HERMES_AUTH_VERSION_ = 'hmac-sha256-v1';
var HERMES_ACTOR_ = 'hermes-sheets-assistant';
var HERMES_MAX_CLOCK_SKEW_SECONDS_ = 300;
var HERMES_REPLAY_TTL_SECONDS_ = 600;
var HERMES_MAX_HEADCOUNT_ = 5000;
var HERMES_CREATE_SCHEMA_ = 'hermes-line-sheets-assistant-v1';
var HERMES_REVISION_SCHEMA_ = 'hermes-sheets-revision-v1';
var HERMES_CREATE_ACTION_ = 'createQuoteShell';
var HERMES_REVISION_ACTION_ = 'appendQuoteRevisionRequest';

var HERMES_REGISTRY_HEADERS_ = [
  'CASE_ID',
  'SUMMARY_DIGEST',
  'QUOTE_ID',
  'CONTACT_REF_HASH',
  'CREATED_AT',
  'STATUS'
];

var HERMES_REVISION_HEADERS_ = [
  'CASE_ID',
  'QUOTE_ID',
  'REVISION_NO',
  'CHANGE_DIGEST',
  'CHANGE_TEXT',
  'CONTACT_REF_HASH',
  'CREATED_AT',
  'STATUS'
];


function doPost(e) {
  try {
    var envelope = parseJsonBody_(e);
    var payload = verifySignedEnvelope_(envelope);
    var result;

    if (payload.action === HERMES_CREATE_ACTION_) {
      result = createQuoteShell_(payload);
    } else if (payload.action === HERMES_REVISION_ACTION_) {
      result = appendQuoteRevisionRequest_(payload);
    } else {
      throw appError_('ACTION_NOT_ALLOWED');
    }

    return jsonResponse_({ ok: true, result: result });
  } catch (error) {
    return jsonResponse_({ ok: false, error: publicErrorCode_(error) });
  }
}


function doGet() {
  return jsonResponse_({ ok: false, error: 'METHOD_NOT_ALLOWED' });
}


function parseJsonBody_(e) {
  if (!e || !e.postData || typeof e.postData.contents !== 'string') {
    throw appError_('JSON_BODY_REQUIRED');
  }
  if (e.postData.contents.length < 2 || e.postData.contents.length > 65536) {
    throw appError_('JSON_BODY_SIZE_INVALID');
  }
  var parsed;
  try {
    parsed = JSON.parse(e.postData.contents);
  } catch (error) {
    throw appError_('JSON_BODY_INVALID');
  }
  if (!isPlainObject_(parsed)) {
    throw appError_('JSON_OBJECT_REQUIRED');
  }
  return parsed;
}


function verifySignedEnvelope_(envelope) {
  assertExactKeys_(envelope, [
    'authVersion',
    'actor',
    'issuedAt',
    'nonce',
    'action',
    'signedPayload',
    'signature'
  ]);

  if (envelope.authVersion !== HERMES_AUTH_VERSION_) {
    throw appError_('AUTH_VERSION_INVALID');
  }
  if (envelope.actor !== HERMES_ACTOR_) {
    throw appError_('ACTOR_INVALID');
  }
  assertInteger_(envelope.issuedAt, 'ISSUED_AT_INVALID', 0, 9999999999);
  assertString_(envelope.nonce, 'NONCE_INVALID', 16, 128, /^[A-Za-z0-9_-]+$/);
  assertString_(envelope.action, 'ACTION_INVALID', 1, 64, /^[A-Za-z][A-Za-z0-9]+$/);
  if (
    envelope.action !== HERMES_CREATE_ACTION_ &&
    envelope.action !== HERMES_REVISION_ACTION_
  ) {
    throw appError_('ACTION_NOT_ALLOWED');
  }
  assertString_(envelope.signedPayload, 'SIGNED_PAYLOAD_INVALID', 2, 60000);
  assertString_(envelope.signature, 'SIGNATURE_INVALID', 64, 64, /^[a-f0-9]{64}$/);

  var nowSeconds = Math.floor(Date.now() / 1000);
  if (Math.abs(nowSeconds - envelope.issuedAt) > HERMES_MAX_CLOCK_SKEW_SECONDS_) {
    throw appError_('TIMESTAMP_OUTSIDE_WINDOW');
  }

  var secret = PropertiesService.getScriptProperties().getProperty(
    'HERMES_SHEETS_HMAC_SECRET'
  );
  if (typeof secret !== 'string' || secret.length < 32) {
    throw appError_('AUTH_NOT_CONFIGURED');
  }

  var message = [
    HERMES_AUTH_VERSION_,
    envelope.actor,
    String(envelope.issuedAt),
    envelope.nonce,
    envelope.action,
    envelope.signedPayload
  ].join('\n');
  var expected = bytesToHex_(Utilities.computeHmacSha256Signature(
    message,
    secret,
    Utilities.Charset.UTF_8
  ));
  if (!constantTimeEqual_(expected, envelope.signature)) {
    throw appError_('SIGNATURE_INVALID');
  }

  var payload;
  try {
    payload = JSON.parse(envelope.signedPayload);
  } catch (error) {
    throw appError_('SIGNED_PAYLOAD_JSON_INVALID');
  }
  if (!isPlainObject_(payload)) {
    throw appError_('SIGNED_PAYLOAD_OBJECT_REQUIRED');
  }
  if (payload.action !== envelope.action) {
    throw appError_('ACTION_BINDING_MISMATCH');
  }

  consumeNonce_(envelope.actor, envelope.nonce);
  return payload;
}


function consumeNonce_(actor, nonce) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) {
    throw appError_('AUTH_LOCK_UNAVAILABLE');
  }
  try {
    var cache = CacheService.getScriptCache();
    var cacheKey = 'hermes_replay_' + sha256Hex_(actor + '\n' + nonce);
    if (cache.get(cacheKey) !== null) {
      throw appError_('NONCE_REPLAYED');
    }
    cache.put(cacheKey, '1', HERMES_REPLAY_TTL_SECONDS_);
  } finally {
    lock.releaseLock();
  }
}


function createQuoteShell_(payload) {
  validateCreatePayload_(payload);
  var lock = LockService.getScriptLock();
  var createdQuoteId = '';
  if (!lock.tryLock(20000)) {
    throw appError_('WRITE_LOCK_UNAVAILABLE');
  }

  try {
    var registryBook = openRegistryBook_();
    var registry = requireLedgerSheet_(
      registryBook,
      'HERMES_SHEET_REQUESTS',
      HERMES_REGISTRY_HEADERS_
    );
    var existing = findCaseRegistryRow_(registry, payload.caseId);
    if (existing) {
      if (existing.summaryDigest !== payload.summaryDigest) {
        throw appError_('CASE_ID_SUMMARY_CONFLICT');
      }
      if (existing.contactRefHash !== payload.contactRefHash) {
        throw appError_('CASE_ID_CONTACT_CONFLICT');
      }
      return {
        action: HERMES_CREATE_ACTION_,
        status: existing.status,
        quoteId: existing.quoteId,
        idempotent: true
      };
    }

    var quoteBook = SpreadsheetApp.create(
      'Hermes intake ' + payload.caseId,
      48,
      4
    );
    var quoteId = quoteBook.getId();
    createdQuoteId = quoteId;
    initializeCleanQuoteShell_(quoteBook, payload);
    moveQuoteToConfiguredFolder_(quoteId);

    registry.appendRow([
      safeCellLiteral_(payload.caseId),
      payload.summaryDigest,
      quoteId,
      payload.contactRefHash,
      new Date().toISOString(),
      'NEEDS_MINA_QUOTE'
    ]);
    createdQuoteId = '';

    return {
      action: HERMES_CREATE_ACTION_,
      status: 'NEEDS_MINA_QUOTE',
      quoteId: quoteId,
      idempotent: false
    };
  } catch (error) {
    if (createdQuoteId) {
      try {
        DriveApp.getFileById(createdQuoteId).setTrashed(true);
      } catch (cleanupError) {
        console.error('Hermes orphan cleanup failed: ' + cleanupError.message);
      }
    }
    throw error;
  } finally {
    lock.releaseLock();
  }
}


function appendQuoteRevisionRequest_(payload) {
  validateRevisionPayload_(payload);
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) {
    throw appError_('WRITE_LOCK_UNAVAILABLE');
  }

  try {
    var registryBook = openRegistryBook_();
    var registry = requireLedgerSheet_(
      registryBook,
      'HERMES_SHEET_REQUESTS',
      HERMES_REGISTRY_HEADERS_
    );
    var binding = findCaseRegistryRow_(registry, payload.caseId);
    if (!binding || binding.quoteId !== payload.quoteId) {
      throw appError_('CASE_QUOTE_BINDING_NOT_FOUND');
    }

    var revisions = requireLedgerSheet_(
      registryBook,
      'QUOTE_REVISIONS',
      HERMES_REVISION_HEADERS_
    );
    var prior = findRevisionByDigest_(
      revisions,
      payload.caseId,
      payload.quoteId,
      payload.changeDigest
    );
    if (prior) {
      return {
        action: HERMES_REVISION_ACTION_,
        status: prior.status,
        quoteId: payload.quoteId,
        revisionNo: prior.revisionNo,
        idempotent: true
      };
    }

    var revisionNo = nextRevisionNumber_(
      revisions,
      payload.caseId,
      payload.quoteId
    );
    revisions.appendRow([
      safeCellLiteral_(payload.caseId),
      safeCellLiteral_(payload.quoteId),
      revisionNo,
      payload.changeDigest,
      safeCellLiteral_(payload.customerChangeVerbatim),
      payload.contactRefHash,
      new Date().toISOString(),
      'PENDING_MINA'
    ]);
    SpreadsheetApp.flush();

    return {
      action: HERMES_REVISION_ACTION_,
      status: 'PENDING_MINA',
      quoteId: payload.quoteId,
      revisionNo: revisionNo,
      idempotent: false
    };
  } finally {
    lock.releaseLock();
  }
}


function validateCreatePayload_(payload) {
  assertExactKeys_(payload, [
    'action',
    'schemaVersion',
    'caseId',
    'source',
    'clientName',
    'company',
    'contactRefHash',
    'businessCategory',
    'eventDate',
    'eventTime',
    'venue',
    'indoorOutdoor',
    'headcount',
    'serviceFormat',
    'dietaryNotesVerbatim',
    'logisticsNotesVerbatim',
    'summaryConfirmed',
    'summaryConfirmedAt',
    'summaryText',
    'summaryDigest',
    'confirmationMessageDigest',
    'confirmationSourceRefHash',
    'availabilityStatus',
    'dietaryReviewStatus',
    'commercialReviewStatus'
  ]);

  if (payload.action !== HERMES_CREATE_ACTION_) {
    throw appError_('CREATE_ACTION_INVALID');
  }
  if (payload.schemaVersion !== HERMES_CREATE_SCHEMA_) {
    throw appError_('CREATE_SCHEMA_INVALID');
  }
  assertIdentifier_(payload.caseId, 'CASE_ID_INVALID');
  if (payload.source !== 'line') {
    throw appError_('SOURCE_INVALID');
  }
  assertString_(payload.clientName, 'CLIENT_NAME_INVALID', 0, 120);
  assertString_(payload.company, 'COMPANY_INVALID', 0, 160);
  assertOptionalHash_(payload.contactRefHash, 'CONTACT_REF_HASH_INVALID');
  assertString_(payload.businessCategory, 'BUSINESS_CATEGORY_INVALID', 1, 120);
  assertAllowedValue_(payload.businessCategory, [
    '外燴', '外帶／餐盒', 'Candy Bar／甜品桌', '企業長期合作'
  ], 'BUSINESS_CATEGORY_INVALID');
  assertIsoDate_(payload.eventDate, 'EVENT_DATE_INVALID');
  assertTimeOrRange_(payload.eventTime, 'EVENT_TIME_INVALID');
  assertString_(payload.venue, 'VENUE_INVALID', 1, 500);
  assertString_(payload.indoorOutdoor, 'INDOOR_OUTDOOR_INVALID', 1, 64);
  assertAllowedValue_(payload.indoorOutdoor, ['室內', '戶外'], 'INDOOR_OUTDOOR_INVALID');
  assertInteger_(payload.headcount, 'HEADCOUNT_INVALID', 1, HERMES_MAX_HEADCOUNT_);
  assertString_(payload.serviceFormat, 'SERVICE_FORMAT_INVALID', 1, 160);
  assertAllowedValue_(payload.serviceFormat, [
    '現場外燴', '送達擺盤', '自取／外帶'
  ], 'SERVICE_FORMAT_INVALID');
  assertString_(payload.dietaryNotesVerbatim, 'DIETARY_NOTES_INVALID', 1, 2000);
  assertString_(payload.logisticsNotesVerbatim, 'LOGISTICS_NOTES_INVALID', 1, 2000);

  if (payload.summaryConfirmed !== true) {
    throw appError_('SUMMARY_CONFIRMATION_REQUIRED');
  }
  assertIsoTimestamp_(payload.summaryConfirmedAt, 'SUMMARY_CONFIRMED_AT_INVALID');
  assertString_(payload.summaryText, 'SUMMARY_TEXT_INVALID', 1, 12000);
  assertHash_(payload.summaryDigest, 'SUMMARY_DIGEST_INVALID');
  if (sha256Hex_(payload.summaryText) !== payload.summaryDigest) {
    throw appError_('SUMMARY_DIGEST_MISMATCH');
  }
  assertHash_(payload.confirmationMessageDigest, 'CONFIRMATION_MESSAGE_DIGEST_INVALID');
  assertHash_(payload.confirmationSourceRefHash, 'CONFIRMATION_SOURCE_REF_HASH_INVALID');

  if (payload.availabilityStatus !== 'UNVERIFIED') {
    throw appError_('AVAILABILITY_STATUS_INVALID');
  }
  if (payload.dietaryReviewStatus !== 'PENDING_HUMAN') {
    throw appError_('DIETARY_REVIEW_STATUS_INVALID');
  }
  if (payload.commercialReviewStatus !== 'PENDING_MINA') {
    throw appError_('COMMERCIAL_REVIEW_STATUS_INVALID');
  }
}


function validateRevisionPayload_(payload) {
  assertExactKeys_(payload, [
    'action',
    'schemaVersion',
    'caseId',
    'quoteId',
    'source',
    'contactRefHash',
    'customerChangeVerbatim',
    'changeDigest',
    'changeStatus'
  ]);
  if (payload.action !== HERMES_REVISION_ACTION_) {
    throw appError_('REVISION_ACTION_INVALID');
  }
  if (payload.schemaVersion !== HERMES_REVISION_SCHEMA_) {
    throw appError_('REVISION_SCHEMA_INVALID');
  }
  assertIdentifier_(payload.caseId, 'CASE_ID_INVALID');
  assertString_(payload.quoteId, 'QUOTE_ID_INVALID', 10, 128, /^[A-Za-z0-9_-]+$/);
  if (payload.source !== 'line') {
    throw appError_('SOURCE_INVALID');
  }
  assertOptionalHash_(payload.contactRefHash, 'CONTACT_REF_HASH_INVALID');
  assertString_(payload.customerChangeVerbatim, 'CUSTOMER_CHANGE_INVALID', 1, 4000);
  assertHash_(payload.changeDigest, 'CHANGE_DIGEST_INVALID');
  if (sha256Hex_(payload.customerChangeVerbatim) !== payload.changeDigest) {
    throw appError_('CHANGE_DIGEST_MISMATCH');
  }
  if (payload.changeStatus !== 'PENDING_MINA') {
    throw appError_('CHANGE_STATUS_INVALID');
  }
}


function initializeCleanQuoteShell_(book, payload) {
  var sheets = book.getSheets();
  if (sheets.length !== 1) {
    throw appError_('CLEAN_SHEET_INVARIANT_FAILED');
  }
  var sheet = sheets[0];
  sheet.setName('報價資料');
  sheet.clear();
  sheet.getRange('A1:D48').setNumberFormat('@');
  sheet.getRange('A1:D1').merge();
  sheet.getRange('A1').setValue('Hermes 收件資料｜待 Mina 人工處理');

  var rows = [
    ['案件欄位', '已確認資料'],
    ['case_id', payload.caseId],
    ['source', payload.source],
    ['contact_ref_hash', payload.contactRefHash],
    ['client_name', payload.clientName],
    ['company', payload.company],
    ['business_category', payload.businessCategory],
    ['event_date', payload.eventDate],
    ['event_time', payload.eventTime],
    ['venue', payload.venue],
    ['indoor_outdoor', payload.indoorOutdoor],
    ['headcount', String(payload.headcount)],
    ['service_format', payload.serviceFormat],
    ['dietary_notes_verbatim', payload.dietaryNotesVerbatim],
    ['logistics_notes_verbatim', payload.logisticsNotesVerbatim],
    ['availability_status', payload.availabilityStatus],
    ['dietary_review_status', payload.dietaryReviewStatus],
    ['commercial_review_status', payload.commercialReviewStatus],
    ['summary_confirmed_at', payload.summaryConfirmedAt],
    ['summary_digest', payload.summaryDigest]
  ];
  var safeRows = rows.map(function(row) {
    return [safeCellLiteral_(row[0]), safeCellLiteral_(row[1])];
  });
  sheet.getRange(3, 1, safeRows.length, 2).setValues(safeRows);

  sheet.getRange('A25:D25').merge();
  sheet.getRange('A25').setValue('Mina 填寫區（保持空白，僅供人工）');
  sheet.getRange('A26:D48').clearContent();
  sheet.setFrozenRows(3);
  sheet.setColumnWidth(1, 220);
  sheet.setColumnWidth(2, 520);

  SpreadsheetApp.flush();
  if (book.getSheets().length !== 1 || book.getNamedRanges().length !== 0) {
    throw appError_('CLEAN_SHEET_READBACK_FAILED');
  }
  var formulas = sheet.getDataRange().getFormulas();
  for (var i = 0; i < formulas.length; i += 1) {
    for (var j = 0; j < formulas[i].length; j += 1) {
      if (formulas[i][j] !== '') {
        throw appError_('CLEAN_SHEET_FORMULA_FOUND');
      }
    }
  }
}


function moveQuoteToConfiguredFolder_(quoteId) {
  var folderId = PropertiesService.getScriptProperties().getProperty(
    'HERMES_QUOTE_FOLDER_ID'
  );
  if (!folderId) {
    return;
  }
  assertString_(folderId, 'QUOTE_FOLDER_ID_INVALID', 10, 128, /^[A-Za-z0-9_-]+$/);
  DriveApp.getFileById(quoteId).moveTo(DriveApp.getFolderById(folderId));
}


function openRegistryBook_() {
  var registryId = PropertiesService.getScriptProperties().getProperty(
    'HERMES_REGISTRY_SPREADSHEET_ID'
  );
  if (!registryId) {
    throw appError_('REGISTRY_NOT_CONFIGURED');
  }
  assertString_(registryId, 'REGISTRY_ID_INVALID', 10, 128, /^[A-Za-z0-9_-]+$/);
  return SpreadsheetApp.openById(registryId);
}


function requireLedgerSheet_(book, sheetName, expectedHeaders) {
  var sheet = book.getSheetByName(sheetName);
  if (!sheet) {
    sheet = book.insertSheet(sheetName);
    sheet.getRange(1, 1, 1, expectedHeaders.length).setValues([expectedHeaders]);
    sheet.setFrozenRows(1);
    return sheet;
  }
  if (sheet.getLastRow() < 1) {
    sheet.getRange(1, 1, 1, expectedHeaders.length).setValues([expectedHeaders]);
    sheet.setFrozenRows(1);
    return sheet;
  }
  var actual = sheet.getRange(1, 1, 1, expectedHeaders.length).getValues()[0];
  for (var i = 0; i < expectedHeaders.length; i += 1) {
    if (actual[i] !== expectedHeaders[i]) {
      throw appError_('LEDGER_SCHEMA_MISMATCH');
    }
  }
  return sheet;
}


function findCaseRegistryRow_(sheet, caseId) {
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    return null;
  }
  var values = sheet.getRange(2, 1, lastRow - 1, HERMES_REGISTRY_HEADERS_.length)
    .getValues();
  for (var i = 0; i < values.length; i += 1) {
    if (String(values[i][0]) === caseId) {
      return {
        summaryDigest: String(values[i][1]),
        quoteId: String(values[i][2]),
        contactRefHash: String(values[i][3]),
        status: String(values[i][5])
      };
    }
  }
  return null;
}


function findRevisionByDigest_(sheet, caseId, quoteId, changeDigest) {
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    return null;
  }
  var values = sheet.getRange(2, 1, lastRow - 1, HERMES_REVISION_HEADERS_.length)
    .getValues();
  for (var i = 0; i < values.length; i += 1) {
    if (
      String(values[i][0]) === caseId &&
      String(values[i][1]) === quoteId &&
      String(values[i][3]) === changeDigest
    ) {
      return {
        revisionNo: Number(values[i][2]),
        status: String(values[i][7])
      };
    }
  }
  return null;
}


function nextRevisionNumber_(sheet, caseId, quoteId) {
  var lastRow = sheet.getLastRow();
  var highest = 0;
  if (lastRow >= 2) {
    var values = sheet.getRange(2, 1, lastRow - 1, HERMES_REVISION_HEADERS_.length)
      .getValues();
    for (var i = 0; i < values.length; i += 1) {
      if (String(values[i][0]) === caseId && String(values[i][1]) === quoteId) {
        var candidate = Number(values[i][2]);
        if (!Number.isFinite(candidate) || Math.floor(candidate) !== candidate || candidate < 1) {
          throw appError_('REVISION_LEDGER_CORRUPT');
        }
        highest = Math.max(highest, candidate);
      }
    }
  }
  return highest + 1;
}


function assertExactKeys_(value, expectedKeys) {
  if (!isPlainObject_(value)) {
    throw appError_('OBJECT_REQUIRED');
  }
  var actual = Object.keys(value).sort();
  var expected = expectedKeys.slice().sort();
  if (actual.length !== expected.length) {
    throw appError_('SCHEMA_KEYS_INVALID');
  }
  for (var i = 0; i < expected.length; i += 1) {
    if (actual[i] !== expected[i]) {
      throw appError_('SCHEMA_KEYS_INVALID');
    }
  }
}


function assertIdentifier_(value, code) {
  assertString_(value, code, 6, 128, /^[A-Za-z0-9][A-Za-z0-9._:-]+$/);
}


function assertString_(value, code, minLength, maxLength, pattern) {
  if (typeof value !== 'string') {
    throw appError_(code);
  }
  if (value.length < minLength || value.length > maxLength) {
    throw appError_(code);
  }
  if (pattern && !pattern.test(value)) {
    throw appError_(code);
  }
  if (value.indexOf('\u0000') !== -1) {
    throw appError_(code);
  }
}


function assertInteger_(value, code, minimum, maximum) {
  if (
    typeof value !== 'number' ||
    !Number.isFinite(value) ||
    Math.floor(value) !== value ||
    value < minimum ||
    value > maximum
  ) {
    throw appError_(code);
  }
}


function assertAllowedValue_(value, allowed, code) {
  if (allowed.indexOf(value) === -1) {
    throw appError_(code);
  }
}


function assertHash_(value, code) {
  assertString_(value, code, 64, 64, /^[a-f0-9]{64}$/);
}


function assertOptionalHash_(value, code) {
  if (value === '') {
    return;
  }
  assertHash_(value, code);
}


function assertIsoDate_(value, code) {
  assertString_(value, code, 10, 10, /^\d{4}-\d{2}-\d{2}$/);
  var parts = value.split('-').map(Number);
  var parsed = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
  var roundTrip = [
    String(parsed.getUTCFullYear()).padStart(4, '0'),
    String(parsed.getUTCMonth() + 1).padStart(2, '0'),
    String(parsed.getUTCDate()).padStart(2, '0')
  ].join('-');
  if (roundTrip !== value) {
    throw appError_(code);
  }
}


function assertIsoTimestamp_(value, code) {
  assertString_(
    value,
    code,
    20,
    24,
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/
  );
  var parsed = new Date(value);
  if (!Number.isFinite(parsed.getTime())) {
    throw appError_(code);
  }
  var normalized = parsed.toISOString();
  var expected = value.length === 20 ? normalized.replace('.000Z', 'Z') : normalized;
  if (expected !== value) {
    throw appError_(code);
  }
}


function assertTimeOrRange_(value, code) {
  assertString_(value, code, 5, 11, /^\d{2}:\d{2}(?:-\d{2}:\d{2})?$/);
  var pieces = value.split('-');
  for (var i = 0; i < pieces.length; i += 1) {
    var timeParts = pieces[i].split(':').map(Number);
    if (timeParts[0] > 23 || timeParts[1] > 59) {
      throw appError_(code);
    }
    var roundTrip = String(timeParts[0]).padStart(2, '0') + ':' +
      String(timeParts[1]).padStart(2, '0');
    if (roundTrip !== pieces[i]) {
      throw appError_(code);
    }
  }
}


function safeCellLiteral_(value) {
  var text = value === null || value === undefined ? '' : String(value);
  if (/^\s*[=+\-@]/.test(text)) {
    return "'" + text;
  }
  return text;
}


function sha256Hex_(text) {
  return bytesToHex_(Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256,
    text,
    Utilities.Charset.UTF_8
  ));
}


function bytesToHex_(bytes) {
  return bytes.map(function(byte) {
    return ('0' + ((byte & 255).toString(16))).slice(-2);
  }).join('');
}


function constantTimeEqual_(left, right) {
  if (typeof left !== 'string' || typeof right !== 'string') {
    return false;
  }
  var mismatch = left.length ^ right.length;
  var length = Math.max(left.length, right.length);
  for (var i = 0; i < length; i += 1) {
    mismatch |= (left.charCodeAt(i % left.length) ^ right.charCodeAt(i % right.length));
  }
  return mismatch === 0;
}


function isPlainObject_(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}


function jsonResponse_(value) {
  return ContentService.createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}


function appError_(code) {
  var error = new Error(code);
  error.hermesPublicCode = code;
  return error;
}


function publicErrorCode_(error) {
  if (error && typeof error.hermesPublicCode === 'string') {
    return error.hermesPublicCode;
  }
  return 'INTERNAL_ERROR';
}
