#!/usr/bin/env python3
"""
Script para testar o dashboard COPACOL
"""

import os
import webbrowser
from pathlib import Path

def test_dashboard():
    """Abre o dashboard no navegador para teste"""
    
    dashboard_path = Path(__file__).parent / "static" / "dash_copacol_institucional_programatica.html"
    
    if dashboard_path.exists():
        print(f"✅ Dashboard encontrado: {dashboard_path}")
        
        # Abrir no navegador
        file_url = f"file://{dashboard_path.absolute()}"
        print(f"🌐 Abrindo dashboard: {file_url}")
        
        try:
            webbrowser.open(file_url)
            print("✅ Dashboard aberto no navegador!")
        except Exception as e:
            print(f"❌ Erro ao abrir no navegador: {e}")
            print(f"📁 Abra manualmente: {dashboard_path.absolute()}")
    else:
        print(f"❌ Dashboard não encontrado: {dashboard_path}")
        return False
    
    return True

def show_dashboard_info():
    """Mostra informações sobre o dashboard"""
    
    print("=" * 60)
    print("📊 DASHBOARD COPACOL INSTITUCIONAL PROGRAMÁTICA 30s")
    print("=" * 60)
    print()
    print("📋 Especificações da Campanha:")
    print("   • Nome: COPACOL INSTITUCIONAL PROGRAMÁTICA 30s")
    print("   • Canal: Programática Video")
    print("   • Período: 08/09/2025 a 05/10/2025")
    print("   • Valor Contratado: R$ 46.373,00")
    print("   • CPV: R$ 0,23")
    print("   • Impressões Contratadas: 201.625")
    print()
    print("🎯 Características do Dashboard:")
    print("   • Interface moderna com tema escuro")
    print("   • 4 abas: Visão Geral, Performance, Publishers, Planejamento")
    print("   • Gráficos interativos com Chart.js")
    print("   • Dados simulados baseados nas especificações")
    print("   • Lista completa de publishers premium")
    print()
    print("📁 Arquivos Criados:")
    print("   • /static/dash_copacol_institucional_programatica.html")
    print("   • /extract_copacol_data.py")
    print("   • /COPACOL_DASHBOARD_README.md")
    print("   • /test_copacol_dashboard.py")
    print()
    print("🔗 URLs das Planilhas:")
    print("   • Dados: https://docs.google.com/spreadsheets/d/1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8/edit?gid=1667459933")
    print("   • Publishers: https://docs.google.com/spreadsheets/d/1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8/edit?gid=1065935170")
    print()

if __name__ == "__main__":
    show_dashboard_info()
    
    print("🚀 Testando dashboard...")
    success = test_dashboard()
    
    if success:
        print()
        print("✅ Dashboard criado com sucesso!")
        print("📖 Consulte o arquivo COPACOL_DASHBOARD_README.md para mais detalhes.")
    else:
        print()
        print("❌ Erro ao criar/testar dashboard.")
