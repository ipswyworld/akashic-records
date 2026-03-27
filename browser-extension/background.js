const DEFAULT_API_URL = "http://localhost:8001";
const DEFAULT_USER_ID = "system_user";

// Keep track of the last URL to avoid duplicate pings on refresh
let lastUrl = "";

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://')) {
    if (tab.url === lastUrl) return;
    lastUrl = tab.url;

    logTelemetry({
      type: "BROWSER_VISIT",
      title: tab.title || "Unknown Title",
      url: tab.url,
      user_id: DEFAULT_USER_ID
    });
  }
});

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
