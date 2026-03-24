#!/usr/bin/env python3
"""
Script para atualizar dados do dashboard CarnaPortal a partir da planilha pública.

Planilha de referência (Report Portal AutoShopping - Fevereiro):
https://docs.google.com/spreadsheets/d/1tLz31iH7xVJgIvdGbMlfs8kf0mdeWhZuG8D8x1n3fDY/edit?gid=304137877#gid=304137877
"""

import requests
from io import StringIO
import pandas as pd
import json
import re
from pathlib import Path

# Planilha Report Portal AutoShopping - Fevereiro
SPREADSHEET_ID = "1tLz31iH7xVJgIvdGbMlfs8kf0mdeWhZuG8D8x1n3fDY"
REPORT_GID = "304137877"  # GID da aba Report (dados diários: Day, Creative, Imps, Clicks, Valor investido, etc.)
CONTRACT_GID = "1939638014"  # GID da aba Informações de contrato (ajustar se necessário nesta planilha)
FOOTFALL_GID = "1714301106"  # GID da aba Footfall (ajustar se necessário nesta planilha)
DASHBOARD_PATH = "static/dash_portal_auto_shopping_jan2026_carnaPortal_footfall.html"

def parse_coordinate(val_str):
    """Converte coordenada com pontos como separadores para float"""
    if not val_str or pd.isna(val_str) or val_str == '' or str(val_str) == 'nan':
        return None
    try:
        val_str = str(val_str).strip()
        # Remover todos os pontos (separadores de milhares)
        val_clean = val_str.replace('.', '').replace(',', '')
        
        # Se começa com negativo
        if val_clean.startswith('-'):
            digits = val_clean[1:]
            # Coordenadas geográficas: inserir ponto decimal após 2 dígitos
            if len(digits) >= 2:
                # Exemplo: -19907788289964400 -> -19.907788289964400
                coord = float(f"-{digits[:2]}.{digits[2:]}")
                return coord
        else:
            digits = val_clean
            if len(digits) >= 2:
                coord = float(f"{digits[:2]}.{digits[2:]}")
                return coord
        
        return float(val_clean)
    except Exception as e:
        print(f"⚠️ Erro ao processar coordenada '{val_str}': {e}")
        return None

def parse_rate(rate_str):
    """Converte taxa percentual para float"""
    if not rate_str or pd.isna(rate_str) or rate_str == '':
        return 0.0
    try:
        val_clean = str(rate_str).replace(',', '.').replace('%', '').strip()
        return float(val_clean)
    except:
        return 0.0

def parse_investimento(valor_str):
    """Converte string de investimento para float"""
    if pd.isna(valor_str) or valor_str == "":
        return 0.0
    valor_str = str(valor_str).strip()
    valor_str = valor_str.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(valor_str)
    except:
        return 0.0

def ler_aba_report():
    """Lê dados da aba Report com dados diários"""
    print("📊 Lendo aba Report (dados diários)...")
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={REPORT_GID}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        print(f"✅ Aba Report: {len(df)} linhas, {len(df.columns)} colunas")
        print(f"   Colunas: {list(df.columns)[:8]}")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler Report: {e}")
        return None

def ler_aba_contrato():
    """Lê dados da aba Informações de contrato"""
    print("📋 Lendo aba Informações de contrato...")
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={CONTRACT_GID}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        print(f"✅ Aba Contrato: {len(df)} linhas")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler Contrato: {e}")
        return None

def ler_aba_footfall():
    """Lê dados da aba Footfall"""
    print("🗺️ Lendo aba Footfall...")
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={FOOTFALL_GID}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        print(f"✅ Aba Footfall: {len(df)} linhas")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler Footfall: {e}")
        return None

def processar_dados_report(df):
    """Processa dados diários da aba Report"""
    if df is None or df.empty:
        return [], {}
    
    print("📊 Processando dados diários da aba Report...")
    daily_data = []
    
    # Normalizar nomes das colunas
    df.columns = [str(c).strip() for c in df.columns]
    
    # Mapear colunas
    date_col = None
    creative_col = None
    impressions_col = None
    clicks_col = None
    spend_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'day' in col_lower or 'data' in col_lower or 'date' in col_lower:
            date_col = col
        elif 'creative' in col_lower or 'criativo' in col_lower:
            creative_col = col
        elif 'imp' in col_lower and 'click' not in col_lower:
            impressions_col = col
        elif 'click' in col_lower:
            clicks_col = col
        elif 'valor investido' in col_lower or 'investido' in col_lower or 'spend' in col_lower:
            spend_col = col
    
    print(f"   Colunas detectadas: date={date_col}, creative={creative_col}, imps={impressions_col}, clicks={clicks_col}, spend={spend_col}")
    
    for idx, row in df.iterrows():
        try:
            # Pular linhas vazias
            if pd.isna(row.get(date_col, '')) or str(row.get(date_col, '')).strip() == '':
                continue
            
            # Data
            date_str = str(row.get(date_col, '')).strip()
            if not date_str or date_str == 'nan':
                continue
            
            # Converter data para formato DD/MM/YYYY
            try:
                # Tentar formato ISO (YYYY-MM-DD)
                from datetime import datetime
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                date_formatted = dt.strftime("%d/%m/%Y")
            except:
                # Tentar formato brasileiro
                try:
                    dt = datetime.strptime(date_str, "%d/%m/%Y")
                    date_formatted = date_str
                except:
                    date_formatted = date_str
            
            # Criativo
            creative = str(row.get(creative_col, '')).strip() if creative_col else 'Footfall Display'
            if not creative or creative == 'nan':
                creative = 'Footfall Display'
            
            # Impressões
            imps = 0
            if impressions_col:
                imps_val = row.get(impressions_col, 0)
                try:
                    imps = int(float(str(imps_val).replace('.', '').replace(',', '')))
                except:
                    imps = 0
            
            # Cliques
            clicks = 0
            if clicks_col:
                clicks_val = row.get(clicks_col, 0)
                try:
                    clicks = int(float(str(clicks_val).replace('.', '').replace(',', '')))
                except:
                    clicks = 0
            
            # Investimento
            spend = 0.0
            if spend_col:
                spend = parse_investimento(row.get(spend_col, 0))
            
            if imps == 0 and spend == 0:
                continue
            
            daily_data.append({
                "date": date_formatted,
                "channel": "Footfall Display",
                "creative": creative,
                "spend": spend,
                "starts": 0,
                "q25": 0,
                "q50": 0,
                "q75": 0,
                "q100": 0,
                "impressions": imps,
                "clicks": clicks,
                "visits": 0
            })
        except Exception as e:
            print(f"⚠️ Erro ao processar linha {idx}: {e}")
            continue
    
    print(f"✅ {len(daily_data)} registros diários processados")
    return daily_data, {}

def processar_dados_contrato(df):
    """Processa dados da aba Informações de contrato"""
    if df is None or df.empty:
        return {}
    
    print("📋 Processando dados de contrato...")
    contract_data = {}
    
    for idx, row in df.iterrows():
        col1 = str(row.iloc[0] if len(row) > 0 else '').strip().lower()
        col2 = str(row.iloc[1] if len(row) > 1 else '').strip()
        col3 = str(row.iloc[2] if len(row) > 2 else '').strip()
        
        # Investimento
        if 'investimento' in col1:
            val = parse_investimento(col2)
            if val > 0:
                contract_data['Budget Contratado (R$)'] = val
        
        # CPM contratado
        if 'cpm contratado' in col1:
            val = parse_investimento(col2)
            if val > 0:
                contract_data['CPM (R$)'] = val
        
        # Impressões Contratadas
        if 'impress' in col1 and ('contrado' in col1 or 'contratado' in col1):
            val_str = col2.replace('.', '').replace(',', '')
            try:
                val = int(float(val_str))
                if val > 0:
                    contract_data['Impressões Contratadas'] = val
            except:
                pass
        
        # Período
        if 'periodo' in col1 or 'veicula' in col1:
            if col2 and '/' in col2:
                contract_data['period_start'] = col2
            if col3 and '/' in col3:
                contract_data['period_end'] = col3
    
    print(f"✅ Dados de contrato: {contract_data}")
    return contract_data

def processar_dados_footfall(df):
    """Processa dados da aba Footfall"""
    if df is None or df.empty:
        return []
    
    print("🗺️ Processando dados de Footfall...")
    footfall_points = []
    
    for idx, row in df.iterrows():
        try:
            lat = parse_coordinate(row.get('lat', ''))
            lon = parse_coordinate(row.get('long', ''))
            name = str(row.get('name', '')).strip()
            users = int(float(str(row.get('Footfall Users', 0)).replace('.', '').replace(',', ''))) if pd.notna(row.get('Footfall Users', 0)) else 0
            rate = parse_rate(row.get('Footfall Rate %', 0))
            
            if lat is None or lon is None or not name or name == 'nan' or users == 0:
                continue
            
            footfall_points.append({
                "lat": lat,
                "lon": lon,
                "name": name,
                "users": users,
                "rate": rate
            })
        except Exception as e:
            print(f"⚠️ Erro ao processar linha {idx}: {e}")
            continue
    
    print(f"✅ {len(footfall_points)} pontos de footfall processados")
    return footfall_points

def atualizar_dashboard_html(cons_data, per_data, daily_data, footfall_points, contract_data):
    """Atualiza o arquivo HTML"""
    dashboard_path = Path(DASHBOARD_PATH)
    
    if not dashboard_path.exists():
        print(f"❌ Arquivo não encontrado: {dashboard_path}")
        return False
    
    print(f"📝 Lendo arquivo HTML...")
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Atualizar CONS
    cons_json = json.dumps(cons_data, ensure_ascii=False, indent=2)
    cons_pattern = r'const CONS = \{[\s\S]*?\};'
    cons_replacement = f'const CONS = {cons_json};'
    html_content = re.sub(cons_pattern, cons_replacement, html_content)
    
    # Atualizar PER
    per_json = json.dumps(per_data, ensure_ascii=False, indent=2)
    per_pattern = r'const PER = \[[\s\S]*?\];'
    per_replacement = f'const PER = {per_json};'
    html_content = re.sub(per_pattern, per_replacement, html_content)
    
    # Atualizar DAILY
    if daily_data:
        daily_json = json.dumps(daily_data, ensure_ascii=False, indent=2)
        daily_pattern = r'const DAILY = \[[\s\S]*?\];'
        daily_replacement = f'const DAILY = {daily_json};'
        html_content = re.sub(daily_pattern, daily_replacement, html_content)
    
    # Atualizar FOOTFALL_POINTS
    if footfall_points:
        footfall_json = json.dumps(footfall_points, ensure_ascii=False, indent=2)
        footfall_pattern = r'const FOOTFALL_POINTS = \[[\s\S]*?\];'
        footfall_replacement = f'const FOOTFALL_POINTS = {footfall_json};'
        html_content = re.sub(footfall_pattern, footfall_replacement, html_content)
    
    # Atualizar seção de Planejamento (JavaScript)
    if contract_data:
        period_start = contract_data.get('period_start', '07/02/2026')
        period_end = contract_data.get('period_end', '28/02/2026')
        period = f"{period_start} a {period_end}"
        
        budget_total = contract_data.get('Budget Contratado (R$)', 3750.0)
        budget_used = cons_data.get('Budget Utilizado (R$)', 0)
        pacing_budget = (budget_used / budget_total * 100) if budget_total > 0 else 0
        
        meta_imp = contract_data.get('Impressões Contratadas', 150000)
        imp_entregues = cons_data.get('Impressões', 0)
        pacing_imp = (imp_entregues / meta_imp * 100) if meta_imp > 0 else 0
        
        cpm_contratado = contract_data.get('CPM (R$)', 25.0)
        
        # Função helper para formatar números
        def fmtBR(v, dec=2):
            return f"{v:,.{dec}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        def fmtInt(v):
            return f"{int(v):,}".replace(',', '.')
        
        # Atualizar seção de planejamento
        # Inclui eventual })(); duplicado para não deixar sobra
        planning_pattern = r'// ====== PLANNING POPULATION ======.*?setTxt\([\'"]plan-cpm[\'"], fmtBR\(cpmContratado\)\);\s*\}\)\(\);(?:\s*\}\)\(\);)?'
        planning_replacement = f'''// ====== PLANNING POPULATION ======
(function(){{
  const period = '{period}';
  const metaImp = {meta_imp};
  const cpmContratado = {cpm_contratado};
  const budgetTotal = Number(CONS["Budget Contratado (R$)"]||0);
  const budgetUsed = Number(CONS["Budget Utilizado (R$)"]||0);
  const pacingBudget = budgetTotal>0 ? budgetUsed/budgetTotal : 0;
  const impEnt = Number(CONS["Impressões"]||0);
  const pacingImp = metaImp>0 ? impEnt/metaImp : 0;

  const setTxt = (id, txt)=>{{ const el=document.getElementById(id); if(el) el.textContent = txt; }};
  setTxt('plan-periodo', period);
  setTxt('plan-budget-total', fmtBR(budgetTotal));
  setTxt('plan-budget-used', fmtBR(budgetUsed));
  setTxt('plan-pacing', `${{(pacingBudget*100).toFixed(2)}}%`);
  setTxt('plan-imp-meta', fmtInt(metaImp));
  setTxt('plan-imp-entregues', fmtInt(impEnt));
  setTxt('plan-imp-pacing', `${{(pacingImp*100).toFixed(2)}}%`);
  setTxt('plan-cpm', fmtBR(cpmContratado));
}})();'''
        
        html_content = re.sub(planning_pattern, planning_replacement, html_content, flags=re.DOTALL)
        print("✅ Seção de Planejamento atualizada")
    
    # Salvar arquivo
    print(f"💾 Salvando arquivo atualizado...")
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard atualizado com sucesso!")
    return True

def main():
    print("🚀 Atualizando dados do dashboard CarnaPortal...")
    print(f"📊 Planilha: {SPREADSHEET_ID}\n")
    
    # 1. Ler dados
    df_report = ler_aba_report()
    df_contrato = ler_aba_contrato()
    df_footfall = ler_aba_footfall()
    
    # 2. Processar dados
    daily_data, _ = processar_dados_report(df_report)
    contract_data = processar_dados_contrato(df_contrato)
    footfall_points = processar_dados_footfall(df_footfall)
    
    # 3. Calcular métricas (usar dados existentes se não houver novos)
    # Por enquanto, vamos manter os dados existentes e apenas atualizar o Footfall
    # Se você quiser atualizar os dados diários, precisamos ver a estrutura completa da aba Report
    
    # 4. Preparar dados CONS (manter existentes por enquanto)
    # Os dados serão atualizados quando tivermos acesso completo à aba Report
    
    # 3. Calcular métricas totais
    print("\n📊 Calculando métricas totais...")
    total_spend = sum(d.get('spend', 0) for d in daily_data)
    total_impressions = sum(d.get('impressions', 0) for d in daily_data)
    total_clicks = sum(d.get('clicks', 0) for d in daily_data)
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
    
    budget_contratado = contract_data.get('Budget Contratado (R$)', 3750.0)
    pacing = (total_spend / budget_contratado * 100) if budget_contratado > 0 else 0
    
    # Preparar dados CONS
    cons_data = {
        "Budget Contratado (R$)": budget_contratado,
        "Budget Utilizado (R$)": total_spend,
        "Impressões": total_impressions,
        "Cliques": total_clicks,
        "CTR (%)": ctr / 100,
        "VC (100%)": 0,
        "VTR (100%)": 0,
        "CPV (R$)": 0,
        "CPM (R$)": contract_data.get('CPM (R$)', cpm),
        "Pacing (%)": pacing / 100
    }
    
    # Preparar dados PER
    per_data = [{
        "Canal": "Footfall Display",
        "Budget Contratado (R$)": budget_contratado,
        "Budget Utilizado (R$)": total_spend,
        "Impressões": total_impressions,
        "Cliques": total_clicks,
        "CTR (%)": ctr / 100,
        "VC (100%)": 0,
        "VTR (100%)": 0,
        "CPV (R$)": 0,
        "CPM (R$)": contract_data.get('CPM (R$)', cpm),
        "Pacing (%)": pacing / 100,
        "Criativos Únicos": len(set(d.get('creative', '') for d in daily_data if d.get('creative')))
    }]
    
    print(f"   Budget Utilizado: R$ {total_spend:,.2f}")
    print(f"   Impressões: {total_impressions:,}")
    print(f"   Cliques: {total_clicks:,}")
    print(f"   CTR: {ctr:.2f}%")
    print(f"   Pacing: {pacing:.2f}%")
    
    # 4. Atualizar dados no HTML
    print("\n🔄 Atualizando dados no HTML...")
    sucesso = atualizar_dashboard_html(cons_data, per_data, daily_data, footfall_points, contract_data)
    
    if sucesso:
        print("\n✅ Processo concluído com sucesso!")
        print(f"   - {len(daily_data)} registros diários")
        print(f"   - {len(footfall_points)} pontos de footfall")
        print(f"   - Budget utilizado: R$ {total_spend:,.2f}")
        print(f"   - Impressões: {total_impressions:,}")
    else:
        print("\n❌ Erro ao atualizar dashboard")

if __name__ == "__main__":
    main()
