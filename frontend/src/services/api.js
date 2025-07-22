const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://south-media-ia-backend-609095880025.us-central1.run.app/api'
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

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Auth methods
  async login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async logout() {
    return this.request('/auth/logout', {
      method: 'POST',
    });
  }

  // Admin Dashboard methods
  async getAdminStats() {
    return this.request('/dashboard/admin/stats');
  }

  async getClients() {
    return this.request('/dashboard/admin/clients');
  }

  async getClientCampaigns(clientId) {
    return this.request(`/dashboard/admin/clients/${clientId}/campaigns`);
  }

  // Campaign Dashboard methods
  async getCampaignDashboard(campaignId) {
    return this.request(`/dashboard/campaign/${campaignId}`);
  }

  async getCampaignStrategies(campaignId) {
    return this.request(`/dashboard/campaign/${campaignId}/strategies`);
  }

  async getCampaignDeviceBreakdown(campaignId) {
    return this.request(`/dashboard/campaign/${campaignId}/device-breakdown`);
  }

  async getCampaignPerformanceHistory(campaignId) {
    return this.request(`/dashboard/campaign/${campaignId}/performance-history`);
  }

  // User management methods
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

const authService = new ApiService();
export default authService;
export { authService };
