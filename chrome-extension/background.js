// background.js

const POLL_INTERVAL_MS = 2000;
const SERVER_URL = "http://127.0.0.1:9876/poll";
const RESULT_URL = "http://127.0.0.1:9876/result";

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
        
        // Find the first tab matching one of these patterns
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
      
      // Inject content script dynamically
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ["content.js"]
      }, () => {
        if (chrome.runtime.lastError) {
          console.error("Injection failed:", chrome.runtime.lastError.message);
          sendResult(data.command_id, false, `Failed to inject content script into ${tab.url}: ${chrome.runtime.lastError.message}`);
        } else {
          console.log("Successfully injected content.js, retrying message...");
          
          // Retry sending message after script injection
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

async function pollServer() {
  let waitTime = 1000; // default poll interval of 1s when idle
  try {
    const response = await fetch(SERVER_URL);
    if (response.ok) {
      const data = await response.json();
      if (data && data.command_id) {
        console.log("Received command from server:", data);
        
        findTargetTab((tab) => {
          sendMessageToTab(tab, data);
        });
        
        // Command found, query again quickly to check for any queued commands
        waitTime = 100;
      }
    } else {
      // Server returned error (e.g. 502/503), wait 2s
      waitTime = 2000;
    }
  } catch (err) {
    // Server probably offline, wait 5s to avoid CPU spinning
    waitTime = 5000;
  }
  
  // Schedule next poll sequentially to avoid overlapping requests
  setTimeout(pollServer, waitTime);
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

function startPolling() {
  pollServer();
}

startPolling();
