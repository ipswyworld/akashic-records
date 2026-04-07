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
  const tokenInput = document.getElementById('userId'); 
  const summaryText = document.getElementById('summary-text');
  const msgEl = document.getElementById('msg');

  // Chat Elements
  const chatInput = document.getElementById('chat-input');
  const chatSendBtn = document.getElementById('chat-send');
  const chatHistory = document.getElementById('chat-history');

  const modelSelect = document.getElementById('model-select');
  const ragStatus = document.getElementById('rag-status');
  const ghostToggle = document.getElementById('ghost-toggle');
  const ghostStatus = document.getElementById('ghost-status');

  const fillBtn = document.getElementById('fill-form');
  const monitorBtn = document.getElementById('monitor-page');
  const semanticSearch = document.getElementById('semantic-search');
  const piiShield = document.getElementById('pii-shield');
  const zeroData = document.getElementById('zero-data');

  let isGhostMode = false;

  // Load saved settings
  const settings = await chrome.storage.local.get(['apiUrl', 'token', 'selectedModel', 'piiShield', 'zeroData']);
  apiUrlInput.value = settings.apiUrl || 'http://localhost:8001';
  tokenInput.value = settings.token || '';
  modelSelect.value = settings.selectedModel || 'local';
  piiShield.checked = settings.piiShield !== false;
  zeroData.checked = settings.zeroData === true;

  const getHeaders = () => {
    const headers = { 'Content-Type': 'application/json' };
    if (tokenInput.value) headers['Authorization'] = `Bearer ${tokenInput.value}`;
    return headers;
  };

  // Sidebar / Panel Support
  if (chrome.sidePanel) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  }

  // Toggle settings panel
  toggleBtn.addEventListener('click', () => {
    const isVisible = settingsPanel.style.display === 'block';
    settingsPanel.style.display = isVisible ? 'none' : 'block';
    mainActions.style.display = isVisible ? 'flex' : 'none';
  });

  // Toggle Ghostwriter
  ghostToggle.addEventListener('click', () => {
    isGhostMode = !isGhostMode;
    ghostStatus.innerText = isGhostMode ? 'ON' : 'OFF';
    ghostToggle.style.color = isGhostMode ? '#4ade80' : '#ff79c6';
  });

  // Batch 2: Semantic Search
  semanticSearch.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
      const query = semanticSearch.value.trim();
      if (!query) return;
      addMessage(`Searching Library for: ${query}`, 'user');
      try {
        const response = await fetch(`${apiUrlInput.value}/search/semantic`, {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({ query: query })
        });
        const data = await response.json();
        if (data.length > 0) {
          addMessage(`Found ${data.length} related records. Top match: ${data[0].content.substring(0, 200)}...`, 'ai');
        } else {
          addMessage("No direct matches in your Library.", 'ai');
        }
      } catch (err) { addMessage("Library Search failed.", 'ai'); }
    }
  });

  // Batch 3: Smart Form Fill
  fillBtn.addEventListener('click', async () => {
    setLoading(fillBtn, 'Predicting fields...');
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      chrome.tabs.sendMessage(tab.id, { action: "get_form_fields" }, async (response) => {
        if (response && response.fields) {
          const fillData = await fetch(`${apiUrlInput.value}/automation/form_fill`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ url: tab.url, fields: response.fields })
          });
          const mapping = await fillData.json();
          chrome.tabs.sendMessage(tab.id, { action: "fill_form", data: mapping });
          showMsg('Form fields predicted and filled. 📝', '#03dac6');
        }
      });
    } catch (err) { showMsg('Form Fill failed.', '#cf6679'); }
    finally { stopLoading(fillBtn, '📝 Smart Fill'); }
  });

  // Batch 3: Monitor Page
  monitorBtn.addEventListener('click', async () => {
    const condition = prompt("What condition should the Butler watch for? (e.g. 'price below $500')");
    if (!condition) return;
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await fetch(`${apiUrlInput.value}/automation/monitor`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ url: tab.url, trigger_condition: condition })
      });
      showMsg('Butler is now watching this page. 👁️', '#bb86fc');
    } catch (err) { showMsg('Monitor failed.', '#cf6679'); }
  });

  // Batch 4: Privacy Settings Save
  saveBtn.addEventListener('click', async () => {
    await chrome.storage.local.set({
      apiUrl: apiUrlInput.value,
      token: tokenInput.value,
      piiShield: piiShield.checked,
      zeroData: zeroData.checked
    });
    settingsPanel.style.display = 'none';
    mainActions.style.display = 'flex';
    showMsg('Sovereign Settings Synchronized. 🗝️', '#03dac6');
  });

  const syncNotion = document.getElementById('sync-notion');
  const syncSlack = document.getElementById('sync-slack');

  // Batch 8: LaTeX & Math Formatting
  const formatMath = (text) => {
    return text.replace(/\$(.*?)\$/g, '<span class="math-tex">$1</span>');
  };

  // Batch 8: Connectors (Notion/Slack)
  const triggerSync = async (platform) => {
    const btn = document.getElementById(`sync-${platform}`);
    setLoading(btn, 'Syncing...');
    try {
      const response = await fetch(`${apiUrlInput.value}/automation/sync`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ platform: platform, context: window.pageContext })
      });
      if (response.ok) showMsg(`${platform} Sync Successful. 🔗`, '#bb86fc');
    } catch (err) { showMsg(`${platform} Sync Failed.`, '#cf6679'); }
    finally { stopLoading(btn, platform.charAt(0).toUpperCase() + platform.slice(1)); }
  };

  syncNotion.addEventListener('click', () => triggerSync('notion'));
  syncSlack.addEventListener('click', () => triggerSync('slack'));

  // Chat Functionality
  const addMessage = (text, sender, monologue = "") => {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${sender === 'user' ? 'msg-user' : 'msg-ai'}`;
    msgDiv.innerHTML = formatMath(text);
    if (monologue) msgDiv.title = `Archivist Thought: ${monologue}`;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  };

  const handleChat = async () => {
    const query = chatInput.value.trim();
    if (!query) return;
    addMessage(query, 'user');
    chatInput.value = '';
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const response = await fetch(`${apiUrlInput.value}/query/rag`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ 
          query: query,
          context: window.pageContext || tab.url,
          model_tier: modelSelect.value,
          is_ghost_writer: isGhostMode
        })
      });
      const data = await response.json();
      if (response.ok) {
        addMessage(data.answer, 'ai', data.monologue);
      } else {
        addMessage("Connection failed. Check API URL.", 'ai');
      }
    } catch (err) {
      addMessage("Agent disconnected. Ensure Akasha core is running.", 'ai');
    }
  };

  chatSendBtn.addEventListener('click', handleChat);
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleChat();
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
      if (response.ok) showMsg('Artifact successfully vaulted. ✨', '#03dac6');
      else showMsg('Authorization Required. 🔐', '#cf6679');
    } catch (err) { showMsg('Connection refused. 📡', '#cf6679'); }
    finally { stopLoading(clipBtn, '✨ Vault'); }
  });

  // Summarize current page
  summarizeBtn.addEventListener('click', async () => {
    setLoading(summarizeBtn, 'Synthesizing knowledge...');
    summaryBox.style.display = 'none';
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const response = await fetch(`${apiUrlInput.value}/query/rag`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ query: `Summarize this page briefly: ${tab.url}` })
      });
      const data = await response.json();
      if (response.ok) {
        summaryText.innerText = data.answer || "No summary available.";
        summaryBox.style.display = 'block';
        showMsg('Knowledge distilled. 🧠', '#03dac6');
      } else showMsg('Synthesis failed.', '#cf6679');
    } catch (err) { showMsg('Agent disconnected. 📡', '#cf6679'); }
    finally { stopLoading(summarizeBtn, '🧠 Synthesize'); }
  });

  // Target specific element
  targetBtn.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { action: "start_targeting" });
    showMsg('Targeting Mode: Click an element. 🎯', '#bb86fc');
    window.close();
  });

  const visualBtn = document.getElementById('visual-reason');
  const egoMirror = document.getElementById('ego-mirror');
  const egoMood = document.getElementById('ego-mood');
  const egoTraits = document.getElementById('ego-traits');

  visualBtn.addEventListener('click', async () => {
    setLoading(visualBtn, 'Capturing Vision...');
    chrome.runtime.sendMessage({ action: "capture_screenshot" }, (response) => {
      if (response && response.dataUrl) {
        chrome.runtime.sendMessage({ action: "visual_reasoning", payload: response.dataUrl });
        showMsg('Vision sent to Archivist. 📷', '#03dac6');
      }
      stopLoading(visualBtn, '📷 Visual Reasoner');
    });
  });

  const syncDigitalEgo = async () => {
    try {
      const response = await fetch(`${apiUrlInput.value}/user/psychology`, { headers: getHeaders() });
      const data = await response.json();
      if (data.ocean_traits) {
        egoMirror.style.display = 'block';
        egoMood.innerText = data.current_mood || 'Neutral';
        const traits = Object.entries(data.ocean_traits)
          .map(([k, v]) => `${k.charAt(0).toUpperCase()}: ${Math.round(v * 100)}%`)
          .join(' | ');
        egoTraits.innerText = traits;
      }
    } catch (e) { console.error("Ego sync failed", e); }
  };
  syncDigitalEgo();

  function setLoading(btn, text) { btn.disabled = true; btn.innerText = text; }
  function stopLoading(btn, text) { btn.disabled = false; btn.innerText = text; }
  function showMsg(text, color) {
    msgEl.innerText = text; msgEl.style.color = color;
    setTimeout(() => { msgEl.innerText = ''; }, 3000);
  }

  // Update RAG status polling
  const updateRagStatus = async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) return;
      chrome.tabs.sendMessage(tab.id, { action: "getPageContent" }, (response) => {
        if (response && response.content) {
          ragStatus.innerText = "Page Context Active";
          ragStatus.classList.add('rag-active');
          window.pageContext = response.content;
        } else {
          ragStatus.innerText = "Page Context Offline";
          ragStatus.classList.remove('rag-active');
        }
      });
    } catch (e) { ragStatus.innerText = "Bridge Offline"; }
  };
  setInterval(updateRagStatus, 5000);
  updateRagStatus();
});