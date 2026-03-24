#!/usr/bin/env python3
"""
Lê planilha com permissão "Qualquer pessoa com o link" via export CSV.
Uso: python read_sheet_public.py [sheet_id] [gid_report] [gid_contract]

Exemplo FPS Youtube:
  python read_sheet_public.py 1m75KVkyj7nQJTJ2GTI8o1Bp7HnJVPlOYeHjTBqnrxCE 364193781 0

Exemplo CarnaPortal:
  python read_sheet_public.py 1tLz31iH7xVJgIvdGbMlfs8kf0mdeWhZuG8D8x1n3fDY 304137877 1939638014
"""
import sys
import requests
from io import StringIO

def main():
    sheet_id = sys.argv[1] if len(sys.argv) > 1 else "1m75KVkyj7nQJTJ2GTI8o1Bp7HnJVPlOYeHjTBqnrxCE"
    gid_report = sys.argv[2] if len(sys.argv) > 2 else "364193781"
    gid_contract = sys.argv[3] if len(sys.argv) > 3 else "0"  # 0 = primeira aba

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

    print(f"📊 Planilha: {sheet_id}")
    print(f"   Report (gid={gid_report}), Contrato (gid={gid_contract})\n")

    # Aba Report
    url_report = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid_report}"
    try:
        r = requests.get(url_report, headers=headers, timeout=15)
        r.raise_for_status()
        text = r.text
        lines = text.strip().split("\n")
        print(f"=== ABA REPORT ({len(lines)} linhas) ===")
        print(lines[0])  # header
        for i, line in enumerate(lines[1:11], 1):
            print(f"  {i}: {line[:120]}{'...' if len(line) > 120 else ''}")
        if len(lines) > 11:
            print(f"  ... e mais {len(lines) - 11} linhas")
        # Soma coluna 100% Complete com parsing CSV correto (campos entre aspas)
        if lines:
            import csv
            reader = csv.reader(StringIO(text))
            rows = list(reader)
            header = rows[0]
            idx_vc = next((i for i, h in enumerate(header) if h.strip() == "100% Complete"), None)
            if idx_vc is not None:
                total = 0
                count = 0
                for row in rows[1:]:
                    if len(row) > idx_vc and (row[0].strip() if row else ""):
                        try:
                            v = row[idx_vc].strip().replace(".", "")
                            total += int(v)
                            count += 1
                        except ValueError:
                            pass
                print(f"\n  Linhas com data: {count}")
                print(f"  Total coluna '100% Complete' (VC): {total}")
        print()
    except Exception as e:
        print(f"❌ Erro ao ler Report: {e}\n")

    # Aba Contrato (se gid diferente de report)
    if gid_contract != gid_report and gid_contract != "0":
        url_contract = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid_contract}"
        try:
            r = requests.get(url_contract, headers=headers, timeout=15)
            r.raise_for_status()
            text = r.text
            lines = text.strip().split("\n")
            print(f"=== ABA CONTRATO ({len(lines)} linhas) ===")
            for line in lines[:15]:
                print(f"  {line}")
            print()
        except Exception as e:
            print(f"❌ Erro ao ler Contrato: {e}\n")

    # Se gid_contract é 0, tentar primeira aba (às vezes é a de contrato)
    if gid_contract == "0":
        url_any = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        try:
            r = requests.get(url_any, headers=headers, timeout=15)
            r.raise_for_status()
            text = r.text
            lines = text.strip().split("\n")
            print(f"=== PRIMEIRA ABA ({len(lines)} linhas) ===")
            for line in lines[:12]:
                print(f"  {line[:100]}")
            print()
        except Exception as e:
            print(f"❌ Erro ao ler primeira aba: {e}")

    print("✅ Concluído.")

if __name__ == "__main__":
    main()
