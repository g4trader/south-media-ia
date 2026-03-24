# Diagnóstico: diferença na soma da coluna 100% Complete

## Resultado

| Origem | Total 100% Complete (VC) |
|--------|---------------------------|
| **Soma na planilha** (selecionando a coluna) | **301.166** |
| **Soma na importação** (CSV/API) | **311.982** |
| **Diferença** | **10.816** |

## Causa identificada

A diferença vem de **uma única linha**:

- **Data:** 2026-02-05  
- **Na planilha:** o valor da célula na coluna **100% Complete** é **0** (ou está vazia), por isso a soma na planilha dá 301.166.  
- **No CSV/importação:** o mesmo campo vem como **10.816**.

Ou seja: na exportação CSV (e na leitura que fazemos), o valor **10.816** aparece na coluna **100% Complete** do dia 2026-02-05. Esse 10.816 é exatamente o valor da coluna **75% Video Complete** dessa mesma linha (75% = 10.942 na planilha; 10.816 é próximo e pode ser valor antigo ou de outra célula deslocada).

Conclusão: **na linha 2026-02-05 o valor da coluna 100% Complete está “errado” na exportação** (aparece 10.816 em vez de 0), o que explica por que a soma selecionando a coluna na planilha (301.166) é diferente da soma que importamos (311.982).

## Por que pode acontecer

1. **Célula na planilha com 0 ou vazia**  
   Se na planilha a célula 2026-02-05 × 100% Complete está em 0 (ou vazia), a soma da coluna será 301.166. O CSV/API pode estar trazendo um valor antigo ou de outra célula (ex.: 75%) por:
   - cache da exportação, ou  
   - desalinhamento pontual na exportação (vírgula, fórmula, formato).

2. **Fórmula na célula**  
   Se a célula de 100% Complete tiver fórmula (ex.: referenciando 75%), o valor exportado pode ser o calculado (10.816) e não o “0” que você vê por formatação/regra na planilha.

3. **Número de colunas**  
   No CSV, a linha 2026-02-05 tem o mesmo número de colunas que as outras (13). Ou seja, não há coluna “a mais” ou “a menos” nessa linha; o problema é o **valor** que aparece na posição da coluna 100% Complete (10.816 em vez de 0).

## O que fazer

1. **Na planilha**  
   - Abra a célula **2026-02-05** na coluna **100% Complete**.  
   - Confirme se está **0** ou vazia (para bater com a soma 301.166).  
   - Se estiver 10.816, altere para 0 e salve; na próxima exportação/importação a soma deve ficar 301.166.

2. **No código (extrator)**  
   Existe uma regra de segurança: se em alguma linha **100% Complete > 75% Video Complete**, o valor de 100% é corrigido para 0 (desalinhamento).  
   No 2026-02-05 temos 10.816 < 10.942 (75%), então essa regra **não** se aplica. Para a importação bater com 301.166, o mais seguro é **ajustar na planilha** a célula 2026-02-05 da coluna 100% Complete para **0** (ou deixar vazia). Assim a próxima exportação/importação já virá correta.
