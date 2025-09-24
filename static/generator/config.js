/**
 * Configuração do Sistema de Geração de Dashboards
 * Integração Vercel + Google Cloud Run
 */

const CONFIG = {
    // URLs dos serviços
    CLOUD_RUN_URL: 'https://south-media-ia-609095880025.us-central1.run.app',
    VERCEL_URL: window.location.origin,
    
    // Detectar ambiente
    isVercel: () => window.location.hostname.includes('vercel.app'),
    isCloudRun: () => window.location.hostname.includes('run.app'),
    isLocal: () => window.location.hostname.includes('localhost'),
    
    // URLs da API
    getApiUrl: (endpoint) => {
        const baseUrl = CONFIG.isVercel() ? CONFIG.CLOUD_RUN_URL : CONFIG.VERCEL_URL;
        return `${baseUrl}${endpoint}`;
    },
    
    // URLs de dashboards
    getDashboardUrl: (dashboardPath) => {
        if (CONFIG.isVercel()) {
            return `${CONFIG.CLOUD_RUN_URL}${dashboardPath}`;
        }
        return dashboardPath;
    },
    
    // Configurações de timeout
    API_TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3,
    
    // Endpoints da API
    ENDPOINTS: {
        GENERATE_DASHBOARD: '/api/generate-dashboard',
        CAMPAIGNS: '/api/campaigns',
        CAMPAIGN_DATA: '/api/{campaign_key}/data'
    }
};

// Função para fazer requisições com retry
async function apiRequest(url, options = {}, retryCount = 0) {
    try {
        const response = await fetch(url, {
            ...options,
            timeout: CONFIG.API_TIMEOUT
        });
        
        if (!response.ok && retryCount < CONFIG.RETRY_ATTEMPTS) {
            console.warn(`Tentativa ${retryCount + 1} falhou, tentando novamente...`);
            await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
            return apiRequest(url, options, retryCount + 1);
        }
        
        return response;
    } catch (error) {
        if (retryCount < CONFIG.RETRY_ATTEMPTS) {
            console.warn(`Erro na tentativa ${retryCount + 1}, tentando novamente...`);
            await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
            return apiRequest(url, options, retryCount + 1);
        }
        throw error;
    }
}

// Função para processar resposta JSON com tratamento de erro
async function processJsonResponse(response) {
    try {
        return await response.json();
    } catch (error) {
        console.error('Erro ao processar resposta JSON:', error);
        throw new Error(`Resposta inválida do servidor (${response.status}): ${response.statusText}`);
    }
}

// Exportar para uso global
window.CONFIG = CONFIG;
window.apiRequest = apiRequest;
window.processJsonResponse = processJsonResponse;
