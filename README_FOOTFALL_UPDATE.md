# 🏪 Sistema de Atualização - Footfall Out

Este sistema permite atualizar os dados da aba **Footfall Out** do dashboard com dados da planilha do Google Sheets.

## 📊 Fonte dos Dados

**Google Sheets:** [Report Sonho - Footfall Out](https://docs.google.com/spreadsheets/d/1etGnblqr5YZIqXIweKj5qTMGqmWlxL9OLbN_Ss5tzlQ/edit?gid=120680471#gid=120680471)

## 🚀 Como Atualizar os Dados

### Método 1: Atualização Automática (Recomendado)

```bash
python3 update_footfall_out_data.py
```

Este script:
- ✅ Extrai dados da planilha do Google Sheets
- ✅ Atualiza o arquivo `dash_sonho_v2.html`
- ✅ Salva dados em `footfall_out_data.json`
- ✅ Calcula métricas automaticamente

### Método 2: Gerenciador Interativo

```bash
python3 footfall_data_manager.py
```

Menu interativo com opções:
1. Atualizar do arquivo JSON
2. Adicionar nova loja
3. Remover loja
4. Listar lojas
5. Mostrar status
6. Sair

### Método 3: Edição Manual

1. Edite o arquivo `footfall_out_data.json`
2. Execute: `python3 footfall_data_manager.py` → Opção 1

## 📁 Arquivos do Sistema

| Arquivo | Descrição |
|---------|-----------|
| `update_footfall_out_data.py` | Script principal de atualização |
| `footfall_data_manager.py` | Gerenciador interativo de dados |
| `footfall_out_data.json` | Arquivo de dados atualizados |
| `static/dash_sonho_v2.html` | Dashboard com dados atualizados |

## 📋 Estrutura dos Dados

```json
{
  "last_updated": "2024-10-27 15:30:00",
  "source": "Google Sheets URL",
  "data": [
    {
      "lat": -8.092339308671470,
      "lon": -34.888475077469840,
      "name": "Recibom - Av. Eng. Domingos Ferreira, 306 - Pina",
      "users": 5673,
      "rate": 12.1
    }
  ],
  "metrics": {
    "total_users": 51216,
    "active_stores": 12,
    "avg_conversion": 10.0,
    "best_store": "Recibom boa viagem - R. Barão de Souza Leão, 767 - Boa Viagem",
    "best_store_users": 6731
  }
}
```

## 🔄 Processo de Atualização

1. **Extração**: Dados são extraídos da planilha do Google Sheets
2. **Processamento**: Cálculo de métricas e validação
3. **Atualização**: Arquivo HTML é atualizado com novos dados
4. **Backup**: Dados são salvos em arquivo JSON para futuras atualizações

## 📊 Dados Atuais (Outubro 2024)

- **Total de Usuários**: 51,216
- **Lojas Ativas**: 12
- **Taxa de Conversão Média**: 10.0%
- **Melhor Loja**: Recibom Boa Viagem (6,731 usuários)

## 🛠️ Manutenção

### Adicionar Nova Loja

```bash
python3 footfall_data_manager.py
# Escolha opção 2 e preencha os dados
```

### Remover Loja

```bash
python3 footfall_data_manager.py
# Escolha opção 3 e informe o nome da loja
```

### Verificar Status

```bash
python3 footfall_data_manager.py
# Escolha opção 5 para ver status atual
```

## 🧪 Teste de Atualização

```bash
python3 test_updated_data.py
```

Este script verifica se:
- ✅ Dados foram carregados corretamente
- ✅ Métricas estão corretas
- ✅ Interface está funcionando
- ✅ Total de usuários e lojas correspondem

## 📈 Próximas Melhorias

- [ ] Integração direta com Google Sheets API
- [ ] Atualização automática por cron job
- [ ] Validação de dados mais robusta
- [ ] Histórico de alterações
- [ ] Notificações de atualização

## 🆘 Solução de Problemas

### Erro: "Arquivo não encontrado"
- Verifique se está no diretório correto
- Execute: `ls -la static/dash_sonho_v2.html`

### Erro: "Dados não correspondem"
- Verifique se a planilha foi atualizada
- Execute o script de atualização novamente

### Erro: "Métricas incorretas"
- Verifique o arquivo `footfall_out_data.json`
- Execute o teste: `python3 test_updated_data.py`

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs de erro
2. Execute o teste de validação
3. Consulte este README
4. Verifique a planilha do Google Sheets

---

**Última atualização**: 27 de Outubro de 2024  
**Versão**: 1.0  
**Status**: ✅ Funcionando

