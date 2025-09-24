#!/usr/bin/env python3
"""
Script para mostrar os dados atuais sendo usados no dashboard
"""

import json
import requests

def show_current_data():
    """Mostrar os dados atuais sendo usados"""
    print("📊 DADOS ATUAIS DO DASHBOARD SEBRAE")
    print("=" * 60)
    
    try:
        # Fazer requisição para a API
        response = requests.get("http://localhost:5000/api/sebrae/data")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Status: {data.get('success')}")
            print(f"📋 Fonte dos dados: {data.get('source')}")
            print(f"⏰ Timestamp: {data.get('timestamp')}")
            
            if data.get('data'):
                dashboard_data = data['data']
                
                print("\n📺 PUBLISHERS ATUAIS:")
                print("-" * 30)
                
                publishers = dashboard_data.get('publishers', [])
                if publishers:
                    for i, publisher in enumerate(publishers, 1):
                        print(f"{i}. {publisher.get('name')} - {publisher.get('type')}")
                else:
                    print("❌ Nenhum publisher encontrado")
                
                print("\n🎯 ESTRATÉGIAS ATUAIS:")
                print("-" * 30)
                
                strategies = dashboard_data.get('strategies', {})
                if strategies:
                    segmentation = strategies.get('segmentation', [])
                    objectives = strategies.get('objectives', [])
                    
                    print("Segmentação:")
                    for seg in segmentation:
                        print(f"  - {seg}")
                    
                    print("Objetivos:")
                    for obj in objectives:
                        print(f"  - {obj}")
                else:
                    print("❌ Nenhuma estratégia encontrada")
                
                print("\n📋 CONTRATO ATUAL:")
                print("-" * 30)
                
                contract = dashboard_data.get('contract', {})
                if contract:
                    print(f"Investimento: R$ {contract.get('investment', 'N/A')}")
                    print(f"CPV Contratado: R$ {contract.get('cpv_contracted', 'N/A')}")
                    print(f"VC Contratados: {contract.get('complete_views_contracted', 'N/A')}")
                    print(f"Período: {contract.get('period_start', 'N/A')} - {contract.get('period_end', 'N/A')}")
                else:
                    print("❌ Nenhum contrato encontrado")
                
                print("\n💡 INFORMAÇÕES IMPORTANTES:")
                print("-" * 30)
                print("⚠️  Os dados mostrados acima são DADOS DE TESTE")
                print("⚠️  Para usar dados reais da planilha, é necessário:")
                print("   1. Configurar credenciais do Google Sheets")
                print("   2. Baixar arquivo JSON de credenciais do Google Cloud Console")
                print("   3. Renomear para 'google_credentials.json'")
                print("   4. Colocar na pasta raiz do projeto")
                
            else:
                print("❌ Nenhum dado encontrado na resposta")
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao acessar API: {e}")

if __name__ == "__main__":
    show_current_data()
