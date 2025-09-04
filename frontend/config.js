// Configuration file for South Media IA Frontend
const config = {
  // API Configuration
  api: {
    baseURL: process.env.REACT_APP_API_URL || 'https://api.iasouth.tech/api',
    timeout: 30000,
  },
  
  // Vercel Configuration
  vercel: {
    token: process.env.REACT_APP_VERCEL_TOKEN || '5w8zipRxMJnLEET9OMESteB7',
    projectId: 'south-media-ia',
  },
  
  // GitHub Configuration
  github: {
    token: process.env.REACT_APP_GITHUB_TOKEN || 'REPLACED_TOKEN',
    repo: 'south-media-ia',
    owner: 'your-github-username', // Update this with your actual GitHub username
  },
  
  // App Configuration
  app: {
    name: 'South Media IA',
    version: '3.0.0',
    environment: process.env.NODE_ENV || 'development',
    debug: process.env.REACT_APP_DEBUG === 'true',
  },
  
  // Authentication
  auth: {
    tokenKey: 'south_media_token',
    userKey: 'south_media_user',
  },
};

export default config;
