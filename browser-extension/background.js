const DEFAULT_API_URL = "http://localhost:8001";
const DEFAULT_USER_ID = "system_user";

// --- Batch 1: Context Menus & Sidebar ---
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "akasha-ghostwrite",
    title: "Ghostwrite this selection 👻",
    contexts: ["selection"]
  });
  
  chrome.contextMenus.create({
    id: "akasha-vault",
    title: "Vault this selection ✨",
    contexts: ["selection"]
  });

  if (chrome.sidePanel) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  }
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "akasha-ghostwrite") {
    chrome.tabs.sendMessage(tab.id, { 
      action: "ghostwrite_selection", 
      text: info.selectionText 
    });
  }
  
  if (info.menuItemId === "akasha-vault") {
    logTelemetry({
      type: "SELECTION_VAULTED",
      title: `Selection from: ${tab.title}`,
      url: tab.url,
      content: info.selectionText,
      user_id: DEFAULT_USER_ID
    });
  }
});

// Keep track of the last URL to avoid duplicate pings on refresh
let lastUrl = "";

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://')) {
    if (tab.url === lastUrl) return;
    lastUrl = tab.url;

    logTelemetry({
      type: "BROWSER_VISIT",
      title: tab.title || "Unknown Title",
      url: tab.url,
      user_id: DEFAULT_USER_ID
    });

    // Automatic Ingestion: Auto-vault the page content if the user stays for a while (e.g. basic auto-feed)
    try {
      const { apiUrl, token } = await chrome.storage.local.get(["apiUrl", "token"]);
      const targetUrl = `${apiUrl || DEFAULT_API_URL}/ingest/clipper`;
      
      console.log("Auto-feeding page to Akasha:", tab.url);
      fetch(targetUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ url: tab.url })
      }).catch(e => console.error("Auto-feed failed:", e));
    } catch (e) {
      console.error("Auto-feed error:", e);
    }
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "open_side_panel") {
    chrome.sidePanel.open({ tabId: sender.tab.id });
  }

  if (message.action === "capture_screenshot") {
    chrome.tabs.captureVisibleTab(null, { format: 'png' }, (dataUrl) => {
      sendResponse({ dataUrl: dataUrl });
    });
    return true; // Keep channel open
  }

  if (message.action === "visual_reasoning") {
    handleVisualReasoning(message.payload, sender.tab);
  }
  
  if (message.action === "quick_synthesize") {
    logTelemetry({
      type: "QUICK_SYNTHESIS",
      title: "Selection Distillation",
      content: message.text,
      user_id: DEFAULT_USER_ID
    });
    // Trigger notification or sidebar update
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Akasha Knowledge Distilled',
      message: 'Synthesis sent to your personal Library.'
    });
  }
  
  if (message.action === "cross_app_sync") {
    // Phase 3 Feature: Sync summarized context to Notion/Slack
    console.log("Cross-App Sync Triggered:", message.payload);
  }
});

async function handleVisualReasoning(dataUrl, tab) {
  const { apiUrl, token } = await chrome.storage.local.get(["apiUrl", "token"]);
  const targetUrl = `${apiUrl || DEFAULT_API_URL}/vision/analyze`;
  
  // Convert DataURL to Blob for multipart upload
  const blob = await (await fetch(dataUrl)).blob();
  const formData = new FormData();
  formData.append('file', blob, 'screenshot.png');
  formData.append('user_id', DEFAULT_USER_ID);

  try {
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    const data = await response.json();
    chrome.tabs.sendMessage(tab.id, { 
      action: "show_visual_results", 
      analysis: data.description 
    });
  } catch (error) {
    console.error("Visual Reasoning failed:", error);
  }
}

async function logTelemetry(payload) {
  try {
    const { apiUrl, userId } = await chrome.storage.local.get(["apiUrl", "userId"]);
    const targetUrl = `${apiUrl || DEFAULT_API_URL}/telemetry`;
    const finalUserId = userId || DEFAULT_USER_ID;
    
    payload.user_id = finalUserId;

    console.log("Streaming telemetry to Akasha:", payload);

    const response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      console.error("Failed to stream telemetry:", response.statusText);
    }
  } catch (error) {
    console.error("Telemetry streaming error:", error);
  }
}
