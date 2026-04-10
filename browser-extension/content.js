// content.js - Enhanced with Vision HUD (Phase 6)
console.log("Akasha Vision HUD Script Active.");

let isTargeting = false;
let hoverElement = null;
let hudElement = null;

// 1. Create the Vision HUD Side-Panel
function createHUD() {
    if (hudElement) return;
    hudElement = document.createElement("div");
    hudElement.id = "akasha-vision-hud";
    hudElement.style.cssText = `
        position: fixed;
        right: 20px;
        top: 20px;
        width: 320px;
        max-height: 80vh;
        background: rgba(10, 10, 10, 0.95);
        color: #00ffcc;
        border: 1px solid #00ffcc;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 12px;
        z-index: 999999;
        overflow-y: auto;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.3);
        display: none;
        transition: all 0.3s ease;
    `;
    hudElement.innerHTML = `
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #00ffcc; padding-bottom: 5px; margin-bottom: 10px;">
            <strong style="text-transform: uppercase;">Akasha Vision HUD</strong>
            <span id="close-hud" style="cursor: pointer;">[X]</span>
        </div>
        <div id="hud-content">
            <p style="color: #aaa;">Scanning consciousness...</p>
        </div>
        <div id="hud-wisdom" style="margin-top: 15px; padding-top: 10px; border-top: 1px dashed #444;">
        </div>
    `;
    document.body.appendChild(hudElement);
    
    document.getElementById("close-hud").onclick = () => {
        hudElement.style.display = "none";
    };
}

createHUD();

// 2. Proactive Critique Polling
let lastUrl = "";
async function pollProactiveCritique() {
    const settings = await chrome.storage.local.get(['isFocusMode']);
    if (settings.isFocusMode) {
        if (hudElement) hudElement.style.display = "none";
        return;
    }

    const currentUrl = window.location.href;
    if (currentUrl === lastUrl) return;
    lastUrl = currentUrl;

    const pageTitle = document.title;
    const pageContent = document.body.innerText.substring(0, 5000);

    try {
        const response = await fetch("http://localhost:8001/proactive/critique", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                url: currentUrl,
                title: pageTitle,
                content: pageContent
            })
        });
        
        const data = await response.json();
        updateHUD(data);
    } catch (err) {
        console.error("Vision HUD: Critique poll failed", err);
    }
}

function updateHUD(data) {
    if (!hudElement) return;
    hudElement.style.display = "block";
    const content = document.getElementById("hud-content");
    const wisdom = document.getElementById("hud-wisdom");

    if (content) {
        content.innerHTML = `
            <div style="margin-bottom: 10px;">
                <span style="color: #ff3366;">[LOGIC]:</span> ${data.logic_critique || "Analyzing..."}
            </div>
            <div style="margin-bottom: 10px;">
                <span style="color: #ffcc00;">[BIAS]:</span> ${data.bias_critique || "Analyzing..."}
            </div>
        `;
    }

    if (wisdom) {
        const conf = data.crowd_confidence ? Math.round(data.crowd_confidence * 100) : 0;
        wisdom.innerHTML = `
            <div style="color: #00ffcc; margin-bottom: 5px;">[CROWD WISDOM - Conf: ${conf}%]:</div>
            <div style="color: #eee; font-style: italic;">"${data.crowd_wisdom || "Gathering perspectives..."}"</div>
        `;
    }
}

// Start polling every 30 seconds if the page changed
setInterval(pollProactiveCritique, 30000);
pollProactiveCritique(); // Initial run

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getPageContent") {
        chrome.storage.local.get(['piiShield'], (settings) => {
            let content = document.body.innerText;
            if (settings.piiShield !== false) {
                content = scrubLocalPII(content);
            }
            sendResponse({ content: content.substring(0, 50000) });
        });
        return true;
    }

    if (request.action === "get_form_fields") {
        const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
        const fields = inputs.map(i => i.name || i.id || i.placeholder).filter(f => f);
        sendResponse({ fields: fields });
    }

    if (request.action === "fill_form") {
        const data = request.data;
        for (const [key, value] of Object.entries(data)) {
            const el = document.getElementsByName(key)[0] || document.getElementById(key);
            if (el) el.value = value;
        }
    }

    if (request.action === "toggleTargeting") {
        isTargeting = !isTargeting;
        document.body.style.cursor = isTargeting ? "crosshair" : "default";
        if (!isTargeting && hoverElement) {
            hoverElement.style.outline = "";
        }
        sendResponse({status: isTargeting ? "active" : "inactive"});
    }

    if (request.action === "toggleHUD") {
        if (hudElement) {
            hudElement.style.display = hudElement.style.display === "none" ? "block" : "none";
        }
        sendResponse({status: "toggled"});
    }

    if (request.action === "show_visual_results") {
        createHUD();
        hudElement.style.display = "block";
        const content = document.getElementById("hud-content");
        content.innerHTML = `<div style="color: #03dac6; font-weight: bold; margin-bottom: 5px;">[VISUAL ANALYSIS]:</div>
                             <div style="color: #eee;">${request.analysis}</div>`;
    }

    if (request.action === "quick_synthesize") {
        createHUD();
        hudElement.style.display = "block";
        const content = document.getElementById("hud-content");
        content.innerHTML = `<em>Archivist is distilling selection...</em>`;
        // Actual synthesis call already handled by background.js telemetry
    }

    if (request.action === "ghostwrite_selection") {
        handleGhostwrite(request.text);
    }
});

// Feature: Inline Ghostwriter UI
function handleGhostwrite(text) {
    const selection = window.getSelection();
    if (!selection.rangeCount) return;
    const range = selection.getRangeAt(0);

    const ghostDiv = document.createElement("div");
    ghostDiv.style.cssText = `
        background: #1e1e1e; color: #ff79c6; border: 1px solid #ff79c6;
        padding: 10px; border-radius: 4px; font-family: sans-serif;
        font-size: 12px; margin-top: 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        z-index: 10000; max-width: 300px;
    `;
    ghostDiv.innerHTML = "<em>Archivist is drafting...</em>";

    // Position near selection
    const rect = range.getBoundingClientRect();
    ghostDiv.style.position = "absolute";
    ghostDiv.style.top = `${window.scrollY + rect.bottom + 5}px`;
    ghostDiv.style.left = `${window.scrollX + rect.left}px`;

    document.body.appendChild(ghostDiv);

    // Call backend for ghostwriting
    chrome.storage.local.get(['apiUrl', 'token'], async (settings) => {
        try {
            const response = await fetch(`${settings.apiUrl || 'http://localhost:8001'}/query/rag`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${settings.token}`
                },
                body: JSON.stringify({ 
                    query: `Improve or expand on this text in the Archivist tone: "${text}"`,
                    is_ghost_writer: true 
                })
            });
            const data = await response.json();
            ghostDiv.innerHTML = `<div style="margin-bottom:8px;">${data.answer}</div>
                                  <button id="ghost-apply" style="background:#ff79c6; color:#000; border:none; padding:4px 8px; cursor:pointer; font-size:10px; border-radius:2px;">Apply</button>
                                  <button id="ghost-close" style="background:none; color:#888; border:none; margin-left:10px; cursor:pointer;">Discard</button>`;

            ghostDiv.querySelector('#ghost-apply').onclick = () => {
                document.execCommand("insertText", false, data.answer);
                ghostDiv.remove();
            };
            ghostDiv.querySelector('#ghost-close').onclick = () => ghostDiv.remove();
        } catch (e) {
            ghostDiv.innerText = "Connection to Akasha lost.";
            setTimeout(() => ghostDiv.remove(), 2000);
        }
    });
}
// Original Selector Logic (Keeping for compatibility)
document.addEventListener("mouseover", (e) => {
    if (!isTargeting) return;
    if (hoverElement) hoverElement.style.outline = "";
    hoverElement = e.target;
    hoverElement.style.outline = "2px solid #00ffcc";
});

document.addEventListener("click", (e) => {
    if (!isTargeting) return;
    e.preventDefault();
    e.stopPropagation();
    
    const selector = getSelector(e.target);
    const content = e.target.innerText;
    
    chrome.runtime.sendMessage({
        action: "elementSelected",
        selector: selector,
        content: content,
        url: window.location.href
    });
    
    isTargeting = false;
    document.body.style.cursor = "default";
    if (hoverElement) hoverElement.style.outline = "";
    
    return false;
});

function scrubLocalPII(text) {
    // Basic regex for email, phone, and SSN-like patterns
    return text
        .replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, "[EMAIL_REDACTED]")
        .replace(/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, "[PHONE_REDACTED]")
        .replace(/\b\d{3}-\d{2}-\d{4}\b/g, "[SSN_REDACTED]");
}

// Batch 4: Librarian Quick-Actions (Selection Overlay)
document.addEventListener('mouseup', (e) => {
    const selection = window.getSelection().toString().trim();
    if (selection && selection.length > 5) {
        // Show a tiny Akasha icon near selection for quick synthesis
        showQuickActionIcon(e.pageX, e.pageY, selection);
    }
});

function getSelector(el) {
  let path = [];
  while (el && el.nodeType === Node.ELEMENT_NODE) {
    let tag = el.tagName.toLowerCase();
    if (el.id) {
      tag += "#" + el.id;
      path.unshift(tag);
      break;
    } else {
      let siblings = Array.from(el.parentNode.children).filter(s => s.tagName === el.tagName);
      if (siblings.length > 1) {
        let index = siblings.indexOf(el) + 1;
        tag += `:nth-child(${index})`;
      }
      path.unshift(tag);
      el = el.parentNode;
    }
  }
  return path.join(" > ");
}
