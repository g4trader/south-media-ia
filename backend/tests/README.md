# 🧪 Sistema de Testes - South Media IA

Este diretório contém um sistema completo de testes para o sistema South Media IA, incluindo testes unitários, de integração, E2E com Selenium, testes de performance e todas as boas práticas de testes para sistemas web.

## 📋 Visão Geral

### **Tipos de Teste Implementados**

1. **🧩 Testes Unitários** (`test_models.py`)
   - Validação de modelos Pydantic
   - Testes de enums e relacionamentos
   - Validação de campos obrigatórios e restrições

2. **🔗 Testes de Integração** (`test_integration_api.py`)
   - Testes de endpoints da API
   - Validação de middleware de autenticação
   - Testes de permissões e autorização
   - Tratamento de erros e validações

3. **🌐 Testes E2E com Selenium** (`test_e2e_selenium.py`)
   - Navegação completa da aplicação web
   - Testes de formulários e validações
   - Verificação de dados e consistência
   - Testes de responsividade e acessibilidade

4. **⚡ Testes de Performance** (`test_performance.py`)
   - Testes de throughput e latência
   - Testes de concorrência e simultaneidade
   - Testes de carga e estresse
   - Monitoramento de recursos (CPU, memória)

## 🚀 Como Executar os Testes

### **Execução Rápida**

```bash
# Executar todos os testes
python run_tests.py

# Executar apenas testes unitários
python run_tests.py --type unit

# Executar apenas testes de integração
python run_tests.py --type integration

# Executar apenas testes E2E
python run_tests.py --type selenium

# Executar apenas testes de performance
python run_tests.py --type performance
```

### **Execução com Pytest Direto**

```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_models.py -v
pytest tests/test_integration_api.py -v
pytest tests/test_e2e_selenium.py -v
pytest tests/test_performance.py -v

# Testes por marcadores
pytest -m unit -v
pytest -m integration -v
pytest -m selenium -v
pytest -m performance -v
pytest -m slow -v
```

### **Execução com Cobertura**

```bash
# Com cobertura HTML
pytest --cov=src --cov-report=html

# Com cobertura no terminal
pytest --cov=src --cov-report=term-missing

# Com cobertura XML (para CI/CD)
pytest --cov=src --cov-report=xml
```

## 📊 Relatórios e Cobertura

### **Relatórios Gerados**

- **HTML**: `htmlcov/` - Relatórios visuais detalhados
- **XML**: `coverage.xml` - Para integração com CI/CD
- **JUnit**: `test_reports/junit.xml` - Para integração com ferramentas de CI
- **Markdown**: `test_reports/` - Relatórios resumidos em Markdown

### **Cobertura de Código**

O sistema exige **mínimo de 80% de cobertura** para:
- Modelos Pydantic
- Rotas da API
- Serviços de negócio
- Middleware de autenticação

## 🔧 Configuração

### **Dependências de Teste**

```bash
# Instalar dependências de teste
pip install -r requirements.txt

# Ou instalar apenas dependências de teste
pip install pytest pytest-cov pytest-selenium webdriver-manager
```

### **Configuração do Pytest**

O arquivo `pytest.ini` configura:
- Marcadores personalizados
- Configurações de cobertura
- Filtros de avisos
- Relatórios automáticos

### **Variáveis de Ambiente**

```bash
# Para testes E2E
export BASE_URL="http://localhost:8000"
export HEADLESS="true"

# Para testes de performance
export MAX_RESPONSE_TIME="2.0"
export MAX_CONCURRENT_USERS="50"
```

## 🧪 Estrutura dos Testes

### **Fixtures Disponíveis**

```python
# Dados mock
mock_company_data
mock_user_data
mock_campaign_data
mock_notification_data
mock_alert_data
mock_integration_data

# Serviços mock
mock_company_service
mock_user_service
mock_campaign_service
mock_notification_service
mock_alert_service
mock_dashboard_service

# Autenticação
mock_auth_headers
mock_current_user

# Dados em massa
mock_companies_bulk
mock_campaigns_bulk
mock_users_bulk
```

### **Marcadores de Teste**

```python
@pytest.mark.unit          # Testes unitários
@pytest.mark.integration   # Testes de integração
@pytest.mark.e2e          # Testes end-to-end
@pytest.mark.selenium     # Testes com Selenium
@pytest.mark.performance  # Testes de performance
@pytest.mark.slow         # Testes lentos
@pytest.mark.smoke        # Testes críticos
@pytest.mark.regression   # Testes de regressão
```

## 🌐 Testes E2E com Selenium

### **Configuração do Driver**

```python
# Chrome em modo headless (padrão)
HEADLESS = True

# Configurações do Chrome
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
```

### **Testes de Navegação**

1. **Login e Autenticação**
   - Validação de credenciais
   - Troca de empresa
   - Logout

2. **Gerenciamento de Campanhas**
   - Criação de campanhas
   - Edição e atualização
   - Visualização de performance

3. **Dashboards e Relatórios**
   - Geração de dashboards
   - Filtros e busca
   - Responsividade mobile

4. **Validação de Dados**
   - Consistência entre visualizações
   - Persistência de dados
   - Validação de formulários

## ⚡ Testes de Performance

### **Métricas Monitoradas**

- **Tempo de Resposta**: Média, P95, P99
- **Throughput**: Requisições por segundo
- **Concorrência**: Usuários simultâneos
- **Recursos**: CPU, memória, I/O

### **Cenários de Teste**

1. **Carga Básica**: 50-100 requisições simultâneas
2. **Alta Carga**: 200+ requisições simultâneas
3. **Estresse**: Testes de longa duração
4. **Escalabilidade**: Diferentes volumes de dados

### **Thresholds de Performance**

```python
performance_config = {
    "max_response_time": 2.0,        # segundos
    "max_avg_response_time": 1.0,    # segundos
    "max_memory_usage": 500,         # MB
    "max_cpu_usage": 80,             # percentual
    "min_success_rate": 0.95,        # 95%
    "max_concurrent_users": 50
}
```

## 🔍 Verificação de Código

### **Ferramentas de Qualidade**

```bash
# Formatação de código
black src/ --check

# Verificação de estilo
flake8 src/

# Organização de imports
isort src/ --check-only

# Verificação de tipos
mypy src/

# Verificação de segurança
bandit -r src/
```

### **Integração com Pre-commit**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

## 🚀 CI/CD Integration

### **GitHub Actions**

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py --type all
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### **Jenkins Pipeline**

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'python run_tests.py --type all'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
    }
}
```

## 📈 Monitoramento e Métricas

### **Relatórios Automáticos**

- **Cobertura de Código**: HTML, XML, Terminal
- **Performance**: Tempos de resposta, throughput
- **Qualidade**: Linting, type checking, security
- **Execução**: JUnit XML, relatórios Markdown

### **Métricas de Qualidade**

```python
# Exemplo de métricas coletadas
test_metrics = {
    "total_tests": 150,
    "passed": 145,
    "failed": 5,
    "coverage": 85.2,
    "avg_response_time": 0.8,
    "p95_response_time": 1.2,
    "max_memory_usage": 450,
    "max_cpu_usage": 65
}
```

## 🐛 Troubleshooting

### **Problemas Comuns**

1. **Testes E2E falhando**
   - Verificar se a aplicação está rodando
   - Verificar versão do Chrome/ChromeDriver
   - Verificar configurações de headless

2. **Testes de performance lentos**
   - Verificar recursos do sistema
   - Ajustar thresholds de performance
   - Verificar configurações de timeout

3. **Cobertura baixa**
   - Verificar se todos os arquivos estão sendo testados
   - Adicionar testes para código não coberto
   - Verificar configurações de exclusão

### **Logs e Debug**

```bash
# Executar com logs detalhados
pytest -v -s --tb=long

# Executar com logs de Selenium
pytest --selenium-capture=log

# Executar com logs de performance
pytest --benchmark-only
```

## 📚 Recursos Adicionais

### **Documentação**

- [Pytest Documentation](https://docs.pytest.org/)
- [Selenium Python](https://selenium-python.readthedocs.io/)
- [Pytest-cov](https://pytest-cov.readthedocs.io/)
- [Performance Testing Best Practices](https://k6.io/docs/testing-guides/)

### **Ferramentas Recomendadas**

- **Locust**: Testes de carga avançados
- **JMeter**: Testes de performance enterprise
- **Playwright**: Alternativa ao Selenium
- **Coverage.py**: Análise de cobertura detalhada

## 🤝 Contribuindo

### **Adicionando Novos Testes**

1. **Criar arquivo de teste** seguindo a convenção `test_*.py`
2. **Usar fixtures existentes** quando possível
3. **Adicionar marcadores apropriados** para categorização
4. **Manter cobertura alta** (mínimo 80%)
5. **Documentar casos de teste** complexos

### **Padrões de Nomenclatura**

```python
# Arquivos de teste
test_models.py          # Testes de modelos
test_integration_api.py # Testes de integração
test_e2e_selenium.py   # Testes E2E
test_performance.py     # Testes de performance

# Classes de teste
class TestUserModels:           # Testes para modelos de usuário
class TestCompanyEndpoints:     # Testes para endpoints de empresa
class TestE2ESelenium:          # Testes E2E principais
class TestPerformanceBasics:    # Testes básicos de performance

# Métodos de teste
def test_user_creation_success():     # Teste de criação bem-sucedida
def test_user_creation_validation():  # Teste de validação
def test_user_performance_under_load(): # Teste de performance
```

---

**🎯 Objetivo**: Garantir qualidade, confiabilidade e performance do sistema South Media IA através de testes abrangentes e automatizados.

**📞 Suporte**: Para dúvidas sobre testes, consulte a documentação ou entre em contato com a equipe de desenvolvimento.

