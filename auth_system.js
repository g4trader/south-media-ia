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
     * Inicializar sistema com usuários padrão e empresas
     */
    initializeSystem() {
        const systemData = this.getSystemData();
        
        if (!systemData.companies) {
            // Empresas iniciais do sistema
            systemData.companies = [
                {
                    id: 'company_001',
                    name: 'IA South Tech',
                    code: 'IASOUTH',
                    description: 'Empresa principal de tecnologia',
                    status: 'active',
                    created_at: new Date().toISOString(),
                    settings: {
                        theme: 'default',
                        timezone: 'America/Sao_Paulo',
                        language: 'pt-BR'
                    },
                    contact: {
                        email: 'contato@iasouth.tech',
                        phone: '+55 11 99999-9999',
                        address: 'São Paulo, SP, Brasil'
                    }
                },
                {
                    id: 'company_002',
                    name: 'Sonho Digital',
                    code: 'SONHO',
                    description: 'Empresa de marketing digital',
                    status: 'active',
                    created_at: new Date().toISOString(),
                    settings: {
                        theme: 'default',
                        timezone: 'America/Sao_Paulo',
                        language: 'pt-BR'
                    },
                    contact: {
                        email: 'contato@sonhodigital.com',
                        phone: '+55 11 88888-8888',
                        address: 'São Paulo, SP, Brasil'
                    }
                },
                {
                    id: 'company_003',
                    name: 'Analytics Pro',
                    code: 'ANALYTICS',
                    description: 'Empresa de análise de dados',
                    status: 'active',
                    created_at: new Date().toISOString(),
                    settings: {
                        theme: 'default',
                        timezone: 'America/Sao_Paulo',
                        language: 'pt-BR'
                    },
                    contact: {
                        email: 'contato@analyticspro.com',
                        phone: '+55 11 77777-7777',
                        address: 'Rio de Janeiro, RJ, Brasil'
                    }
                }
            ];
        }
        
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
                    company_id: null, // Super admin não tem empresa específica
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
                    company_id: 'company_001', // IA South Tech
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
                    company_id: 'company_001', // IA South Tech
                    profile: {
                        full_name: 'Visualizador',
                        department: 'Comercial',
                        avatar: null
                    }
                },
                {
                    id: 'sonho_manager_001',
                    username: 'sonho_manager',
                    password: 'sonho2025',
                    email: 'manager@sonhodigital.com',
                    role: 'manager',
                    permissions: ['dashboard:view', 'dashboard:sync', 'reports:view'],
                    status: 'active',
                    created_at: new Date().toISOString(),
                    last_login: null,
                    company_id: 'company_002', // Sonho Digital
                    profile: {
                        full_name: 'Gerente Sonho Digital',
                        department: 'Marketing',
                        avatar: null
                    }
                },
                {
                    id: 'analytics_viewer_001',
                    username: 'analytics_viewer',
                    password: 'analytics2025',
                    email: 'viewer@analyticspro.com',
                    role: 'viewer',
                    permissions: ['dashboard:view'],
                    status: 'active',
                    created_at: new Date().toISOString(),
                    last_login: null,
                    company_id: 'company_003', // Analytics Pro
                    profile: {
                        full_name: 'Analista de Dados',
                        department: 'Analytics',
                        avatar: null
                    }
                }
            ];
        }
            
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
                { id: 'companies:view', name: 'Visualizar Empresas', category: 'companies' },
                { id: 'companies:manage', name: 'Gerenciar Empresas', category: 'companies' },
                { id: 'reports:view', name: 'Visualizar Relatórios', category: 'reports' },
                { id: 'reports:create', name: 'Criar Relatórios', category: 'reports' },
                { id: 'system:config', name: 'Configurar Sistema', category: 'system' }
            ];

            // Inicializar dashboards com associação às empresas
            if (!systemData.dashboards) {
                systemData.dashboards = [
                    {
                        id: 'dashboard_001',
                        file: 'dash_sonho.html',
                        name: 'Dashboard Sonho',
                        description: 'Dashboard principal com métricas de performance e análise de dados',
                        category: 'Principal',
                        icon: '📈',
                        status: 'active',
                        company_id: 'company_002', // Sonho Digital
                        permissions: ['dashboard:view', 'dashboard:sync'],
                        created_at: new Date().toISOString()
                    },
                    {
                        id: 'dashboard_002',
                        file: 'dash_analytics.html',
                        name: 'Analytics Dashboard',
                        description: 'Análise detalhada de métricas e KPIs do negócio',
                        category: 'Analytics',
                        icon: '📊',
                        status: 'active',
                        company_id: 'company_001', // IA South Tech
                        permissions: ['dashboard:view'],
                        created_at: new Date().toISOString()
                    },
                    {
                        id: 'dashboard_003',
                        file: 'dash_financeiro.html',
                        name: 'Dashboard Financeiro',
                        description: 'Controle financeiro e métricas de receita',
                        category: 'Financeiro',
                        icon: '💰',
                        status: 'active',
                        company_id: 'company_001', // IA South Tech
                        permissions: ['dashboard:view'],
                        created_at: new Date().toISOString()
                    },
                    {
                        id: 'dashboard_004',
                        file: 'dash_operacional.html',
                        name: 'Dashboard Operacional',
                        description: 'Métricas operacionais e indicadores de produção',
                        category: 'Operacional',
                        icon: '⚙️',
                        status: 'active',
                        company_id: 'company_001', // IA South Tech
                        permissions: ['dashboard:view'],
                        created_at: new Date().toISOString()
                    },
                    {
                        id: 'dashboard_005',
                        file: 'dash_comercial.html',
                        name: 'Dashboard Comercial',
                        description: 'Análise de vendas e performance comercial',
                        category: 'Comercial',
                        icon: '🛒',
                        status: 'active',
                        company_id: 'company_002', // Sonho Digital
                        permissions: ['dashboard:view'],
                        created_at: new Date().toISOString()
                    },
                    {
                        id: 'dashboard_006',
                        file: 'dash_rh.html',
                        name: 'Dashboard RH',
                        description: 'Métricas de recursos humanos e produtividade',
                        category: 'RH',
                        icon: '👥',
                        status: 'active',
                        company_id: 'company_001', // IA South Tech
                        permissions: ['dashboard:view'],
                        created_at: new Date().toISOString()
                    },
                    {
                        id: 'dashboard_007',
                        file: 'dash_marketing.html',
                        name: 'Dashboard Marketing',
                        description: 'Análise de campanhas e métricas de marketing',
                        category: 'Marketing',
                        icon: '📢',
                        status: 'active',
                        company_id: 'company_002', // Sonho Digital
                        permissions: ['dashboard:view'],
                        created_at: new Date().toISOString()
                    },
                    {
                        id: 'dashboard_008',
                        file: 'dash_data_analytics.html',
                        name: 'Data Analytics Pro',
                        description: 'Análise avançada de dados e machine learning',
                        category: 'Analytics',
                        icon: '🤖',
                        status: 'active',
                        company_id: 'company_003', // Analytics Pro
                        permissions: ['dashboard:view'],
                        created_at: new Date().toISOString()
                    }
                ];
            }

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

    /**
     * Obter empresa do usuário atual
     */
    getCurrentUserCompany() {
        const user = this.getCurrentUser();
        if (!user || !user.company_id) return null;
        
        const systemData = this.getSystemData();
        return systemData.companies.find(c => c.id === user.company_id);
    }

    /**
     * Obter todas as empresas (apenas para super admin)
     */
    getAllCompanies() {
        if (!this.hasPermission('companies:view')) {
            return { success: false, message: 'Sem permissão' };
        }

        const systemData = this.getSystemData();
        return {
            success: true,
            companies: systemData.companies || []
        };
    }

    /**
     * Criar nova empresa (apenas para super admin)
     */
    createCompany(companyData) {
        if (!this.hasPermission('companies:manage')) {
            return { success: false, message: 'Sem permissão' };
        }

        const systemData = this.getSystemData();
        
        // Verificar se empresa já existe
        if (systemData.companies.find(c => c.code === companyData.code)) {
            return { success: false, message: 'Código da empresa já existe' };
        }

        const newCompany = {
            id: `company_${Date.now()}`,
            name: companyData.name,
            code: companyData.code,
            description: companyData.description || '',
            status: 'active',
            created_at: new Date().toISOString(),
            settings: {
                theme: 'default',
                timezone: 'America/Sao_Paulo',
                language: 'pt-BR',
                ...companyData.settings
            },
            contact: {
                email: companyData.email || '',
                phone: companyData.phone || '',
                address: companyData.address || '',
                ...companyData.contact
            }
        };

        systemData.companies.push(newCompany);
        this.saveSystemData(systemData);

        return { success: true, company: newCompany };
    }

    /**
     * Obter dashboards filtrados por empresa
     */
    getDashboardsForUser() {
        const user = this.getCurrentUser();
        if (!user) return [];

        const systemData = this.getSystemData();
        const dashboards = systemData.dashboards || [];
        
        // Super admin vê todos os dashboards
        if (user.role === 'super_admin') {
            return dashboards;
        }
        
        // Outros usuários veem apenas dashboards da sua empresa
        if (user.company_id) {
            return dashboards.filter(d => d.company_id === user.company_id);
        }
        
        return [];
    }

    /**
     * Associar dashboard a empresa
     */
    associateDashboardToCompany(dashboardId, companyId) {
        if (!this.hasPermission('dashboard:manage')) {
            return { success: false, message: 'Sem permissão' };
        }

        const systemData = this.getSystemData();
        const dashboard = systemData.dashboards.find(d => d.id === dashboardId);
        
        if (!dashboard) {
            return { success: false, message: 'Dashboard não encontrado' };
        }

        dashboard.company_id = companyId;
        this.saveSystemData(systemData);

        return { success: true, dashboard };
    }

    /**
     * Verificar se usuário tem acesso a dashboard específico
     */
    hasDashboardAccess(dashboardId) {
        const user = this.getCurrentUser();
        if (!user) return false;

        // Super admin tem acesso a tudo
        if (user.role === 'super_admin') return true;

        const systemData = this.getSystemData();
        const dashboard = systemData.dashboards.find(d => d.id === dashboardId);
        
        if (!dashboard) return false;

        // Usuário deve ter a mesma empresa do dashboard
        return dashboard.company_id === user.company_id;
    }
}

// Instância global do sistema de autenticação
window.authSystem = new AuthSystem();

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthSystem;
}
