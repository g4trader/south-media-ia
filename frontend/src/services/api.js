
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://api.iasouth.tech/api'
  : 'http://localhost:8080/api';

async function request(endpoint, method = 'GET', body = null, token = null) {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
    credentials: 'include',
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}

const authService = {
  login: (username, password) =>
    request('/auth/login', 'POST', { username, password }),
  logout: () => request('/auth/logout', 'POST'),
};

export default authService;
export { authService };
