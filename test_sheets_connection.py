#!/usr/bin/env python3
"""
Script para testar conexão com as planilhas específicas fornecidas
"""

import os
import sys
from datetime import datetime

def test_sheet_connection():
    """Testa conexão com cada planilha específica"""
    
    print("🧪 TESTE DE CONEXÃO COM PLANILHAS ESPECÍFICAS")
    print("=" * 60)
    
    # URLs fornecidas pelo usuário
    sheets_info = [
        {
            "name": "YouTube",
            "sheet_id": "1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo",
            "gid": "1863167182",
            "url": "https://docs.google.com/spreadsheets/d/1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo/edit?gid=1863167182#gid=1863167182"
        },
        {
            "name": "TikTok", 
            "sheet_id": "1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM",
            "gid": "1727929489",
            "url": "https://docs.google.com/spreadsheets/d/1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM/edit?gid=1727929489#gid=1727929489"
        },
        {
            "name": "Netflix",
            "sheet_id": "1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo", 
            "gid": "1743413064",
            "url": "https://docs.google.com/spreadsheets/d/1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo/edit?gid=1743413064#gid=1743413064"
        },
        {
            "name": "CTV",
            "sheet_id": "1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U",
            "gid": "1743413064", 
            "url": "https://docs.google.com/spreadsheets/d/1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U/edit?gid=1743413064#gid=1743413064"
        },
        {
            "name": "Disney",
            "sheet_id": "1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o",
            "gid": "1743413064",
            "url": "https://docs.google.com/spreadsheets/d/1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o/edit?gid=1743413064#gid=1743413064"
        },
        {
            "name": "Footfall Display",
            "sheet_id": "10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA",
            "gid": "1743413064",
            "url": "https://docs.google.com/spreadsheets/d/10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA/edit?gid=1743413064#gid=1743413064"
        },
        {
            "name": "Footfall Data",
            "sheet_id": "10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA", 
            "gid": "120680471",
            "url": "https://docs.google.com/spreadsheets/d/10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA/edit?gid=120680471#gid=120680471"
        }
    ]
    
    try:
        from google_sheets_processor import GoogleSheetsProcessor
        
        processor = GoogleSheetsProcessor()
        print("✅ Processador Google Sheets inicializado")
        
        results = []
        
        for sheet_info in sheets_info:
            print(f"\n📊 Testando: {sheet_info['name']}")
            print(f"   Sheet ID: {sheet_info['sheet_id']}")
            print(f"   GID: {sheet_info['gid']}")
            
            try:
                # Testar conexão
                df = processor.read_sheet_data(
                    sheet_id=sheet_info['sheet_id'],
                    gid=sheet_info['gid']
                )
                
                if not df.empty:
                    print(f"   ✅ SUCESSO! {len(df)} linhas encontradas")
                    print(f"   📋 Colunas: {list(df.columns)}")
                    
                    # Mostrar algumas linhas de exemplo
                    if len(df) > 0:
                        print(f"   📄 Primeira linha: {df.iloc[0].to_dict()}")
                    
                    results.append({
                        'name': sheet_info['name'],
                        'success': True,
                        'rows': len(df),
                        'columns': list(df.columns)
                    })
                else:
                    print(f"   ⚠️ CONECTADO mas sem dados")
                    results.append({
                        'name': sheet_info['name'], 
                        'success': False,
                        'error': 'Sem dados'
                    })
                    
            except Exception as e:
                print(f"   ❌ ERRO: {e}")
                results.append({
                    'name': sheet_info['name'],
                    'success': False, 
                    'error': str(e)
                })
        
        # Resumo final
        print(f"\n📊 RESUMO DOS TESTES")
        print("=" * 40)
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['name']}")
            
            if result['success']:
                print(f"    📊 {result['rows']} linhas, {len(result['columns'])} colunas")
            else:
                print(f"    ❌ Erro: {result['error']}")
        
        print(f"\n📈 Resultado: {successful}/{total} planilhas conectadas com sucesso")
        
        if successful == total:
            print("\n🎉 TODAS AS PLANILHAS ESTÃO ACESSÍVEIS!")
            print("✅ A automação está pronta para usar essas planilhas")
            return True
        else:
            print(f"\n⚠️ {total - successful} planilha(s) com problemas")
            print("❌ Verifique as permissões e URLs das planilhas")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("Execute: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    try:
        success = test_sheet_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
