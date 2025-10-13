#!/usr/bin/env python3
"""
Script para corrigir filtros por canal nos dashboards principais
"""

import os
from pathlib import Path

def fix_channel_filtering(source_file, target_file):
    """Aplicar correções de filtros por canal de um arquivo para outro"""
    
    print(f"🔄 Corrigindo filtros por canal de {source_file} para {target_file}")
    
    try:
        # Ler arquivo fonte
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # Ler arquivo destino
        with open(target_file, 'r', encoding='utf-8') as f:
            target_content = f.read()
        
        # Aplicar correções específicas
        
        # 1. Corrigir renderTables para usar dados por canal
        old_render_tables = '''    renderTables(data) {
        // Renderizar tabela de resumo consolidado
        const tbodyChannels = document.getElementById('tbodyChannels');
        if (tbodyChannels && data.campaign_summary && data.contract) {
            const summary = data.campaign_summary;
            const contract = data.contract;
            
            // Calcular pacing
            const pacing = contract.investment > 0 ? (summary.total_spend / contract.investment * 100) : 0;
            
            tbodyChannels.innerHTML = `
                <tr>
                    <td>${contract.canal || 'Video Programática'}</td>
                    <td>R$ ${this.formatCurrency(contract.investment || 0)}</td>
                    <td>R$ ${this.formatCurrency(summary.total_spend || 0)}</td>
                    <td>${this.formatPercentage(pacing)}</td>
                    <td>${this.formatNumber(summary.total_impressions || 0)}</td>
                    <td>${this.formatNumber(summary.total_clicks || 0)}</td>
                    <td>${this.formatPercentage(summary.ctr || 0)}</td>
                    <td>${this.formatNumber(summary.total_video_completions || 0)}</td>
                    <td>${this.formatPercentage(summary.vtr || 0)}</td>
                    <td>R$ ${contract.cpv_contracted ? contract.cpv_contracted.toFixed(2).replace('.', ',') : '0,00'}</td>
                    <td>R$ ${this.formatCurrency(summary.cpm || 0)}</td>
                </tr>
            `;
        }'''
        
        new_render_tables = '''    renderTables(data) {
        // Renderizar tabela de resumo consolidado
        const tbodyChannels = document.getElementById('tbodyChannels');
        if (tbodyChannels && data.campaign_summary && data.contract) {
            const summary = data.campaign_summary;
            const contract = data.contract;
            
            // Verificar se há dados filtrados por canal
            const hasChannelMetrics = data.channel_metrics && Object.keys(data.channel_metrics).length > 0;
            
            if (hasChannelMetrics) {
                // Renderizar dados por canal filtrados
                tbodyChannels.innerHTML = Object.keys(data.channel_metrics).map(channel => {
                    const channelData = data.channel_metrics[channel];
                    const pacing = contract.investment > 0 ? (channelData.spend / contract.investment * 100) : 0;
                    
                    return `
                        <tr>
                            <td>${channel}</td>
                            <td>R$ ${this.formatCurrency(contract.investment || 0)}</td>
                            <td>R$ ${this.formatCurrency(channelData.spend || 0)}</td>
                            <td>${this.formatPercentage(pacing)}</td>
                            <td>${this.formatNumber(channelData.impressions || 0)}</td>
                            <td>${this.formatNumber(channelData.clicks || 0)}</td>
                            <td>${this.formatPercentage(channelData.ctr || 0)}</td>
                            <td>${this.formatNumber(channelData.video_completions || 0)}</td>
                            <td>${this.formatPercentage(channelData.vtr || 0)}</td>
                            <td>R$ ${contract.cpv_contracted ? contract.cpv_contracted.toFixed(2).replace('.', ',') : '0,00'}</td>
                            <td>R$ ${this.formatCurrency(channelData.cpm || 0)}</td>
                        </tr>
                    `;
                }).join('');
            } else {
                // Renderizar dados consolidados (sem filtros)
                const pacing = contract.investment > 0 ? (summary.total_spend / contract.investment * 100) : 0;
                
                tbodyChannels.innerHTML = `
                    <tr>
                        <td>${contract.canal || 'Video Programática'}</td>
                        <td>R$ ${this.formatCurrency(contract.investment || 0)}</td>
                        <td>R$ ${this.formatCurrency(summary.total_spend || 0)}</td>
                        <td>${this.formatPercentage(pacing)}</td>
                        <td>${this.formatNumber(summary.total_impressions || 0)}</td>
                        <td>${this.formatNumber(summary.total_clicks || 0)}</td>
                        <td>${this.formatPercentage(summary.ctr || 0)}</td>
                        <td>${this.formatNumber(summary.total_video_completions || 0)}</td>
                        <td>${this.formatPercentage(summary.vtr || 0)}</td>
                        <td>R$ ${contract.cpv_contracted ? contract.cpv_contracted.toFixed(2).replace('.', ',') : '0,00'}</td>
                        <td>R$ ${this.formatCurrency(summary.cpm || 0)}</td>
                    </tr>
                `;
            }
        }'''
        
        if old_render_tables in target_content:
            target_content = target_content.replace(old_render_tables, new_render_tables)
        
        # 2. Corrigir indicadores visuais
        old_indicator1 = '(data.channel_metrics && Object.keys(data.channel_metrics).length > 0)'
        new_indicator1 = 'data.channel_metrics_filtered'
        
        if old_indicator1 in target_content:
            target_content = target_content.replace(old_indicator1, new_indicator1)
        
        # 3. Adicionar armazenamento de datas atuais no applyDateFilter
        old_apply_filter = '''    applyDateFilter(startDate, endDate) {
        if (!this.originalData) return;
        
        // Fazer cópia dos dados originais
        this.filteredData = JSON.parse(JSON.stringify(this.originalData));'''
        
        new_apply_filter = '''    applyDateFilter(startDate, endDate) {
        if (!this.originalData) return;
        
        // Armazenar datas atuais para uso nos indicadores
        this.currentStartDate = startDate;
        this.currentEndDate = endDate;
        
        // Fazer cópia dos dados originais
        this.filteredData = JSON.parse(JSON.stringify(this.originalData));'''
        
        if old_apply_filter in target_content:
            target_content = target_content.replace(old_apply_filter, new_apply_filter)
        
        # 4. Adicionar chamada para recalculateChannelMetrics mesmo sem filtros
        old_no_filters = '''        // Se não há filtros, usar todos os dados
        if (!startDate && !endDate) {
            this.renderDashboard(this.filteredData);
            return;
        }'''
        
        new_no_filters = '''        // Se não há filtros, usar todos os dados
        if (!startDate && !endDate) {
            // Recalcular métricas por canal mesmo sem filtros (para dados consolidados)
            this.recalculateChannelMetrics();
            this.renderDashboard(this.filteredData);
            return;
        }'''
        
        if old_no_filters in target_content:
            target_content = target_content.replace(old_no_filters, new_no_filters)
        
        # 5. Adicionar marcação de filtros ativos
        old_channel_metrics = '''        // Armazenar dados por canal para uso na aba "Por Canal"
        this.filteredData.channel_metrics = channelData;
        
        console.log('Métricas por canal recalculadas:', channelData);'''
        
        new_channel_metrics = '''        // Armazenar dados por canal para uso na aba "Por Canal"
        this.filteredData.channel_metrics = channelData;
        
        // Marcar se os dados foram filtrados (para indicadores visuais)
        this.filteredData.channel_metrics_filtered = this.currentStartDate || this.currentEndDate;
        
        console.log('Métricas por canal recalculadas:', channelData);'''
        
        if old_channel_metrics in target_content:
            target_content = target_content.replace(old_channel_metrics, new_channel_metrics)
        
        # Salvar arquivo modificado
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(target_content)
        
        print(f"✅ Filtros por canal corrigidos: {target_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar {target_file}: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 Corrigindo filtros por canal nos dashboards principais...")
    
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
            if fix_channel_filtering(source_file, dashboard_file):
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
        print(f"\n🎉 Filtros por canal corrigidos em {success_count} dashboards!")
        print(f"🔗 Agora os filtros funcionam corretamente:")
        print(f"   - 📊 Visão Geral: Métricas totais filtradas")
        print(f"   - 🧭 Por Canal: Dados por canal filtrados")
        print(f"   - 📅 Indicadores visuais funcionais")
        print(f"   - 🔄 Recálculo automático correto")

if __name__ == "__main__":
    main()
