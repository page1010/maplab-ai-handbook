// MAPLAB Agent Commander v5.6.1 — popup.js
// 角色選擇 + GitHub dynamic role task modules + runtime handoff prompt
const DEFAULT_BASE = 'https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main';
const GITHUB_API   = 'https://api.github.com/repos/page1010/maplab-ai-handbook';
const COMMIT_COUNT = 8;
const MODULE_INDEX_PATH = 'chrome-extension/task-modules/index.json';
const el = id => document.getElementById(id);

// Side Panel
if (chrome.sidePanel) {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
}

// === 全域狀態 ===
let cachedParsed = null;
let cachedCommits = [];
let cachedOverdue = [];
let cachedRecallPrompts = {};
let cachedModuleIndex = null;
let cachedRoleModules = {};
let cachedFreshness = {};

// === UI helpers ===
function setStatus(state, text) {
  el('statusDot').className = 'status-dot ' + state;
  el('statusText').textContent = text;
}
function updateCharCount(text) {
  const n = text.length;
  const el_ = el('tokenCount');
  el_.textContent = n + ' chars';
  el_.className = 'token-count' + (n > 1800 ? ' warn' : '');
}
function escapeHtml(text) {
  return String(text || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}
function truncate(text, max) {
  if (!text) return '';
  if (text.length <= max) return text;
  return text.slice(0, max) + `\n\n[truncated: ${text.length - max} chars omitted]`;
}
function formatVersion(version) {
  const value = String(version || '?').trim();
  return value.startsWith('v') ? value : `v${value}`;
}
const RUNTIME_TARGETS = {
  claude_code: 'Claude Code',
  codex: 'Codex',
  gpt: 'GPT / ChatGPT',
  claude_chrome_tab: 'Claude Chrome tab',
  antigravity: 'Antigravity',
  gemini: 'Gemini',
  openclaw: 'OpenClaw',
  hermes: 'Hermes',
  gemini_chrome_tab: 'Gemini Chrome tab',
};
function normalizeRuntimeTarget(runtime) {
  const aliases = {
    claude_tab: 'claude_chrome_tab',
    gemini_sidebar: 'gemini',
    gemini_tab: 'gemini_chrome_tab',
  };
  const key = aliases[runtime] || runtime;
  return RUNTIME_TARGETS[key] ? key : 'claude_code';
}
function runtimeTargetLabel(runtime) {
  return RUNTIME_TARGETS[normalizeRuntimeTarget(runtime)];
}
function sortedRoleModules() {
  return [...(cachedModuleIndex?.modules || [])].sort((a, b) =>
    String(a.role_id).localeCompare(String(b.role_id), undefined, { numeric: true })
  );
}
function roleOptionLabel(module) {
  const name = module.department || module.role_name || module.role_id;
  return `${module.role_id}｜${name}`;
}
function appendRoleGroup(select, label, modules) {
  if (!modules.length) return;
  const sep = document.createElement('option');
  sep.disabled = true;
  sep.value = `__sep_${label}`;
  sep.textContent = `── ${label} ──`;
  select.appendChild(sep);
  modules.forEach(module => {
    const option = document.createElement('option');
    option.value = module.role_id;
    option.textContent = roleOptionLabel(module);
    select.appendChild(option);
  });
}
function populateRoleSelectFromIndex(preferredRole = '') {
  const select = el('roleSelect');
  const modules = sortedRoleModules();
  if (!select || modules.length === 0) return;
  const selected = preferredRole || select.value || '';
  select.textContent = '';
  select.appendChild(new Option('-- 總覽模式 --', ''));
  appendRoleGroup(select, 'MAPLAB / A Department', modules.filter(m => String(m.role_id).startsWith('A')));
  appendRoleGroup(select, 'Investment OS / Cross-Project', modules.filter(m => String(m.role_id).startsWith('B')));
  appendRoleGroup(select, 'Investment OS / Strategy Owners', modules.filter(m => String(m.role_id).startsWith('IOS-')));
  appendRoleGroup(
    select,
    'Other',
    modules.filter(m => !String(m.role_id).startsWith('A') && !String(m.role_id).startsWith('B') && !String(m.role_id).startsWith('IOS-'))
  );
  const valid = [...select.options].some(option => option.value === selected && !option.disabled);
  select.value = valid ? selected : '';
}

// === GitHub fetch ===
function authHeaders(token) {
  const h = {
    'Accept': 'application/vnd.github.v3+json',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
  };
  if (token) h['Authorization'] = `token ${token}`;
  return h;
}
async function fetchCommits(token) {
  try {
    const url = `${GITHUB_API}/commits?per_page=${COMMIT_COUNT}&t=${Date.now()}`;
    const resp = await fetch(url, { headers: authHeaders(token), cache: 'no-store' });
    if (!resp.ok) return [];
    const data = await resp.json();
    return data.map(c => ({
      sha:     c.sha.substring(0, 7),
      message: c.commit.message.split('\n')[0],
      date:    c.commit.author.date,
      author:  c.commit.author.name
    }));
  } catch { return []; }
}
async function fetchFile(base, path, token) {
  // Private repo: raw.githubusercontent.com 不支援 Authorization header
  // 有 token 時改用 GitHub Contents API（回傳 base64 內容）
  if (token) {
    const apiUrl = `${GITHUB_API}/contents/${path}?ref=main&cb=${Date.now()}`;
    const resp = await fetch(apiUrl, { headers: authHeaders(token), cache: 'no-store' });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const json = await resp.json();
    const binary = atob(json.content.replace(/\n/g, ''));
    const bytes = Uint8Array.from(binary, ch => ch.charCodeAt(0));
    return new TextDecoder('utf-8').decode(bytes);
  }
  const url = base.replace(/\/$/, '') + '/' + path + '?t=' + Date.now();
  const resp = await fetch(url, { cache: 'no-store' });
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  return resp.text();
}
async function fetchJsonFile(base, path, token) {
  if (path.startsWith('chrome-extension/task-modules/')) {
    const localUrl = chrome.runtime.getURL(path.replace(/^chrome-extension\//, ''));
    try {
      const localResp = await fetch(localUrl, { cache: 'no-store' });
      if (localResp.ok) return JSON.parse(await localResp.text());
    } catch(e) {
      // Fall back to GitHub raw below when local packaged data is unavailable.
    }
    const url = rawUrl(base, path) + '?cb=' + Date.now();
    try {
      const resp = await fetch(url, { cache: 'no-store' });
      if (resp.ok) return JSON.parse(await resp.text());
    } catch(e) {
      // Fall back to Contents API below when raw access is blocked.
    }
  }
  return JSON.parse(await fetchFile(base, path, token));
}
function rawUrl(base, path) {
  return base.replace(/\/$/, '') + '/' + path;
}
async function sha256Hex(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
}
function shortHash(hash) {
  return hash ? hash.slice(0, 10) : 'no-hash';
}
function sourceIsHashable(item) {
  return item?.exists === 'true' && item?.source_sha256 && item?.load_mode !== 'a1_only';
}

// === Parse CURRENT_STATUS.md ===
function parseStatus(md) {
  const r = { version:'?', phase:'?', activeTasks:[], blockers:[], recentDecisions:[] };
  let section = '';
  for (const line of md.split('\n')) {
    const t = line.trim();
    if (t.startsWith('- **Version**:')) r.version = t.replace('- **Version**:','').trim();
    if (t.startsWith('- **Phase**:'))   r.phase   = t.replace('- **Phase**:','').trim();
    if (t.startsWith('## ')) { section = t.toLowerCase(); continue; }
    if (section.includes('進行中') || section.includes('current task')) {
      if (t.startsWith('|') && !t.includes('Task ID') && !t.includes('---')) {
        const cols = t.split('|').map(c=>c.trim()).filter(Boolean);
        if (cols.length >= 4) r.activeTasks.push({ id:cols[0], name:cols[1], agent:cols[2], status:cols[3] });
      }
    }
    if (section.includes('blocker')) {
      if (t.startsWith('-') && !t.includes('~~') && !t.includes('✅ resolved')) {
        const text = t.replace(/^-\s*/,'').trim();
        if (text.length > 5) r.blockers.push(text.substring(0,100));
      }
    }
    if (section.includes('最新決策') || section.includes('decision')) {
      if (t.startsWith('- ') && r.recentDecisions.length < 3)
        r.recentDecisions.push(t.replace(/^-\s*/,'').substring(0,120));
    }
  }
  return r;
}

// === Lazy-load per-agent recall from recalls/Ax_recall.md ===
async function loadAgentRecall(role, base, token) {
  if (cachedRecallPrompts[role]) return; // already cached
  try {
    const md = await fetchFile(base, `recalls/${role}_recall.md`, token);
    cachedRecallPrompts[role] = md.trim();
  } catch(e) {
    const module = cachedRoleModules[role] || await loadRoleModule(role, base, token);
    cachedRecallPrompts[role] = module?.packaged_role_recall_excerpt?.trim()
      || `// ${role} recall 載入失敗: ${e.message}`;
  }
}
async function loadModuleIndex(base, token) {
  cachedModuleIndex = await fetchJsonFile(base, MODULE_INDEX_PATH, token);
  return cachedModuleIndex;
}
function modulePathForRole(role) {
  const entry = cachedModuleIndex?.modules?.find(m => m.role_id === role);
  return entry?.path || `chrome-extension/task-modules/${role}.json`;
}
async function loadRoleModule(role, base, token) {
  if (!role) return null;
  if (cachedRoleModules[role]) return cachedRoleModules[role];
  const module = await fetchJsonFile(base, modulePathForRole(role), token);
  cachedRoleModules[role] = module;
  return module;
}

// === Overdue detection — 直接讀 CURRENT_STATUS 的 🔴 CRITICAL 標記（與 checkpoint.sh/patrol.sh 統一邏輯） ===
function detectOverdueTasks(commits, activeTasks) {
  const warnings = [];
  for (const task of activeTasks) {
    if (task.status.includes('🔴') || task.status.includes('CRITICAL')) {
      // 從狀態欄提取時間資訊（如 ~215h無commit）
      const match = task.status.match(/~(\d+)h/);
      const hours = match ? match[1] + 'h' : '?h';
      warnings.push(`${task.id} 🔴 CRITICAL（${hours}無commit）— ${task.name.substring(0,30)}`);
    }
  }
  return warnings;
}

// === Prompt builders ===
function buildOverviewPrompt(parsed, overdueWarnings) {
  const lines = [];
  const requestedTask = getTaskText();
  lines.push(`系統 ${parsed.version} ｜ ${parsed.phase}`);
  lines.push('');
  if (requestedTask) {
    lines.push('【本次召喚任務】');
    lines.push(requestedTask);
    lines.push('');
  }
  const critical   = parsed.activeTasks.filter(t => t.status.includes('🔴') || t.status.includes('CRITICAL'));
  const inProgress = parsed.activeTasks.filter(t => t.status.includes('🔄') && !t.status.includes('🔴') && !t.status.includes('CRITICAL'));
  const available  = parsed.activeTasks.filter(t => t.status.includes('🔲'));
  if (critical.length > 0) {
    lines.push('【🔴 CRITICAL — 需立即處理】');
    critical.forEach(t => lines.push(`🔴 ${t.id} (${t.agent}) — ${t.status.substring(0,60)}`));
    lines.push('');
  }
  if (inProgress.length > 0) {
    lines.push('【進行中】');
    inProgress.forEach(t => lines.push(`🔄 ${t.id} (${t.agent}) — ${t.name.substring(0,40)}`));
    lines.push('');
  }
  if (available.length > 0) {
    lines.push('【可認領】');
    available.forEach(t => lines.push(`🔲 ${t.id} — ${t.name.substring(0,40)}`));
    lines.push('');
  }
  if (parsed.blockers.length > 0) {
    lines.push('【Blockers】');
    parsed.blockers.forEach(b => lines.push(`⛔ ${b}`));
    lines.push('');
  }
  if (overdueWarnings.length > 0) {
    lines.push('【巡查警示】');
    overdueWarnings.forEach(w => lines.push(`⏰ ${w}`));
  }
  return lines.join('\n');
}

// === System snapshot (Task B) ===
function buildSystemSnapshot(parsed) {
  const lines = ['', '---', '【系統快照 — 即時】'];
  lines.push(`版本：${parsed.version} ｜ ${parsed.phase}`);
  const critical   = parsed.activeTasks.filter(t => t.status.includes('🔴') || t.status.includes('CRITICAL'));
  const inProgress = parsed.activeTasks.filter(t => t.status.includes('🔄') && !t.status.includes('🔴') && !t.status.includes('CRITICAL'));
  if (critical.length > 0) {
    lines.push('🔴 CRITICAL：' + critical.map(t => t.id).join('、'));
  }
  if (inProgress.length > 0) {
    lines.push('進行中：' + inProgress.map(t => `${t.id}(${t.name.substring(0,20)})`).join('、'));
  }
  const available = parsed.activeTasks.filter(t => t.status.includes('🔲'));
  if (available.length > 0) {
    lines.push('可認領：' + available.map(t => t.id).join('、'));
  }
  if (parsed.blockers.length > 0) {
    lines.push('Blockers：' + parsed.blockers.slice(0, 2).map(b => b.substring(0, 60)).join(' | '));
  }
  return lines.join('\n');
}
function runtimeInstruction(runtime) {
  const target = normalizeRuntimeTarget(runtime);
  const map = {
    claude_code: [
      '你正在 Claude Code terminal 接手 MAPLAB 角色。請以 /Users/pagemacmini/maplab-ai-handbook 為正式 repo，先讀 CURRENT_STATUS.md、pitfalls.md 與本角色必讀來源。',
      '你可以做 repo 整合、腳本修復、驗證與 commit；不要把 Chrome tab 的聊天輸出當成唯一真相。',
    ],
    codex: [
      '你正在 Codex 執行。請以 /Users/pagemacmini/maplab-ai-handbook 為正式 repo，先讀下方 repo path，再做任何修改。',
      '修改後要留下 review bundle、驗證紀錄與 git commit；不要碰未列入 scope 的 runtime log。',
    ],
    gpt: [
      '你正在 GPT / ChatGPT 接手。你是高判斷研究與第二意見 worker，輸出是 evidence/draft，不是最終系統狀態。',
      '請優先讀 GitHub raw URL；若無法讀本機 repo、UI、API 或附件，明確列為缺資料，不要補猜。',
    ],
    claude_chrome_tab: [
      '你正在 Claude Chrome tab 接手。這是瀏覽器聊天入口，可做長文推理、企劃與審查，但不是 repo 直接執行環境。',
      '請回傳可貼回 repo 的結構化結果；不得宣稱已改檔、已發布、已驗證 live UI，除非有外部證據路徑。',
    ],
    antigravity: [
      '你正在 Antigravity 接手。你適合做公開網站、Google 生態與瀏覽器可見狀態的 bounded review。',
      '若沒有 Owner Chrome 登入態，請只處理 public/live URL 或 A2 提供的 visual bridge evidence，不要要求 secrets 或把缺 cookie 當平台壞掉。',
    ],
    gemini: [
      '你正在 Gemini 接手。你適合做 Google 生態資料理解、長上下文整理、表格/文件分析與策略第二意見。',
      '你可能看不到本機檔案，所以請優先使用下方 GitHub raw URL；如果無法讀取某個來源，請明確列為 blocker。',
    ],
    openclaw: [
      '你正在 OpenClaw 接手。你是 browser/operator worker，負責截圖、讀回、copy/paste 到 ChatGPT/Gemini/NotebookLM 與 UI smoke。',
      '只做 bounded evidence，不決定策略、不發布、不改正式真相源；所有高風險動作需要 Owner/A1 審查。',
    ],
    hermes: [
      '你正在 Hermes 接手。你是 cold-path 摘要、scaffold、question pack 與低風險整理 worker。',
      '不要擁有 hot-path Telegram 決策或正式策略結論；輸出要讓 Codex/A1/B 角色可驗證後整合。',
    ],
    gemini_chrome_tab: [
      '你正在 Gemini Chrome tab 接手。這是使用 Owner 瀏覽器登入態的 Gemini web UI / side tab 路徑，適合人工貼上資料與讀回回覆。',
      '請回傳 raw response、重點摘要與缺資料；不要宣稱已改 repo、已發文、已改 Ads 或已完成外部系統動作。',
    ],
  };
  return map[target] || map.claude_code;
}
function getTaskText() {
  return el('taskInput')?.value.trim() || '';
}
function routeScore(text, needles) {
  return needles.reduce((score, needle) => score + (text.includes(needle) ? 1 : 0), 0);
}
function suggestRoleForTask(text) {
  const t = String(text || '').toLowerCase();
  const routes = [
    {
      role: 'A2',
      label: 'A2 Ads/SEO/WordPress Patrol',
      score: routeScore(t, ['seo', 'ads', 'ad ', 'google ads', 'meta', 'wordpress', 'wp', 'rank math', '品牌', '廣告', '網頁', '官網']),
    },
    {
      role: 'IOS-MOMENTUM',
      label: 'IOS-MOMENTUM 每日動能經理',
      score: routeScore(t, ['momentum', 'limit up', '漲停', '動能', '強勢', '成交量', 'top3', 'top 3', '股期', '開盤劇本']),
    },
    {
      role: 'IOS-KOL',
      label: 'IOS-KOL 網紅雷達經理',
      score: routeScore(t, ['kol', 'influencer', 'youtube', 'podcast', 'notebooklm', '網紅', '操作筆記', '逐字稿', '影片', '頻道']),
    },
    {
      role: 'IOS-FB',
      label: 'IOS-FB FB / 社群情報經理',
      score: routeScore(t, ['fb', 'facebook', 'social', '社群', '粉專', '貼文', '留言', 'fb radar']),
    },
    {
      role: 'IOS-ALPHA',
      label: 'IOS-ALPHA 阿爾法共振經理',
      score: routeScore(t, ['alpha', 'convergence', 'polymarket', 'reddit', 'rss', '共振', '阿爾法', '事件', '預測市場']),
    },
    {
      role: 'IOS-BLACKSWAN',
      label: 'IOS-BLACKSWAN 黑天鵝監控官',
      score: routeScore(t, ['black swan', 'tail risk', 'vix', 'hedge', '黑天鵝', '地緣', '油價', '避險', '崩盤', '戰爭']),
    },
    {
      role: 'IOS-INVENTORY',
      label: 'IOS-INVENTORY 庫存審查經理',
      score: routeScore(t, ['inventory', 'position', 'broker', 'holding', '實單', '庫存', '持股', '部位', '保證金', '風控']),
    },
    {
      role: 'IOS-MACRO',
      label: 'IOS-MACRO 總經大師',
      score: routeScore(t, ['macro', 'fred', 'bls', 'cpi', 'ppi', '美元', '利率', '總經', '景氣', 'regime', '殖利率']),
    },
    {
      role: 'IOS-CHIP',
      label: 'IOS-CHIP 籌碼經理',
      score: routeScore(t, ['chip', 't86', 'margin', '籌碼', '三大法人', '融資', '融券', '集保', '盤後1600', '16:00']),
    },
    {
      role: 'IOS-LEFT',
      label: 'IOS-LEFT 左側預期差經理',
      score: routeScore(t, ['left side', '預期差', '左側', '研究問題', '買前功課', '公開資訊']),
    },
    {
      role: 'IOS-RIGHT',
      label: 'IOS-RIGHT 右側交易經理',
      score: routeScore(t, ['right side', '右側', '交易劇本', 'shortlist', '突破', '追價', '執行']),
    },
    {
      role: 'IOS-EVIDENCE',
      label: 'IOS-EVIDENCE 研究證據經理',
      score: routeScore(t, ['evidence', 'source', 'research evidence', '證據', '來源', '推論', '缺資料', '合理推論', '已驗證事實']),
    },
    {
      role: 'IOS-SIM',
      label: 'IOS-SIM 模擬倉經理',
      score: routeScore(t, ['simulation', 'sim ledger', '模擬倉', '模擬單', 'ledger', 'roi', 'shioaji simulation']),
    },
    {
      role: 'IOS-FAMILY',
      label: 'IOS-FAMILY 家族基金經理',
      score: routeScore(t, ['family fund', '家族基金', '大盤', '資金池', '總帳戶', 'account level']),
    },
    {
      role: 'IOS-HEDGE',
      label: 'IOS-HEDGE 盤後對沖經理',
      score: routeScore(t, ['after hours', 'night session', '盤後', '夜盤', '對沖', '海外期貨', 'hedge playbook']),
    },
    {
      role: 'IOS-SURFACE',
      label: 'IOS-SURFACE 介面契約守門員',
      score: routeScore(t, ['surface', 'readability', 'format', 'markdown', '閱讀', '格式', '太刺眼', '顏色', '卡片', 'telegram格式', 'dashboard格式']),
    },
    {
      role: 'IOS-HYGIENE',
      label: 'IOS-HYGIENE 系統衛生官',
      score: routeScore(t, ['hygiene', 'cleanup', 'dirty', 'worktree', '清掃', '髒', '髒檔', '要不要留', '要不要丟', 'keep/drop', '定時掃']),
    },
    {
      role: 'B1',
      label: 'B1 Builder',
      score: routeScore(t, ['build', 'implement', 'fix', 'bug', '功能', '修', '接', '寫', '改', 'runtime', 'telegram', 'dashboard']),
    },
    {
      role: 'B2',
      label: 'B2 Reviewer',
      score: routeScore(t, ['review', 'check', 'error', 'freshness', '錯', '怪', '檢查', '資料流', '不一致', '驗證', '證據', '報告']),
    },
    {
      role: 'B3',
      label: 'B3 Archivist',
      score: routeScore(t, ['archive', 'handoff', 'resume', 'version', 'log', '紀錄', '交接', '版本', '存檔', 'task card', 'pitfalls']),
    },
    {
      role: 'B4',
      label: 'B4 System Patrol',
      score: routeScore(t, ['patrol', 'fit', '適合', '巡查', '暫停', '重構', '過度', '繼續', '系統', '方向', '還需要']),
    },
  ].sort((a, b) => b.score - a.score);
  if (!t.trim()) return { role: '', label: '請先輸入任務' };
  const best = routes[0];
  if (best.score <= 0) return { role: 'B4', label: 'B4 System Patrol' };
  return best;
}
async function hydrateRole(role) {
  if (!role || (cachedRecallPrompts[role] && cachedRoleModules[role])) return;
  setStatus('loading', `載入 ${role} 任務模組...`);
  const d = await chrome.storage.local.get(['githubRawBase','githubToken']);
  const base  = d.githubRawBase || DEFAULT_BASE;
  const token = d.githubToken  || '';
  if (!cachedModuleIndex) await loadModuleIndex(base, token);
  await loadRoleModule(role, base, token);
  await loadAgentRecall(role, base, token);
  setStatus('ok', `${role} 任務模組已載入`);
}
async function autoRouteTask() {
  const result = suggestRoleForTask(getTaskText());
  const status = el('taskRouteStatus');
  if (!result.role) {
    if (status) status.textContent = result.label;
    return;
  }
  const select = el('roleSelect');
  const exists = [...select.options].some(option => option.value === result.role && !option.disabled);
  if (!exists) {
    if (status) status.textContent = `${result.label} 尚未在 module index 中；請先重載 Extension 或檢查 task-modules。`;
    return;
  }
  select.value = result.role;
  await hydrateRole(result.role);
  updatePromptDisplay();
  chrome.storage.local.set({ lastRole: result.role });
  if (status) status.textContent = `已選 ${result.label}`;
}
function formatSourceLines(sources, base, limit = 40) {
  const list = (sources || []).slice(0, limit);
  const lines = list.map(item => {
    const status = item.load_mode === 'fallback_to_workbook_task_index'
      ? 'fallback'
      : item.exists === 'true' ? 'ok' : 'missing';
    const hash = item.source_sha256 ? ` sha256:${shortHash(item.source_sha256)}` : '';
    return `- [${status}] ${item.path} (${item.purpose || item.load_mode || 'source'}${hash})\n  ${rawUrl(base, item.path)}`;
  });
  if ((sources || []).length > limit) {
    lines.push(`- ... ${sources.length - limit} more sources in the module JSON`);
  }
  return lines.join('\n');
}
function renderFreshnessStatus(role, module) {
  const box = el('moduleFreshness');
  if (!box) return;
  box.className = 'module-freshness';
  if (!role || !module) {
    box.textContent = 'Markdown 同步尚未檢查';
    return;
  }
  const result = cachedFreshness[role];
  if (!result) {
    const hashable = (module.read_first || []).filter(sourceIsHashable).length;
    box.textContent = `Markdown 同步尚未檢查｜module: ${module.generated_at || '?'}｜可檢查 ${hashable} 個來源`;
    return;
  }
  if (result.status === 'checking') {
    box.classList.add('warn');
    box.textContent = `正在檢查 Markdown 同步… ${result.checked || 0}/${result.total || '?'}`;
    return;
  }
  if (result.status === 'ok') {
    box.classList.add('ok');
    box.textContent = `Markdown 已同步｜${result.checked}/${result.total} sources match module hashes`;
    return;
  }
  if (result.status === 'stale') {
    box.classList.add('warn');
    const names = result.stale.slice(0, 3).map(s => s.path).join('、');
    box.textContent = `Markdown 已變更｜${result.stale.length} 個來源和 module hash 不一致：${names}`;
    return;
  }
  box.classList.add('err');
  box.textContent = `Markdown 檢查失敗｜${result.error || 'unknown error'}`;
}
function renderModulePanel(role, module) {
  if (!role) {
    el('moduleTitle').textContent = '任務模組尚未載入';
    el('moduleMeta').innerHTML = '選擇角色後顯示必讀來源、技能組、影響範圍與輸出契約。';
    el('moduleChips').innerHTML = '';
    el('moduleSources').textContent = '—';
    el('moduleAffects').textContent = '—';
    renderFreshnessStatus(role, module);
    return;
  }
  if (!module) {
    el('moduleTitle').textContent = `${role} 任務模組未載入`;
    el('moduleMeta').innerHTML = '請按「重新抓取」或檢查 GitHub dynamic module 檔案。';
    el('moduleChips').innerHTML = '<span class="module-chip warn">missing module</span>';
    el('moduleSources').textContent = '—';
    el('moduleAffects').textContent = '—';
    renderFreshnessStatus(role, module);
    return;
  }
  el('moduleTitle').textContent = `${module.role_id}｜${module.department}｜${module.role_name}`;
  el('moduleMeta').innerHTML =
    `<strong>模擬：</strong>${escapeHtml(module.role_simulation)}<br>` +
    `<strong>輸出：</strong>${escapeHtml((module.output_contract || []).join(' / '))}`;
  const chips = [
    ...(module.runtime_targets || []).map(t => ({ text: t, warn: false })),
    { text: `risk:${module.risk_level || 'medium'}`, warn: module.risk_level === 'high' },
    { text: `src:${module.source_freshness?.hash_algorithm || 'sha256'}`, warn: false },
  ];
  el('moduleChips').innerHTML = chips.map(c => `<span class="module-chip${c.warn ? ' warn' : ''}">${escapeHtml(c.text)}</span>`).join('');
  el('moduleSources').innerHTML = (module.read_first || []).slice(0, 8).map(s => {
    const mark = s.load_mode === 'fallback_to_workbook_task_index' ? '↪' : s.exists === 'true' ? '✓' : '!';
    return `${mark} ${escapeHtml(s.path)}`;
  }).join('<br>') || '—';
  el('moduleAffects').innerHTML = (module.affects || []).map(a => `→ ${escapeHtml(a)}`).join('<br>') || '—';
  renderFreshnessStatus(role, module);
}
function buildModuleHandoff(role, module, recallText, parsed, runtime, base) {
  if (!role || !module) {
    return buildOverviewPrompt(parsed || { version: '?', phase: '?', activeTasks: [], blockers: [] }, cachedOverdue);
  }
  const lines = [];
  lines.push(`# MAPLAB ${module.role_id} Runtime Handoff`);
  lines.push('');
  lines.push(`runtime_target: ${normalizeRuntimeTarget(runtime)}`);
  lines.push(`runtime_target_label: ${runtimeTargetLabel(runtime)}`);
  lines.push(`module_id: ${module.module_id}`);
  lines.push(`canonical_repo: /Users/pagemacmini/maplab-ai-handbook`);
  lines.push(`github_module: ${rawUrl(base, `chrome-extension/task-modules/${role}.json`)}`);
  lines.push(`module_generated_at: ${module.generated_at || '?'}`);
  lines.push('');
  lines.push('## 0. 動態連結與 Markdown 同步規則');
  lines.push('');
  lines.push('- 這份 handoff 是 routing envelope，不是來源內容本體。');
  lines.push('- 請讀下面列出的 GitHub raw Markdown/JSON 連結，以取得最新事實與角色規則。');
  lines.push('- 如果側邊欄顯示 Markdown 已變更，請先請 A1 跑 `python3 tools/ai_workbook/build_extension_task_modules.py` 重建 module，再接手高風險任務。');
  const freshness = cachedFreshness[role];
  if (freshness) {
    lines.push(`- module_source_state: ${freshness.status}${freshness.stale?.length ? ` (${freshness.stale.length} stale)` : ''}`);
  } else {
    lines.push('- module_source_state: not_checked_in_side_panel');
  }
  lines.push('');
  lines.push('## 1. 身份與任務邊界');
  lines.push('');
  lines.push(`你是 ${module.role_id} ${module.department}（${module.role_name}）。`);
  lines.push(module.role_simulation);
  const requestedTask = getTaskText();
  if (requestedTask) {
    lines.push('');
    lines.push('## 1.1 本次召喚任務');
    lines.push('');
    lines.push(requestedTask);
    lines.push('');
    lines.push('- 若本次任務與本角色不吻合，先指出應轉交的角色，再繼續可安全完成的部分。');
  }
  lines.push('');
  runtimeInstruction(runtime).forEach(line => lines.push(`- ${line}`));
  lines.push('');
  lines.push('## 2. 必讀來源');
  lines.push('');
  lines.push(formatSourceLines(module.read_first, base));
  if ((module.restricted_sources || []).length > 0) {
    lines.push('');
    lines.push('## 3. Restricted References');
    lines.push('');
    lines.push('以下是受限來源，只能由 A1/Owner 授權後查閱，不要貼進公開模型 prompt：');
    lines.push(formatSourceLines(module.restricted_sources, base, 20));
  }
  lines.push('');
  lines.push('## 4. 技能組');
  lines.push('');
  (module.skill_group || []).forEach(skill => lines.push(`- ${skill}`));
  lines.push('');
  lines.push('## 5. 任務類型');
  lines.push('');
  (module.task_types || []).forEach(task => lines.push(`- ${task}`));
  lines.push('');
  lines.push('## 6. 指向性影響關係');
  lines.push('');
  (module.affects || []).forEach(target => lines.push(`- 會影響：${target}`));
  lines.push('');
  lines.push('## 7. 輸出契約');
  lines.push('');
  (module.output_contract || []).forEach(output => lines.push(`- ${output}`));
  lines.push('');
  lines.push(`writeback_default: ${module.writeback?.default_review_bundle || 'workbook/reviews/JOB-xxx/'}`);
  lines.push(`relation_graph: ${module.writeback?.task_module_graph || 'workbook/task_modules/role_module_relation_graph.json'}`);
  lines.push('');
  lines.push('## 8. 禁止事項');
  lines.push('');
  (module.forbidden_actions || []).forEach(rule => lines.push(`- ${rule}`));
  lines.push('');
  lines.push('## 9. 即時系統快照');
  lines.push('');
  if (parsed) {
    lines.push(`version: ${parsed.version}`);
    lines.push(`phase: ${parsed.phase}`);
    const roleTasks = parsed.activeTasks.filter(t => t.agent.includes(module.role_id.replace('A', '')) || t.agent.includes(module.role_id));
    if (roleTasks.length > 0) {
      lines.push('active_or_related_tasks:');
      roleTasks.forEach(t => lines.push(`- ${t.id} | ${t.name} | ${t.status}`));
    }
    if (parsed.blockers.length > 0) {
      lines.push('top_blockers:');
      parsed.blockers.slice(0, 5).forEach(b => lines.push(`- ${b}`));
    }
  }
  lines.push('');
  lines.push('## 10. 角色 Recall 摘要');
  lines.push('');
  lines.push(truncate(recallText || `// ${role} recall unavailable`, 6000));
  lines.push('');
  lines.push('## 11. 開始前回覆格式');
  lines.push('');
  lines.push('請先回覆：');
  lines.push('1. 我是什麼角色。');
  lines.push('2. 我會先讀哪些來源。');
  lines.push('3. 這次產出會影響哪些角色/檔案/系統。');
  lines.push('4. 產出會寫到哪裡。');
  lines.push('5. 有哪些高風險動作需要 Owner/A1 批准。');
  return lines.join('\n');
}

// === Inject to Claude tab (Task A) ===
async function injectToClaudeTab() {
  const text = el('promptText').value;
  if (!text || text.startsWith('//')) return;
  const btn = el('injectBtn');

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url?.includes('claude.ai')) {
    btn.textContent = '❌ 請先切到 claude.ai tab';
    btn.style.background = '#e85538'; btn.style.color = '#fff';
    setTimeout(() => { btn.textContent = '⚡ Legacy: 注入 Claude tab'; btn.style.background = ''; btn.style.color = ''; }, 2500);
    return;
  }

  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (promptText) => {
        const editor = document.querySelector('div[contenteditable="true"].ProseMirror') ||
                       document.querySelector('div[contenteditable="true"]');
        if (!editor) return false;
        editor.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, promptText);
        return true;
      },
      args: [text]
    });
    const ok = results?.[0]?.result;
    if (ok) {
      btn.textContent = '✅ 已注入！';
      btn.style.background = '#38e87a'; btn.style.color = '#0a1a10';
    } else {
      btn.textContent = '❌ 找不到輸入框';
      btn.style.background = '#e85538'; btn.style.color = '#fff';
    }
  } catch(e) {
    btn.textContent = '❌ ' + e.message.substring(0, 35);
    btn.style.background = '#e85538'; btn.style.color = '#fff';
  }
  setTimeout(() => { btn.textContent = '⚡ Legacy: 注入 Claude tab'; btn.style.background = ''; btn.style.color = ''; }, 3000);
}

// === Display ===
function updatePromptDisplay() {
  const role = el('roleSelect').value;
  const runtime = normalizeRuntimeTarget(el('runtimeSelect')?.value || 'claude_code');
  if (el('runtimeSelect') && el('runtimeSelect').value !== runtime) el('runtimeSelect').value = runtime;
  const base = el('githubRawBase')?.value.trim() || DEFAULT_BASE;
  if (!role) {
    el('promptBoxLabel').textContent = '總覽模式';
    el('promptLabel').textContent = '⚡ 系統總覽';
    renderModulePanel('', null);
    if (cachedParsed) {
      const prompt = buildOverviewPrompt(cachedParsed, cachedOverdue);
      el('promptText').value = prompt;
      updateCharCount(prompt);
    }
    el('roleStatus').innerHTML = '';
  } else {
    const module = cachedRoleModules[role];
    el('promptBoxLabel').textContent = `${role} → ${runtimeTargetLabel(runtime)} handoff`;
    el('promptLabel').textContent = `⚡ ${role} Runtime Handoff Prompt`;
    renderModulePanel(role, module);

    let prompt = '';
    if (module) {
      prompt = buildModuleHandoff(role, module, cachedRecallPrompts[role], cachedParsed, runtime, base);
      el('promptText').value = prompt;
      updateCharCount(prompt);
    } else {
      el('promptText').value = `// ${role} 的任務模組尚未載入或不存在`;
      updateCharCount('');
    }

    if (cachedParsed) {
      const tasks = cachedParsed.activeTasks.filter(t => t.agent.includes(role.replace('A','')) && !t.status.includes('✅'));
      if (tasks.length > 0) {
        el('roleStatus').innerHTML = tasks.map(t => {
          const cls = (t.status.includes('🔴') || t.status.includes('CRITICAL')) ? 'critical' : t.status.includes('🔄') ? 'active' : 'pending';
          return `<span class="${cls}">${t.status.substring(0,2)}</span> ${t.id} ${t.name.substring(0,35)}`;
        }).join('<br>');
      } else {
        el('roleStatus').innerHTML = '<span class="new">無進行中任務</span>';
      }
    }
  }
}

// === Fetch from Bot (Method 2) ===
async function fetchFromBot() {
  const btn = el('botFetchBtn');
  btn.textContent = '⏳ 抓取中…';
  btn.disabled = true;
  try {
    const resp = await fetch('http://127.0.0.1:9876/clip', { cache: 'no-store' });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    if (!data.text) throw new Error('剪貼板是空的');
    el('promptText').value = data.text;
    updateCharCount(data.text);
    btn.textContent = `✅ 已抓取（${data.ts || '?'}）`;
    btn.style.background = '#1a3a1a'; btn.style.borderColor = '#38e87a'; btn.style.color = '#38e87a';
  } catch(e) {
    btn.textContent = '❌ ' + e.message.substring(0, 40);
    btn.style.background = '#3a1a1a'; btn.style.borderColor = '#e85538'; btn.style.color = '#e85538';
  }
  btn.disabled = false;
  setTimeout(() => {
    btn.textContent = '📋 從 Bot 抓取';
    btn.style.background = ''; btn.style.borderColor = ''; btn.style.color = '';
  }, 3500);
}

// === Reload Extension ===
function reloadExtension() {
  chrome.runtime.reload();
}

// === Copy ===
function copyPrompt() {
  const text = el('promptText').value;
  if (!text || text.startsWith('//')) return;
  navigator.clipboard.writeText(text).then(() => {
    const btn = el('copyBtn');
    const role = el('roleSelect').value;
    btn.textContent = role ? `✅ ${role} prompt 已複製！` : '✅ 已複製！';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = '📋 複製目前文字';
      btn.classList.remove('copied');
    }, 2500);
  }).catch(() => el('promptText').select());
}
function copyHandoff() {
  const role = el('roleSelect').value;
  const module = cachedRoleModules[role];
  const runtime = normalizeRuntimeTarget(el('runtimeSelect')?.value || 'claude_code');
  const base = el('githubRawBase')?.value.trim() || DEFAULT_BASE;
  const text = buildModuleHandoff(role, module, cachedRecallPrompts[role], cachedParsed, runtime, base);
  if (!text || text.startsWith('//')) return;
  navigator.clipboard.writeText(text).then(() => {
    el('promptText').value = text;
    updateCharCount(text);
    const btn = el('handoffBtn');
    btn.textContent = `✅ ${role || '總覽'} → ${runtime} 已複製`;
    setTimeout(() => { btn.textContent = '📦 複製任務模組 Handoff'; }, 2500);
  }).catch(() => el('promptText').select());
}

// === Markdown/source freshness ===
async function checkSelectedModuleFreshness() {
  const role = el('roleSelect').value;
  if (!role) return;
  const module = cachedRoleModules[role];
  if (!module) return;
  const d = await chrome.storage.local.get(['githubRawBase','githubToken']);
  const base  = d.githubRawBase || DEFAULT_BASE;
  const token = d.githubToken  || '';
  const sources = [
    ...(module.read_first || []),
    ...(module.restricted_sources || []).filter(item => item.load_mode !== 'a1_only'),
  ].filter(sourceIsHashable);
  const btn = el('syncBtn');
  cachedFreshness[role] = { status: 'checking', checked: 0, total: sources.length };
  renderFreshnessStatus(role, module);
  if (btn) {
    btn.disabled = true;
    btn.textContent = '檢查中…';
  }
  const stale = [];
  const errors = [];
  try {
    for (const item of sources) {
      try {
        const current = await fetchFile(base, item.path, token);
        const currentHash = await sha256Hex(current);
        if (currentHash !== item.source_sha256) {
          stale.push({
            path: item.path,
            module_sha256: item.source_sha256,
            current_sha256: currentHash,
          });
        }
      } catch(e) {
        errors.push({ path: item.path, error: e.message });
      }
      cachedFreshness[role] = { status: 'checking', checked: cachedFreshness[role].checked + 1, total: sources.length };
      renderFreshnessStatus(role, module);
    }
    cachedFreshness[role] = {
      status: stale.length ? 'stale' : 'ok',
      checked: sources.length,
      total: sources.length,
      stale,
      errors,
      checked_at: new Date().toISOString(),
    };
  } catch(e) {
    cachedFreshness[role] = { status: 'error', error: e.message, checked: 0, total: sources.length };
  }
  renderFreshnessStatus(role, module);
  updatePromptDisplay();
  if (btn) {
    btn.disabled = false;
    btn.textContent = '檢查 MD 同步';
  }
}

// === Auto-save ===
async function autoSave() {
  const base  = el('githubRawBase').value.trim() || DEFAULT_BASE;
  const token = el('githubToken').value.trim();
  await chrome.storage.local.set({ githubRawBase: base, githubToken: token });
  const s = el('saveStatus');
  s.textContent = '✓ 已記住'; s.classList.add('show');
  setTimeout(() => s.classList.remove('show'), 2000);
}

// === Main loader ===
async function loadAll() {
  cachedRecallPrompts = {}; // v5.3: 每次重新抓取都清除 recall 快取，確保拿到最新版
  cachedRoleModules = {};
  cachedFreshness = {};
  setStatus('loading', '讀取中...');
  el('promptText').value = '';
  const data  = await chrome.storage.local.get(['githubRawBase','githubToken','lastRole','lastRuntime','lastTask']);
  const base  = data.githubRawBase || DEFAULT_BASE;
  const token = data.githubToken  || '';

  if (data.lastRuntime && el('runtimeSelect')) el('runtimeSelect').value = normalizeRuntimeTarget(data.lastRuntime);
  if (data.lastTask && el('taskInput')) el('taskInput').value = data.lastTask;

  try {
    const [md, commits] = await Promise.all([
      fetchFile(base, 'CURRENT_STATUS.md', token),
      fetchCommits(token),
      loadModuleIndex(base, token)
    ]);

    cachedParsed  = parseStatus(md);
    cachedCommits = commits;
    cachedOverdue = detectOverdueTasks(commits, cachedParsed.activeTasks);
    populateRoleSelectFromIndex(data.lastRole || el('roleSelect').value);

    // If a role is pre-selected, lazy-load its recall file now
    const selectedRole = el('roleSelect').value;
    if (selectedRole) {
      await loadRoleModule(selectedRole, base, token);
      await loadAgentRecall(selectedRole, base, token);
    }

    updatePromptDisplay();

    el('overdueCount').textContent = cachedOverdue.length > 0 ? `⏰ ${cachedOverdue.length}` : '';
    const vb = document.getElementById('versionBadge');
    if (vb) vb.textContent = formatVersion(chrome.runtime.getManifest?.().version || '5.6.1');
    const moduleCount = cachedModuleIndex?.modules?.length || 0;
    setStatus('ok', `${formatVersion(cachedParsed.version)} ｜ 模組 ${moduleCount} 已載入`);
  } catch(e) {
    setStatus('err', '載入失敗：' + e.message);
    el('promptText').value = '// 錯誤：' + e.message;
  }
}

// === Init ===
document.addEventListener('DOMContentLoaded', async () => {
  const data = await chrome.storage.local.get(['githubRawBase','githubToken','lastRuntime','lastTask']);
  el('githubRawBase').value = data.githubRawBase || DEFAULT_BASE;
  el('githubToken').value   = data.githubToken   || '';
  if (data.lastRuntime && el('runtimeSelect')) el('runtimeSelect').value = normalizeRuntimeTarget(data.lastRuntime);
  if (data.lastTask && el('taskInput')) el('taskInput').value = data.lastTask;

  if (data.githubToken) {
    el('saveStatus').textContent = '✓ Token 已記住';
    el('saveStatus').classList.add('show');
    setTimeout(() => el('saveStatus').classList.remove('show'), 3000);
  }

  el('githubRawBase').addEventListener('blur', autoSave);
  el('githubToken').addEventListener('blur', autoSave);
  el('githubRawBase').addEventListener('keydown', e => { if(e.key==='Enter') { autoSave(); loadAll(); } });
  el('githubToken').addEventListener('keydown',   e => { if(e.key==='Enter') { autoSave(); loadAll(); } });
  el('taskInput')?.addEventListener('input', () => {
    const task = getTaskText();
    chrome.storage.local.set({ lastTask: task });
    updatePromptDisplay();
    const result = suggestRoleForTask(task);
    const status = el('taskRouteStatus');
    if (status) status.textContent = result.role ? `建議：${result.label}` : result.label;
  });
  el('routeBtn')?.addEventListener('click', autoRouteTask);

  el('roleSelect').addEventListener('change', async () => {
    const role = el('roleSelect').value;
    await hydrateRole(role);
    updatePromptDisplay();
    chrome.storage.local.set({ lastRole: role });
  });
  el('runtimeSelect').addEventListener('change', () => {
    updatePromptDisplay();
    chrome.storage.local.set({ lastRuntime: normalizeRuntimeTarget(el('runtimeSelect').value) });
  });
  el('handoffBtn')?.addEventListener('click', copyHandoff);
  el('copyBtn')?.addEventListener('click', copyPrompt);
  el('injectBtn')?.addEventListener('click', injectToClaudeTab);
  el('syncBtn')?.addEventListener('click', checkSelectedModuleFreshness);
  el('reloadBtn')?.addEventListener('click', reloadExtension);
  el('refreshBtn')?.addEventListener('click', loadAll);

  await loadAll();
});
