# Smoke tests (geração e validação)

Este repositório tem um smoke test ponta-a-ponta para acelerar o ciclo **gerar → validar → corrigir**.

## 1) Dependências

O script usa apenas `requests` (já presente em `requirements.txt`).

## 2) Variáveis de ambiente

- `BASE_URL`: URL base do serviço (ex.: `https://gen-dashboard-ia-609095880025.us-central1.run.app`)
- `SMOKE_EMAIL`: e-mail de um usuário **super_admin**
- `SMOKE_PASSWORD`: senha
- `SMOKE_SHEET_HHS`: sheet id (Google Sheets) da planilha HHS
- `SMOKE_SHEET_OHS`: sheet id (Google Sheets) da planilha OHS
- `SMOKE_SHEET_CTV`: sheet id (Google Sheets) da planilha CTV
- `SMOKE_SHEET_DISNEY`: sheet id (Google Sheets) da planilha Disney
- `SMOKE_SHEET_NETFLIX`: sheet id (Google Sheets) da planilha Netflix
- `SMOKE_SHEET_SPOTIFY`: sheet id (Google Sheets) da planilha Spotify
- `SMOKE_SHEET_YOUTUBE`: sheet id (Google Sheets) da planilha Youtube

Opcionais:
- `SMOKE_CLIENT` (default: `SMOKE`)
- `SMOKE_CAMPAIGN_NAME` (default: `smoke_multicanal_<timestamp>`)
- `SMOKE_TIMEOUT_SEC` (default: `40`)

## 3) Rodar

```bash
BASE_URL="https://gen-dashboard-ia-609095880025.us-central1.run.app" \
SMOKE_EMAIL="SEU_EMAIL" \
SMOKE_PASSWORD="SUA_SENHA" \
SMOKE_SHEET_HHS="SHEET_ID_HHS" \
SMOKE_SHEET_OHS="SHEET_ID_OHS" \
SMOKE_SHEET_CTV="SHEET_ID_CTV" \
SMOKE_SHEET_DISNEY="SHEET_ID_DISNEY" \
SMOKE_SHEET_NETFLIX="SHEET_ID_NETFLIX" \
SMOKE_SHEET_SPOTIFY="SHEET_ID_SPOTIFY" \
SMOKE_SHEET_YOUTUBE="SHEET_ID_YOUTUBE" \
python3 smoke_generation.py
```

## 4) O que ele valida

- Login por `POST /api/auth/login`
- Geração multicanal por `POST /api/generate-dashboard-multicanal`
- HTML público em `GET /api/dashboard/<campaign_key>`
  - verifica **marcadores do template novo** (`dash_multicanal_footfall_tabs_template.html`)
  - verifica se `window.EMBEDDED_CAMPAIGN_DATA` contém `footfall_sources` (lista)
- Dados públicos em `GET /api/<campaign_key>/data`

