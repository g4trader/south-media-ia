#!/usr/bin/env python3
"""
Script simples para implementar filtros funcionais nos dashboards principais
"""

import os
from pathlib import Path

def copy_filter_functionality(source_file, target_file):
    """Copiar funcionalidade de filtro de um arquivo para outro"""
    
    print(f"🔄 Copiando filtros de {source_file} para {target_file}")
    
    try:
        # Ler arquivo fonte
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # Ler arquivo destino
        with open(target_file, 'r', encoding='utf-8') as f:
            target_content = f.read()
        
        # Se já tem filtros funcionais, pular
        if 'applyDateFilter' in target_content and 'recalculateMetrics' in target_content:
            print(f"✅ Já possui filtros funcionais: {target_file}")
            return True
        
        # Extrair partes específicas do arquivo fonte
        parts_to_copy = []
        
        # 1. Propriedades do constructor
        start = source_content.find('this.originalData = null;')
        if start != -1:
            end = source_content.find('}', start) + 1
            constructor_part = source_content[start:end]
            parts_to_copy.append(('constructor', constructor_part))
        
        # 2. Armazenamento de dados originais
        start = source_content.find('// Armazenar dados originais para filtros')
        if start != -1:
            end = source_content.find('// 3. Dados recebidos', start)
            data_storage_part = source_content[start:end]
            parts_to_copy.append(('data_storage', data_storage_part))
        
        # 3. Métodos de filtro
        start = source_content.find('// Método para aplicar filtros de data aos dados')
        if start != -1:
            end = source_content.find('hideLoadingScreen()', start)
            filter_methods_part = source_content[start:end]
            parts_to_copy.append(('filter_methods', filter_methods_part))
        
        # 4. Callback de filtro
        start = source_content.find('// Aplicar filtros aos dados do dashboard')
        if start != -1:
            end = source_content.find('window.dashboard = dashboard;', start) + len('window.dashboard = dashboard;')
            callback_part = source_content[start:end]
            parts_to_copy.append(('callback', callback_part))
        
        # Aplicar modificações
        modified_content = target_content
        
        # Aplicar cada parte
        for part_type, part_content in parts_to_copy:
            if part_type == 'constructor':
                # Adicionar propriedades ao constructor
                constructor_end = modified_content.find('this.currentStep = 0;')
                if constructor_end != -1:
                    constructor_end = modified_content.find('}', constructor_end) + 1
                    modified_content = modified_content[:constructor_end-1] + '\n        ' + part_content + modified_content[constructor_end-1:]
            
            elif part_type == 'data_storage':
                # Substituir armazenamento de dados
                old_pattern = 'const data = await this.fetchData();'
                if old_pattern in modified_content:
                    modified_content = modified_content.replace(old_pattern, old_pattern + '\n            \n            ' + part_content)
            
            elif part_type == 'filter_methods':
                # Adicionar métodos após delay
                delay_end = modified_content.find('delay(ms) {')
                if delay_end != -1:
                    delay_end = modified_content.find('}', delay_end) + 1
                    modified_content = modified_content[:delay_end] + '\n    ' + part_content + modified_content[delay_end:]
            
            elif part_type == 'callback':
                # Substituir callback
                old_callback = 'if (typeof window.reloadDashboardData === \'function\') {\n        window.reloadDashboardData(filters);\n      }'
                if old_callback in modified_content:
                    modified_content = modified_content.replace(old_callback, part_content)
        
        # Salvar arquivo modificado
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"✅ Filtros funcionais copiados: {target_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar {target_file}: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 Implementando filtros funcionais nos dashboards principais...")
    
    # Arquivo fonte (já modificado)
    source_file = "static/dash_copacol_video_de_30s_campanha_institucional_netflix.html"
    
    # Dashboards principais para modificar
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
            if copy_filter_functionality(source_file, dashboard_file):
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
        print(f"\n🎉 Filtros funcionais implementados em {success_count} dashboards principais!")
        print(f"🔗 Teste os dashboards em: http://localhost:8080/static/")

if __name__ == "__main__":
    main()
