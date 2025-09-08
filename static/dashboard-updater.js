/**
 * Dashboard Data Updater
 * Sistema de atualização dinâmica dos dados do dashboard
 */

class DashboardUpdater {
    constructor() {
        this.apiUrl = 'http://localhost:8000/api/dashboard';
        this.updateInterval = 5 * 60 * 1000; // 5 minutos
        this.retryInterval = 30 * 1000; // 30 segundos em caso de erro
        this.maxRetries = 3;
        this.isUpdating = false;
        this.lastUpdate = null;
        this.updateTimer = null;
        this.retryTimer = null;
        this.retryCount = 0;
        
        this.init();
    }
    
    init() {
        console.log('🔄 Dashboard Updater inicializado');
        this.startAutoUpdate();
        this.addUpdateIndicator();
        this.addManualRefreshButton();
    }
    
    startAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
        }
        
        this.updateTimer = setInterval(() => {
            this.updateData();
        }, this.updateInterval);
        
        console.log(`⏰ Auto-update configurado para ${this.updateInterval / 1000 / 60} minutos`);
    }
    
    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
        
        if (this.retryTimer) {
            clearTimeout(this.retryTimer);
            this.retryTimer = null;
        }
        
        console.log('⏹️ Auto-update pausado');
    }
    
    async updateData(showNotification = true) {
        if (this.isUpdating) {
            console.log('⏳ Atualização já em andamento, pulando...');
            return;
        }
        
        this.isUpdating = true;
        this.updateIndicator('updating');
        
        try {
            console.log('🔄 Iniciando atualização dos dados...');
            
            const response = await fetch(`${this.apiUrl}/data`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                cache: 'no-cache'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Atualizar dados no dashboard
            this.updateDashboardData(data);
            
            this.lastUpdate = new Date();
            this.retryCount = 0;
            
            if (showNotification) {
                this.showNotification('✅ Dados atualizados com sucesso!', 'success');
            }
            
            console.log('✅ Dados atualizados com sucesso');
            
        } catch (error) {
            console.error('❌ Erro ao atualizar dados:', error);
            
            if (showNotification) {
                this.showNotification('❌ Erro ao atualizar dados', 'error');
            }
            
            this.handleUpdateError();
            
        } finally {
            this.isUpdating = false;
            this.updateIndicator('idle');
        }
    }
    
    handleUpdateError() {
        this.retryCount++;
        
        if (this.retryCount < this.maxRetries) {
            console.log(`🔄 Tentativa ${this.retryCount}/${this.maxRetries} em ${this.retryInterval / 1000} segundos...`);
            
            this.retryTimer = setTimeout(() => {
                this.updateData(false); // Não mostrar notificação nas tentativas automáticas
            }, this.retryInterval);
        } else {
            console.error('❌ Máximo de tentativas atingido');
            this.showNotification('❌ Falha na atualização automática', 'error');
        }
    }
    
    updateDashboardData(data) {
        try {
            // Atualizar dados consolidados
            if (data.consolidated) {
                window.CONS = data.consolidated;
                this.updateConsolidatedMetrics();
            }
            
            // Atualizar dados por canal
            if (data.channels) {
                window.PER = Object.entries(data.channels).map(([channel, metrics]) => ({
                    'Canal': channel,
                    ...metrics
                }));
                this.updateChannelMetrics();
            }
            
            // Atualizar dados diários
            if (data.daily) {
                window.DAILY = data.daily;
                this.updateDailyData();
            }
            
            // Atualizar timestamp
            if (data.last_updated) {
                this.updateLastUpdateTime(data.last_updated);
            }
            
        } catch (error) {
            console.error('❌ Erro ao atualizar dados do dashboard:', error);
        }
    }
    
    updateConsolidatedMetrics() {
        const topMetrics = [
            ["💰 Orçamento Contratado", `R$ ${this.formatBR(window.CONS["Budget Contratado (R$)"])}`],
            ["💸 Orçamento Utilizado", `R$ ${this.formatBR(window.CONS["Budget Utilizado (R$)"])}`],
            ["🎬 Video Completions", this.formatInt(window.CONS["VC (100%)"])],
        ];
        
        const metricsElement = document.getElementById('metrics-overview-top');
        if (metricsElement) {
            metricsElement.innerHTML = topMetrics.map(
                m => `<div class='metric'><div class='label'>${m[0]}</div><div class='value'>${m[1]}</div></div>`
            ).join('');
        }
    }
    
    updateChannelMetrics() {
        // Atualizar tabela de canais
        const tbody = document.getElementById('tbodyChannels');
        if (tbody && window.PER) {
            tbody.innerHTML = window.PER.map(r => `
                <tr>
                    <td>${r['Canal']}</td>
                    <td>R$ ${this.formatBR(r['Budget Contratado (R$)'])}</td>
                    <td>R$ ${this.formatBR(r['Budget Utilizado (R$)'])}</td>
                    <td>${this.formatInt(r['Impressões'])}</td>
                    <td>${this.formatInt(r['Cliques'])}</td>
                    <td>${this.formatPct(r['CTR'])}</td>
                    <td>${this.formatInt(r['VC (100%)'])}</td>
                    <td>${this.formatPct(r['VTR (100%)'])}</td>
                    <td>R$ ${this.formatBR(r['CPV (R$)'])}</td>
                    <td>R$ ${this.formatBR(r['CPM (R$)'])}</td>
                    <td>${this.formatPct(r['Pacing (%)'])}</td>
                </tr>
            `).join('');
        }
    }
    
    updateDailyData() {
        // Atualizar tabela de dados diários se estiver visível
        const dailyBody = document.getElementById('channelDailyBody');
        if (dailyBody && window.DAILY) {
            const currentChannel = document.querySelector('.tab.active')?.dataset.tab;
            if (currentChannel === 'channels') {
                // Recarregar dados diários do canal selecionado
                const select = document.getElementById('channelSelect');
                if (select) {
                    this.renderChannelDailyTable(select.value);
                }
            }
        }
    }
    
    updateLastUpdateTime(timestamp) {
        const lastUpdateElement = document.getElementById('lastUpdateTime');
        if (lastUpdateElement) {
            const date = new Date(timestamp);
            lastUpdateElement.textContent = date.toLocaleString('pt-BR');
        }
    }
    
    addUpdateIndicator() {
        // Adicionar indicador de status no header
        const header = document.querySelector('.header');
        if (header) {
            const indicator = document.createElement('div');
            indicator.id = 'updateIndicator';
            indicator.style.cssText = `
                position: absolute;
                top: 10px;
                right: 10px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #00ff88;
                transition: all 0.3s ease;
                z-index: 1000;
            `;
            header.appendChild(indicator);
        }
    }
    
    updateIndicator(status) {
        const indicator = document.getElementById('updateIndicator');
        if (!indicator) return;
        
        switch (status) {
            case 'updating':
                indicator.style.background = '#ff6b35';
                indicator.style.animation = 'pulse 1s infinite';
                break;
            case 'error':
                indicator.style.background = '#ff4444';
                indicator.style.animation = 'none';
                break;
            case 'idle':
            default:
                indicator.style.background = '#00ff88';
                indicator.style.animation = 'none';
                break;
        }
    }
    
    addManualRefreshButton() {
        // Adicionar botão de refresh manual
        const header = document.querySelector('.header');
        if (header) {
            const refreshBtn = document.createElement('button');
            refreshBtn.innerHTML = '🔄';
            refreshBtn.title = 'Atualizar dados';
            refreshBtn.style.cssText = `
                position: absolute;
                top: 10px;
                right: 30px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                width: 32px;
                height: 32px;
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 1000;
            `;
            
            refreshBtn.addEventListener('click', () => {
                this.updateData(true);
            });
            
            refreshBtn.addEventListener('mouseenter', () => {
                refreshBtn.style.background = 'rgba(255, 107, 53, 0.3)';
                refreshBtn.style.transform = 'scale(1.1)';
            });
            
            refreshBtn.addEventListener('mouseleave', () => {
                refreshBtn.style.background = 'rgba(255, 255, 255, 0.1)';
                refreshBtn.style.transform = 'scale(1)';
            });
            
            header.appendChild(refreshBtn);
        }
    }
    
    showNotification(message, type = 'info') {
        // Criar notificação temporária
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#00ff88' : type === 'error' ? '#ff4444' : '#ff6b35'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remover após 3 segundos
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    // Funções auxiliares de formatação
    formatBR(value, decimals = 2) {
        if (isNaN(value) || value === null || value === "") return "—";
        return new Intl.NumberFormat('pt-BR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(Number(value));
    }
    
    formatInt(value) {
        if (isNaN(value) || value === null || value === "") return "—";
        return new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 }).format(Number(value));
    }
    
    formatPct(value) {
        if (isNaN(value) || value === null || value === "") return "—";
        return `${(Number(value) * 100).toFixed(2)}%`;
    }
    
    // Métodos públicos para controle manual
    pause() {
        this.stopAutoUpdate();
        this.showNotification('⏸️ Auto-update pausado', 'info');
    }
    
    resume() {
        this.startAutoUpdate();
        this.showNotification('▶️ Auto-update retomado', 'success');
    }
    
    forceUpdate() {
        this.updateData(true);
    }
}

// CSS para animações
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardUpdater = new DashboardUpdater();
});

// Exportar para uso global
window.DashboardUpdater = DashboardUpdater;
