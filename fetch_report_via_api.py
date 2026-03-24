#!/usr/bin/env python3
"""
Busca a aba Report da planilha via Google Sheets API e imprime:
- Cabeçalhos, número de linhas, soma da coluna 100% Complete (VC).
Uso: python fetch_report_via_api.py [sheet_id] [gid_report]
     gid_report opcional = GID da aba Report (ex: 364193781) para forçar essa aba.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SHEET_ID_FPS = "1m75KVkyj7nQJTJ2GTI8o1Bp7HnJVPlOYeHjTBqnrxCE"
GID_REPORT_FPS = 364193781

def main():
    sheet_id = (sys.argv[1] if len(sys.argv) > 1 else SHEET_ID_FPS).strip()
    gid_report = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else GID_REPORT_FPS

    print("📊 Planilha (Sheets API):", sheet_id)
    print("   GID aba Report:", gid_report)
    print()

    try:
        from google_sheets_service import GoogleSheetsService
    except ImportError as e:
        print("❌ Import:", e)
        return 1

    svc = GoogleSheetsService()
    if not svc.is_configured():
        print("❌ Google Sheets não configurado (credenciais).")
        return 1
    api = svc._service

    try:
        meta = api.spreadsheets().get(spreadsheetId=sheet_id).execute()
    except Exception as e:
        print("❌ Erro ao acessar planilha:", e)
        if sheet_id == SHEET_ID_FPS and "invalid_grant" in str(e).lower():
            print()
            print("💡 Referência (aba Report, 50 linhas 2025-12-23 a 2026-02-10):")
            print("   Rode com credenciais válidas para ver o somatório real da planilha.")
            print("   Confira credenciais (credentials.json) ou execute no Cloud Run.")
        return 1

    sheets = meta.get("sheets", [])
    report_title = None
    for sh in sheets:
        pid = sh.get("properties", {}).get("sheetId")
        if pid == gid_report:
            report_title = sh["properties"].get("title")
            break
    if not report_title:
        report_title = "Report"
        for sh in sheets:
            t = (sh.get("properties") or {}).get("title", "")
            if "report" in t.lower():
                report_title = t
                break

    range_name = f"'{report_title}'!A:Z" if " " in report_title else f"{report_title}!A:Z"
    try:
        result = api.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name,
        ).execute()
    except Exception as e:
        print("❌ Erro ao ler aba:", e)
        return 1

    values = result.get("values", [])
    if not values:
        print("❌ Aba vazia.")
        return 1

    headers = values[0]
    rows = values[1:]
    print("📋 Aba:", report_title)
    print("📋 Cabeçalhos:", headers)
    print("📊 Linhas de dados (bruto):", len(rows))

    idx_vc = None
    for i, h in enumerate(headers):
        if h is None:
            continue
        h = str(h).strip().lower()
        if "100%" in h and "complete" in h:
            idx_vc = i
            break
    if idx_vc is None:
        print("⚠️ Coluna '100% Complete' não encontrada. Índices:", list(range(len(headers))))
        return 0

    total_vc = 0
    count = 0
    for row in rows:
        if len(row) <= idx_vc:
            continue
        cell = row[idx_vc]
        if cell is None or str(cell).strip() == "":
            continue
        try:
            s = str(cell).strip().replace(".", "").replace(",", ".")
            total_vc += int(float(s))
            count += 1
        except ValueError:
            pass

    print("📊 Linhas com valor em 100% Complete:", count)
    print("📊 SOMA (coluna 100% Complete) =", total_vc)
    print("     (formato BR: {:,})".format(total_vc).replace(",", "X").replace(".", ",").replace("X", "."))
    print()
    # Mostrar linha a linha para conferir com a planilha
    print("--- Linha a linha (Data | 100% Complete) ---")
    idx_date = 0
    for i, h in enumerate(headers):
        if h and "day" in str(h).lower() or (h and "data" in str(h).lower()):
            idx_date = i
            break
    total_check = 0
    for i, row in enumerate(rows):
        if len(row) <= max(idx_date, idx_vc):
            continue
        date_cell = row[idx_date] if len(row) > idx_date else ""
        vc_cell = row[idx_vc] if len(row) > idx_vc else ""
        if not str(vc_cell).strip():
            continue
        try:
            v = int(float(str(vc_cell).strip().replace(".", "").replace(",", ".")))
            total_check += v
            print(f"  {date_cell}  |  {v}")
        except ValueError:
            print(f"  {date_cell}  |  (inválido: {vc_cell})")
    print("--- Soma conferida:", total_check)
    print()
    print("✅ Compare o total acima com o que aparece na planilha e com o dashboard (VC Entregue).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
