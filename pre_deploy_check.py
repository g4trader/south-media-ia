#!/usr/bin/env python3
"""
🔍 Script de Verificação Pré-Deploy
Verifica a integridade de arquivos críticos antes de permitir deploy
"""

import os
import sys

CRITICAL_FILES = [
    # Templates críticos
    'static/dash_generic_template.html',
    'static/dash_remarketing_cpm_template.html', 
    'static/dash_generic_cpe_template.html',
    
    # Arquivos Python críticos
    'cloud_run_mvp.py',
    'real_google_sheets_extractor.py',
    'bigquery_firestore_manager.py',
    
    # Configuração
    'requirements.txt',
    'Dockerfile',
    
    # Backup de templates
    'templates_backup_critical/dash_generic_template.html',
    'templates_backup_critical/dash_remarketing_cpm_template.html',
    'templates_backup_critical/dash_generic_cpe_template.html',
]

def check_file_size(filepath, min_size=100):
    """Verifica se o arquivo tem tamanho mínimo (não está vazio ou corrompido)"""
    # Templates HTML devem ter no mínimo 10KB
    if filepath.endswith('.html'):
        min_size = 10000
    # Python files devem ter no mínimo 1KB
    elif filepath.endswith('.py'):
        min_size = 1000
    # Outros arquivos 100 bytes mínimo
    else:
        min_size = 100
    
    size = os.path.getsize(filepath)
    return size >= min_size

def main():
    print("🔍 VERIFICAÇÃO DE INTEGRIDADE PRÉ-DEPLOY")
    print("=" * 60)
    print()
    
    missing = []
    corrupted = []
    
    for file in CRITICAL_FILES:
        if not os.path.exists(file):
            missing.append(file)
            print(f"❌ FALTANDO: {file}")
        elif not check_file_size(file):
            corrupted.append(file)
            print(f"⚠️ SUSPEITO (muito pequeno): {file}")
        else:
            size_kb = os.path.getsize(file) / 1024
            print(f"✅ OK: {file} ({size_kb:.1f} KB)")
    
    print()
    print("=" * 60)
    
    if missing or corrupted:
        print(f"🚨 ERRO: Problemas encontrados!")
        if missing:
            print(f"   ❌ {len(missing)} arquivo(s) faltando")
        if corrupted:
            print(f"   ⚠️ {len(corrupted)} arquivo(s) suspeito(s)")
        print()
        print("❌ DEPLOY BLOQUEADO")
        print()
        print("🔧 AÇÃO NECESSÁRIA:")
        print("   1. Restaurar arquivos faltando de templates_backup_critical/")
        print("   2. Ou restaurar do ambiente HML")
        print("   3. Ou restaurar do histórico do Git")
        sys.exit(1)
    else:
        print(f"✅ Todos os {len(CRITICAL_FILES)} arquivos críticos presentes e válidos")
        print("✅ Deploy pode prosseguir com segurança")
        sys.exit(0)

if __name__ == "__main__":
    main()

