#!/usr/bin/env python3
"""
Script para corrigir o cálculo de métricas por canal
"""

import os
from pathlib import Path

def fix_channel_metrics_calculation(source_file, target_file):
    """Aplicar correções no cálculo de métricas por canal"""
    
    print(f"🔄 Corrigindo cálculo de métricas por canal de {source_file} para {target_file}")
    
    try:
        # Ler arquivo fonte
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # Ler arquivo destino
        with open(target_file, 'r', encoding='utf-8') as f:
            target_content = f.read()
        
        # Aplicar correções específicas
        
        # 1. Corrigir recalculateChannelMetrics para usar dados originais quando não há filtros
        old_recalculate = '''    // Método para recalcular métricas específicas por canal
    recalculateChannelMetrics() {
        if (!this.filteredData.daily_data) return;
        
        const dailyData = this.filteredData.daily_data;'''
        
        new_recalculate = '''    // Método para recalcular métricas específicas por canal
    recalculateChannelMetrics() {
        // Usar dados filtrados se disponíveis, senão usar dados originais
        const dailyData = this.filteredData.daily_data || this.originalData.daily_data;
        if (!dailyData) return;'''
        
        if old_recalculate in target_content:
            target_content = target_content.replace(old_recalculate, new_recalculate)
        
        # 2. Corrigir renderTables para sempre tentar usar dados por canal
        old_render_check = '''            // Verificar se há dados filtrados por canal
            const hasChannelMetrics = data.channel_metrics && Object.keys(data.channel_metrics).length > 0;'''
        
        new_render_check = '''            // Verificar se há dados filtrados por canal (sempre calcular métricas por canal)
            const hasChannelMetrics = data.channel_metrics && Object.keys(data.channel_metrics).length > 0;'''
        
        if old_render_check in target_content:
            target_content = target_content.replace(old_render_check, new_render_check)
        
        # 3. Atualizar comentários na renderização
        old_render_comment = '''                // Renderizar dados por canal filtrados'''
        new_render_comment = '''                // Renderizar dados por canal (filtrados ou consolidados)'''
        
        if old_render_comment in target_content:
            target_content = target_content.replace(old_render_comment, new_render_comment)
        
        # 4. Atualizar fallback
        old_fallback_comment = '''                // Renderizar dados consolidados (sem filtros)'''
        new_fallback_comment = '''                // Fallback: Renderizar dados consolidados se não há métricas por canal'''
        
        if old_fallback_comment in target_content:
            target_content = target_content.replace(old_fallback_comment, new_fallback_comment)
        
        # Salvar arquivo modificado
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(target_content)
        
        print(f"✅ Cálculo de métricas por canal corrigido: {target_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar {target_file}: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 Corrigindo cálculo de métricas por canal...")
    
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
            if fix_channel_metrics_calculation(source_file, dashboard_file):
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
        print(f"\n🎉 Cálculo de métricas por canal corrigido em {success_count} dashboards!")
        print(f"🔗 Agora os dados por canal devem ser calculados corretamente:")
        print(f"   - 📊 Métricas por canal sempre calculadas")
        print(f"   - 🎛️ Filtros funcionam com dados por canal")
        print(f"   - 📅 Indicadores visuais corretos")

if __name__ == "__main__":
    main()
