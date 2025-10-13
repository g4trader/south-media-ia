#!/usr/bin/env python3
"""
Script para aplicar mensagem "Sem dados" quando filtros não retornam resultados
"""

import os
from pathlib import Path

def fix_empty_filter_message(source_file, target_file):
    """Aplicar correção de mensagem para filtros vazios"""
    
    print(f"🔄 Aplicando correção de {source_file} para {target_file}")
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        with open(target_file, 'r', encoding='utf-8') as f:
            target_content = f.read()
        
        # Aplicar correção no renderTables
        old_render_tables = '''            // Verificar se há dados filtrados por canal (sempre calcular métricas por canal)
            const hasChannelMetrics = data.channel_metrics && Object.keys(data.channel_metrics).length > 0;
            
            console.log('renderTables - hasChannelMetrics:', hasChannelMetrics, 'keys:', data.channel_metrics ? Object.keys(data.channel_metrics) : []);
            
            if (hasChannelMetrics) {'''
        
        new_render_tables = '''            // Verificar se há dados filtrados por canal (sempre calcular métricas por canal)
            const hasChannelMetrics = data.channel_metrics && Object.keys(data.channel_metrics).length > 0;
            
            // Verificar se há dados diários (para não mostrar linha vazia quando filtros não retornam dados)
            const hasDailyData = data.daily_data && data.daily_data.length > 0;
            
            console.log('renderTables - hasChannelMetrics:', hasChannelMetrics, 'hasDailyData:', hasDailyData, 'keys:', data.channel_metrics ? Object.keys(data.channel_metrics) : []);
            
            // Se não há dados diários, mostrar mensagem de "sem dados"
            if (!hasDailyData) {
                tbodyChannels.innerHTML = `
                    <tr>
                        <td colspan="11" style="text-align: center; padding: 30px; color: #9CA3AF;">
                            📅 Nenhum dado disponível para o período selecionado
                        </td>
                    </tr>
                `;
                return;
            }
            
            if (hasChannelMetrics) {'''
        
        if old_render_tables in target_content:
            target_content = target_content.replace(old_render_tables, new_render_tables)
            
            # Também adicionar verificação no log
            old_log = '''        console.log('renderTables chamado:', {
            hasTbody: !!tbodyChannels,
            hasSummary: !!data.campaign_summary,
            hasContract: !!data.contract,
            hasChannelMetrics: data.channel_metrics ? Object.keys(data.channel_metrics).length : 0
        });'''
            
            new_log = '''        console.log('renderTables chamado:', {
            hasTbody: !!tbodyChannels,
            hasSummary: !!data.campaign_summary,
            hasContract: !!data.contract,
            hasChannelMetrics: data.channel_metrics ? Object.keys(data.channel_metrics).length : 0,
            hasDailyData: data.daily_data ? data.daily_data.length : 0
        });'''
            
            if old_log in target_content:
                target_content = target_content.replace(old_log, new_log)
            
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
    
    print("🚀 Aplicando correção de mensagem para filtros vazios...\n")
    
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
            if fix_empty_filter_message(source_file, dashboard_file):
                success_count += 1
    
    print(f"\n✅ Correção aplicada em {success_count} dashboards!")
    print(f"\n🎉 Agora quando não há dados, aparece: '📅 Nenhum dado disponível para o período selecionado'")

if __name__ == "__main__":
    main()
