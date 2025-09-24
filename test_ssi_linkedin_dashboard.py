#!/usr/bin/env python3
"""
Teste do dashboard SSI - LinkedIn PGR
"""

import os
import webbrowser
from pathlib import Path

def test_dashboard():
    """Testar o dashboard criado"""
    
    # Caminho para o dashboard
    dashboard_path = Path("static/dash_ssi_linkedin_pgr.html")
    
    if not dashboard_path.exists():
        print("❌ Dashboard não encontrado!")
        return False
    
    print("✅ Dashboard encontrado!")
    print(f"📁 Localização: {dashboard_path.absolute()}")
    print(f"📊 Tamanho: {dashboard_path.stat().st_size} bytes")
    
    # Verificar se o arquivo tem conteúdo
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if len(content) < 1000:
        print("❌ Dashboard parece estar vazio ou incompleto!")
        return False
    
    print("✅ Dashboard tem conteúdo válido!")
    
    # Verificar elementos essenciais
    essential_elements = [
        "SSI - Linkedin - PGR",
        "LinkedIn",
        "Paraná",
        "R$ 12.000,00",
        "333.333",
        "CAMPAIGN_DATA",
        "showTab",
        "loadData"
    ]
    
    missing_elements = []
    for element in essential_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"⚠️ Elementos faltando: {missing_elements}")
    else:
        print("✅ Todos os elementos essenciais estão presentes!")
    
    # Abrir no navegador
    try:
        file_url = f"file://{dashboard_path.absolute()}"
        print(f"🌐 Abrindo dashboard no navegador: {file_url}")
        webbrowser.open(file_url)
        print("✅ Dashboard aberto no navegador!")
    except Exception as e:
        print(f"❌ Erro ao abrir no navegador: {e}")
        print(f"💡 Abra manualmente: {file_url}")
    
    return True

if __name__ == "__main__":
    print("🧪 Testando Dashboard SSI - LinkedIn PGR")
    print("=" * 50)
    
    success = test_dashboard()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        print("📊 Dashboard SSI - LinkedIn PGR está funcionando!")
    else:
        print("\n❌ Teste falhou!")
        print("🔧 Verifique os problemas reportados acima.")
