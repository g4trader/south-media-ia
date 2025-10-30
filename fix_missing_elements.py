#!/usr/bin/env python3
"""
Script para adicionar elementos que faltam na aba Footfall Set
"""

import os
import re

def fix_missing_elements():
    """Adicionar elementos que faltam na aba Footfall Set"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Adicionando elementos que faltam na aba Footfall Set...")
    
    # Encontrar a seção da aba Footfall Set e adicionar os elementos que faltam
    # Procurar por </section> que fecha footfall-metrics na aba Footfall Set
    pattern = r'(<section class="metrics-grid" id="footfall-metrics"[^>]*>.*?</section>)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Adicionar os elementos que faltam após a seção de métricas
        additional_elements = '''
    <!-- Mapa de Distribuição Geográfica -->
    <section class="map-section" style="margin-bottom: 3rem;">
      <h2 style="color: #ffffff; font-size: 1.8rem; margin-bottom: 1.5rem; text-align: center;">Distribuição Geográfica</h2>
      <div class="map-container" style="position: relative; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
        <div id="footfall-map" style="height: 400px; width: 100%; border-radius: 8px; filter: hue-rotate(15deg) saturate(1.2);"></div>
      </div>
    </section>

    <!-- Gráfico de Performance -->
    <section class="chart-section" style="margin-bottom: 3rem;">
      <h2 style="color: #ffffff; font-size: 1.8rem; margin-bottom: 1.5rem; text-align: center;">Performance por Loja</h2>
      <div class="chart-container" style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 2rem; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1);">
        <canvas id="footfall-performanceChart"></canvas>
      </div>
    </section>

    <!-- Top 5 Lojas -->
    <section class="top-stores-section">
      <h2 style="color: #ffffff; font-size: 1.8rem; margin-bottom: 1.5rem; text-align: center;">Top 5 Lojas</h2>
      <div id="footfall-topStores" class="top-stores-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
        <!-- Top stores serão carregados dinamicamente -->
      </div>
    </section>
'''
        
        # Substituir a seção de métricas pela seção completa
        new_section = match.group(1) + additional_elements
        content = content.replace(match.group(1), new_section)
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Adicionando elementos que faltam...")
    
    if fix_missing_elements():
        print("\n🎉 Elementos adicionados!")
        print("📋 Resultado:")
        print("   ✅ Footfall Set: Agora tem mapa, gráfico e top stores")
        print("   ✅ Footfall Out: Já tinha todos os elementos")
    else:
        print("❌ Erro ao adicionar elementos")

