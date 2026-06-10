// content.js

if (!window.hasMaplabBridgeListener) {
  window.hasMaplabBridgeListener = true;

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "read_last_messages") {
      try {
        const n = request.count || 5;
        let text = "";
        
        // Selectors for chat bubbles/messages in different platforms
        const selectors = [
          // Claude
          '.font-claude-message', '.font-user-message', '[data-testid="user-message"]',
          // ChatGPT
          '[data-message-author-role]', '.markdown.prose',
          // Gemini / AI Studio
          'div.query-content', 'div.model-response-content', '.chat-message', '.message-content', 'message-content',
          // General fallback for common UIs
          '.message', '.bubble', '.chat-bubble', '.chat-text'
        ];
        
        let messages = [];
        for (const selector of selectors) {
          const elements = document.querySelectorAll(selector);
          if (elements.length > 0) {
            messages = Array.from(elements).map(el => el.innerText.trim()).filter(t => t.length > 0);
            break;
          }
        }
        
        // Fallback 1: Find paragraphs inside <main> or article/section tags
        if (messages.length === 0) {
          const container = document.querySelector('main') || document.querySelector('article') || document.body;
          const pElements = container.querySelectorAll('p');
          if (pElements.length > 0) {
            messages = Array.from(pElements).map(el => el.innerText.trim()).filter(t => t.length > 0);
          }
        }
        
        // Fallback 2: Grab the text of the body and split by newlines (original heuristic)
        if (messages.length === 0) {
          const chatContainer = document.querySelector('main') || document.body;
          messages = chatContainer.innerText.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        }
        
        // Get the last n messages
        const lastN = messages.slice(-n);
        text = lastN.join('\n\n---\n\n');
        
        sendResponse({text: text});
      } catch (e) {
        sendResponse({error: e.toString()});
      }
      return true;
    }
    
    if (request.action === "paste_text") {
      try {
        // Find the main input box.
        let inputBox = document.querySelector('div[contenteditable="true"]') || document.querySelector('textarea');
        
        if (inputBox) {
          inputBox.focus();
          
          // Simulating pasting text
          if (inputBox.tagName === "TEXTAREA") {
              inputBox.value = "";
              inputBox.value = request.text;
              inputBox.dispatchEvent(new Event('input', { bubbles: true }));
              inputBox.dispatchEvent(new Event('change', { bubbles: true }));
          } else {
              // contenteditable (like Claude, Gemini, ChatGPT)
              // Use execCommand to insert text, which updates ProseMirror/React state properly.
              try {
                const selection = window.getSelection();
                const range = document.createRange();
                range.selectNodeContents(inputBox);
                selection.removeAllRanges();
                selection.addRange(range);
                
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, request.text);
              } catch (execErr) {
                // Fallback if execCommand fails
                inputBox.innerText = request.text;
              }
              
              // Dispatch input event as fallback/additional trigger
              inputBox.dispatchEvent(new Event('input', { bubbles: true }));
          }
          
          // Auto-send if requested
          if (request.auto_send) {
            setTimeout(() => {
              // Find send button: usually a button with an aria-label like "Send message" or an icon
              const sendBtn = document.querySelector('button[aria-label*="Send"], button[aria-label*="Run"]') || 
                              Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Send') || b.querySelector('mat-icon') || b.querySelector('svg'));
              if (sendBtn) {
                sendBtn.click();
              } else {
                  // Try to dispatch Enter key
                  inputBox.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true}));
              }
            }, 500);
          }
          
          sendResponse({status: "pasted"});
        } else {
          sendResponse({error: "Input box not found"});
        }
      } catch (e) {
        sendResponse({error: e.toString()});
      }
      return true;
    }
  });
}
