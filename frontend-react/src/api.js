const API_BASE_URL = 'http://localhost:8001';

export const fetchArtifacts = async (userId = 'system_user') => {
  const response = await fetch(`${API_BASE_URL}/artifacts?user_id=${userId}`);
  if (!response.ok) throw new Error('Failed to fetch artifacts');
  return response.json();
};

export const updateUserSettings = async (settings, userId = 'system_user') => {
  const response = await fetch(`${API_BASE_URL}/user/settings?user_id=${userId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!response.ok) throw new Error('Failed to update settings');
  return response.json();
};

export const fetchPsychologyProfile = async (userId = 'system_user') => {
  const response = await fetch(`${API_BASE_URL}/user/psychology?user_id=${userId}`);
  if (!response.ok) throw new Error('Failed to fetch psychology profile');
  return response.json();
};

export const fetchAnalytics = async (userId = 'system_user') => {
  const response = await fetch(`${API_BASE_URL}/analytics?user_id=${userId}`);
  if (!response.ok) throw new Error('Failed to fetch analytics');
  return response.json();
};

export const fetchGraphTopology = async (userId = 'system_user') => {
  const response = await fetch(`${API_BASE_URL}/analytics/graph/topology?user_id=${userId}`);
  if (!response.ok) throw new Error('Failed to fetch graph topology');
  return response.json();
};

export const ingestUrl = async (url, userId = 'system_user') => {
  const response = await fetch(`${API_BASE_URL}/ingest/clipper`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, user_id: userId }),
  });
  if (!response.ok) throw new Error('Failed to ingest URL');
  return response.json();
};

export const streamChat = async (query, onToken, userId = 'system_user') => {
  const response = await fetch(`${API_BASE_URL}/query/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, user_id: userId }),
  });

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
  return fullContent;
};

// --- Action Engine (Butler) ---
export const runActionGoal = async (goal, userId = 'system_user') => {
  const response = await fetch(`${API_BASE_URL}/actions/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal, user_id: userId }),
  });
  if (!response.ok) throw new Error('Failed to run action goal');
  return response.json();
};

export const fetchActionHistory = async (userId = 'system_user') => {
  const response = await fetch(`${API_BASE_URL}/actions/history?user_id=${userId}`);
  if (!response.ok) throw new Error('Failed to fetch action history');
  return response.json();
};

// --- Local Code Interpreter ---
export const runLocalCode = async (script) => {
  const response = await fetch(`${API_BASE_URL}/interpreter/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ script }),
  });
  if (!response.ok) throw new Error('Failed to run code');
  return response.json();
};

// --- Self-Improving AI (Feedback) ---
export const sendAIFeedback = async (agentName, feedback) => {
  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ agent_name: agentName, feedback }),
  });
  if (!response.ok) throw new Error('Failed to send feedback');
  return response.json();
};
