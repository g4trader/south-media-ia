/**
 * Dashboard Control Panel - JavaScript
 * Sistema de controle centralizado para dashboards automatizados
 */

class DashboardControlPanel {
    constructor() {
        this.dashboards = [];
        this.dashboardStates = {};
        this.config = null;
        this.init();
    }

    async init() {
        try {
            await this.loadConfig();
            this.loadDashboards();
            this.updatePanelTimestamp();
            
            // Atualizar status a cada 30 segundos
            setInterval(() => this.updateAllStatuses(), 30000);
            
            console.log('🎛️ Painel de Controle inicializado com sucesso');
        } catch (error) {
            console.error('❌ Erro ao inicializar painel:', error);
        }
    }

    async loadConfig() {
        try {
            const response = await fetch('dashboard_config.json');
            this.config = await response.json();
            this.dashboards = this.config.dashboards;
        } catch (error) {
            console.warn('⚠️ Não foi possível carregar config.json, usando configuração padrão');
            this.loadDefaultConfig();
        }
    }

    loadDefaultConfig() {
        this.config = {
            dashboards: [
                {
                    id: 'south-media-dashboard',
                    name: 'South Media Dashboard',
                    url: 'https://dash.iasouth.tech/static/dash_sonho.html',
                    thumbnail: '📊',
                    services: {
                        channels: {
                            name: 'Atualização de Canais',
                            endpoint: 'https://dashboard-automation-6f3ckz7c7q-uc.a.run.app/trigger',
                            statusEndpoint: 'https://dashboard-automation-6f3ckz7c7q-uc.a.run.app/status'
                        },
                        footfall: {
                            name: 'Atualização de Footfall',
                            endpoint: 'https://footfall-automation-609095880025.us-central1.run.app/trigger',
                            statusEndpoint: 'https://footfall-automation-609095880025.us-central1.run.app/status'
                        }
                    }
                }
            ],
            panel: {
                autoRefresh: 30000
            }
        };
        this.dashboards = this.config.dashboards;
    }

    loadDashboards() {
        const grid = document.getElementById('dashboardGrid');
        grid.innerHTML = '';

        this.dashboards.forEach(dashboard => {
            const card = this.createDashboardCard(dashboard);
            grid.appendChild(card);
            
            // Inicializar estado
            this.dashboardStates[dashboard.id] = {
                status: 'unknown',
                lastUpdate: null,
                isUpdating: false,
                logs: []
            };
        });

        // Carregar status inicial
        this.updateAllStatuses();
    }

    createDashboardCard(dashboard) {
        const card = document.createElement('div');
        card.className = 'dashboard-card';
        card.id = `card-${dashboard.id}`;

        card.innerHTML = `
            <div class="dashboard-header">
                <div class="thumbnail">${dashboard.thumbnail}</div>
                <div class="dashboard-info">
                    <div class="dashboard-name">${dashboard.name}</div>
                    <a href="${dashboard.url}" target="_blank" class="dashboard-url">${dashboard.url}</a>
                </div>
            </div>
            
            <div class="dashboard-actions">
                <button class="sync-btn" onclick="controlPanel.syncDashboard('${dashboard.id}')" id="sync-${dashboard.id}">
                    <span class="sync-icon">🔄</span>
                    Sincronizar
                </button>
                <a href="${dashboard.url}" target="_blank" class="view-btn">
                    <span>👁️</span>
                    Visualizar
                </a>
            </div>
            
            <div class="status-section" id="status-${dashboard.id}">
                <div class="status-label">Status</div>
                <div class="status-value" id="status-value-${dashboard.id}">Verificando...</div>
                <div class="last-update" id="last-update-${dashboard.id}">Última atualização: Aguardando...</div>
            </div>
            
            <div class="logs-section" id="logs-${dashboard.id}">
                <div class="log-entry info">Sistema inicializado</div>
            </div>
        `;

        return card;
    }

    async syncDashboard(dashboardId) {
        const dashboard = this.dashboards.find(d => d.id === dashboardId);
        if (!dashboard) return;

        const syncBtn = document.getElementById(`sync-${dashboardId}`);
        const card = document.getElementById(`card-${dashboardId}`);
        const statusValue = document.getElementById(`status-value-${dashboardId}`);
        const lastUpdate = document.getElementById(`last-update-${dashboardId}`);
        const statusSection = document.getElementById(`status-${dashboardId}`);

        // Atualizar UI para estado de atualização
        this.setUpdatingState(dashboardId, true);
        syncBtn.disabled = true;
        syncBtn.classList.add('updating');
        card.classList.add('updating');
        statusValue.textContent = 'Atualizando...';
        statusValue.classList.add('updating');
        statusSection.classList.remove('error');
        statusSection.classList.add('updating');

        // Adicionar log
        this.addLog(dashboardId, 'info', 'Iniciando sincronização...');

        try {
            const results = await this.performSync(dashboard);
            const overallSuccess = results.every(result => result.success);
            
            if (overallSuccess) {
                this.setSuccessState(dashboardId, statusValue, statusSection);
                this.addLog(dashboardId, 'success', 'Sincronização completa!');
            } else {
                this.setErrorState(dashboardId, statusValue, statusSection);
                this.addLog(dashboardId, 'error', 'Sincronização com erros');
            }

            // Atualizar timestamp
            const now = new Date();
            const timestamp = now.toLocaleString('pt-BR');
            lastUpdate.textContent = `Última atualização: ${timestamp}`;

            // Atualizar estado
            this.dashboardStates[dashboardId] = {
                status: overallSuccess ? 'updated' : 'error',
                lastUpdate: now,
                isUpdating: false,
                logs: this.dashboardStates[dashboardId].logs.slice(-10)
            };

        } catch (error) {
            this.setErrorState(dashboardId, statusValue, statusSection);
            this.addLog(dashboardId, 'error', `Erro na sincronização: ${error.message}`);
            
            this.dashboardStates[dashboardId] = {
                ...this.dashboardStates[dashboardId],
                status: 'error',
                isUpdating: false
            };
        } finally {
            this.setUpdatingState(dashboardId, false);
            syncBtn.disabled = false;
            syncBtn.classList.remove('updating');
            card.classList.remove('updating');
        }
    }

    async performSync(dashboard) {
        const results = [];
        
        // Sequência de atualizações
        const services = [
            { name: 'channels', endpoint: dashboard.services.channels.endpoint },
            { name: 'footfall', endpoint: dashboard.services.footfall.endpoint }
        ];

        for (const service of services) {
            this.addLog(dashboard.id, 'info', `Atualizando ${service.name}...`);
            
            try {
                const result = await this.triggerServiceUpdate(service.endpoint);
                results.push(result);
                
                if (result.success) {
                    this.addLog(dashboard.id, 'success', `${service.name} atualizado com sucesso`);
                } else {
                    this.addLog(dashboard.id, 'error', `Erro em ${service.name}: ${result.error}`);
                }
                
                // Aguardar 2 segundos entre as atualizações
                await new Promise(resolve => setTimeout(resolve, 2000));
                
            } catch (error) {
                results.push({ success: false, error: error.message });
                this.addLog(dashboard.id, 'error', `Erro em ${service.name}: ${error.message}`);
            }
        }

        return results;
    }

    async triggerServiceUpdate(endpoint) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ test_mode: false })
            });

            const result = await response.json();
            
            if (response.ok) {
                // Para footfall, verificar se success é true
                if (result.success !== undefined) {
                    return { success: result.success, data: result };
                }
                return { success: true, data: result };
            } else {
                return { success: false, error: result.message || 'Erro desconhecido' };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    setUpdatingState(dashboardId, isUpdating) {
        this.dashboardStates[dashboardId].isUpdating = isUpdating;
    }

    setSuccessState(dashboardId, statusValue, statusSection) {
        statusValue.textContent = 'Atualizado';
        statusValue.classList.remove('updating', 'error');
        statusSection.classList.remove('updating', 'error');
    }

    setErrorState(dashboardId, statusValue, statusSection) {
        statusValue.textContent = 'Erro na atualização';
        statusValue.classList.remove('updating');
        statusValue.classList.add('error');
        statusSection.classList.remove('updating');
        statusSection.classList.add('error');
    }

    addLog(dashboardId, type, message) {
        const logsContainer = document.getElementById(`logs-${dashboardId}`);
        const timestamp = new Date().toLocaleTimeString('pt-BR');
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> ${message}`;
        
        logsContainer.appendChild(logEntry);
        logsContainer.scrollTop = logsContainer.scrollHeight;

        // Manter apenas últimas 20 entradas
        const entries = logsContainer.querySelectorAll('.log-entry');
        if (entries.length > 20) {
            entries[0].remove();
        }
    }

    async updateAllStatuses() {
        for (const dashboard of this.dashboards) {
            await this.updateDashboardStatus(dashboard.id);
        }
    }

    async updateDashboardStatus(dashboardId) {
        const dashboard = this.dashboards.find(d => d.id === dashboardId);
        if (!dashboard) return;

        const statusValue = document.getElementById(`status-value-${dashboardId}`);
        const lastUpdate = document.getElementById(`last-update-${dashboardId}`);
        const statusSection = document.getElementById(`status-${dashboardId}`);

        try {
            // Verificar status dos serviços
            const [channelsStatus, footfallStatus] = await Promise.all([
                this.checkServiceStatus(dashboard.services.channels.statusEndpoint),
                this.checkServiceStatus(dashboard.services.footfall.statusEndpoint)
            ]);

            const overallStatus = channelsStatus && footfallStatus ? 'operational' : 'error';
            
            if (overallStatus === 'operational') {
                statusValue.textContent = 'Operacional';
                statusValue.classList.remove('error', 'updating');
                statusSection.classList.remove('error', 'updating');
            } else {
                statusValue.textContent = 'Serviço indisponível';
                statusValue.classList.remove('updating');
                statusValue.classList.add('error');
                statusSection.classList.remove('updating');
                statusSection.classList.add('error');
            }

            // Atualizar timestamp se não foi atualizado recentemente
            const state = this.dashboardStates[dashboardId];
            if (state && state.lastUpdate && !state.isUpdating) {
                const timestamp = state.lastUpdate.toLocaleString('pt-BR');
                lastUpdate.textContent = `Última atualização: ${timestamp}`;
            }

        } catch (error) {
            statusValue.textContent = 'Erro na verificação';
            statusValue.classList.add('error');
            statusSection.classList.add('error');
        }
    }

    async checkServiceStatus(statusEndpoint) {
        try {
            const response = await fetch(statusEndpoint, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    updatePanelTimestamp() {
        const now = new Date();
        document.getElementById('panelLastUpdate').textContent = now.toLocaleString('pt-BR');
    }

    addNewDashboard() {
        alert('Funcionalidade de adicionar novo dashboard será implementada em breve!');
    }
}

// Instanciar painel quando a página carregar
let controlPanel;
document.addEventListener('DOMContentLoaded', () => {
    controlPanel = new DashboardControlPanel();
});

// Função global para compatibilidade
function addNewDashboard() {
    controlPanel.addNewDashboard();
}
