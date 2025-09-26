#!/usr/bin/env python3
"""
Script para debugar os valores da planilha
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from real_google_sheets_extractor import RealGoogleSheetsExtractor

class Config:
    def __init__(self):
        self.client = "Copacol"
        self.campaign = "Institucional 30s"
        self.sheet_id = "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8"

def debug_values():
    """Debugar valores específicos da planilha"""
    print("🔍 Debugando valores da planilha...")
    
    config = Config()
    
    try:
        # Criar extrator
        extractor = RealGoogleSheetsExtractor(config)
        
        # Acessar diretamente o serviço
        df = extractor._extract_daily_data_real()
        
        if df is not None and not df.empty:
            print(f"✅ DataFrame carregado: {len(df)} linhas, {len(df.columns)} colunas")
            print(f"📋 Colunas disponíveis: {list(df.columns)}")
            
            # Verificar coluna de investimento
            if 'Valor investido' in df.columns:
                print(f"\n💰 Coluna 'Valor investido' encontrada!")
                print(f"📊 Primeiros 10 valores:")
                for i in range(min(10, len(df))):
                    value = df.iloc[i]['Valor investido']
                    print(f"  Linha {i+1}: '{value}' (tipo: {type(value)})")
                
                # Tentar converter
                print(f"\n🔄 Tentando converter valores...")
                import pandas as pd
                converted = pd.to_numeric(df['Valor investido'].astype(str).str.replace(',', '.'), errors='coerce')
                print(f"📊 Valores convertidos (primeiros 10):")
                for i in range(min(10, len(converted))):
                    print(f"  Linha {i+1}: {converted.iloc[i]}")
                
                # Somar total
                total = converted.sum()
                print(f"\n💰 Total de investimento: R$ {total:,.2f}")
                
            else:
                print("❌ Coluna 'Valor investido' não encontrada")
                print("📋 Colunas disponíveis:")
                for col in df.columns:
                    print(f"  - '{col}'")
                    
        else:
            print("❌ DataFrame vazio")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_values()
