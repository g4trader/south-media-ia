# 📋 Guia de Implementação - Variáveis do Template

## 🏷️ Campaign Info

- **
        const response = await fetch(this.apiEndpoint);
        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status**: 
  - Descrição: Status da campanha
  - Exemplo: `'ATIVA'`, `'FINALIZADA'`, `'PAUSADA'`

- **CAMPAIGN_DESCRIPTION**: 

- **CAMPAIGN_KEY**: 

- **CAMPAIGN_NAME**: 
  - Descrição: Nome da campanha
  - Exemplo: `'Institucional Setembro'`

- **CAMPAIGN_OBJECTIVES**: 

- **CAMPAIGN_PERIOD**: 

- **CAMPAIGN_STATUS**: 
  - Descrição: Status da campanha
  - Exemplo: `'ATIVA'`, `'FINALIZADA'`, `'PAUSADA'`

- **CLIENT_NAME**: 
  - Descrição: Nome do cliente
  - Exemplo: `'SEBRAE PR'`

- **response.statusText**: 
  - Descrição: Status da campanha
  - Exemplo: `'ATIVA'`, `'FINALIZADA'`, `'PAUSADA'`


## 🏷️ Financial Data

- **BUDGET_USED**: 
  - Descrição: Valores financeiros
  - Exemplo: `'50.000,00'`

- **TOTAL_BUDGET**: 
  - Descrição: Valores financeiros
  - Exemplo: `'50.000,00'`


## 🏷️ Performance Metrics

- **
        // Restaurar HTML original
        document.body.innerHTML = this.getOriginalHTML();
        
        // Renderizar dados
        this.renderMetrics(data);
        this.renderCharts(data);
        this.renderTables(data);
        this.renderInsights(data);
        this.setupEventListeners();
    **: 

- **.metrics{grid-template-columns:repeat(2,1fr)**: 

- **CREATIVE_STRATEGY**: 

- **OVERVIEW**: 

- **SEGMENTATION_STRATEGY**: 


## 🏷️ Creative Info

- **CHANNELS**: 

- **CHANNEL_BADGES**: 

- **FORMAT_SPECIFICATIONS**: 

- **PRIMARY_CHANNEL**: 


## 🏷️ Technical Settings

- **
        const loadingHtml = `
            <div id="loadingScreen" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #0F0F23 0%, #16213E 50%, #1A1A2E 100%);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                font-family: 'Inter', sans-serif;
                color: white;
            ">
                <div style="text-align: center; max-width: 400px; padding: 40px;">
                    <div style="
                        width: 80px;
                        height: 80px;
                        border: 4px solid rgba(139, 92, 246, 0.3);
                        border-top: 4px solid #8B5CF6;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 30px;
                    "></div>
                    
                    <h2 style="
                        font-size: 24px;
                        font-weight: 700;
                        margin-bottom: 10px;
                        background: linear-gradient(135deg, #8B5CF6, #EC4899);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                    ">Carregando Dashboard</h2>
                    
                    <div style="
                        font-size: 16px;
                        color: #9CA3AF;
                        margin-bottom: 30px;
                    " id="loadingText">Inicializando...</div>
                    
                    <div style="
                        width: 100%;
                        height: 6px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 3px;
                        overflow: hidden;
                        margin-bottom: 20px;
                    ">
                        <div id="progressBar" style="
                            width: 0%;
                            height: 100%;
                            background: linear-gradient(90deg, #8B5CF6, #EC4899);
                            border-radius: 3px;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                    
                    <div style="
                        font-size: 14px;
                        color: #6B7280;
                    " id="progressText">0%</div>
                </div>
                
                <style>
                    @keyframes spin {
                        0% { transform: rotate(0deg); **: 

- **API_ENDPOINT**: 
  - Descrição: URL da API
  - Exemplo: `'http://localhost:5001/api/campaign_key/data'`

- **ORIGINAL_HTML**: 


## 🏷️ Ui Elements

- **
        // Implementar renderização de tabelas
        console.log('Renderizando tabelas:', data);
    **: 


## 🏷️ Unimplemented

- **
            console.error('Erro ao carregar dashboard:', error);
            this.showError(error.message);
        **: 

- **
            throw new Error(result.message || 'Erro ao carregar dados');
        **: 

- **
        // Implementar event listeners
        console.log('Configurando event listeners');
    **: 

- **
        // Implementar renderização de gráficos
        console.log('Renderizando gráficos:', data);
    **: 

- **
        // Implementar renderização de insights
        console.log('Renderizando insights:', data);
    **: 

- **
        // Implementar renderização de métricas
        console.log('Renderizando métricas:', data);
    **: 

- **
        const errorHtml = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #0F0F23 0%, #16213E 50%, #1A1A2E 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                font-family: 'Inter', sans-serif;
                color: white;
            ">
                <div style="
                    text-align: center;
                    max-width: 500px;
                    padding: 40px;
                    background: rgba(26, 26, 46, 0.8);
                    border: 1px solid rgba(139, 92, 246, 0.3);
                    border-radius: 16px;
                    backdrop-filter: blur(10px);
                ">
                    <div style="
                        font-size: 48px;
                        margin-bottom: 20px;
                    ">❌</div>
                    
                    <h2 style="
                        font-size: 24px;
                        font-weight: 700;
                        margin-bottom: 15px;
                        color: #EF4444;
                    ">Erro ao Carregar Dashboard</h2>
                    
                    <p style="
                        font-size: 16px;
                        color: #9CA3AF;
                        margin-bottom: 30px;
                        line-height: 1.5;
                    ">${message**: 

- **
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.remove();
        **: 

- **
        const loadingText = document.getElementById('loadingText');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (loadingText) loadingText.textContent = step.text;
        if (progressBar) progressBar.style.width = step.progress + '%';
        if (progressText) progressText.textContent = step.progress + '%';
    **: 

- **
        return new Promise(resolve => setTimeout(resolve, ms));
    **: 

- **
        try {
            this.showLoadingScreen();
            
            // Simular progresso
            for (let i = 0; i < this.loadingSteps.length; i++) {
                await this.updateProgress(this.loadingSteps[i]);
                await this.delay(800); // Delay realista
            **: 

- ** text: "Concluído!", progress: 100 **: 

- ** text: "Conectando com Google Sheets...", progress: 30 **: 

- ** text: "Extraindo dados da planilha...", progress: 50 **: 

- ** text: "Inicializando...", progress: 10 **: 

- ** text: "Processando métricas...", progress: 70 **: 

- ** text: "Renderizando dashboard...", progress: 90 **: 

- ** transform: rotate(360deg); **: 

- **--bg:#0F1023;--bg2:#16213E;--panel:#1A1A2E;--muted:#9CA3AF;--stroke: rgba(139,92,246,.28);
         --grad: linear-gradient(135deg,#8B5CF6,#EC4899);**: 

- **CPV_CONTRACTED**: 

- **CPV_CURRENT**: 

- **INSIGHTS**: 

- **PACING_PERCENTAGE**: 

- **PLANNING**: 

- **TARGET_VC**: 

- **background:rgba(26,26,46,.8);border:1px solid var(--stroke);border-radius:14px;padding:20px;margin-bottom:24px;backdrop-filter:blur(8px)**: 

- **background:var(--grad);color:#fff;box-shadow:0 8px 24px rgba(139,92,246,.35)**: 

- **border:1px solid rgba(148,163,184,.18);border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:6px**: 

- **border:1px solid rgba(148,163,184,.2);background:rgba(255,255,255,.04);padding:10px;border-radius:10px;text-align:center;cursor:pointer;color:var(--muted);font-weight:600**: 

- **box-sizing:border-box;margin:0;padding:0**: 

- **color:var(--muted)**: 

- **color:var(--muted);text-transform:uppercase;letter-spacing:.06em;font-size:.8rem;text-align:left;border-bottom:1px solid rgba(148,163,184,.22);padding:1rem**: 

- **display:flex;align-items:center;gap:12px**: 

- **display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px**: 

- **display:grid;grid-template-columns:1fr 1fr;gap:20px**: 

- **display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:20px 0**: 

- **display:grid;grid-template-columns:repeat(4,1fr);gap:16px**: 

- **display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;background:rgba(0,255,136,.2);border:1px solid rgba(0,255,136,.4);font-weight:600;color:#00ff88**: 

- **display:none**: 

- **font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#fff;
       background:linear-gradient(135deg,var(--bg) 0%,var(--bg2) 50%,var(--panel) 100%)**: 

- **font-size:1.7rem;font-weight:800;line-height:1.15**: 

- **grid-template-columns:repeat(2,1fr)**: 

- **max-width:1320px;margin:0 auto;padding:32px 32px 40px**: 

- **padding:1rem;border-bottom:1px solid rgba(148,163,184,.14)**: 

- **text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-size:.82rem**: 

- **width:100%;border-collapse:collapse**: 

- **width:40px;height:40px;border-radius:10px;background:var(--grad);display:grid;place-items:center;font-weight:700**: 


