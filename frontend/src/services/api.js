const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('token');
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erro na requisição' }));
    const errorObj = new Error(error.detail || 'Erro na requisição');
    errorObj.response = { data: error, status: response.status };
    throw errorObj;
  }

  return { data: await response.json() };
};

// Auth Service
export const authService = {
  login: (username, password) =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
  
  me: () => apiRequest('/auth/me'),
};

// Client Service
export const clientService = {
  getAll: () => apiRequest('/clients'),
  getById: (id) => apiRequest(`/clients/${id}`),
  create: (data) => apiRequest('/clients', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => apiRequest(`/clients/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => apiRequest(`/clients/${id}`, { method: 'DELETE' }),
};

// Campaign Service
export const campaignService = {
  getAll: () => apiRequest('/campaigns'),
  getById: (id) => apiRequest(`/campaigns/${id}`),
  getByClient: (clientId) => apiRequest(`/campaigns/client/${clientId}`),
  create: (data) => apiRequest('/campaigns', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => apiRequest(`/campaigns/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => apiRequest(`/campaigns/${id}`, { method: 'DELETE' }),
};

// Dashboard Service
export const dashboardService = {
  getStats: () => apiRequest('/dashboard/stats'),
  getClientDashboard: (clientId, campaignId) => 
    apiRequest(`/dashboard/client/${clientId}/campaign/${campaignId}`),
};

