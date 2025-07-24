const API_BASE_URL = 'https://api.iasouth.tech/api';

const getToken = () => {
  return localStorage.getItem('token');
};

const request = async (endpoint, method = 'GET', data = null, isPrivate = false) => {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (isPrivate) {
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const options = {
    method,
    headers,
    body: data ? JSON.stringify(data) : null,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const responseData = await response.json();

    if (!response.ok) {
      throw new Error(responseData.detail || 'Erro na requisição.');
    }

    return responseData;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

const authService = {
  login: async (username, password) => {
    return request('/auth/login', 'POST', { username, password });
  },
};

const dashboardService = {
  getSummary: async () => {
    return request('/dashboard/resumo', 'GET', null, true);
  },
  getCampaign: async () => {
    return request('/dashboard/campanha', 'GET', null, true);
  },
};

export default {
  authService,
  dashboardService,
};
