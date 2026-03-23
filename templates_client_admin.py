# -*- coding: utf-8 -*-
"""Templates HTML para admin de clientes e painel do cliente (retornados como string)."""

def get_admin_clients_html():
    return r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerenciar clientes e usuários</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Inter, system-ui, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #fff; min-height: 100vh; padding: 24px; }
        .container { max-width: 900px; margin: 0 auto; }
        a { color: #fff; text-decoration: none; }
        a:hover { color: #f97316; }
        .nav-link { display: inline-flex; align-items: center; gap: 8px; color: #fff; padding: 6px 10px; border: 1px solid transparent; border-radius: 8px; transition: all .16s ease; }
        .nav-link:hover { border-color: rgba(249,115,22,.35); background: rgba(249,115,22,.06); }
        .nav-link.active { color: #f97316; }
        .nav-link svg { width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 1.75; stroke-linecap: round; stroke-linejoin: round; }
        h1 { font-size: 1.8rem; margin-bottom: 8px; }
        .sub { color: #9CA3AF; margin-bottom: 24px; }
        .card { background: rgba(255,255,255,0.05); border: 1px solid rgba(148,163,184,0.2); border-radius: 12px; padding: 20px; margin-bottom: 16px; }
        .card h3 { margin-bottom: 12px; font-size: 1.1rem; }
        input, select, button { padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(148,163,184,0.3); background: rgba(255,255,255,0.1); color: #fff; margin-right: 8px; margin-bottom: 8px; }
        button { cursor: pointer; background: rgba(139,92,246,0.4); border-color: #8B5CF6; font-weight: 500; }
        button:hover { opacity: 0.9; }
        button.danger { background: rgba(239,68,68,0.3); border-color: #EF4444; }
        .users-list { margin-top: 12px; font-size: 0.9rem; color: #9CA3AF; }
        .users-list div { padding: 6px 0; border-bottom: 1px solid rgba(148,163,184,0.1); display: flex; justify-content: space-between; align-items: center; }
        .users-list button { padding: 4px 10px; font-size: 0.8rem; }
        .add-user { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
        #clientList { margin-top: 20px; }
        .empty { color: #9CA3AF; padding: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div style="display:flex; gap:16px; flex-wrap:wrap; margin-bottom:12px;">
            <a href="/dashboards-list" class="nav-link"><svg viewBox="0 0 24 24"><path d="M15 18 9 12l6-6"></path></svg>Voltar à listagem de dashboards</a>
            <a href="/admin/users" class="nav-link"><svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="10" rx="2"></rect><path d="M7 11V8a5 5 0 0 1 10 0v3"></path></svg>Administrar usuários</a>
            <a href="/me/dashboards" class="nav-link"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="8" height="8" rx="1.5"></rect><rect x="13" y="3" width="8" height="5" rx="1.5"></rect><rect x="13" y="10" width="8" height="11" rx="1.5"></rect><rect x="3" y="13" width="8" height="8" rx="1.5"></rect></svg>Meus dashboards</a>
            <a href="/logout" class="nav-link"><svg viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><path d="M16 17l5-5-5-5"></path><path d="M21 12H9"></path></svg>Sair</a>
        </div>
        <h1>Gerenciar clientes e usuários</h1>
        <p class="sub">Crie clientes e associe usuários para que cada cliente acesse apenas seus dashboards.</p>
        
        <div class="card">
            <h3>Novo cliente</h3>
            <input type="text" id="newClientName" placeholder="Nome do cliente" style="min-width:200px">
            <input type="text" id="newClientSlug" placeholder="Slug (opcional, ex: acme)">
            <button type="button" id="btnCreateClient">Criar cliente</button>
        </div>
        
        <div id="clientList"></div>
    </div>
    <script>
        const api = (path, opts) => fetch(path, { headers: { 'Content-Type': 'application/json' }, ...opts }).then(r => r.json());
        async function loadClients() {
            const res = await api('/api/clients');
            const list = document.getElementById('clientList');
            if (!res.success || !res.clients.length) {
                list.innerHTML = '<div class="card empty">Nenhum cliente cadastrado. Crie um acima.</div>';
                return;
            }
            list.innerHTML = res.clients.map(c => `
                <div class="card" data-client-id="${c.client_id}">
                    <h3>${escapeHtml(c.name || c.client_id)} <span style="color:#9CA3AF;font-size:0.9rem">(${c.client_id})</span></h3>
                    <p style="margin-bottom:8px"><a href="/client/${c.client_id}/dashboards" class="nav-link"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="8" height="8" rx="1.5"></rect><rect x="13" y="3" width="8" height="5" rx="1.5"></rect><rect x="13" y="10" width="8" height="11" rx="1.5"></rect><rect x="3" y="13" width="8" height="8" rx="1.5"></rect></svg>Ver painel de dashboards</a></p>
                    <div class="users-list" id="users-${c.client_id}">Carregando usuários...</div>
                    <div class="add-user">
                        <input type="email" placeholder="E-mail do usuário" id="email-${c.client_id}" style="min-width:180px">
                        <input type="text" placeholder="Nome (opcional)" id="name-${c.client_id}">
                        <input type="password" placeholder="Senha inicial" id="password-${c.client_id}">
                        <button type="button" class="add-user-btn" data-client-id="${c.client_id}">Adicionar usuário</button>
                    </div>
                    <button type="button" class="danger" style="margin-top:12px" data-client-id="${c.client_id}" data-client-name="${escapeHtml(c.name || '')}">Excluir cliente</button>
                </div>
            `).join('');
            for (const c of res.clients) {
                loadUsers(c.client_id);
                document.querySelector(`.add-user-btn[data-client-id="${c.client_id}"]`).onclick = () => addUser(c.client_id);
                document.querySelector(`.danger[data-client-id="${c.client_id}"]`).onclick = () => deleteClient(c.client_id, c.name);
            }
        }
        function escapeHtml(s) {
            const d = document.createElement('div');
            d.textContent = s || '';
            return d.innerHTML;
        }
        async function loadUsers(clientId) {
            const res = await api('/api/clients/' + clientId + '/users');
            const el = document.getElementById('users-' + clientId);
            if (!el) return;
            if (!res.success || !res.users.length) {
                el.innerHTML = '<div>Nenhum usuário. Adicione abaixo.</div>';
                return;
            }
            el.innerHTML = res.users.map(u => `
                <div>
                    <span>${escapeHtml(u.email)} ${u.name ? '(' + escapeHtml(u.name) + ')' : ''}</span>
                    <button type="button" class="danger remove-user" data-user-id="${u.user_id}">Remover</button>
                </div>
            `).join('');
            el.querySelectorAll('.remove-user').forEach(btn => {
                btn.onclick = () => removeUser(clientId, btn.dataset.userId);
            });
        }
        async function addUser(clientId) {
            const email = document.getElementById('email-' + clientId).value.trim();
            const name = document.getElementById('name-' + clientId).value.trim();
            const password = document.getElementById('password-' + clientId).value;
            if (!email) { alert('Informe o e-mail'); return; }
            if (!password) { alert('Informe a senha inicial'); return; }
            const res = await api('/api/clients/' + clientId + '/users', { method: 'POST', body: JSON.stringify({ email, name, password }) });
            if (res.success) { document.getElementById('email-' + clientId).value = ''; document.getElementById('name-' + clientId).value = ''; document.getElementById('password-' + clientId).value = ''; loadUsers(clientId); }
            else alert(res.message || 'Erro');
        }
        async function removeUser(clientId, userId) {
            if (!confirm('Remover este usuário?')) return;
            const res = await api('/api/clients/' + clientId + '/users/' + userId, { method: 'DELETE' });
            if (res.success) loadUsers(clientId);
            else alert(res.message || 'Erro');
        }
        async function deleteClient(clientId, name) {
            if (!confirm('Excluir o cliente "' + (name || clientId) + '"? Isso não desvincula os dashboards.')) return;
            const res = await api('/api/clients/' + clientId, { method: 'DELETE' });
            if (res.success) loadClients();
            else alert(res.message || 'Erro');
        }
        document.getElementById('btnCreateClient').onclick = async () => {
            const name = document.getElementById('newClientName').value.trim();
            if (!name) { alert('Informe o nome do cliente'); return; }
            const slug = document.getElementById('newClientSlug').value.trim() || undefined;
            const res = await api('/api/clients', { method: 'POST', body: JSON.stringify({ name, slug }) });
            if (res.success) { document.getElementById('newClientName').value = ''; document.getElementById('newClientSlug').value = ''; loadClients(); }
            else alert(res.message || 'Erro');
        };
        loadClients();
    </script>
</body>
</html>
"""


def get_client_portal_html(client, dashboards):
    """Gera HTML do painel do cliente com lista de dashboards."""
    name = (client.get('name') or client.get('client_id') or 'Cliente')
    client_id = client.get('client_id') or ''
    cards = []
    for d in dashboards:
        ckey = d.get('campaign_key') or ''
        cname = d.get('campaign_name') or d.get('dashboard_name') or ckey
        channel = d.get('channel') or ''
        cards.append(f'''
            <div class="card">
                <div class="card-title">{cname}</div>
                <div class="card-meta">{channel}</div>
                <a href="/api/dashboard/{ckey}" class="btn-primary">Ver Dashboard</a>
            </div>
        ''')
    cards_html = '\n'.join(cards) if cards else '<p class="empty">Nenhum dashboard vinculado a este cliente.</p>'
    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel - {name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Inter, system-ui, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #fff; min-height: 100vh; padding: 24px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        a {{ color: #fff; text-decoration: none; }}
        a:hover {{ color: #f97316; }}
        .nav-link {{ display: inline-flex; align-items: center; gap: 8px; color: #fff; padding: 6px 10px; border: 1px solid transparent; border-radius: 8px; transition: all .16s ease; }}
        .nav-link:hover {{ border-color: rgba(249,115,22,.35); background: rgba(249,115,22,.06); }}
        .nav-link svg {{ width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 1.75; stroke-linecap: round; stroke-linejoin: round; }}
        h1 {{ font-size: 1.8rem; margin-bottom: 8px; }}
        .sub {{ color: #9CA3AF; margin-bottom: 24px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-top: 20px; }}
        .card {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(148,163,184,0.2); border-radius: 12px; padding: 20px; }}
        .card-title {{ font-weight: 600; margin-bottom: 8px; }}
        .card-meta {{ color: #9CA3AF; font-size: 0.9rem; margin-bottom: 12px; }}
        .btn-primary {{ display: inline-block; padding: 10px 16px; background: rgba(139,92,246,0.4); border-radius: 8px; color: #C4B5FD; font-weight: 500; }}
        .btn-primary:hover {{ opacity: 0.9; }}
        .empty {{ color: #9CA3AF; padding: 40px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div style="display:flex; gap:16px; flex-wrap:wrap; margin-bottom:12px;">
            <a href="/me/dashboards" class="nav-link"><svg viewBox="0 0 24 24"><path d="M15 18 9 12l6-6"></path></svg>Meus dashboards</a>
            <a href="/logout" class="nav-link"><svg viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><path d="M16 17l5-5-5-5"></path><path d="M21 12H9"></path></svg>Sair</a>
        </div>
        <h1>Painel - {name}</h1>
        <p class="sub">Dashboards disponíveis para este cliente</p>
        <div class="grid">
            {cards_html}
        </div>
    </div>
</body>
</html>
"""
