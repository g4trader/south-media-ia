#!/usr/bin/env python3
"""
Teste simples do template sem Selenium
"""

import requests
import time

def test_template_simple():
    """Teste simples via HTTP"""
    print("🔍 Testando template via HTTP...")
    
    urls = [
        "http://localhost:5001/static/dash_template_corrigido_test.html",
        "http://localhost:5001/static/dash_sebrae_pr_institucional_setembro.html"
    ]
    
    for url in urls:
        print(f"\n🌐 Testando: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                checks = [
                    ("HTML válido", "<!DOCTYPE html>" in content),
                    ("Título correto", "<title>" in content and "Dashboard" in content),
                    ("CSS South Media", "South Media" in content),
                    ("Container", 'class="container"' in content),
                    ("Tabs", 'class="tab"' in content),
                    ("Métricas", 'id="metrics-overview-top"' in content),
                    ("Gráficos", 'id="chartSpendShare"' in content),
                    ("Tabelas", 'id="tbodyChannels"' in content),
                    ("JavaScript", "DashboardLoader" in content),
                    ("Chart.js", "chart.js" in content)
                ]
                
                print("  📊 Resultados:")
                passed = 0
                for name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"    {status} {name}")
                    if result:
                        passed += 1
                
                success_rate = (passed / len(checks)) * 100
                print(f"  📈 Taxa de sucesso: {success_rate:.1f}%")
                
            else:
                print(f"  ❌ Erro HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")

if __name__ == "__main__":
    test_template_simple()

