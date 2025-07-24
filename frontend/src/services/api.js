const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.iasouth.tech/api'
  : 'https://8080-ibb8c5dgcr7sbiz6k13da-be6dae4d.manusvm.computer/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = localStorage.getItem('token');

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

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

  async me() {
    return this.request('/auth/me');
  }

  // Novos métodos para vídeo
  async getVideoCampaigns() {
    return this.request('/dashboard/video/campaigns');
  }

  async getVideoCampaignDashboard(campaignId) {
    return this.request(`/dashboard/video/campaign/${campaignId}`);
  }

  async getVideoFormatsComparison() {
    return this.request('/dashboard/video/formats/comparison');
  }
}

const apiService = new ApiService();

const authService = {
  login: (username, password) => apiService.login({ username, password }),
  logout: () => apiService.logout(),
  me: () => apiService.me(),
};

export { authService };
export default apiService;

