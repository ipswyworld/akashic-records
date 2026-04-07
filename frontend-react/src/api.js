const API_BASE_URL = 'http://localhost:8001';

const getHeaders = (isJson = true) => {
  const token = localStorage.getItem('akasha_token');
  const headers = {};
  if (isJson) headers['Content-Type'] = 'application/json';
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
};

// --- Auth ---
export const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Invalid credentials');
  const data = await response.json();
  localStorage.setItem('akasha_token', data.access_token);
  return data;
};

export const signup = async (username, email, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  });
  if (!response.ok) throw new Error('Signup failed');
  const data = await response.json();
  localStorage.setItem('akasha_token', data.access_token);
  return data;
};

export const logout = () => {
  localStorage.removeItem('akasha_token');
  window.location.reload();
};

// --- Artifacts ---
export const fetchArtifacts = async () => {
  const response = await fetch(`${API_BASE_URL}/artifacts`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch artifacts');
  return response.json();
};

export const fetchUserSettings = async () => {
  const response = await fetch(`${API_BASE_URL}/user/settings`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch settings');
  return response.json();
};

export const updateUserSettings = async (settings) => {
  const response = await fetch(`${API_BASE_URL}/user/settings`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(settings),
  });
  if (!response.ok) throw new Error('Failed to update settings');
  return response.json();
};

export const fetchPsychologyProfile = async () => {
  const response = await fetch(`${API_BASE_URL}/user/psychology`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch psychology profile');
  return response.json();
};

export const fetchAnalytics = async () => {
  const response = await fetch(`${API_BASE_URL}/analytics`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch analytics');
  return response.json();
};

export const fetchGraphTopology = async () => {
  const response = await fetch(`${API_BASE_URL}/analytics/graph/topology`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch graph topology');
  return response.json();
};

export const ingestUrl = async (url) => {
  const response = await fetch(`${API_BASE_URL}/ingest/clipper`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ url }),
  });
  if (!response.ok) throw new Error('Failed to ingest URL');
  return response.json();
};

// --- Project Flash: Client-Side Reflex Cache ---
const REFLEX_CACHE_KEY = 'akasha_reflex_cache';

const getReflexCache = () => {
  const cached = localStorage.getItem(REFLEX_CACHE_KEY);
  return cached ? JSON.parse(cached) : {};
};

const storeInReflexCache = (query, response) => {
  const cache = getReflexCache();
  cache[query.toLowerCase().trim()] = response;
  // Keep only last 50 items
  const keys = Object.keys(cache);
  if (keys.length > 50) delete cache[keys[0]];
  localStorage.setItem(REFLEX_CACHE_KEY, JSON.stringify(cache));
};

export const streamChat = async (query, onToken) => {
  const q = query.toLowerCase().trim();
  const cache = getReflexCache();
  
  // 1. Instant Reflex Hit (<1ms)
  if (cache[q]) {
    console.log("Project Flash: Client Reflex HIT.");
    onToken(cache[q], cache[q]);
    return cache[q];
  }

  const response = await fetch(`${API_BASE_URL}/query/stream`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ query }),
  });
  
  // ... (rest of the streaming logic)
  if (!response.ok) throw new Error('Failed to start stream');

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullContent = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const token = decoder.decode(value, { stream: true });
    fullContent += token;
    onToken(token, fullContent);
  }
  
  // Store in reflex cache for next time
  storeInReflexCache(query, fullContent);
  return fullContent;
};

// --- Action Engine (Butler) ---
export const runActionGoal = async (goal) => {
  const response = await fetch(`${API_BASE_URL}/actions/run`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ goal }),
  });
  if (!response.ok) throw new Error('Failed to run action goal');
  return response.json();
};

export const fetchActionHistory = async () => {
  const response = await fetch(`${API_BASE_URL}/actions/history`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch action history');
  return response.json();
};

// --- Local Code Interpreter ---
export const runLocalCode = async (script) => {
  const response = await fetch(`${API_BASE_URL}/interpreter/run`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ script }),
  });
  if (!response.ok) throw new Error('Failed to run code');
  return response.json();
};

// --- P2P Neural Mesh ---
export const fetchP2PStatus = async () => {
  const response = await fetch(`${API_BASE_URL}/p2p/status`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch P2P status');
  return response.json();
};

export const toggleP2PStealth = async (enabled) => {
  const response = await fetch(`${API_BASE_URL}/p2p/stealth`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ enabled }),
  });
  if (!response.ok) throw new Error('Failed to toggle stealth mode');
  return response.json();
};

export const fetchEvolutionAnalytics = async () => {
  const response = await fetch(`${API_BASE_URL}/analytics/evolution`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch evolution analytics');
  return response.json();
};

export const triggerMutation = async (filePath, instruction) => {
  const response = await fetch(`${API_BASE_URL}/forge/mutate`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ file_path: filePath, instruction }),
  });
  if (!response.ok) throw new Error('Mutation failed');
  return response.json();
};

export const fetchNeuralSkills = async () => {
  const response = await fetch(`${API_BASE_URL}/forge/skills`, {
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch neural skills');
  return response.json();
};

export const speakText = async (text) => {
  const response = await fetch(`${API_BASE_URL}/voice/speak`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ text }),
  });
  if (!response.ok) throw new Error('Failed to speak');
  return response.json();
};

// --- Self-Improving AI (Feedback) ---
export const sendAIFeedback = async (agentName, feedback) => {
  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ agent_name: agentName, feedback }),
  });
  if (!response.ok) throw new Error('Failed to send feedback');
  return response.json();
};
