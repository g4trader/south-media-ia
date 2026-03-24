#!/usr/bin/env python3
"""
Diagnóstico: por que a soma da coluna 100% Complete na planilha
diferente da soma que importamos (API/CSV).

Identifica:
- Qual linha contribui com a diferença (311.982 - 301.166 = 10.816)
- Se há desalinhamento de colunas (vírgula dentro de célula, etc.)
- Se há linha extra (total/resumo) sendo contada
"""
import sys
import requests
import csv
from io import StringIO

SHEET_ID = "1m75KVkyj7nQJTJ2GTI8o1Bp7HnJVPlOYeHjTBqnrxCE"
GID = "364193781"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

def run():
    print("📥 Baixando aba Report (CSV)...")
    r = requests.get(URL, timeout=15)
    r.raise_for_status()
    text = r.text

    # Parse com csv.reader (respeita aspas e vírgulas dentro de células)
    reader = csv.reader(StringIO(text))
    rows = list(reader)
    if not rows:
        print("❌ Nenhuma linha.")
        return

    header = rows[0]
    # Encontrar índices exatos pelos nomes das colunas
    col_75 = col_100 = None
    for i, h in enumerate(header):
        h = (h or "").strip()
        if "75%" in h and "Complete" in h:
            col_75 = i
        if "100%" in h and "Complete" in h:
            col_100 = i

    if col_75 is None or col_100 is None:
        print("❌ Colunas 75% ou 100% Complete não encontradas.")
        print("   Header:", header)
        return

    print(f"\n📋 Colunas: 75% Complete = índice {col_75}, 100% Complete = índice {col_100}")
    print(f"   Header (primeiros 10): {header[:10]}\n")

    total_75 = 0
    total_100 = 0
    excess_100 = []   # linhas em que 100% > 75% (inconsistência)
    by_date = []     # (date, n75, n100, num_cols) para debug

    for i, row in enumerate(rows[1:], start=2):
        if not row:
            continue
        date = row[0].strip() if len(row) > 0 else ""
        # Pular linhas sem data (totais/resumo)
        if not date or date.lower() in ("total", "resumo", "soma", ""):
            if len(row) > col_100:
                try:
                    v = row[col_100].strip().replace(".", "")
                    if v and v.isdigit():
                        print(f"⚠️ Linha {i} (sem data): parece linha de TOTAL/RESUMO com valor na col 100%: {v}")
                except Exception:
                    pass
            continue

        n75 = n100 = 0
        try:
            if len(row) > col_75:
                n75 = int(row[col_75].strip().replace(".", ""))
            if len(row) > col_100:
                n100 = int(row[col_100].strip().replace(".", ""))
        except ValueError:
            print(f"⚠️ Linha {i} date={date!r}: valor não numérico 75%={row[col_75] if len(row) > col_75 else '?'} 100%={row[col_100] if len(row) > col_100 else '?'}")
            continue

        total_75 += n75
        total_100 += n100
        by_date.append((date, n75, n100, len(row)))

        if n75 > 0 and n100 > n75:
            excess_100.append((i, date, n75, n100))

    print("=== SOMA IMPORTADA (como o código usa) ===")
    print(f"   Total 75% Video Complete: {total_75}")
    print(f"   Total 100% Complete (VC): {total_100}")
    print()

    # Diferença que o usuário relatou
    expected = 301_166
    diff = total_100 - expected
    print("=== DIFERENÇA EM RELAÇÃO AO VALOR DA PLANILHA ===")
    print(f"   Valor que você vê na planilha (soma da coluna 100%): {expected}")
    print(f"   Valor que importamos: {total_100}")
    print(f"   Diferença: {diff}")
    print()

    if excess_100:
        print("=== LINHAS COM 100% > 75% (possível desalinhamento de colunas) ===")
        for line_no, date, n75, n100 in excess_100:
            print(f"   Linha {line_no} | data={date} | 75%={n75} | 100%={n100} (diferença +{n100 - n75})")
        print("   → Nestas linhas, o valor da coluna 75% pode ter ‘entrado’ na coluna 100% na exportação.")
        print()

    # Qual linha, se tivesse 0 em 100%, daria o total esperado?
    if diff > 0:
        print("=== QUAL LINHA CAUSA A DIFERENÇA? ===")
        print(f"   Se uma única linha tivesse 0 em 100% em vez do valor atual, a soma cairia em {diff}.")
        print("   Linhas cujo valor em 100% é exatamente essa diferença:")
        for date, n75, n100, ncols in by_date:
            if n100 == diff:
                print(f"   → data={date} | 75%={n75} | 100%={n100} ← esta linha tem 100% = {diff}")
        if not any(n100 == diff for _, _, n100, _ in by_date):
            print("   (Nenhuma linha tem 100% exatamente =", diff, ")")
            print("   Linhas com maior 100%:")
            sorted_by_100 = sorted(by_date, key=lambda x: -x[2])
            for date, n75, n100, _ in sorted_by_100[:5]:
                print(f"      {date}: 100%={n100} 75%={n75}")
    print()

    # Verificar se alguma linha tem número de colunas diferente (possível quebra de parsing)
    lens = [len(row) for row in rows[1:] if row and (row[0].strip() or "").replace(".", "").replace("-", "").isdigit()]
    if lens:
        from collections import Counter
        c = Counter(lens)
        if len(c) > 1:
            print("=== NÚMERO DE COLUNAS POR LINHA (possível desalinhamento) ===")
            for ncols, count in sorted(c.items(), key=lambda x: -x[1]):
                print(f"   {count} linhas com {ncols} colunas")
            print("   → Se variar, pode ser vírgula/aspas dentro de célula deslocando colunas.")
    print("\n✅ Diagnóstico concluído.")

if __name__ == "__main__":
    run()
