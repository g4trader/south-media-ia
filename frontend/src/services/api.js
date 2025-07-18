const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Função auxiliar para fazer requisições
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
    throw { response: { data: error, status: response.status } };
  }

  return { data: await response.json() };
};

// Serviços de autenticação
export const authService = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    return apiRequest('/auth/login', {
      method: 'POST',
      headers: {},
      body: formData,
    });
  },

  me: async () => {
    return apiRequest('/auth/me');
  },
};

// Serviços de clientes
export const clientService = {
  getAll: async () => {
    return apiRequest('/admin/clients');
  },

  create: async (clientData) => {
    return apiRequest('/admin/clients', {
      method: 'POST',
      body: JSON.stringify(clientData),
    });
  },

  update: async (clientId, clientData) => {
    return apiRequest(`/admin/clients/${clientId}`, {
      method: 'PUT',
      body: JSON.stringify(clientData),
    });
  },

  delete: async (clientId) => {
    return apiRequest(`/admin/clients/${clientId}`, {
      method: 'DELETE',
    });
  },

  getDashboard: async (clientId) => {
    return apiRequest(`/client/${clientId}/dashboard`);
  },
};

// Serviços de campanhas
export const campaignService = {
  getAll: async () => {
    return apiRequest('/admin/campaigns');
  },

  create: async (campaignData) => {
    return apiRequest('/admin/campaigns', {
      method: 'POST',
      body: JSON.stringify(campaignData),
    });
  },

  update: async (campaignId, campaignData) => {
    return apiRequest(`/admin/campaigns/${campaignId}`, {
      method: 'PUT',
      body: JSON.stringify(campaignData),
    });
  },

  delete: async (campaignId) => {
    return apiRequest(`/admin/campaigns/${campaignId}`, {
      method: 'DELETE',
    });
  },

  getDetails: async (clientId, campaignId) => {
    return apiRequest(`/client/${clientId}/campaign/${campaignId}`);
  },

  uploadPerformanceData: async (campaignId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    return apiRequest(`/admin/campaigns/${campaignId}/upload-data`, {
      method: 'POST',
      headers: {},
      body: formData,
    });
  },
};

// Serviços administrativos
export const adminService = {
  getStats: async () => {
    return apiRequest('/admin/stats');
  },
};

