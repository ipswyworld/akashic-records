document.addEventListener('DOMContentLoaded', async () => {
  const clipBtn = document.getElementById('clip-page');
  const summarizeBtn = document.getElementById('summarize-page');
  const targetBtn = document.getElementById('target-element');
  const toggleBtn = document.getElementById('toggle-settings');
  const saveBtn = document.getElementById('save-settings');
  
  const settingsPanel = document.getElementById('settings-panel');
  const summaryBox = document.getElementById('summary-box');
  
  const apiUrlInput = document.getElementById('apiUrl');
  const tokenInput = document.getElementById('userId'); 
  const summaryText = document.getElementById('summary-text');
  const msgEl = document.getElementById('msg');

  // Nav Elements
  const navActions = document.getElementById('nav-actions');
  const navTodos = document.getElementById('nav-todos');
  const navChat = document.getElementById('nav-chat');
  const viewActions = document.getElementById('view-actions');
  const viewTodos = document.getElementById('view-todos');
  const viewChat = document.getElementById('view-chat');

  // Chat Elements
  const chatInput = document.getElementById('chat-input');
  const chatSendBtn = document.getElementById('chat-send');
  const chatHistory = document.getElementById('chat-history');

  const modelSelect = document.getElementById('model-select');
  const ragStatus = document.getElementById('rag-status');
  const ghostToggle = document.getElementById('ghost-toggle');
  const ghostStatus = document.getElementById('ghost-status');
  const focusToggle = document.getElementById('focus-toggle');
  const focusStatus = document.getElementById('focus-status');

  // Todo Elements
  const todoList = document.getElementById('todo-list');
  const todoInput = document.getElementById('todo-input');
  const addTodoBtn = document.getElementById('add-todo');

  const fillBtn = document.getElementById('fill-form');
  const monitorBtn = document.getElementById('monitor-page');
  const semanticSearch = document.getElementById('semantic-search');
  const piiShield = document.getElementById('pii-shield');
  const zeroData = document.getElementById('zero-data');

  let isGhostMode = false;
  let isFocusMode = false;

  // Load saved settings
  const settings = await chrome.storage.local.get(['apiUrl', 'token', 'selectedModel', 'piiShield', 'zeroData', 'isFocusMode']);
  apiUrlInput.value = settings.apiUrl || 'http://localhost:8001';
  tokenInput.value = settings.token || '';
  modelSelect.value = settings.selectedModel || 'local';
  piiShield.checked = settings.piiShield !== false;
  zeroData.checked = settings.zeroData === true;
  isFocusMode = settings.isFocusMode === true;
  updateFocusUI();

  const getHeaders = () => {
    const headers = { 'Content-Type': 'application/json' };
    if (tokenInput.value) headers['Authorization'] = `Bearer ${tokenInput.value}`;
    return headers;
  };

  // View Switching
  const switchView = (targetView) => {
    [viewActions, viewTodos, viewChat, settingsPanel].forEach(v => v.classList.remove('active'));
    [navActions, navTodos, navChat].forEach(n => n.classList.remove('active'));
    
    if (targetView === 'actions') { viewActions.classList.add('active'); navActions.classList.add('active'); }
    if (targetView === 'todos') { viewTodos.classList.add('active'); navTodos.classList.add('active'); fetchTodos(); }
    if (targetView === 'chat') { viewChat.classList.add('active'); navChat.classList.add('active'); }
    if (targetView === 'settings') { settingsPanel.classList.add('active'); }
  };

  navActions.addEventListener('click', () => switchView('actions'));
  navTodos.addEventListener('click', () => switchView('todos'));
  navChat.addEventListener('click', () => switchView('chat'));
  toggleBtn.addEventListener('click', () => switchView('settings'));

  // Todo Logic
  async function fetchTodos() {
    try {
      const response = await fetch(`${apiUrlInput.value}/todos`, { headers: getHeaders() });
      const todos = await response.json();
      renderTodos(todos);
    } catch (err) { console.error("Failed to fetch todos", err); }
  }

  function renderTodos(todos) {
    todoList.innerHTML = '';
    todos.forEach(todo => {
      const li = document.createElement('li');
      li.className = `todo-item ${todo.completed ? 'completed' : ''}`;
      li.innerHTML = `
        <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''}>
        <span class="todo-text">${todo.text}</span>
      `;
      li.querySelector('input').addEventListener('change', async () => {
        await fetch(`${apiUrlInput.value}/todos/${todo.id}`, {
          method: 'PATCH',
          headers: getHeaders(),
          body: JSON.stringify({ completed: !todo.completed })
        });
        fetchTodos();
      });
      todoList.appendChild(li);
    });
  }

  addTodoBtn.addEventListener('click', async () => {
    const text = todoInput.value.trim();
    if (!text) return;
    try {
      await fetch(`${apiUrlInput.value}/todos`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ text, category: 'personal' })
      });
      todoInput.value = '';
      fetchTodos();
    } catch (err) { console.error("Failed to add todo", err); }
  });

  // Toggle Focus Mode
  focusToggle.addEventListener('click', async () => {
    isFocusMode = !isFocusMode;
    await chrome.storage.local.set({ isFocusMode });
    updateFocusUI();
    showMsg(`Focus Mode ${isFocusMode ? 'ON' : 'OFF'}`, isFocusMode ? '#4ade80' : '#888');
  });

  function updateFocusUI() {
    focusStatus.innerText = isFocusMode ? 'ON' : 'OFF';
    focusToggle.style.color = isFocusMode ? '#4ade80' : '#888';
  }

  // Toggle Ghostwriter
  ghostToggle.addEventListener('click', () => {
    isGhostMode = !isGhostMode;
    ghostStatus.innerText = isGhostMode ? 'ON' : 'OFF';
    ghostToggle.style.color = isGhostMode ? '#4ade80' : '#ff79c6';
  });

  // Semantic Search
  semanticSearch.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
      const query = semanticSearch.value.trim();
      if (!query) return;
      showMsg('Searching Library...', '#bb86fc');
      try {
        const response = await fetch(`${apiUrlInput.value}/search/semantic`, {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({ query: query })
        });
        const data = await response.json();
        if (data.length > 0) {
          summaryText.innerText = `Top match: ${data[0].content.substring(0, 500)}...`;
          summaryBox.style.display = 'block';
        } else {
          showMsg("No direct matches found.", '#888');
        }
      } catch (err) { showMsg("Library Search failed.", '#cf6679'); }
    }
  });

  // Smart Form Fill
  fillBtn.addEventListener('click', async () => {
    setLoading(fillBtn, 'Predicting...');
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
          showMsg('Form filled. 📝', '#03dac6');
        }
      });
    } catch (err) { showMsg('Form Fill failed.', '#cf6679'); }
    finally { stopLoading(fillBtn, '📝 Smart Fill'); }
  });

  // Monitor Page
  monitorBtn.addEventListener('click', async () => {
    const condition = prompt("Condition to watch for? (e.g. 'price < $500')");
    if (!condition) return;
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await fetch(`${apiUrlInput.value}/automation/monitor`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ url: tab.url, trigger_condition: condition })
      });
      showMsg('Butler watching page. 👁️', '#bb86fc');
    } catch (err) { showMsg('Monitor failed.', '#cf6679'); }
  });

  // Privacy Settings Save
  saveBtn.addEventListener('click', async () => {
    await chrome.storage.local.set({
      apiUrl: apiUrlInput.value,
      token: tokenInput.value,
      piiShield: piiShield.checked,
      zeroData: zeroData.checked
    });
    switchView('actions');
    showMsg('Settings Synchronized. 🗝️', '#03dac6');
  });

  const syncNotion = document.getElementById('sync-notion');
  const syncSlack = document.getElementById('sync-slack');

  const formatMath = (text) => text.replace(/\$(.*?)\$/g, '<span class="math-tex">$1</span>');

  const triggerSync = async (platform) => {
    const btn = document.getElementById(`sync-${platform}`);
    setLoading(btn, 'Syncing...');
    try {
      await fetch(`${apiUrlInput.value}/automation/sync`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ platform: platform, context: window.pageContext })
      });
      showMsg(`${platform} Sync Successful. 🔗`, '#bb86fc');
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
    if (monologue) msgDiv.title = `Thought: ${monologue}`;
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
        addMessage("Connection failed.", 'ai');
      }
    } catch (err) {
      addMessage("Agent disconnected.", 'ai');
    }
  };

  chatSendBtn.addEventListener('click', handleChat);
  chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleChat(); });

  // Clip current page
  clipBtn.addEventListener('click', async () => {
    setLoading(clipBtn, 'Vaulting...');
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const response = await fetch(`${apiUrlInput.value}/ingest/clipper`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ url: tab.url })
      });
      if (response.ok) showMsg('Vaulted. ✨', '#03dac6');
      else showMsg('Auth Required. 🔐', '#cf6679');
    } catch (err) { showMsg('Connection refused. 📡', '#cf6679'); }
    finally { stopLoading(clipBtn, '✨ Vault'); }
  });

  // Summarize current page
  summarizeBtn.addEventListener('click', async () => {
    setLoading(summarizeBtn, 'Synthesizing...');
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
        showMsg('Distilled. 🧠', '#03dac6');
      } else showMsg('Failed.', '#cf6679');
    } catch (err) { showMsg('Agent disconnected.', '#cf6679'); }
    finally { stopLoading(summarizeBtn, '🧠 Synthesize'); }
  });

  targetBtn.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { action: "start_targeting" });
    showMsg('Click an element. 🎯', '#bb86fc');
    window.close();
  });

  const visualBtn = document.getElementById('visual-reason');
  const egoMirror = document.getElementById('ego-mirror');
  const egoMood = document.getElementById('ego-mood');
  const egoTraits = document.getElementById('ego-traits');

  visualBtn.addEventListener('click', async () => {
    setLoading(visualBtn, 'Vision...');
    chrome.runtime.sendMessage({ action: "capture_screenshot" }, (response) => {
      if (response && response.dataUrl) {
        chrome.runtime.sendMessage({ action: "visual_reasoning", payload: response.dataUrl });
        showMsg('Vision sent. 📷', '#03dac6');
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
    } catch (e) { }
  };
  syncDigitalEgo();

  function setLoading(btn, text) { btn.disabled = true; btn.innerText = text; }
  function stopLoading(btn, text) { btn.disabled = false; btn.innerText = text; }
  function showMsg(text, color) {
    msgEl.innerText = text; msgEl.style.color = color;
    setTimeout(() => { msgEl.innerText = ''; }, 3000);
  }

  const updateRagStatus = async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) return;
      chrome.tabs.sendMessage(tab.id, { action: "getPageContent" }, (response) => {
        if (response && response.content) {
          ragStatus.innerText = "Page Active";
          ragStatus.classList.add('rag-active');
          window.pageContext = response.content;
        } else {
          ragStatus.innerText = "Page Offline";
          ragStatus.classList.remove('rag-active');
        }
      });
    } catch (e) { ragStatus.innerText = "Bridge Offline"; }
  };
  setInterval(updateRagStatus, 5000);
  updateRagStatus();
});