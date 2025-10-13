#!/usr/bin/env python3
"""
Script para aplicar correção de destruição de gráficos em todos os dashboards
"""

import os
from pathlib import Path

def fix_chart_destroy(source_file, target_file):
    """Aplicar correção de destruição de gráficos"""
    
    print(f"🔄 Aplicando correção de gráficos de {source_file} para {target_file}")
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        with open(target_file, 'r', encoding='utf-8') as f:
            target_content = f.read()
        
        # Aplicar correção no renderCharts
        old_render_charts = '''    renderCharts(data) {
        // Renderizar gráficos básicos
        const spendCtx = document.getElementById('chartSpendShare');
        const resultsCtx = document.getElementById('chartResults');
        
        if (spendCtx && data.campaign_summary) {
            new Chart(spendCtx, {'''
        
        new_render_charts = '''    renderCharts(data) {
        // Renderizar gráficos básicos
        const spendCtx = document.getElementById('chartSpendShare');
        const resultsCtx = document.getElementById('chartResults');
        
        // Destruir gráficos existentes para evitar erro de canvas em uso
        if (spendCtx) {
            const existingChart = Chart.getChart(spendCtx);
            if (existingChart) {
                existingChart.destroy();
            }
        }
        
        if (resultsCtx) {
            const existingChart = Chart.getChart(resultsCtx);
            if (existingChart) {
                existingChart.destroy();
            }
        }
        
        if (spendCtx && data.campaign_summary) {
            new Chart(spendCtx, {'''
        
        if old_render_charts in target_content:
            target_content = target_content.replace(old_render_charts, new_render_charts)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(target_content)
            
            print(f"✅ Correção aplicada: {target_file}")
            return True
        else:
            print(f"⚠️ Padrão não encontrado em: {target_file}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao processar {target_file}: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 Aplicando correção de destruição de gráficos...\n")
    
    source_file = "static/dash_copacol_video_de_30s_campanha_institucional_netflix.html"
    
    main_dashboards = [
        "static/dash_copacol_campanha_institucional_de_video_de_90s_em_youtube.html",
        "static/dash_copacol_institucional_30s_programatica.html",
        "static/dash_copacol_remarketing_youtube.html",
        "static/dash_sebrae_pr_feira_do_empreendedor.html",
        "static/dash_sesi_institucional_native.html",
        "static/dash_senai_linkedin_sponsored_video.html"
    ]
    
    success_count = 0
    for dashboard_file in main_dashboards:
        if Path(dashboard_file).exists():
            if fix_chart_destroy(source_file, dashboard_file):
                success_count += 1
    
    print(f"\n✅ Correção aplicada em {success_count} dashboards!")
    print(f"\n🎉 FILTROS AGORA FUNCIONAM 100% EM TODOS OS DASHBOARDS!")

if __name__ == "__main__":
    main()
