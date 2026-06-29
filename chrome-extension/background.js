// background.js — MV3 compatible
// Bot bridge polls http://127.0.0.1:9876/poll for commands and dispatches them to the active tab.
// MV3 service workers are ephemeral; chrome.alarms wakes the worker every 30s so polling never
// silently stops when Chrome recycles the worker.

const SERVER_URL = "http://127.0.0.1:9876/poll";
const RESULT_URL = "http://127.0.0.1:9876/result";
const ALARM_NAME = "bot-bridge-keepalive";
const ALARM_PERIOD_MINUTES = 0.5; // 30 seconds — minimum reliable period for MV3 alarms

function isRestrictedUrl(url) {
  if (!url) return true;
  return url.startsWith("chrome://") ||
         url.startsWith("chrome-extension://") ||
         url.startsWith("about:") ||
         url.startsWith("edge://") ||
         url.startsWith("devtools://");
}

function findTargetTab(callback) {
  // 1. Try active tab in the last focused window
  chrome.tabs.query({active: true, lastFocusedWindow: true}, (tabs) => {
    if (tabs && tabs.length > 0 && !isRestrictedUrl(tabs[0].url)) {
      callback(tabs[0]);
      return;
    }

    // 2. Try active tab in any window
    chrome.tabs.query({active: true}, (tabs) => {
      if (tabs && tabs.length > 0 && !isRestrictedUrl(tabs[0].url)) {
        callback(tabs[0]);
        return;
      }

      // 3. Query all tabs and find one matching chat systems
      chrome.tabs.query({}, (allTabs) => {
        if (!allTabs || allTabs.length === 0) {
          callback(null);
          return;
        }

        const chatPatterns = [
          "claude.ai",
          "gemini.google.com",
          "aistudio.google.com",
          "chatgpt.com",
          "chat.openai.com",
          "maplabkitchen.com"
        ];

        for (const pattern of chatPatterns) {
          const found = allTabs.find(t => t.url && t.url.toLowerCase().includes(pattern));
          if (found) {
            console.log("Found chat tab:", found.url);
            callback(found);
            return;
          }
        }

        // 4. Fallback to any non-restricted web tab
        const webTab = allTabs.find(t => t.url && !isRestrictedUrl(t.url));
        if (webTab) {
          callback(webTab);
        } else if (tabs && tabs.length > 0) {
          callback(tabs[0]);
        } else {
          callback(allTabs[0]);
        }
      });
    });
  });
}

function sendMessageToTab(tab, data) {
  if (!tab) {
    sendResult(data.command_id, false, "No active or available browser tabs found.");
    return;
  }

  const tabId = tab.id;

  if (isRestrictedUrl(tab.url)) {
    console.error("Cannot control restricted URL:", tab.url);
    sendResult(data.command_id, false, `Cannot control restricted page: ${tab.url}. Please open or switch to a chat tab (e.g., Claude, Gemini, AI Studio).`);
    return;
  }

  console.log(`Sending action '${data.action}' to tab ID ${tabId} (${tab.url})`);
  chrome.tabs.sendMessage(tabId, data, (response) => {
    if (chrome.runtime.lastError) {
      const errMsg = chrome.runtime.lastError.message;
      console.log(`Message failed (${errMsg}), trying to dynamically inject content.js...`);

      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ["content.js"]
      }, () => {
        if (chrome.runtime.lastError) {
          console.error("Injection failed:", chrome.runtime.lastError.message);
          sendResult(data.command_id, false, `Failed to inject content script into ${tab.url}: ${chrome.runtime.lastError.message}`);
        } else {
          console.log("Successfully injected content.js, retrying message...");
          chrome.tabs.sendMessage(tabId, data, (retryResponse) => {
            if (chrome.runtime.lastError) {
              console.error("Retry failed:", chrome.runtime.lastError.message);
              sendResult(data.command_id, false, `Failed to communicate with content script after injection: ${chrome.runtime.lastError.message}`);
            } else {
              console.log("Retry succeeded:", retryResponse);
              sendResult(data.command_id, true, retryResponse);
            }
          });
        }
      });
    } else {
      console.log("Message succeeded:", response);
      sendResult(data.command_id, true, response);
    }
  });
}

async function pollOnce() {
  try {
    const response = await fetch(SERVER_URL);
    if (response.ok) {
      const data = await response.json();
      if (data && data.command_id) {
        console.log("Received command from server:", data);
        findTargetTab((tab) => {
          sendMessageToTab(tab, data);
        });
        return true; // command found — caller should poll again quickly
      }
    }
  } catch {
    // server offline — normal when ccbot is not running
  }
  return false;
}

// Poll in a burst for up to 25 seconds (safely inside the 30s SW idle window).
// The alarm fires every 30s to restart the burst, ensuring no silent gap.
let burstActive = false;

async function pollBurst() {
  if (burstActive) return;
  burstActive = true;
  try {
    const deadline = Date.now() + 25000;
    while (Date.now() < deadline) {
      const found = await pollOnce();
      const wait = found ? 100 : 2000;
      await new Promise(r => setTimeout(r, wait));
    }
  } finally {
    burstActive = false;
  }
}

async function sendResult(commandId, success, resultData) {
  try {
    await fetch(RESULT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        command_id: commandId,
        success: success,
        result: resultData
      })
    });
  } catch (err) {
    console.error("Failed to send result back to server", err);
  }
}

// Alarm wakes the service worker every 30s; each wake starts a fresh 25s burst.
chrome.alarms.create(ALARM_NAME, { periodInMinutes: ALARM_PERIOD_MINUTES });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === ALARM_NAME) {
    pollBurst();
  }
});

// Start immediately on service worker startup (install, update, browser launch).
pollBurst();
