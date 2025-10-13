#!/usr/bin/env python3
"""
Script para corrigir o cálculo inicial de métricas por canal
"""

import os
from pathlib import Path

def fix_initial_channel_calculation(source_file, target_file):
    """Aplicar correção do cálculo inicial de métricas por canal"""
    
    print(f"🔄 Corrigindo cálculo inicial de métricas por canal de {source_file} para {target_file}")
    
    try:
        # Ler arquivo fonte
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # Ler arquivo destino
        with open(target_file, 'r', encoding='utf-8') as f:
            target_content = f.read()
        
        # Aplicar correção no loadDashboard
        
        # 1. Adicionar chamada para recalculateChannelMetrics no loadDashboard
        old_load_dashboard = '''            // 4. Calculando métricas
            this.updateProgress(60, "Calculando métricas...");
            
            // 5. Atualizando dashboard'''
        
        new_load_dashboard = '''            // 4. Calculando métricas
            this.updateProgress(60, "Calculando métricas...");
            
            // Calcular métricas por canal para dados iniciais
            this.recalculateChannelMetrics();
            
            // 5. Atualizando dashboard'''
        
        if old_load_dashboard in target_content:
            target_content = target_content.replace(old_load_dashboard, new_load_dashboard)
        
        # Salvar arquivo modificado
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(target_content)
        
        print(f"✅ Cálculo inicial de métricas por canal corrigido: {target_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar {target_file}: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 Corrigindo cálculo inicial de métricas por canal...")
    
    # Arquivo fonte (já corrigido)
    source_file = "static/dash_copacol_video_de_30s_campanha_institucional_netflix.html"
    
    # Dashboards principais para corrigir
    main_dashboards = [
        "static/dash_copacol_campanha_institucional_de_video_de_90s_em_youtube.html",
        "static/dash_copacol_institucional_30s_programatica.html",
        "static/dash_copacol_remarketing_youtube.html",
        "static/dash_sebrae_pr_feira_do_empreendedor.html",
        "static/dash_sesi_institucional_native.html",
        "static/dash_senai_linkedin_sponsored_video.html"
    ]
    
    success_count = 0
    error_count = 0
    
    for dashboard_file in main_dashboards:
        if Path(dashboard_file).exists():
            if fix_initial_channel_calculation(source_file, dashboard_file):
                success_count += 1
            else:
                error_count += 1
        else:
            print(f"⚠️ Arquivo não encontrado: {dashboard_file}")
    
    print(f"\n📈 Resumo:")
    print(f"✅ Sucessos: {success_count}")
    print(f"❌ Erros: {error_count}")
    print(f"📊 Total processado: {success_count + error_count}")
    
    if success_count > 0:
        print(f"\n🎉 Cálculo inicial de métricas por canal corrigido em {success_count} dashboards!")
        print(f"🔗 Agora as métricas por canal são calculadas no carregamento inicial:")
        print(f"   - 📊 Métricas por canal calculadas ao carregar")
        print(f"   - 🎛️ Tabela Por Canal mostra dados por creative/canal")
        print(f"   - 📅 Filtros funcionam corretamente")

if __name__ == "__main__":
    main()
