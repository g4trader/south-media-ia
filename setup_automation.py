#!/usr/bin/env python3
"""
Script de configuração e setup da automação do dashboard
"""

import os
import json
import shutil
from datetime import datetime

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        'logs',
        'backups',
        'credentials'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Diretório criado: {directory}")

def setup_google_credentials():
    """Configura credenciais do Google Sheets"""
    print("\n🔑 CONFIGURAÇÃO DAS CREDENCIAIS DO GOOGLE SHEETS")
    print("=" * 50)
    
    print("""
Para usar a automação, você precisa:

1. Criar um projeto no Google Cloud Console
2. Habilitar a API do Google Sheets
3. Criar credenciais (OAuth 2.0)
4. Baixar o arquivo credentials.json

Passos detalhados:

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto ou selecione um existente
3. Vá em "APIs & Services" > "Library"
4. Procure por "Google Sheets API" e habilite
5. Vá em "APIs & Services" > "Credentials"
6. Clique em "Create Credentials" > "OAuth 2.0 Client ID"
7. Escolha "Desktop Application"
8. Baixe o arquivo JSON
9. Renomeie para 'credentials.json'
10. Coloque na pasta 'credentials/'

Depois de fazer isso, execute novamente este script.
""")
    
    credentials_file = 'credentials/credentials.json'
    
    if os.path.exists(credentials_file):
        print(f"✅ Arquivo de credenciais encontrado: {credentials_file}")
        
        # Copiar para a raiz do projeto
        shutil.copy2(credentials_file, 'credentials.json')
        print("✅ Credenciais copiadas para a raiz do projeto")
        return True
    else:
        print(f"❌ Arquivo de credenciais não encontrado: {credentials_file}")
        print("📋 Siga as instruções acima para configurar as credenciais")
        return False

def setup_sheet_ids():
    """Configura IDs das planilhas"""
    print("\n📊 CONFIGURAÇÃO DOS IDs DAS PLANILHAS")
    print("=" * 40)
    
    print("""
Para cada canal, você precisa do ID da planilha do Google Sheets.

Como encontrar o ID:
1. Abra a planilha no Google Sheets
2. O ID está na URL: https://docs.google.com/spreadsheets/d/ID_AQUI/edit
3. Copie apenas a parte do ID (sem as barras)

Exemplo de URL:
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
ID: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
""")
    
    channels = [
        "YouTube",
        "TikTok", 
        "Netflix",
        "Disney",
        "CTV",
        "Footfall Display"
    ]
    
    sheet_ids = {}
    
    for channel in channels:
        print(f"\n📋 Canal: {channel}")
        sheet_id = input(f"Digite o ID da planilha para {channel}: ").strip()
        
        if sheet_id:
            sheet_ids[channel] = sheet_id
            print(f"✅ ID configurado para {channel}")
        else:
            print(f"⚠️ Pulando {channel} (ID vazio)")
    
    if sheet_ids:
        # Atualizar config.py
        update_config_with_sheet_ids(sheet_ids)
        print(f"\n✅ {len(sheet_ids)} IDs de planilhas configurados!")
        return True
    else:
        print("\n❌ Nenhum ID de planilha foi configurado")
        return False

def update_config_with_sheet_ids(sheet_ids):
    """Atualiza config.py com os IDs das planilhas"""
    try:
        # Ler config.py atual
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir IDs das planilhas
        for channel, sheet_id in sheet_ids.items():
            old_pattern = f'"sheet_id": "YOUR_{channel.upper().replace(" ", "_")}_SHEET_ID"'
            new_pattern = f'"sheet_id": "{sheet_id}"'
            content = content.replace(old_pattern, new_pattern)
        
        # Salvar config.py atualizado
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Arquivo config.py atualizado com os IDs das planilhas")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar config.py: {e}")

def create_env_file():
    """Cria arquivo .env com as configurações"""
    try:
        env_content = """# Configurações da automação do dashboard
GOOGLE_CREDENTIALS_FILE=credentials.json

# Configurações de log
LOG_LEVEL=INFO

# Configurações de backup
BACKUP_ENABLED=true

# Configurações de notificação (opcional)
NOTIFICATION_ENABLED=false
WEBHOOK_URL=
SMTP_SERVER=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
NOTIFICATION_EMAIL=
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado")
        
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")

def create_startup_scripts():
    """Cria scripts de inicialização"""
    
    # Script para Windows
    windows_script = """@echo off
echo Iniciando automação do dashboard...
python dashboard_automation.py
pause
"""
    
    with open('start_automation.bat', 'w', encoding='utf-8') as f:
        f.write(windows_script)
    
    # Script para Linux/Mac
    unix_script = """#!/bin/bash
echo "Iniciando automação do dashboard..."
python3 dashboard_automation.py
"""
    
    with open('start_automation.sh', 'w', encoding='utf-8') as f:
        f.write(unix_script)
    
    # Tornar executável no Unix
    os.chmod('start_automation.sh', 0o755)
    
    print("✅ Scripts de inicialização criados:")
    print("  - start_automation.bat (Windows)")
    print("  - start_automation.sh (Linux/Mac)")

def create_documentation():
    """Cria documentação básica"""
    doc_content = """# AUTOMAÇÃO DO DASHBOARD

## Descrição
Sistema de automação que atualiza o dashboard a cada 3 horas usando dados do Google Sheets.

## Configuração Inicial

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Credenciais Google
- Siga as instruções no arquivo `setup_automation.py`
- Coloque o arquivo `credentials.json` na pasta `credentials/`

### 3. Configurar IDs das Planilhas
- Execute `python setup_automation.py`
- Digite os IDs das planilhas para cada canal

### 4. Iniciar Automação
```bash
# Windows
start_automation.bat

# Linux/Mac
./start_automation.sh

# Ou diretamente
python dashboard_automation.py
```

## Estrutura de Arquivos
- `dashboard_automation.py` - Script principal
- `google_sheets_processor.py` - Processador de dados
- `monitoring.py` - Sistema de monitoramento
- `config.py` - Configurações
- `logs/` - Logs de execução
- `backups/` - Backups do dashboard

## Monitoramento
Execute `python monitoring.py` para verificar a saúde do sistema.

## Logs
Os logs são salvos em `logs/dashboard_automation.log`

## Backup
Backups automáticos são criados em `backups/` antes de cada atualização.
"""
    
    with open('README_AUTOMATION.md', 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print("✅ Documentação criada: README_AUTOMATION.md")

def main():
    """Função principal de setup"""
    print("🚀 CONFIGURAÇÃO DA AUTOMAÇÃO DO DASHBOARD")
    print("=" * 50)
    
    # Criar diretórios
    create_directories()
    
    # Configurar credenciais
    credentials_ok = setup_google_credentials()
    
    if not credentials_ok:
        print("\n❌ Configure as credenciais primeiro e execute novamente")
        return
    
    # Configurar IDs das planilhas
    sheets_ok = setup_sheet_ids()
    
    if not sheets_ok:
        print("\n❌ Configure os IDs das planilhas primeiro")
        return
    
    # Criar arquivos adicionais
    create_env_file()
    create_startup_scripts()
    create_documentation()
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 30)
    print("✅ Diretórios criados")
    print("✅ Credenciais configuradas")
    print("✅ IDs das planilhas configurados")
    print("✅ Scripts de inicialização criados")
    print("✅ Documentação criada")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Execute: python dashboard_automation.py")
    print("2. Ou use: start_automation.bat/sh")
    print("3. Para monitoramento: python monitoring.py")
    
    print("\n📚 Consulte README_AUTOMATION.md para mais detalhes")

if __name__ == "__main__":
    main()
