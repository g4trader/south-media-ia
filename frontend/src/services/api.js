
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.iasouth.tech/api'
  : 'http://localhost:8080/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async logout() {
    return this.request('/auth/logout', {
      method: 'POST',
    });
  }

  async getAdminStats() {
    return this.request('/dashboard/admin/stats');
  }

  async getAdminClients() {
    return this.request('/dashboard/admin/clients');
  }

  async getClientCampaigns(clientId) {
    return this.request(`/dashboard/admin/clients/${clientId}/campaigns`);
  }

  async getCampaignDashboard(campaignId) {
    return this.request(`/dashboard/campaign/${campaignId}`);
  }

  async getUsers() {
    return this.request('/users');
  }

  async createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(userId, userData) {
    return this.request(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(userId) {
    return this.request(`/users/${userId}`, {
      method: 'DELETE',
    });
  }
}

<<<<<<< HEAD
// Auth service instance
export const authService = {
  async login(username, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao fazer login');
    }

    return await response.json();
  },

  async me() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Token inválido');
    }

    return await response.json();
  }
};

export default new ApiService();
=======
const apiService = new ApiService();
>>>>>>> dc356a268fbf4d4ad9599f21ae3b52af8d0b3cce

const authService = {
  login: (username, password) => apiService.login({ username, password }),
  logout: () => apiService.logout(),
};

export { authService };
export default apiService;
