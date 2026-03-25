// MAPLAB Extension — popup.js
// 從 GitHub 載入最新邏輯，本地永遠不需要更新

const REMOTE_LOGIC_URL = 'https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main/chrome-extension/remote-logic.js';

// 點圖示開側邊欄，不會因切換 tab 而消失
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });

async function loadRemoteLogic() {
  const data = await chrome.storage.local.get(['githubToken']);
  const token = data.githubToken || '';
  const headers = token ? { 'Authorization': `token ${token}` } : {};

  try {
    const resp = await fetch(REMOTE_LOGIC_URL + '?t=' + Date.now(), { headers });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const code = await resp.text();
    const script = document.createElement('script');
    script.textContent = code;
    document.head.appendChild(script);
  } catch(e) {
    document.getElementById('statusText').textContent = '載入失敗：' + e.message;
  }
}

loadRemoteLogic();
