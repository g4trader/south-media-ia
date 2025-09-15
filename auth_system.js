/**
 * Sistema de Autenticação Robusto
 * Arquitetura escalável para gerenciamento de usuários e roles
 */

class AuthSystem {
    constructor() {
        this.storageKey = 'dashboard_auth_system';
        this.sessionKey = 'dashboard_session';
        this.initializeSystem();
    }

    /**
     * Inicializar sistema com usuários padrão
     */
    initializeSystem() {
        const systemData = this.getSystemData();
        
        if (!systemData.users) {
            // Usuários iniciais do sistema
            systemData.users = [
                {
                    id: 'admin_001',
                    username: 'admin',
                    password: 'dashboard2025', // Hash será implementado
                    email: 'admin@iasouth.tech',
                    role: 'super_admin',
                    permissions: ['*'], // Todas as permissões
                    status: 'active',
                    created_at: new Date().toISOString(),
                    last_login: null,
                    profile: {
                        full_name: 'Administrador do Sistema',
                        department: 'TI',
                        avatar: null
                    }
                },
                {
                    id: 'manager_001',
                    username: 'manager',
                    password: 'manager2025',
                    email: 'manager@iasouth.tech',
                    role: 'manager',
                    permissions: ['dashboard:view', 'dashboard:sync', 'reports:view'],
                    status: 'active',
                    created_at: new Date().toISOString(),
                    last_login: null,
                    profile: {
                        full_name: 'Gerente de Operações',
                        department: 'Operações',
                        avatar: null
                    }
                },
                {
                    id: 'viewer_001',
                    username: 'viewer',
                    password: 'viewer2025',
                    email: 'viewer@iasouth.tech',
                    role: 'viewer',
                    permissions: ['dashboard:view'],
                    status: 'active',
                    created_at: new Date().toISOString(),
                    last_login: null,
                    profile: {
                        full_name: 'Visualizador',
                        department: 'Comercial',
                        avatar: null
                    }
                }
            ];
            
            // Roles do sistema
            systemData.roles = [
                {
                    id: 'super_admin',
                    name: 'Super Administrador',
                    description: 'Acesso total ao sistema',
                    permissions: ['*'],
                    level: 100
                },
                {
                    id: 'admin',
                    name: 'Administrador',
                    description: 'Acesso administrativo completo',
                    permissions: [
                        'dashboard:view', 'dashboard:sync', 'dashboard:manage',
                        'users:view', 'users:manage', 'reports:view', 'reports:create'
                    ],
                    level: 80
                },
                {
                    id: 'manager',
                    name: 'Gerente',
                    description: 'Acesso gerencial limitado',
                    permissions: [
                        'dashboard:view', 'dashboard:sync', 'reports:view', 'reports:create'
                    ],
                    level: 60
                },
                {
                    id: 'analyst',
                    name: 'Analista',
                    description: 'Acesso para análise e relatórios',
                    permissions: [
                        'dashboard:view', 'reports:view', 'reports:create'
                    ],
                    level: 40
                },
                {
                    id: 'viewer',
                    name: 'Visualizador',
                    description: 'Apenas visualização',
                    permissions: ['dashboard:view'],
                    level: 20
                }
            ];

            // Permissões do sistema
            systemData.permissions = [
                { id: 'dashboard:view', name: 'Visualizar Dashboard', category: 'dashboard' },
                { id: 'dashboard:sync', name: 'Sincronizar Dashboard', category: 'dashboard' },
                { id: 'dashboard:manage', name: 'Gerenciar Dashboard', category: 'dashboard' },
                { id: 'users:view', name: 'Visualizar Usuários', category: 'users' },
                { id: 'users:manage', name: 'Gerenciar Usuários', category: 'users' },
                { id: 'reports:view', name: 'Visualizar Relatórios', category: 'reports' },
                { id: 'reports:create', name: 'Criar Relatórios', category: 'reports' },
                { id: 'system:config', name: 'Configurar Sistema', category: 'system' }
            ];

            this.saveSystemData(systemData);
        }
    }

    /**
     * Obter dados do sistema
     */
    getSystemData() {
        const data = localStorage.getItem(this.storageKey);
        return data ? JSON.parse(data) : {};
    }

    /**
     * Salvar dados do sistema
     */
    saveSystemData(data) {
        localStorage.setItem(this.storageKey, JSON.stringify(data));
    }

    /**
     * Autenticar usuário
     */
    async authenticate(username, password) {
        const systemData = this.getSystemData();
        const user = systemData.users.find(u => 
            u.username === username && 
            u.password === password && 
            u.status === 'active'
        );

        if (!user) {
            return { success: false, message: 'Credenciais inválidas' };
        }

        // Atualizar último login
        user.last_login = new Date().toISOString();
        this.saveSystemData(systemData);

        // Criar sessão
        const session = {
            user_id: user.id,
            username: user.username,
            role: user.role,
            permissions: user.permissions,
            login_time: new Date().toISOString(),
            expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24 horas
            token: this.generateToken(user),
            profile: user.profile
        };

        localStorage.setItem(this.sessionKey, JSON.stringify(session));
        
        return { 
            success: true, 
            user: this.sanitizeUser(user),
            session: session
        };
    }

    /**
     * Verificar se usuário está autenticado
     */
    isAuthenticated() {
        const session = this.getCurrentSession();
        if (!session) return false;

        // Verificar se sessão não expirou
        if (new Date(session.expires_at) < new Date()) {
            this.logout();
            return false;
        }

        return true;
    }

    /**
     * Obter sessão atual
     */
    getCurrentSession() {
        const sessionData = localStorage.getItem(this.sessionKey);
        if (!sessionData) return null;

        try {
            return JSON.parse(sessionData);
        } catch {
            return null;
        }
    }

    /**
     * Obter usuário atual
     */
    getCurrentUser() {
        const session = this.getCurrentSession();
        if (!session) return null;

        const systemData = this.getSystemData();
        return systemData.users.find(u => u.id === session.user_id);
    }

    /**
     * Verificar permissão
     */
    hasPermission(permission) {
        const session = this.getCurrentSession();
        if (!session) return false;

        // Super admin tem todas as permissões
        if (session.permissions.includes('*')) return true;

        return session.permissions.includes(permission);
    }

    /**
     * Verificar role
     */
    hasRole(role) {
        const session = this.getCurrentSession();
        if (!session) return false;

        return session.role === role;
    }

    /**
     * Obter nível de acesso
     */
    getAccessLevel() {
        const session = this.getCurrentSession();
        if (!session) return 0;

        const systemData = this.getSystemData();
        const role = systemData.roles.find(r => r.id === session.role);
        return role ? role.level : 0;
    }

    /**
     * Logout
     */
    logout() {
        localStorage.removeItem(this.sessionKey);
    }

    /**
     * Gerar token simples (para evolução futura)
     */
    generateToken(user) {
        // Implementação simples - pode ser melhorada com JWT
        return btoa(`${user.id}:${user.username}:${Date.now()}`);
    }

    /**
     * Remover dados sensíveis do usuário
     */
    sanitizeUser(user) {
        const { password, ...sanitized } = user;
        return sanitized;
    }

    /**
     * Obter todos os usuários (apenas para admin)
     */
    getAllUsers() {
        if (!this.hasPermission('users:view')) {
            return { success: false, message: 'Sem permissão' };
        }

        const systemData = this.getSystemData();
        return {
            success: true,
            users: systemData.users.map(user => this.sanitizeUser(user))
        };
    }

    /**
     * Criar novo usuário (apenas para admin)
     */
    createUser(userData) {
        if (!this.hasPermission('users:manage')) {
            return { success: false, message: 'Sem permissão' };
        }

        const systemData = this.getSystemData();
        
        // Verificar se usuário já existe
        if (systemData.users.find(u => u.username === userData.username)) {
            return { success: false, message: 'Usuário já existe' };
        }

        const newUser = {
            id: `user_${Date.now()}`,
            username: userData.username,
            password: userData.password, // Hash será implementado
            email: userData.email,
            role: userData.role || 'viewer',
            permissions: userData.permissions || [],
            status: 'active',
            created_at: new Date().toISOString(),
            last_login: null,
            profile: userData.profile || {}
        };

        systemData.users.push(newUser);
        this.saveSystemData(systemData);

        return { success: true, user: this.sanitizeUser(newUser) };
    }

    /**
     * Obter roles disponíveis
     */
    getRoles() {
        const systemData = this.getSystemData();
        return systemData.roles || [];
    }

    /**
     * Obter permissões disponíveis
     */
    getPermissions() {
        const systemData = this.getSystemData();
        return systemData.permissions || [];
    }
}

// Instância global do sistema de autenticação
window.authSystem = new AuthSystem();

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthSystem;
}
