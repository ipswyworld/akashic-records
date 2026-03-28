document.addEventListener('DOMContentLoaded', async () => {
  const clipBtn = document.getElementById('clip-page');
  const summarizeBtn = document.getElementById('summarize-page');
  const targetBtn = document.getElementById('target-element');
  const toggleBtn = document.getElementById('toggle-settings');
  const saveBtn = document.getElementById('save-settings');
  
  const settingsPanel = document.getElementById('settings-panel');
  const mainActions = document.getElementById('main-actions');
  const summaryBox = document.getElementById('summary-box');
  
  const apiUrlInput = document.getElementById('apiUrl');
  const tokenInput = document.getElementById('userId'); // Reusing existing ID for token
  const summaryText = document.getElementById('summary-text');
  const msgEl = document.getElementById('msg');

  // Load saved settings
  const settings = await chrome.storage.local.get(['apiUrl', 'token']);
  apiUrlInput.value = settings.apiUrl || 'http://localhost:8001';
  tokenInput.value = settings.token || '';
  tokenInput.placeholder = 'Akasha JWT Token';

  const getHeaders = () => {
    const headers = { 'Content-Type': 'application/json' };
    if (tokenInput.value) headers['Authorization'] = `Bearer ${tokenInput.value}`;
    return headers;
  };

  // Toggle settings
  toggleBtn.addEventListener('click', () => {
    const isVisible = settingsPanel.style.display === 'block';
    settingsPanel.style.display = isVisible ? 'none' : 'block';
    mainActions.style.display = isVisible ? 'flex' : 'none';
  });

  // Save settings
  saveBtn.addEventListener('click', async () => {
    await chrome.storage.local.set({
      apiUrl: apiUrlInput.value,
      token: tokenInput.value
    });
    settingsPanel.style.display = 'none';
    mainActions.style.display = 'flex';
    showMsg('Sovereign Bridge Linked. 🗝️', '#03dac6');
  });

  // Clip current page
  clipBtn.addEventListener('click', async () => {
    setLoading(clipBtn, 'Vaulting Artifact...');
    
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const response = await fetch(`${apiUrlInput.value}/ingest/clipper`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ url: tab.url })
      });

      if (response.ok) {
        showMsg('Artifact successfully vaulted. ✨', '#03dac6');
      } else {
        showMsg('Authorization Required. 🔐', '#cf6679');
      }
    } catch (err) {
      showMsg('Connection refused. 📡', '#cf6679');
    } finally {
      stopLoading(clipBtn, '<span>✨</span> Clip to Akashic Records');
    }
  });

  // Summarize current page (Autonomous Sub-Agent Action)
  summarizeBtn.addEventListener('click', async () => {
    setLoading(summarizeBtn, 'Synthesizing knowledge...');
    summaryBox.style.display = 'none';
    
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const response = await fetch(`${apiUrlInput.value}/query/rag`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ 
          query: `Summarize this page briefly: ${tab.url}` 
        })
      });

      const data = await response.json();
      if (response.ok) {
        summaryText.innerText = data.answer || "No summary available.";
        summaryBox.style.display = 'block';
        showMsg('Knowledge distilled. 🧠', '#03dac6');
      } else {
        showMsg('Synthesis failed.', '#cf6679');
      }
    } catch (err) {
      showMsg('Agent disconnected. 📡', '#cf6679');
    } finally {
      stopLoading(summarizeBtn, '<span>🧠</span> AI Summary (Autonomous)');
    }
  });

  // Target specific element
  targetBtn.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { action: "start_targeting" });
    showMsg('Targeting Mode: Click an element. 🎯', '#bb86fc');
    window.close(); // Close popup to let user click
  });

  // Listen for targeted element data from content script
  chrome.runtime.onMessage.addListener(async (message) => {
    if (message.action === "element_targeted") {
      const { apiUrl, token } = await chrome.storage.local.get(['apiUrl', 'token']);
      
      try {
        await fetch(`${apiUrl || 'http://localhost:8001'}/telemetry`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            type: "ELEMENT_TARGETED",
            title: `Targeted: ${message.selector}`,
            url: message.url,
            content: message.text
          })
        });
        console.log("Element vaulted.");
      } catch (err) {
        console.error("Failed to vault targeted element:", err);
      }
    }
  });

  function setLoading(btn, text) {
    btn.disabled = true;
    btn.innerText = text;
  }

  function stopLoading(btn, originalHtml) {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }

  function showMsg(text, color) {
    msgEl.innerText = text;
    msgEl.style.color = color;
    setTimeout(() => { msgEl.innerText = ''; }, 3000);
  }
});
