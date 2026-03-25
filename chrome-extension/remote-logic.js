// MAPLAB Agent Commander v3.0 — popup.js
const DEFAULT_BASE = 'https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main';
const GITHUB_API   = 'https://api.github.com/repos/page1010/maplab-ai-handbook';
const COMMIT_COUNT = 8;
const el = id => document.getElementById(id);

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
async function fetchCurrentStatus(base, token) {
  const url = base.replace(/\/$/, '') + '/CURRENT_STATUS.md?t=' + Date.now();
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  return resp.text();
}
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
function buildStartupPrompt(parsed, commits, cpInfo, overdueWarnings) {
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
    inProgress.slice(0,3).forEach(t => lines.push(`🔄 ${t.id} (${t.agent}) — ${t.name.substring(0,40)}`));
    lines.push('');
  }
  if (available.length > 0) {
    lines.push('【可認領】');
    available.slice(0,2).forEach(t => lines.push(`🔲 ${t.id} — ${t.name.substring(0,40)}`));
    lines.push('');
  }
  if (parsed.blockers.length > 0) {
    lines.push('【Blockers】');
    parsed.blockers.slice(0,2).forEach(b => lines.push(`⛔ ${b}`));
    lines.push('');
  }
  if (overdueWarnings.length > 0) {
    lines.push('【巡查警示】');
    overdueWarnings.forEach(w => lines.push(`⏰ ${w}`));
    lines.push('');
  }
  lines.push('開工步驟：');
  lines.push('1. 讀 CURRENT_STATUS.md 確認任務');
  lines.push('2. 若上次無 checkpoint → 先補寫再繼續');
  lines.push('3. 輸出 Startup Check（Skills loaded 不能空）');
  lines.push('必拿：skills/task-progress-guide.md');
  return lines.join('\n');
}
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
function copyPrompt() {
  const text = el('promptText').value;
  if (!text || text.startsWith('//')) return;
  navigator.clipboard.writeText(text).then(() => {
    const btn = el('copyBtn');
    btn.textContent = '✅ 已複製！';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = '📋 複製 Startup Prompt';
      btn.classList.remove('copied');
    }, 2500);
  }).catch(() => el('promptText').select());
}
async function saveAndReload() {
  const base  = el('githubRawBase').value.trim() || DEFAULT_BASE;
  const token = el('githubToken').value.trim();
  await chrome.storage.local.set({ githubRawBase: base, githubToken: token });
  const s = el('saveStatus');
  s.textContent = '已儲存'; s.classList.add('show');
  setTimeout(() => s.classList.remove('show'), 1500);
  await loadAll();
}
async function loadAll() {
  setStatus('loading', '讀取中...');
  el('promptText').value = '';
  el('commitList').innerHTML = '<div class="commit-placeholder">載入中...</div>';
  const data  = await chrome.storage.local.get(['githubRawBase','githubToken']);
  const base  = data.githubRawBase || DEFAULT_BASE;
  const token = data.githubToken  || '';
  try {
    const [md, commits] = await Promise.all([
      fetchCurrentStatus(base, token),
      fetchCommits(token)
    ]);
    const parsed  = parseStatus(md);
    const cpInfo  = detectCheckpoints(commits);
    const overdue = detectOverdueTasks(commits, parsed.activeTasks);
    const prompt  = buildStartupPrompt(parsed, commits, cpInfo, overdue);
    el('promptText').value = prompt;
    updateCharCount(prompt);
    renderCommits(commits, cpInfo);
    el('overdueCount').textContent = overdue.length > 0 ? `⏰ ${overdue.length}` : '';
    const cpMsg = cpInfo.hoursSince !== null ? `最後 checkpoint ${cpInfo.hoursSince}h 前` : '無 checkpoint';
    setStatus(cpInfo.hoursSince === null || cpInfo.hoursSince > 24 ? 'loading' : 'ok',
      `v${parsed.version} ｜ ${cpMsg}`);
  } catch(e) {
    setStatus('err', '載入失敗：' + e.message);
    el('promptText').value = '// 錯誤：' + e.message;
  }
}
document.addEventListener('DOMContentLoaded', async () => {
  const data = await chrome.storage.local.get(['githubRawBase','githubToken']);
  el('githubRawBase').value = data.githubRawBase || DEFAULT_BASE;
  el('githubToken').value   = data.githubToken   || '';
  el('githubRawBase').addEventListener('keydown', e => { if(e.key==='Enter') saveAndReload(); });
  el('githubToken').addEventListener('keydown',   e => { if(e.key==='Enter') saveAndReload(); });
  await loadAll();
});
