#!/usr/bin/env python3
"""
Script para atualizar o dashboard Portal Auto Shopping - Carbank Janeiro 2026
a partir dos dados da planilha do Google Sheets.

Uso:
    python update_portal_auto_jan2026_dashboard.py

Este script:
1. Lê os dados da aba "Report" da planilha do Google Sheets
2. Lê os dados da aba "Footfall" da planilha do Google Sheets
3. Processa e valida os dados
4. Garante que todos os dias tenham todos os formatos de criativo
5. Atualiza o arquivo HTML do dashboard com os dados corretos
6. Recalcula os totais consolidados (CONS e PER)
7. Atualiza os dados de Footfall (FOOTFALL_POINTS)
"""

import sys
from pathlib import Path
from datetime import datetime
import re
import json

import pandas as pd
import requests

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Mantemos a dependência para casos futuros, mas o acesso principal usa URLs públicas
from google_sheets_service import GoogleSheetsService

# Configurações da campanha / planilha
SPREADSHEET_ID = "1L9rzKij4eFNhRxFVTQbcaT_73WfD3nTaBkHOQXSWvxE"
REPORT_SHEET_NAME = "Report"
FOOTFALL_SHEET_NAME = "Footfall"
REPORT_GID = 304137877  # GID da aba Report
FOOTFALL_GID = 1714301106  # GID da aba Footfall

# URLs públicas (leitura anônima) das abas da planilha
REPORT_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export"
    f"?format=csv&gid={REPORT_GID}"
)
# FOOTFALL_CSV_URL será construída quando necessário
DASHBOARD_PATH = Path("static/dash_portal_auto_shopping_jan2026_footfall.html")
BUDGET_CONTRATADO = 3750.0  # Ajustar conforme necessário
CPM_CONTRATADO = 25.0  # Ajustar conforme necessário

# Lista de todos os formatos de criativo esperados
# Nota: Pode precisar ser ajustado conforme os criativos da campanha de janeiro
FORMATOS_ESPERADOS = [
    "20251201_ly_Drive-To-Store-360x300_A.png",
    "20251201_ly_Drive-To-Store_300x250px_A.png",
    "20251201_ly_Drive-To-Store_300x50px_A.png",
    "20251201_ly_Drive-To-Store_320x480px_A.png",
    "20251201_ly_Drive-To-Store_336x336px_A.png",
]


def parse_investimento(valor_str):
    """Converte string de investimento (R$ 20,80) para float"""
    if not valor_str or valor_str == '':
        return 0.0
    # Remove R$, espaços e substitui vírgula por ponto
    valor_limpo = str(valor_str).replace('R$', '').replace(' ', '').replace(',', '.')
    try:
        return float(valor_limpo)
    except:
        return 0.0


def ler_dados_planilha():
    """Lê os dados da aba Report usando a URL pública (CSV)."""
    print("📊 Lendo dados da aba Report via URL pública (HTTP)...")
    try:
        resp = requests.get(REPORT_CSV_URL, timeout=30, verify=False)
        resp.raise_for_status()
        from io import StringIO
        df = pd.read_csv(StringIO(resp.text))
        if df.empty:
            print("⚠️  Nenhum dado encontrado na aba Report")
            return None
        print(f"✅ Encontrados {len(df)} registros na aba Report")
        print(f"📋 Colunas encontradas: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler aba Report via URL pública: {e}")
        return None


def ler_dados_footfall(gid=None):
    """Lê os dados da aba Footfall usando a URL pública (CSV)."""
    if gid is None:
        print("⚠️  GID da aba Footfall não especificado, tentando detectar...")
        # Tentar alguns GIDs comuns ou detectar automaticamente
        # Por enquanto, retornar None se não especificado
        return None
    
    print("🗺️  Lendo dados da aba Footfall via URL pública (HTTP)...")
    try:
        footfall_url = (
            f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export"
            f"?format=csv&gid={gid}"
        )
        resp = requests.get(footfall_url, timeout=30, verify=False)
        resp.raise_for_status()
        from io import StringIO
        df = pd.read_csv(StringIO(resp.text))
        if df.empty:
            print("⚠️  Nenhum dado encontrado na aba Footfall")
            return None
        print(f"✅ Encontrados {len(df)} registros na aba Footfall")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler aba Footfall via URL pública: {e}")
        return None


def processar_dados(df):
    """Processa os dados do DataFrame e retorna lista de registros"""
    import pandas as pd
    
    dados_processados = {}
    
    # Tentar detectar automaticamente as colunas
    print("🔍 Detectando estrutura da planilha...")
    
    # Procurar coluna de data (pode ser "Date", "Data", "Day", "Dia", ou primeira coluna)
    date_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if 'date' in col_lower or 'data' in col_lower or 'day' in col_lower or 'dia' in col_lower:
            date_col = col
            break
    
    if date_col is None and len(df.columns) > 0:
        date_col = df.columns[0]
        print(f"   Usando primeira coluna como data: {date_col}")
    else:
        print(f"   Coluna de data detectada: {date_col}")
    
    # Procurar coluna de criativo
    creative_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if 'creative' in col_lower or 'criativo' in col_lower or 'format' in col_lower or 'formato' in col_lower:
            creative_col = col
            break
    
    if creative_col is None and len(df.columns) > 1:
        creative_col = df.columns[1]
        print(f"   Usando segunda coluna como criativo: {creative_col}")
    else:
        print(f"   Coluna de criativo detectada: {creative_col}")
    
    # Procurar colunas de impressões, cliques, investimento
    imps_col = None
    clicks_col = None
    spend_col = None
    
    for col in df.columns:
        col_lower = str(col).lower()
        if 'impression' in col_lower or 'impress' in col_lower or 'imps' in col_lower:
            imps_col = col
        elif 'click' in col_lower or 'clique' in col_lower:
            clicks_col = col
        elif 'spend' in col_lower or 'invest' in col_lower or 'gasto' in col_lower or 'valor' in col_lower:
            spend_col = col
    
    # Fallback para posições padrão se não encontrou por nome
    if imps_col is None and len(df.columns) > 2:
        imps_col = df.columns[2]
    if clicks_col is None and len(df.columns) > 3:
        clicks_col = df.columns[3]
    if spend_col is None and len(df.columns) > 6:
        spend_col = df.columns[6]
    
    print(f"   Colunas detectadas: imps={imps_col}, clicks={clicks_col}, spend={spend_col}")
    
    for idx, row in df.iterrows():
        # Extrair dados usando colunas detectadas ou posições
        if date_col:
            day = str(row[date_col]) if pd.notna(row[date_col]) else ""
        else:
            day = str(row.iloc[0]) if len(row) > 0 and pd.notna(row.iloc[0]) else ""
        
        if creative_col:
            creative = str(row[creative_col]) if pd.notna(row[creative_col]) else ""
        else:
            creative = str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else ""
        
        if imps_col:
            imps = int(float(row[imps_col])) if pd.notna(row[imps_col]) else 0
        else:
            imps = int(float(row.iloc[2])) if len(row) > 2 and pd.notna(row.iloc[2]) else 0
        
        if clicks_col:
            clicks = int(float(row[clicks_col])) if pd.notna(row[clicks_col]) else 0
        else:
            clicks = int(float(row.iloc[3])) if len(row) > 3 and pd.notna(row.iloc[3]) else 0
        
        if spend_col:
            investido_str = str(row[spend_col]) if pd.notna(row[spend_col]) else "0"
        else:
            investido_str = str(row.iloc[6]) if len(row) > 6 and pd.notna(row.iloc[6]) else "0"
        
        investido = parse_investimento(investido_str)
        
        if not day or day == '' or day == 'nan':
            continue
        
        # Converter data (pode estar em vários formatos)
        try:
            # Tentar formato ISO (YYYY-MM-DD)
            dt = datetime.strptime(day, "%Y-%m-%d")
            date_key = dt.strftime("%Y-%m-%d")
            date_str = dt.strftime("%d/%m/%Y")
        except:
            try:
                # Tentar formato brasileiro (DD/MM/YYYY)
                dt = datetime.strptime(day, "%d/%m/%Y")
                date_key = dt.strftime("%Y-%m-%d")
                date_str = dt.strftime("%d/%m/%Y")
            except:
                try:
                    # Tentar formato com timestamp do Excel
                    dt = datetime.fromtimestamp((float(day) - 25569) * 86400)
                    date_key = dt.strftime("%Y-%m-%d")
                    date_str = dt.strftime("%d/%m/%Y")
                except:
                    continue
        
        # Agrupar por data e criativo
        if date_key not in dados_processados:
            dados_processados[date_key] = {}
        
        dados_processados[date_key][creative] = {
            "date": date_str,
            "creative": creative,
            "impressions": imps,
            "clicks": clicks,
            "spend": investido
        }
    
    return dados_processados


def garantir_formatos_completos(dados_processados):
    """Garante que todos os dias tenham todos os formatos de criativo"""
    # Encontrar todas as datas
    todas_datas = sorted(dados_processados.keys())
    
    # Detectar formatos reais usados nos dados
    formatos_reais = set()
    for date_key in todas_datas:
        formatos_reais.update(dados_processados[date_key].keys())
    
    # Se não encontrou formatos, usar os esperados
    formatos_para_usar = FORMATOS_ESPERADOS
    if not formatos_reais:
        formatos_para_usar = FORMATOS_ESPERADOS
        print(f"⚠️  Nenhum formato detectado, usando formatos esperados: {formatos_para_usar}")
    else:
        print(f"✅ Formatos detectados: {formatos_reais}")
        formatos_para_usar = sorted(formatos_reais)
    
    # Para cada data, garantir que tenha todos os formatos
    dados_completos = {}
    for date_key in todas_datas:
        dados_completos[date_key] = {}
        
        # Adicionar dados existentes
        if date_key in dados_processados:
            dados_completos[date_key].update(dados_processados[date_key])
        
        # Adicionar formatos faltantes com valores zero
        date_str = datetime.strptime(date_key, "%Y-%m-%d").strftime("%d/%m/%Y")
        for formato in formatos_para_usar:
            if formato not in dados_completos[date_key]:
                dados_completos[date_key][formato] = {
                    "date": date_str,
                    "creative": formato,
                    "impressions": 0,
                    "clicks": 0,
                    "spend": 0.0
                }
    
    return dados_completos, formatos_para_usar


def gerar_array_daily(dados_completos, formatos_para_usar=None):
    """Gera o array DAILY no formato JavaScript"""
    if formatos_para_usar is None:
        formatos_para_usar = FORMATOS_ESPERADOS
    daily_array = []
    
    for date_key in sorted(dados_completos.keys()):
        for formato in formatos_para_usar:
            if formato in dados_completos[date_key]:
                item = dados_completos[date_key][formato]
                daily_array.append({
                    "date": item["date"],
                    "channel": "Footfall Display",
                    "creative": item["creative"],
                    "spend": item["spend"],
                    "starts": 0,
                    "q25": 0,
                    "q50": 0,
                    "q75": 0,
                    "q100": 0,
                    "impressions": item["impressions"],
                    "clicks": item["clicks"],
                    "visits": 0
                })
    
    return daily_array


def calcular_totais(daily_array):
    """Calcula os totais consolidados"""
    total_impressions = sum(d['impressions'] for d in daily_array)
    total_clicks = sum(d['clicks'] for d in daily_array)
    total_spend = sum(d['spend'] for d in daily_array)
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    pacing = (total_spend / BUDGET_CONTRATADO * 100) if BUDGET_CONTRATADO > 0 else 0
    
    return {
        "impressions": total_impressions,
        "clicks": total_clicks,
        "spend": total_spend,
        "ctr": ctr,
        "pacing": pacing
    }


def parse_coordinate(val_str):
    """Converte coordenada com pontos como separadores para float"""
    if not val_str or val_str == '':
        return None
    try:
        val_clean = str(val_str).strip().replace('.', '').replace(',', '.')
        # Coordenadas geográficas: formato -XX.XXXX...
        # Se tem muitos dígitos, inserir ponto após o segundo dígito após o sinal
        if val_clean.startswith('-'):
            digits = val_clean[1:].replace('.', '')
            if len(digits) > 2:
                coord = float('-' + digits[:2] + '.' + digits[2:])
            else:
                coord = float(val_clean)
        else:
            digits = val_clean.replace('.', '')
            if len(digits) > 2:
                coord = float(digits[:2] + '.' + digits[2:])
            else:
                coord = float(val_clean)
        return coord
    except Exception as e:
        return None


def parse_rate(rate_str):
    """Converte taxa percentual (ex: '8,5' ou '8.5') para float"""
    if not rate_str or rate_str == '':
        return 0.0
    try:
        val_clean = str(rate_str).replace(',', '.').replace('%', '').strip()
        return float(val_clean)
    except:
        return 0.0


def processar_dados_footfall(df):
    """Processa os dados da aba Footfall e retorna lista de pontos"""
    import pandas as pd
    
    footfall_points = []
    
    for idx, row in df.iterrows():
        try:
            lat_val = None
            lon_val = None
            name = None
            users = 0
            rate = 0.0
            
            # Tentar encontrar por nome de coluna primeiro
            if 'lat' in df.columns:
                lat_val = row.get('lat')
            elif len(row) >= 1:
                lat_val = row.iloc[0] if pd.notna(row.iloc[0]) else None
                
            if 'long' in df.columns:
                lon_val = row.get('long')
            elif 'lon' in df.columns:
                lon_val = row.get('lon')
            elif len(row) >= 2:
                lon_val = row.iloc[1] if pd.notna(row.iloc[1]) else None
                
            if 'name' in df.columns:
                name = row.get('name')
            elif len(row) >= 4:
                name = row.iloc[3] if pd.notna(row.iloc[3]) else None
            elif len(row) >= 3:
                name = row.iloc[2] if pd.notna(row.iloc[2]) else None
                
            if 'Footfall Users' in df.columns:
                users_val = row.get('Footfall Users')
                try:
                    users = int(float(users_val)) if pd.notna(users_val) else 0
                except:
                    users = 0
            elif len(row) >= 5:
                users_val = row.iloc[4] if pd.notna(row.iloc[4]) else 0
                try:
                    users = int(float(users_val))
                except:
                    users = 0
            elif len(row) >= 4:
                users_val = row.iloc[3] if pd.notna(row.iloc[3]) else 0
                try:
                    users = int(float(users_val))
                except:
                    users = 0
                    
            if 'Footfall Rate %' in df.columns:
                rate_val = row.get('Footfall Rate %')
                rate = parse_rate(rate_val) if pd.notna(rate_val) else 0.0
            elif len(row) >= 6:
                rate_val = row.iloc[5] if pd.notna(row.iloc[5]) else 0
                rate = parse_rate(rate_val)
            elif len(row) >= 5:
                rate_val = row.iloc[4] if pd.notna(row.iloc[4]) else 0
                rate = parse_rate(rate_val)
            
            # Processar coordenadas
            lat = parse_coordinate(lat_val) if lat_val is not None else None
            lon = parse_coordinate(lon_val) if lon_val is not None else None
            
            # Validar dados
            if lat is None or lon is None:
                print(f"⚠️  Linha {idx}: coordenadas inválidas (lat={lat_val}, lon={lon_val})")
                continue
                
            if not name or name == '' or str(name) == 'nan':
                print(f"⚠️  Linha {idx}: nome inválido ({name})")
                continue
                
            # Validar coordenadas geográficas
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                print(f"⚠️  Linha {idx}: coordenadas fora do range (lat={lat}, lon={lon})")
                continue
            
            footfall_points.append({
                "lat": lat,
                "lon": lon,
                "name": str(name).strip(),
                "users": users,
                "rate": rate
            })
            
        except Exception as e:
            print(f"⚠️  Erro ao processar linha {idx} do Footfall: {e}")
            continue
    
    return footfall_points


def atualizar_dashboard(daily_array, totais, footfall_points=None, formatos_para_usar=None):
    """Atualiza o arquivo HTML do dashboard"""
    if not DASHBOARD_PATH.exists():
        print(f"❌ Arquivo do dashboard não encontrado: {DASHBOARD_PATH}")
        return False
    
    print(f"📝 Atualizando arquivo: {DASHBOARD_PATH}")
    
    try:
        text = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        # Gerar string do array DAILY
        daily_str = "const DAILY = [\n"
        for i, item in enumerate(daily_array):
            daily_str += f'  {{"date":"{item["date"]}","channel":"{item["channel"]}","creative":"{item["creative"]}","spend":{item["spend"]},"starts":{item["starts"]},"q25":{item["q25"]},"q50":{item["q50"]},"q75":{item["q75"]},"q100":{item["q100"]},"impressions":{item["impressions"]},"clicks":{item["clicks"]},"visits":{item["visits"]}}}'
            if i < len(daily_array) - 1:
                daily_str += ",\n"
            else:
                daily_str += "\n"
        daily_str += "];"
        
        # Substituir array DAILY
        start = text.index("const DAILY = [")
        end = text.index("];", start) + 2
        text = text[:start] + daily_str + text[end:]
        
        # Atualizar FOOTFALL_POINTS se fornecido
        if footfall_points is not None and len(footfall_points) > 0:
            footfall_str = "const FOOTFALL_POINTS = [\n"
            for i, point in enumerate(footfall_points):
                # Escapar aspas no nome
                name_escaped = str(point["name"]).replace('"', '\\"')
                footfall_str += f'  {{\n    "lat": {point["lat"]},\n    "lon": {point["lon"]},\n    "name": "{name_escaped}",\n    "users": {point["users"]},\n    "rate": {point["rate"]}\n  }}'
                if i < len(footfall_points) - 1:
                    footfall_str += ",\n"
                else:
                    footfall_str += "\n"
            footfall_str += "];"
            
            # Substituir array FOOTFALL_POINTS
            if "const FOOTFALL_POINTS = [" in text:
                start_footfall = text.index("const FOOTFALL_POINTS = [")
                end_footfall = text.index("];", start_footfall) + 2
                text = text[:start_footfall] + footfall_str + text[end_footfall:]
            else:
                # Se não existir, adicionar após DAILY
                text = text.replace(daily_str + "\n", daily_str + "\n\n" + footfall_str + "\n")
        
        # Atualizar CONS
        cons_new = f'''const CONS = {{
  "Budget Contratado (R$)": {BUDGET_CONTRATADO},
  "Budget Utilizado (R$)": {totais["spend"]:.2f},
  "Impressões": {totais["impressions"]},
  "Cliques": {totais["clicks"]},
  "CTR (%)": {totais["ctr"]/100:.6f},
  "VC (100%)": 0,
  "VTR (100%)": 0,
  "CPV (R$)": 0,
  "CPM (R$)": {CPM_CONTRATADO},
  "Pacing (%)": {totais["pacing"]/100:.5f}
}};'''
        
        cons_start = text.index("const CONS = {")
        cons_end = text.index("};", cons_start) + 2
        text = text[:cons_start] + cons_new + "\n" + text[cons_end:]
        
        # Atualizar PER
        per_new = f'''const PER = [
  {{
    "Canal": "Footfall Display",
    "Budget Contratado (R$)": {BUDGET_CONTRATADO},
    "Budget Utilizado (R$)": {totais["spend"]:.2f},
    "Impressões": {totais["impressions"]},
    "Cliques": {totais["clicks"]},
    "CTR (%)": {totais["ctr"]/100:.6f},
    "VC (100%)": 0,
    "VTR (100%)": 0,
    "CPV (R$)": 0,
    "CPM (R$)": {CPM_CONTRATADO},
    "Pacing (%)": {totais["pacing"]/100:.5f},
    "Criativos Únicos": {len(formatos_para_usar) if formatos_para_usar else len(FORMATOS_ESPERADOS)}
  }}
];'''
        
        per_start = text.index("const PER = [")
        per_end = text.index("];", per_start) + 2
        text = text[:per_start] + per_new + "\n" + text[per_end:]
        
        # Salvar arquivo
        DASHBOARD_PATH.write_text(text, encoding='utf-8')
        
        print("✅ Dashboard atualizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    print("=" * 70)
    print("🔄 ATUALIZANDO DASHBOARD PORTAL AUTO SHOPPING - CARBANK JANEIRO 2026")
    print("=" * 70)
    print()
    
    # 1. Ler dados da aba Report
    df = ler_dados_planilha()
    if df is None:
        print("❌ Não foi possível ler os dados da planilha")
        return 1
    
    # 2. Processar dados da aba Report
    print("\n📊 Processando dados da aba Report...")
    dados_processados = processar_dados(df)
    
    if not dados_processados:
        print("❌ Nenhum dado válido encontrado")
        return 1
    
    print(f"✅ Processados dados de {len(dados_processados)} dias")
    
    # 3. Garantir que todos os dias tenham todos os formatos
    print("\n🔧 Garantindo formatos completos...")
    dados_completos, formatos_para_usar = garantir_formatos_completos(dados_processados)
    
    # 4. Gerar array DAILY
    print("\n📝 Gerando array DAILY...")
    daily_array = gerar_array_daily(dados_completos, formatos_para_usar)
    print(f"✅ Gerados {len(daily_array)} registros")
    
    # 5. Calcular totais
    print("\n🧮 Calculando totais...")
    totais = calcular_totais(daily_array)
    print(f"   Impressões: {totais['impressions']:,}")
    print(f"   Cliques: {totais['clicks']:,}")
    print(f"   Investimento: R$ {totais['spend']:,.2f}")
    print(f"   CTR: {totais['ctr']:.2f}%")
    print(f"   Pacing: {totais['pacing']:.2f}%")
    
    # 6. Ler dados da aba Footfall (opcional)
    print("\n🗺️  Processando dados da aba Footfall...")
    df_footfall = ler_dados_footfall(FOOTFALL_GID)
    footfall_points = None
    
    if df_footfall is not None:
        footfall_points = processar_dados_footfall(df_footfall)
        if footfall_points:
            print(f"✅ Processados {len(footfall_points)} pontos de Footfall")
        else:
            print("⚠️  Nenhum ponto de Footfall válido encontrado")
    else:
        print("⚠️  Não foi possível ler dados da aba Footfall (continuando sem atualizar)")
    
    # 7. Atualizar dashboard
    print("\n💾 Atualizando arquivo do dashboard...")
    sucesso = atualizar_dashboard(daily_array, totais, footfall_points, formatos_para_usar)
    
    if sucesso:
        print("\n" + "=" * 70)
        print("✅ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        
        # Mostrar distribuição por dia
        from collections import Counter
        dates = [d['date'] for d in daily_array]
        date_counts = Counter(dates)
        
        print("\n📅 Distribuição por dia:")
        for date in sorted(set(dates)):
            count = date_counts[date]
            registros_com_dados = len([d for d in daily_array if d['date'] == date and d['impressions'] > 0])
            total_imps = sum([d['impressions'] for d in daily_array if d['date'] == date])
            total_clicks_dia = sum([d['clicks'] for d in daily_array if d['date'] == date])
            total_spend_dia = sum([d['spend'] for d in daily_array if d['date'] == date])
            print(f"   {date}: {count} formatos | {registros_com_dados} com dados | "
                  f"{total_imps:,} imps | {total_clicks_dia} clicks | R$ {total_spend_dia:.2f}")
        
        return 0
    else:
        print("\n❌ Erro ao atualizar dashboard")
        return 1


if __name__ == "__main__":
    sys.exit(main())
