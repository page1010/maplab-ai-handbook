// MAPLAB Agent Commander v2.0 — Popup JS
const DEFAULT_RAW_BASE = 'https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main';
const DEFAULT_STATE_PATH = 'CURRENT_STATUS.md';

document.addEventListener('DOMContentLoaded', async () => {
  const baseInput = document.getElementById('githubRawBase');
  const pathInput = document.getElementById('projectStatePath');
  const saveBtn = document.getElementById('saveBtn');
  const status = document.getElementById('status');
  const preview = document.getElementById('statePreview');

  // Load saved settings
  const data = await chrome.storage.local.get(['githubRawBase', 'projectStatePath']);
  baseInput.value = data.githubRawBase || DEFAULT_RAW_BASE;
  pathInput.value = data.projectStatePath || DEFAULT_STATE_PATH;

  // Save settings
  saveBtn.addEventListener('click', async () => {
    await chrome.storage.local.set({
      githubRawBase: baseInput.value.trim() || DEFAULT_RAW_BASE,
      projectStatePath: pathInput.value.trim() || DEFAULT_STATE_PATH
    });
    status.textContent = 'Settings saved!';
    status.classList.add('show');
    setTimeout(() => status.classList.remove('show'), 2000);
    loadPreview();
  });

  // Load state preview
  async function loadPreview() {
    try {
      const base = baseInput.value.trim() || DEFAULT_RAW_BASE;
      const path = pathInput.value.trim() || DEFAULT_STATE_PATH;
      const url = base + '/' + path;
      const resp = await fetch(url);
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const text = await resp.text();
      const version = text.match(/Version:\\s*(.+)/)?.[1] || '?';
      const phase = text.match(/Phase:\\s*(.+)/)?.[1] || '?';
      preview.innerHTML = '<span class="label">Version:</span> <span class="version">' + version + '</span><br>' +
        '<span class="label">Phase:</span> <span class="value">' + phase + '</span>';
    } catch (e) {
      preview.textContent = 'Error: ' + e.message;
    }
  }

  loadPreview();
});
