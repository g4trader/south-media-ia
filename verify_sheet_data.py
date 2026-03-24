#!/usr/bin/env python3
"""
Script para acessar planilhas via API e listar dados (contrato, report) para verificação.
Uso: python verify_sheet_data.py [sheet_id] [--contract-only]
"""
import sys
import os
import json

# Garantir que o projeto está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    # Planilha FPS Youtube (Faculdade Pernambucana de Saúde)
    sheet_id_fps = "1m75KVkyj7nQJTJ2GTI8o1Bp7HnJVPlOYeHjTBqnrxCE"
    # Planilha CarnaPortal
    sheet_id_carna = "1tLz31iH7xVJgIvdGbMlfs8kf0mdeWhZuG8D8x1n3fDY"

    sheet_id = (sys.argv[1] if len(sys.argv) > 1 else sheet_id_fps).strip()
    contract_only = "--contract-only" in sys.argv

    print(f"📊 Verificando planilha: {sheet_id}\n")

    try:
        from real_google_sheets_extractor import RealGoogleSheetsExtractor, CampaignConfig
    except ImportError as e:
        print(f"❌ Erro ao importar extrator: {e}")
        return 1

    config = CampaignConfig(
        client="Verificação",
        campaign="Verificação",
        campaign_key="verify",
        sheet_id=sheet_id,
    )
    # KPI CPV para planilha FPS (Youtube); para CarnaPortal pode ser CPM/Display
    if sheet_id == sheet_id_fps:
        config.kpi = "CPV"
    if sheet_id == sheet_id_carna:
        config.kpi = "CPM"

    try:
        extractor = RealGoogleSheetsExtractor(config)
        data = extractor.extract_data()
    except Exception as e:
        print(f"❌ Erro ao extrair dados: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if not data:
        print("❌ Nenhum dado retornado.")
        return 1

    # === CONTRATO ===
    contract = data.get("contract") or {}
    print("=== ABA CONTRATO (Informações de contrato) ===")
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    print()

    # Métricas que vêm do contrato e são usadas no dashboard
    print("--- Valores usados no dashboard ---")
    print(f"  complete_views_contracted (VC Contratadas): {contract.get('complete_views_contracted')}")
    print(f"  period_start: {contract.get('period_start')}")
    print(f"  period_end:   {contract.get('period_end')}")
    print(f"  investment:   {contract.get('investment')}")
    print()

    if contract_only:
        return 0

    # === RESUMO DA CAMPANHA (métricas calculadas) ===
    summary = data.get("campaign_summary") or {}
    print("=== MÉTRICAS CALCULADAS (a partir da aba Report) ===")
    print(f"  total_video_completions (VCs entregues): {summary.get('total_video_completions')}")
    print(f"  total_impressions: {summary.get('total_impressions')}")
    print(f"  total_spend:       {summary.get('total_spend')}")
    print(f"  total_clicks:      {summary.get('total_clicks')}")
    print(f"  pacing:            {summary.get('pacing')}%")
    print()

    # === DADOS DIÁRIOS ===
    daily = data.get("daily_data") or []
    print(f"=== ABA REPORT (dados diários): {len(daily)} linhas ===")
    if daily:
        total_vc = sum(int(d.get("video_completions") or 0) for d in daily)
        dates = [d.get("date") for d in daily[:3]]
        print(f"  Soma de video_completions (total VCs): {total_vc}")
        print(f"  Primeiras datas: {dates} ...")
        if len(daily) <= 15:
            for i, row in enumerate(daily):
                print(f"    [{i+1}] date={row.get('date')} impressions={row.get('impressions')} video_completions={row.get('video_completions')} spend={row.get('spend')}")
    print()
    print("✅ Verificação concluída.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
