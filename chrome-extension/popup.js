// MAPLAB Agent Commander v4.3 — popup.js
// 角色選擇 + 專屬召喚 prompt + commit history
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
let cachedCpInfo = null;
let cachedOverdue = [];
let cachedRecallPrompts = {};  // { 'A2': '...prompt...', 'A3': '...' }

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
  const url = base.replace(/\/$/, '') + '/' + path + '?t=' + Date.now();
  const resp = await fetch(url, { headers: authHeaders(token) });
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

// === Parse AGENT_RECALL_PROMPTS.md ===
function parseRecallPrompts(md) {
  const prompts = {};
  const regex = /## (A\d)[^\n]*\n[\s\S]*?```\n([\s\S]*?)```/g;
  let match;
  while ((match = regex.exec(md)) !== null) {
    prompts[match[1]] = match[2].trim();
  }
  return prompts;
}

// === Checkpoint / Overdue detection ===
function detectCheckpoints(commits) {
  const keywords = ['checkpoint','progress','handoff','done:','feat:','fix:','data(','chore('];
  const lastCheckpoint = commits.find(c =>
    keywords.some(k => c.message.toLowerCase().includes(k))
  );
  let hoursSince = null;
  if (lastCheckpoint) {
    const ms = Date.now() - new Date(lastCheckpoint.date).getTime();
    hoursSince = Math.round(ms / 3600000);
  }
  return { lastCheckpoint, hoursSince };
}
function detectOverdueTasks(commits, activeTasks) {
  const warnings = [];
  const OVERDUE_HOURS = 48;
  const taskLastSeen = {};
  for (const c of commits) {
    for (const t of activeTasks) {
      if (t.id && c.message.includes(t.id) && !taskLastSeen[t.id])
        taskLastSeen[t.id] = c.date;
    }
  }
  for (const task of activeTasks) {
    if (!task.status.includes('🔄')) continue;
    if (taskLastSeen[task.id]) {
      const hours = Math.round((Date.now() - new Date(taskLastSeen[task.id]).getTime()) / 3600000);
      if (hours > OVERDUE_HOURS)
        warnings.push(`${task.id} 超過 ${hours}h 無 commit（${task.name.substring(0,30)}）`);
    } else {
      warnings.push(`${task.id} 在最近 ${COMMIT_COUNT} 筆 commit 無紀錄`);
    }
  }
  return warnings;
}

// === Prompt builders ===
function buildOverviewPrompt(parsed, commits, cpInfo, overdueWarnings) {
  const lines = [];
  lines.push(`系統 ${parsed.version} ｜ ${parsed.phase}`);
  lines.push('');
  if (commits.length > 0) {
    lines.push('【最近動態】');
    commits.slice(0,4).forEach(c => {
      const d = new Date(c.date);
      const tag = `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
      lines.push(`${tag} ${c.sha} — ${c.message.substring(0,60)}`);
    });
    lines.push('');
  }
  if (cpInfo.lastCheckpoint) {
    lines.push(`【上次 checkpoint】${cpInfo.hoursSince}h 前 ｜ ${cpInfo.lastCheckpoint.message.substring(0,60)}`);
  } else {
    lines.push('【上次 checkpoint】最近 commit 無 checkpoint 紀錄 ⚠️');
  }
  lines.push('');
  const inProgress = parsed.activeTasks.filter(t => t.status.includes('🔄'));
  const available  = parsed.activeTasks.filter(t => t.status.includes('🔲'));
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

function buildRolePrompt(role, recallPrompt) {
  // 角色專屬 prompt，不注入 commit history（commit history 在 Extension 面板已可見）
  return recallPrompt;
}

// === Render ===
function renderCommits(commits, cpInfo) {
  const container = el('commitList');
  if (!commits.length) {
    container.innerHTML = '<div class="commit-placeholder">無法抓取 commit</div>';
    return;
  }
  container.innerHTML = commits.map(c => {
    const isCP = cpInfo.lastCheckpoint && cpInfo.lastCheckpoint.sha === c.sha;
    const d = new Date(c.date);
    const timeStr = `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
    return `<div class="commit-row ${isCP ? 'is-checkpoint' : ''}">
      <span class="commit-sha">${c.sha}</span>
      <span class="commit-time">${timeStr}</span>
      <span class="commit-msg">${c.message.substring(0,55).replace(/&/g,'&amp;').replace(/</g,'&lt;')}</span>
      ${isCP ? '<span class="cp-badge">CP</span>' : ''}
    </div>`;
  }).join('');
}

function updatePromptDisplay() {
  const role = el('roleSelect').value;
  if (!role) {
    // 總覽模式
    el('promptBoxLabel').textContent = '總覽模式';
    el('promptLabel').textContent = '⚡ 系統總覽';
    if (cachedParsed) {
      const prompt = buildOverviewPrompt(cachedParsed, cachedCommits, cachedCpInfo, cachedOverdue);
      el('promptText').value = prompt;
      updateCharCount(prompt);
    }
    el('roleStatus').innerHTML = '';
  } else {
    // 角色模式
    const roleNames = {
      A2:'搜尋流量作戰部', A3:'社群與廣告成長部', A4:'影像資產整理部',
      A5:'報價與提案引擎部', A6:'業務快反應部隊', A7:'客服與對話轉單部', A8:'多媒體影音製作部'
    };
    el('promptBoxLabel').textContent = `${role} 召喚 prompt`;
    el('promptLabel').textContent = `⚡ ${role} Startup Prompt`;

    if (cachedRecallPrompts[role]) {
      const prompt = buildRolePrompt(role, cachedRecallPrompts[role]);
      el('promptText').value = prompt;
      updateCharCount(prompt);
    } else {
      el('promptText').value = `// ${role} 的召喚 prompt 尚未載入或不存在`;
      updateCharCount('');
    }

    // 顯示該角色的相關任務
    if (cachedParsed) {
      const tasks = cachedParsed.activeTasks.filter(t => t.agent.includes(role.replace('A','')));
      if (tasks.length > 0) {
        el('roleStatus').innerHTML = tasks.map(t =>
          `<span class="${t.status.includes('🔄') ? 'active' : 'pending'}">${t.status.substring(0,2)}</span> ${t.id} ${t.name.substring(0,30)}`
        ).join('<br>');
      } else {
        el('roleStatus').innerHTML = '<span class="new">無進行中任務</span>';
      }
    }
  }
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

// === Save & Reload ===
async function saveAndReload() {
  const base  = el('githubRawBase').value.trim() || DEFAULT_BASE;
  const token = el('githubToken').value.trim();
  await chrome.storage.local.set({ githubRawBase: base, githubToken: token });
  const s = el('saveStatus');
  s.textContent = '已儲存'; s.classList.add('show');
  setTimeout(() => s.classList.remove('show'), 1500);
  await loadAll();
}

// === Main loader ===
async function loadAll() {
  setStatus('loading', '讀取中...');
  el('promptText').value = '';
  el('commitList').innerHTML = '<div class="commit-placeholder">載入中...</div>';
  const data  = await chrome.storage.local.get(['githubRawBase','githubToken','lastRole']);
  const base  = data.githubRawBase || DEFAULT_BASE;
  const token = data.githubToken  || '';

  // 恢復上次選的角色
  if (data.lastRole) el('roleSelect').value = data.lastRole;

  try {
    const [md, recallMd, commits] = await Promise.all([
      fetchFile(base, 'CURRENT_STATUS.md', token),
      fetchFile(base, 'AGENT_RECALL_PROMPTS.md', token).catch(() => ''),
      fetchCommits(token)
    ]);

    cachedParsed  = parseStatus(md);
    cachedCommits = commits;
    cachedCpInfo  = detectCheckpoints(commits);
    cachedOverdue = detectOverdueTasks(commits, cachedParsed.activeTasks);
    cachedRecallPrompts = recallMd ? parseRecallPrompts(recallMd) : {};

    renderCommits(commits, cachedCpInfo);
    updatePromptDisplay();

    el('overdueCount').textContent = cachedOverdue.length > 0 ? `⏰ ${cachedOverdue.length}` : '';
    const cpMsg = cachedCpInfo.hoursSince !== null ? `最後 CP ${cachedCpInfo.hoursSince}h 前` : '無 CP';
    setStatus(cachedCpInfo.hoursSince === null || cachedCpInfo.hoursSince > 24 ? 'loading' : 'ok',
      `v${cachedParsed.version} ｜ ${cpMsg} ｜ ${Object.keys(cachedRecallPrompts).length} 角色已載入`);
  } catch(e) {
    setStatus('err', '載入失敗：' + e.message);
    el('promptText').value = '// 錯誤：' + e.message;
  }
}

// === Auto-save token/URL on blur ===
async function autoSave() {
  const base  = el('githubRawBase').value.trim() || DEFAULT_BASE;
  const token = el('githubToken').value.trim();
  await chrome.storage.local.set({ githubRawBase: base, githubToken: token });
  const s = el('saveStatus');
  s.textContent = '✓ 已記住'; s.classList.add('show');
  setTimeout(() => s.classList.remove('show'), 2000);
}

// === Init ===
document.addEventListener('DOMContentLoaded', async () => {
  const data = await chrome.storage.local.get(['githubRawBase','githubToken']);
  el('githubRawBase').value = data.githubRawBase || DEFAULT_BASE;
  el('githubToken').value   = data.githubToken   || '';

  // 顯示 token 已記住狀態
  if (data.githubToken) {
    el('saveStatus').textContent = '✓ Token 已記住';
    el('saveStatus').classList.add('show');
    setTimeout(() => el('saveStatus').classList.remove('show'), 3000);
  }

  // 自動儲存：失焦就存，不需要按按鈕
  el('githubRawBase').addEventListener('blur', autoSave);
  el('githubToken').addEventListener('blur', autoSave);
  // Enter 也可以觸發重新抓取
  el('githubRawBase').addEventListener('keydown', e => { if(e.key==='Enter') { autoSave(); loadAll(); } });
  el('githubToken').addEventListener('keydown',   e => { if(e.key==='Enter') { autoSave(); loadAll(); } });

  // 角色切換事件
  el('roleSelect').addEventListener('change', () => {
    updatePromptDisplay();
    chrome.storage.local.set({ lastRole: el('roleSelect').value });
  });

  await loadAll();
});
