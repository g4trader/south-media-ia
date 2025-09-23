/**
 * Integração da Interface com a API
 * Substitui as funções simuladas por chamadas reais à API
 */

// Configuração da API
const API_BASE_URL = 'https://dashboard-builder-6f3ckz7c7q-uc.a.run.app/api';

// Substituir função createDashboard no dashboard-builder-user-friendly.html
function createDashboard() {
    if (!validateStep(currentStep)) {
        return;
    }

    const createBtn = document.getElementById('create-btn');
    const loading = document.getElementById('create-loading');
    const text = document.getElementById('create-text');

    // Mostrar loading
    createBtn.disabled = true;
    loading.style.display = 'flex';
    text.style.display = 'none';

    // Coletar dados do formulário
    const formData = collectFormData();

    // Chamar API real
    fetch(`${API_BASE_URL}/dashboards`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess(`Dashboard "${data.dashboard.name}" criado com sucesso! 🎉`);
            
            // Mostrar informações do dashboard criado
            setTimeout(() => {
                const dashboardInfo = `
                    <div style="background: var(--dark); padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid var(--border);">
                        <h4>📊 Dashboard Criado</h4>
                        <p><strong>ID:</strong> ${data.dashboard.id}</p>
                        <p><strong>Status:</strong> ${data.dashboard.status}</p>
                        <p><strong>Arquivo:</strong> ${data.dashboard.html_file || 'Em processamento...'}</p>
                        <div style="margin-top: 1rem;">
                            <button class="btn btn-primary" onclick="viewDashboard('${data.dashboard.id}')">
                                👁️ Visualizar Dashboard
                            </button>
                            <button class="btn btn-secondary" onclick="downloadDashboard('${data.dashboard.id}')">
                                📥 Download
                            </button>
                        </div>
                    </div>
                `;
                
                const successDiv = document.getElementById('success-message');
                successDiv.innerHTML += dashboardInfo;
            }, 1000);
            
        } else {
            showError(`Erro ao criar dashboard: ${data.error}`);
            if (data.details) {
                console.error('Detalhes do erro:', data.details);
            }
        }
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
        showError('Erro de conexão com o servidor. Verifique se a API está rodando.');
    })
    .finally(() => {
        // Resetar loading
        createBtn.disabled = false;
        loading.style.display = 'none';
        text.style.display = 'inline';
    });
}

// Função para visualizar dashboard
function viewDashboard(dashboardId) {
    fetch(`${API_BASE_URL}/dashboards/${dashboardId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success && data.dashboard.html_file) {
            const dashboardUrl = `static/${data.dashboard.html_file}`;
            window.open(dashboardUrl, '_blank');
        } else {
            showError('Dashboard não encontrado ou ainda não foi processado.');
        }
    })
    .catch(error => {
        console.error('Erro ao obter dashboard:', error);
        showError('Erro ao carregar dashboard.');
    });
}

// Função para download do dashboard
function downloadDashboard(dashboardId) {
    fetch(`${API_BASE_URL}/dashboards/${dashboardId}/download`)
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Erro no download');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dashboard_${dashboardId}.html`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Erro no download:', error);
        showError('Erro ao fazer download do dashboard.');
    });
}

// Função para validar dashboard
function validateDashboard(dashboardId) {
    fetch(`${API_BASE_URL}/dashboards/${dashboardId}/validate`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Dashboard validado com sucesso!');
        } else {
            showError(`Erro ao validar dashboard: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Erro ao validar dashboard:', error);
        showError('Erro ao validar dashboard.');
    });
}

// Função para ativar dashboard
function activateDashboard(dashboardId) {
    fetch(`${API_BASE_URL}/dashboards/${dashboardId}/activate`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Dashboard ativado com sucesso!');
        } else {
            showError(`Erro ao ativar dashboard: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Erro ao ativar dashboard:', error);
        showError('Erro ao ativar dashboard.');
    });
}

// Função para listar dashboards existentes
function loadExistingDashboards() {
    fetch(`${API_BASE_URL}/dashboards`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayExistingDashboards(data.dashboards);
        } else {
            console.error('Erro ao carregar dashboards:', data.error);
        }
    })
    .catch(error => {
        console.error('Erro ao carregar dashboards:', error);
    });
}

// Função para exibir dashboards existentes
function displayExistingDashboards(dashboards) {
    const container = document.getElementById('existing-dashboards');
    if (!container) return;

    if (dashboards.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 2rem;">Nenhum dashboard criado ainda.</p>';
        return;
    }

    const dashboardsHTML = dashboards.map(dashboard => `
        <div class="dashboard-card" style="background: var(--dark); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                <h4 style="color: var(--primary); margin: 0;">${dashboard.name}</h4>
                <span class="status-badge status-${dashboard.status}" style="padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">
                    ${getStatusText(dashboard.status)}
                </span>
            </div>
            <p style="color: var(--text-muted); margin: 0 0 1rem 0; font-size: 0.9rem;">
                Criado em: ${new Date(dashboard.created_at).toLocaleString('pt-BR')}
            </p>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <button class="btn btn-primary" onclick="viewDashboard('${dashboard.id}')" style="font-size: 0.8rem; padding: 0.5rem 1rem;">
                    👁️ Visualizar
                </button>
                <button class="btn btn-secondary" onclick="downloadDashboard('${dashboard.id}')" style="font-size: 0.8rem; padding: 0.5rem 1rem;">
                    📥 Download
                </button>
                ${dashboard.status === 'created' ? `
                    <button class="btn btn-success" onclick="validateDashboard('${dashboard.id}')" style="font-size: 0.8rem; padding: 0.5rem 1rem;">
                        ✅ Validar
                    </button>
                ` : ''}
                ${dashboard.status === 'validated' ? `
                    <button class="btn btn-success" onclick="activateDashboard('${dashboard.id}')" style="font-size: 0.8rem; padding: 0.5rem 1rem;">
                        🚀 Ativar
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');

    container.innerHTML = dashboardsHTML;
}

// Função para obter texto do status
function getStatusText(status) {
    const statusMap = {
        'created': 'Criado',
        'validated': 'Validado',
        'active': 'Ativo'
    };
    return statusMap[status] || status;
}

// Função para testar conexão com a API
function testAPIConnection() {
    fetch(`${API_BASE_URL.replace('/api', '')}/health`)
    .then(response => response.json())
    .then(data => {
        if (data.status === 'healthy') {
            console.log('✅ API conectada com sucesso');
            console.log('📊 Google Sheets:', data.sheets_available ? 'Disponível' : 'Não disponível');
        } else {
            console.warn('⚠️ API respondeu mas não está saudável');
        }
    })
    .catch(error => {
        console.error('❌ Erro ao conectar com a API:', error);
        showError('Não foi possível conectar com a API. Verifique se o servidor está rodando na porta 8081.');
    });
}

// Adicionar seção de dashboards existentes ao HTML
function addExistingDashboardsSection() {
    const wizardContent = document.querySelector('.wizard-content');
    if (!wizardContent) return;

    const existingSection = document.createElement('div');
    existingSection.innerHTML = `
        <div class="form-section">
            <h3>📊 Dashboards Existentes</h3>
            <div id="existing-dashboards" style="max-height: 400px; overflow-y: auto;">
                <div class="loading" style="text-align: center; padding: 2rem;">
                    <div class="spinner"></div>
                    <p>Carregando dashboards...</p>
                </div>
            </div>
            <button class="btn btn-secondary" onclick="loadExistingDashboards()" style="margin-top: 1rem;">
                🔄 Atualizar Lista
            </button>
        </div>
    `;

    wizardContent.insertBefore(existingSection, wizardContent.firstChild);
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Testar conexão com a API
    testAPIConnection();
    
    // Adicionar seção de dashboards existentes
    addExistingDashboardsSection();
    
    // Carregar dashboards existentes
    loadExistingDashboards();
});

// Adicionar estilos para os status badges
const statusStyles = `
    <style>
        .status-created {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
            border: 1px solid #3b82f6;
        }
        .status-validated {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid #10b981;
        }
        .status-active {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid #f59e0b;
        }
    </style>
`;

// Adicionar estilos ao head
document.head.insertAdjacentHTML('beforeend', statusStyles);
