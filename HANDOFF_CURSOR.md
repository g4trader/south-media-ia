# Handoff - South Media IA (Cursor)

## Objetivo atual
Padronizar o sistema com painel superadmin consistente, sidebar persistente e visual unificado no estilo da rota `/dash-generator-pro-multicanal`.

## O que foi implementado
- Fluxo pós-login:
  - Superadmin redireciona para `/panel`.
  - Usuário cliente redireciona para `/me/dashboards` e depois para `/client/<client_id>/dashboards`.
- Painel superadmin:
  - Rota principal: `/panel`.
  - Menu lateral com rotas administrativas.
  - Tela inicial com cards de clientes e quantidade de dashboards vinculados.
- Sidebar persistente:
  - Mantida nas rotas principais de superadmin:
    - `/panel`
    - `/dashboards-list`
    - `/dash-generator-pro`
    - `/dash-generator-pro-multicanal`
    - `/admin/users`
    - `/admin/clients`
- Ícones:
  - Atualizados para SVG outline (sem preenchimento sólido).
  - Estado normal em branco, ativo em laranja.
- Visual unificado:
  - Base visual alinhada ao estilo multicanal (paleta, cards, painéis, botões, campos, hover).

## Arquivos principais alterados
- `cloud_run_mvp.py`
- `templates_client_admin.py`

## Produção (Cloud Run)
- Serviço: `gen-dashboard-ia`
- URL: `https://gen-dashboard-ia-609095880025.us-central1.run.app`
- Rota principal superadmin: `/panel`

## Como validar rapidamente
1. Login com usuário superadmin.
2. Confirmar redirecionamento para `/panel`.
3. Navegar entre:
   - `/dashboards-list`
   - `/dash-generator-pro`
   - `/dash-generator-pro-multicanal`
   - `/admin/users`
   - `/admin/clients`
4. Verificar que a sidebar não desaparece e o estilo visual permanece consistente.

## Próximos passos sugeridos
- Refinar responsividade (mobile/tablet) para menu e grids.
- Ajustar estado ativo contextual em `/client/<client_id>/dashboards` (ex.: destacar "Clientes").
- Criar testes automatizados básicos de navegação autenticada (smoke tests).

## Contexto para retomar em outro chat
Cole este prompt no novo chat:

> "Continuar o projeto South Media IA a partir do handoff em `HANDOFF_CURSOR.md`. Priorizar consistência visual do superadmin e validar navegação com sidebar persistente em todas as rotas administrativas."

