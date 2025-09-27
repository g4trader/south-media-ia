# 🔧 Especificações Técnicas - MVP Dashboard Builder

## 🐳 Containerização

### Dockerfile Principal
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git curl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cloud_run_mvp.py .
COPY real_google_sheets_extractor.py .
COPY google_sheets_service.py .
COPY config.py .
COPY static/ ./static/
RUN useradd --create-home --shell /bin/bash app
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
CMD ["python", "cloud_run_mvp.py"]
```

### Dependências Python (requirements.txt)
```
Flask==2.3.3
gunicorn==21.2.0
pandas==2.0.3
google-auth==2.23.3
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.100.0
google-cloud-storage==2.10.0
requests==2.31.0
sqlite3
unidecode==1.3.7
```

## 🗄️ Estrutura do Banco de Dados

### Tabela: campaigns
```sql
CREATE TABLE campaigns (
    campaign_key TEXT PRIMARY KEY,
    client TEXT NOT NULL,
    campaign_name TEXT NOT NULL,
    sheet_id TEXT NOT NULL,
    channel TEXT,
    kpi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: dashboard_configs
```sql
CREATE TABLE dashboard_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_key TEXT NOT NULL,
    config_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📊 Estrutura de Dados da API

### Resposta da API `/api/{campaign_key}/data`
```json
{
  "data": {
    "campaign_summary": {
      "campaign": "string",
      "client": "string",
      "investment": "number",
      "complete_views_contracted": "number",
      "cpv_contracted": "number",
      "pacing": "number",
      "ctr": "number",
      "days_passed": "number",
      "period": "string",
      "status": "string"
    },
    "contract": {
      "client": "string",
      "campaign": "string",
      "period": "string",
      "investment_contracted": "number",
      "investment_utilized": "number",
      "complete_views_contracted": "number",
      "cpv_contracted": "number"
    },
    "daily_data": [
      {
        "date": "string",
        "investment": "number",
        "impressions": "number",
        "clicks": "number",
        "video_completions": "number",
        "ctr": "number",
        "vtr": "number",
        "cpv": "number"
      }
    ],
    "publishers": [
      {
        "publisher": "string",
        "investment": "number",
        "impressions": "number",
        "clicks": "number",
        "video_completions": "number",
        "ctr": "number",
        "vtr": "number",
        "cpv": "number"
      }
    ],
    "insights": [
      "string"
    ]
  },
  "success": true
}
```

## 🔄 Fluxo de Geração de Dashboard

### 1. Recebimento da Requisição
```python
@app.route('/api/generate-dashboard', methods=['POST'])
def generate_dashboard():
    data = request.get_json()
    client = data.get('client')
    campaign_name = data.get('campaign_name')
    sheet_id = data.get('sheet_id')
    channel = data.get('channel')
    kpi = data.get('kpi')
```

### 2. Processamento
```python
# Gerar campaign_key
campaign_key = generate_campaign_key(client, campaign_name)

# Salvar no banco
db_manager.save_campaign(campaign_key, client, campaign_name, sheet_id, channel, kpi)

# Selecionar template
template_file = select_template(kpi)

# Gerar dashboard
generate_dashboard_file(campaign_key, template_file, api_endpoint)
```

### 3. Notificação do Git Manager
```python
# Notificar Git Manager para commit automático
notify_git_manager(campaign_key, file_path)
```

## 🎨 Templates de Dashboard

### Template CPV (dash_generic_template.html)
- **Métricas**: Complete Views, CPV, VTR
- **Gráficos**: Investimento, Impressões, Cliques, VC
- **Tabelas**: Resumo por Canal, Dados Diários

### Template CPM (dash_remarketing_cpm_template.html)
- **Métricas**: Impressões, CPM, CTR
- **Gráficos**: Investimento, Impressões, Cliques
- **Tabelas**: Resumo por Canal, Dados Diários

### Variáveis de Substituição
```javascript
const VARIABLES = {
    '{{CAMPAIGN_KEY}}': campaign_key,
    '{{CAMPAIGN_NAME}}': campaign_name,
    '{{CLIENT}}': client,
    '{{CHANNEL}}': channel,
    '{{API_ENDPOINT}}': api_endpoint,
    '{{CAMPAIGN_STATUS}}': 'Ativa',
    '{{CAMPAIGN_DESCRIPTION}}': description,
    '{{PRIMARY_CHANNEL}}': channel
};
```

## 🔐 Sistema de Credenciais

### Google Sheets Service
```python
class GoogleSheetsService:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def _load_credentials(self):
        # 1. Variáveis de ambiente JSON
        # 2. Variáveis de ambiente base64
        # 3. Arquivos locais
        # 4. Google Cloud Storage
        # 5. Application Default Credentials
```

### Ordem de Prioridade
1. `GOOGLE_SERVICE_ACCOUNT_JSON`
2. `GOOGLE_SERVICE_ACCOUNT_INFO`
3. `GOOGLE_SHEETS_SERVICE_ACCOUNT`
4. `GOOGLE_SERVICE_ACCOUNT_JSON_B64`
5. Google Cloud Storage (`south-media-credentials`)
6. Application Default Credentials

## 📈 Monitoramento e Métricas

### Health Check Endpoints
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'database': check_database_connection(),
        'google_sheets': check_google_sheets_connection()
    })
```

### Logs Estruturados
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Exemplos de logs
logger.info("✅ Dashboard gerado com sucesso: %s", campaign_key)
logger.error("❌ Erro ao conectar Google Sheets: %s", error)
logger.warning("⚠️ Arquivo não encontrado: %s", file_path)
```

## 🚀 Performance e Otimização

### Configurações do Cloud Run
- **CPU**: 1 vCPU
- **Memória**: 2GB
- **Timeout**: 300s
- **Max Instances**: 10
- **Min Instances**: 0

### Otimizações Implementadas
- Cache de credenciais Google Sheets
- Processamento assíncrono de dados
- Compressão de respostas JSON
- Retry logic para operações críticas

## 🔧 Comandos de Manutenção

### Deploy Completo
```bash
# 1. Build da imagem
gcloud builds submit --tag gcr.io/automatizar-452311/mvp-dashboard-builder

# 2. Deploy do serviço
gcloud run deploy mvp-dashboard-builder \
  --image gcr.io/automatizar-452311/mvp-dashboard-builder \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10

# 3. Verificar deploy
gcloud run services describe mvp-dashboard-builder --region=us-central1
```

### Backup e Restore
```bash
# Backup
mkdir -p backup/$(date +%Y%m%d_%H%M%S)
cp static/dash_*.html backup/$(date +%Y%m%d_%H%M%S)/
cp *.db backup/$(date +%Y%m%d_%H%M%S)/
tar -czf backup/$(date +%Y%m%d_%H%M%S).tar.gz backup/$(date +%Y%m%d_%H%M%S)/

# Upload para GCS
gsutil cp backup/$(date +%Y%m%d_%H%M%S).tar.gz gs://south-media-backups/

# Restore
gsutil cp gs://south-media-backups/YYYYMMDD_HHMMSS.tar.gz .
tar -xzf YYYYMMDD_HHMMSS.tar.gz
cp YYYYMMDD_HHMMSS/dashboards/* static/
cp YYYYMMDD_HHMMSS/database/* .
```

## 🧪 Testes e Validação

### Teste de Conectividade
```bash
# Health check
curl -s https://mvp-dashboard-builder-609095880025.us-central1.run.app/health

# API de dados
curl -s https://mvp-dashboard-builder-609095880025.us-central1.run.app/api/sebrae_pr_feira_do_empreendedor_spotify/data

# Gerador
curl -s https://mvp-dashboard-builder-609095880025.us-central1.run.app/dash-generator-pro
```

### Teste de Geração
```bash
curl -X POST "https://mvp-dashboard-builder-609095880025.us-central1.run.app/api/generate-dashboard" \
  -H "Content-Type: application/json" \
  -d '{
    "client": "Test",
    "campaign_name": "Test Campaign",
    "sheet_id": "1test_sheet_id",
    "channel": "YouTube",
    "kpi": "CPV"
  }'
```

---

**Documentação técnica atualizada em**: 27/09/2025  
**Versão**: 1.0.0  
**Ambiente**: Produção
