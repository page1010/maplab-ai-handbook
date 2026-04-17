// MAPLAB Agent Commander v5.3 — popup.js
// 角色選擇 + 專屬召喚 prompt（精簡版，無 commit history 面板）
const DEFAULT_BASE = 'https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main';
const GITHUB_API   = 'https://api.github.com/repos/page1010/maplab-ai-handbook';
const COMMIT_COUNT = 8;
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

// === GitHub fetch ===
function authHeaders(token) {
  const h = { 'Accept': 'application/vnd.github.v3+json' };
  if (token) h['Authorization'] = `token ${token}`;
  return h;
}
async function fetchCommits(token) {
  try {
    const url = `${GITHUB_API}/commits?per_page=${COMMIT_COUNT}&t=${Date.now()}`;
    const resp = await fetch(url, { headers: authHeaders(token) });
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
    const apiUrl = `${GITHUB_API}/contents/${path}?t=${Date.now()}`;
    const resp = await fetch(apiUrl, { headers: authHeaders(token) });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const json = await resp.json();
    return atob(json.content.replace(/\n/g, ''));
  }
  const url = base.replace(/\/$/, '') + '/' + path + '?t=' + Date.now();
  const resp = await fetch(url);
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  return resp.text();
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
    cachedRecallPrompts[role] = `// ${role} recall 載入失敗: ${e.message}`;
  }
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
  lines.push(`系統 ${parsed.version} ｜ ${parsed.phase}`);
  lines.push('');
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

// === Inject to Claude tab (Task A) ===
async function injectToClaudeTab() {
  const text = el('promptText').value;
  if (!text || text.startsWith('//')) return;
  const btn = el('injectBtn');

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url?.includes('claude.ai')) {
    btn.textContent = '❌ 請先切到 claude.ai tab';
    btn.style.background = '#e85538'; btn.style.color = '#fff';
    setTimeout(() => { btn.textContent = '⚡ 注入到 Claude tab'; btn.style.background = ''; btn.style.color = ''; }, 2500);
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
  setTimeout(() => { btn.textContent = '⚡ 注入到 Claude tab'; btn.style.background = ''; btn.style.color = ''; }, 3000);
}

// === Display ===
function updatePromptDisplay() {
  const role = el('roleSelect').value;
  if (!role) {
    el('promptBoxLabel').textContent = '總覽模式';
    el('promptLabel').textContent = '⚡ 系統總覽';
    if (cachedParsed) {
      const prompt = buildOverviewPrompt(cachedParsed, cachedOverdue);
      el('promptText').value = prompt;
      updateCharCount(prompt);
    }
    el('roleStatus').innerHTML = '';
  } else {
    el('promptBoxLabel').textContent = `${role} 召喚 prompt`;
    el('promptLabel').textContent = `⚡ ${role} Startup Prompt`;

    let prompt = '';
    if (cachedRecallPrompts[role]) {
      prompt = cachedRecallPrompts[role];
      // Task B: append live system snapshot
      if (cachedParsed) {
        prompt += buildSystemSnapshot(cachedParsed);
      }
      el('promptText').value = prompt;
      updateCharCount(prompt);
    } else {
      el('promptText').value = `// ${role} 的召喚 prompt 尚未載入或不存在`;
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
      btn.textContent = '📋 複製 Startup Prompt';
      btn.classList.remove('copied');
    }, 2500);
  }).catch(() => el('promptText').select());
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
  setStatus('loading', '讀取中...');
  el('promptText').value = '';
  const data  = await chrome.storage.local.get(['githubRawBase','githubToken','lastRole']);
  const base  = data.githubRawBase || DEFAULT_BASE;
  const token = data.githubToken  || '';

  if (data.lastRole) el('roleSelect').value = data.lastRole;

  try {
    const [md, commits] = await Promise.all([
      fetchFile(base, 'CURRENT_STATUS.md', token),
      fetchCommits(token)
    ]);

    cachedParsed  = parseStatus(md);
    cachedCommits = commits;
    cachedOverdue = detectOverdueTasks(commits, cachedParsed.activeTasks);

    // If a role is pre-selected, lazy-load its recall file now
    const selectedRole = el('roleSelect').value;
    if (selectedRole) {
      await loadAgentRecall(selectedRole, base, token);
    }

    updatePromptDisplay();

    el('overdueCount').textContent = cachedOverdue.length > 0 ? `⏰ ${cachedOverdue.length}` : '';
    const vb = document.getElementById('versionBadge');
    if (vb && cachedParsed.version) vb.textContent = `v${cachedParsed.version}`;
    setStatus('ok', `v${cachedParsed.version} ｜ 系統已載入`);
  } catch(e) {
    setStatus('err', '載入失敗：' + e.message);
    el('promptText').value = '// 錯誤：' + e.message;
  }
}

// === Init ===
document.addEventListener('DOMContentLoaded', async () => {
  const data = await chrome.storage.local.get(['githubRawBase','githubToken']);
  el('githubRawBase').value = data.githubRawBase || DEFAULT_BASE;
  el('githubToken').value   = data.githubToken   || '';

  if (data.githubToken) {
    el('saveStatus').textContent = '✓ Token 已記住';
    el('saveStatus').classList.add('show');
    setTimeout(() => el('saveStatus').classList.remove('show'), 3000);
  }

  el('githubRawBase').addEventListener('blur', autoSave);
  el('githubToken').addEventListener('blur', autoSave);
  el('githubRawBase').addEventListener('keydown', e => { if(e.key==='Enter') { autoSave(); loadAll(); } });
  el('githubToken').addEventListener('keydown',   e => { if(e.key==='Enter') { autoSave(); loadAll(); } });

  el('roleSelect').addEventListener('change', async () => {
    const role = el('roleSelect').value;
    if (role && !cachedRecallPrompts[role]) {
      setStatus('loading', `載入 ${role} recall...`);
      const d = await chrome.storage.local.get(['githubRawBase','githubToken']);
      const base  = d.githubRawBase || DEFAULT_BASE;
      const token = d.githubToken  || '';
      await loadAgentRecall(role, base, token);
      setStatus('ok', `${role} recall 已載入`);
    }
    updatePromptDisplay();
    chrome.storage.local.set({ lastRole: role });
  });

  await loadAll();
});
