# 📊 CORREÇÃO DO CTR NA TABELA DA ABA VISÃO GERAL

## ❌ **PROBLEMA IDENTIFICADO:**
CTR estava aparecendo como "—" em vez dos valores reais na tabela "Resumo por Canal" da aba "Visão Geral".

## 🔍 **CAUSA DO PROBLEMA:**
- **Código incorreto**: `pct(r['CTR'])`
- **Chave correta**: `pct(r['CTR (%)'])`
- **Resultado**: JavaScript não encontrava a chave, retornava "—"

## ✅ **CORREÇÃO APLICADA:**

### **Arquivos Corrigidos:**
1. **static/dash_sonho.html**: Referência corrigida
2. **index.html**: Atualizado com correção

### **Mudanças:**
```javascript
// ANTES (incorreto):
['📈 CTR', pct(r['CTR'])],

// DEPOIS (correto):
['📈 CTR', pct(r['CTR (%)'])],
```

## 📋 **LOCAIS CORRIGIDOS:**
- ✅ **Aba Por Canal**: Métricas de canal individual
- ✅ **Aba Visão Geral**: Tabela "Resumo por Canal"

## 🎯 **RESULTADO ESPERADO:**
Agora o CTR deve aparecer com os valores reais:
- **TikTok**: 2.88%
- **Footfall Display**: 1.61%
- **Outros canais**: 0.00% (quando aplicável)

## ⏱️ **TEMPO DE ATUALIZAÇÃO:**
- **Deploy**: 1-3 minutos
- **Cache**: 1-2 minutos
- **Total**: 2-5 minutos

## 🔍 **VERIFICAÇÃO:**
Após deploy concluído:
1. Acesse a aba "Visão Geral"
2. Verifique a tabela "Resumo por Canal"
3. Confirme que CTR mostra valores reais

---

**Status**: ✅ Correção aplicada  
**Problema**: CTR como "—"  
**Solução**: Chave correta 'CTR (%)'  
**Resultado**: Valores reais do CTR
