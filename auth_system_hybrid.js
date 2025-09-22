/**
 * Sistema de Autenticação Híbrido
 * Firebase Firestore como prioridade + localStorage como fallback
 */

class HybridAuthSystem {
    constructor() {
        this.storageKey = 'dashboard_auth_system';
        this.sessionKey = 'dashboard_session';
        this.firebaseAuth = null;
        this.isFirebaseAvailable = false;
        this.isInitialized = false;
        this.init();
    }

    async init() {
        try {
            console.log('🔄 Inicializando sistema híbrido...');
            
            // Try to load Firebase first
            await this.initializeFirebase();
            
            // If Firebase fails, use localStorage
            if (!this.isFirebaseAvailable) {
                console.log('⚠️ Firebase não disponível, usando localStorage');
                this.initializeLocalStorage();
            }
            
            this.isInitialized = true;
            console.log('✅ Sistema híbrido inicializado com sucesso!');
            
        } catch (error) {
            console.error('❌ Erro ao inicializar sistema híbrido:', error);
            this.initializeLocalStorage();
        }
    }

    async initializeFirebase() {
        try {
            // Check if Firebase is available
            if (typeof window !== 'undefined' && window.firebaseAuthSystem) {
                this.firebaseAuth = window.firebaseAuthSystem;
                this.isFirebaseAvailable = true;
                console.log('✅ Firebase disponível e carregado');
                return true;
            }
            
            // Try to load Firebase modules
            try {
                // Check if Firebase is available globally
                if (typeof window !== 'undefined' && window.firebaseAuthSystem) {
                    this.firebaseAuth = window.firebaseAuthSystem;
                    this.isFirebaseAvailable = true;
                    console.log('✅ Firebase carregado globalmente');
                    return true;
                }
            } catch (error) {
                console.log('⚠️ Firebase não pôde ser carregado:', error.message);
            }
            
            return false;
        } catch (error) {
            console.error('❌ Erro ao inicializar Firebase:', error);
            return false;
        }
    }

    initializeLocalStorage() {
        console.log('🔄 Inicializando localStorage...');
        const systemData = this.getSystemData();
        
        if (!systemData.companies) {
            systemData.companies = this.getDefaultCompanies();
        }
        
        if (!systemData.users) {
            systemData.users = this.getDefaultUsers();
        }
        
        if (!systemData.dashboards) {
            systemData.dashboards = this.getDefaultDashboards();
        }
        
        if (!systemData.roles) {
            systemData.roles = this.getDefaultRoles();
        }
        
        if (!systemData.permissions) {
            systemData.permissions = this.getDefaultPermissions();
        }
        
        this.saveSystemData(systemData);
        console.log('✅ localStorage inicializado');
    }

    // Authentication methods
    async authenticate(username, password) {
        try {
            if (!this.isInitialized) {
                await this.init();
            }

            if (this.isFirebaseAvailable && this.firebaseAuth) {
                console.log('🔥 Usando Firebase para autenticação');
                return await this.firebaseAuth.authenticate(username, password);
            } else {
                console.log('💾 Usando localStorage para autenticação');
                return this.authenticateLocal(username, password);
            }
        } catch (error) {
            console.error('❌ Erro na autenticação:', error);
            return { success: false, message: 'Erro interno do servidor' };
        }
    }

    authenticateLocal(username, password) {
        const systemData = this.getSystemData();
        const user = systemData.users.find(u => u.username === username);
        
        if (!user) {
            return { success: false, message: 'Usuário não encontrado' };
        }
        
        if (user.password !== password) {
            return { success: false, message: 'Senha incorreta' };
        }
        
        if (user.status !== 'active') {
            return { success: false, message: 'Usuário inativo' };
        }
        
        // Create session
        const sessionData = {
            user_id: user.id,
            username: user.username,
            role: user.role,
            company_id: user.company_id,
            login_time: new Date().toISOString(),
            expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
        };
        
        localStorage.setItem(this.sessionKey, JSON.stringify(sessionData));
        
        return {
            success: true,
            user: user,
            session: sessionData
        };
    }

    async logout() {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.logout();
            } else {
                localStorage.removeItem(this.sessionKey);
                return true;
            }
        } catch (error) {
            console.error('❌ Erro no logout:', error);
            return false;
        }
    }

    isAuthenticated() {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return this.firebaseAuth.isAuthenticated();
            } else {
                const sessionData = this.getCurrentSession();
                if (!sessionData) return false;
                
                if (new Date() > new Date(sessionData.expires_at)) {
                    this.logout();
                    return false;
                }
                
                return true;
            }
        } catch (error) {
            console.error('❌ Erro ao verificar autenticação:', error);
            return false;
        }
    }

    getCurrentSession() {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return this.firebaseAuth.getCurrentSession();
            } else {
                const sessionData = localStorage.getItem(this.sessionKey);
                return sessionData ? JSON.parse(sessionData) : null;
            }
        } catch (error) {
            console.error('❌ Erro ao obter sessão:', error);
            return null;
        }
    }

    async getCurrentUser() {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.getCurrentUser();
            } else {
                const session = this.getCurrentSession();
                if (!session) return null;
                
                const systemData = this.getSystemData();
                return systemData.users.find(u => u.id === session.user_id);
            }
        } catch (error) {
            console.error('❌ Erro ao obter usuário atual:', error);
            return null;
        }
    }

    async getCurrentUserCompany() {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.getCurrentUserCompany();
            } else {
                const user = await this.getCurrentUser();
                if (!user || !user.company_id) return null;
                
                const systemData = this.getSystemData();
                return systemData.companies.find(c => c.id === user.company_id);
            }
        } catch (error) {
            console.error('❌ Erro ao obter empresa do usuário:', error);
            return null;
        }
    }

    // Company management
    async getAllCompanies() {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.getAllCompanies();
            } else {
                const systemData = this.getSystemData();
                return systemData.companies || [];
            }
        } catch (error) {
            console.error('❌ Erro ao obter empresas:', error);
            return [];
        }
    }

    async createCompany(companyData) {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.createCompany(companyData);
            } else {
                const systemData = this.getSystemData();
                const newCompany = {
                    ...companyData,
                    id: 'company_' + Date.now(),
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                };
                systemData.companies.push(newCompany);
                this.saveSystemData(systemData);
                return newCompany.id;
            }
        } catch (error) {
            console.error('❌ Erro ao criar empresa:', error);
            throw error;
        }
    }

    // Dashboard management
    async getDashboardsForUser() {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.getDashboardsForUser();
            } else {
                // Listar dashboards dinamicamente da pasta /static
                const dashboards = await this.getStaticDashboards();
                const user = await this.getCurrentUser();
                
                if (!user) return [];
                
                if (user.role === 'super_admin') {
                    return dashboards;
                } else if (user.company_id) {
                    return dashboards.filter(d => d.company_id === user.company_id);
                }
                
                return [];
            }
        } catch (error) {
            console.error('❌ Erro ao obter dashboards do usuário:', error);
            return [];
        }
    }

    // Nova função para listar dashboards da pasta /static
    async getStaticDashboards() {
        try {
            // Lista de arquivos HTML na pasta static (atualizada com arquivos existentes)
            const staticFiles = [
                'dash_copacol.html',
                'dash_copacol_mestre_das_grelhas.html',
                'dash_dauher_hidrabene.html',
                'dash_sebrae.html',
                'dash_semana_do_pescado_FINAL_NO_NETFLIX_20250916_172902.html',
                'dash_sonho.html',
                'dash_unicesusc.html',
                'dash_unimed.html'
            ];

            const dashboards = staticFiles.map((file, index) => {
                // Extrair nome da campanha do arquivo
                let name = file.replace('dash_', '').replace('.html', '');
                
                // Limpar nome removendo timestamps e sufixos
                name = name.replace(/_\d{8}_\d{6}/g, ''); // Remove timestamps
                name = name.replace(/_FINAL_NO_NETFLIX/g, '');
                name = name.replace(/_NO_NETFLIX/g, '');
                name = name.replace(/_PLANNING_UPDATED/g, '');
                
                // Capitalizar primeira letra de cada palavra
                name = name.split('_').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
                ).join(' ');

                // Determinar ícone baseado no nome
                let icon = '📊';
                if (name.toLowerCase().includes('sonho')) icon = '🌟';
                else if (name.toLowerCase().includes('copacol')) icon = '🏢';
                else if (name.toLowerCase().includes('sebrae')) icon = '💼';
                else if (name.toLowerCase().includes('unimed')) icon = '🏥';
                else if (name.toLowerCase().includes('unicesusc')) icon = '🎓';
                else if (name.toLowerCase().includes('dauher')) icon = '💊';
                else if (name.toLowerCase().includes('pescado')) icon = '🐟';
                else if (name.toLowerCase().includes('campaign')) icon = '📈';

                return {
                    id: `dashboard_${index + 1}`,
                    file: file,
                    name: name,
                    company_id: 'company_001', // Default para super admin
                    description: `Dashboard ${name} - Relatório analítico completo`,
                    icon: icon,
                    status: 'active',
                    category: 'Campanha',
                    last_updated: new Date().toISOString(),
                    created_at: new Date().toISOString()
                };
            });

            console.log(`✅ ${dashboards.length} dashboards encontrados na pasta /static`);
            return dashboards;

        } catch (error) {
            console.error('❌ Erro ao listar dashboards da pasta /static:', error);
            return [];
        }
    }

    async createDashboard(dashboardData) {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.createDashboard(dashboardData);
            } else {
                const systemData = this.getSystemData();
                const newDashboard = {
                    ...dashboardData,
                    id: 'dashboard_' + Date.now(),
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                };
                systemData.dashboards.push(newDashboard);
                this.saveSystemData(systemData);
                return newDashboard.id;
            }
        } catch (error) {
            console.error('❌ Erro ao criar dashboard:', error);
            throw error;
        }
    }

    // User management
    async getAllUsers() {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.getAllUsers();
            } else {
                const systemData = this.getSystemData();
                return systemData.users || [];
            }
        } catch (error) {
            console.error('❌ Erro ao obter usuários:', error);
            return [];
        }
    }

    async createUser(userData) {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.createUser(userData);
            } else {
                const systemData = this.getSystemData();
                const newUser = {
                    ...userData,
                    id: 'user_' + Date.now(),
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                };
                systemData.users.push(newUser);
                this.saveSystemData(systemData);
                return newUser.id;
            }
        } catch (error) {
            console.error('❌ Erro ao criar usuário:', error);
            throw error;
        }
    }

    // Permission checking
    hasPermission(permission) {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return this.firebaseAuth.hasPermission(permission);
            } else {
                const session = this.getCurrentSession();
                if (!session) return false;
                
                if (session.role === 'super_admin') return true;
                
                const basicPermissions = ['dashboard:view', 'dashboard:sync'];
                return basicPermissions.includes(permission);
            }
        } catch (error) {
            console.error('❌ Erro ao verificar permissão:', error);
            return false;
        }
    }

    // System status
    async getSystemStatus() {
        try {
            if (this.isFirebaseAvailable && this.firebaseAuth) {
                return await this.firebaseAuth.getSystemStatus();
            } else {
                const systemData = this.getSystemData();
                return {
                    companies: systemData.companies?.length || 0,
                    users: systemData.users?.length || 0,
                    dashboards: systemData.dashboards?.length || 0,
                    isInitialized: this.isInitialized,
                    database: 'localStorage'
                };
            }
        } catch (error) {
            console.error('❌ Erro ao obter status do sistema:', error);
            return {
                companies: 0,
                users: 0,
                dashboards: 0,
                isInitialized: false,
                database: 'error'
            };
        }
    }

    // Local storage methods
    getSystemData() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : {};
        } catch (error) {
            console.error('❌ Erro ao obter dados do sistema:', error);
            return {};
        }
    }

    saveSystemData(data) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('❌ Erro ao salvar dados do sistema:', error);
            return false;
        }
    }

    // Default data methods
    getDefaultCompanies() {
        return [
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
                description: 'Especialistas em análise de dados',
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

    getDefaultUsers() {
        return [
            {
                id: 'admin_001',
                username: 'admin',
                password: 'dashboard2025',
                role: 'super_admin',
                company_id: null,
                profile: {
                    full_name: 'Administrador do Sistema',
                    email: 'admin@iasouth.tech',
                    avatar: '👑'
                },
                status: 'active',
                last_login: null,
                created_at: new Date().toISOString()
            },
            {
                id: 'manager_001',
                username: 'manager',
                password: 'manager2025',
                role: 'manager',
                company_id: 'company_001',
                profile: {
                    full_name: 'Gerente IA South',
                    email: 'manager@iasouth.tech',
                    avatar: '👨‍💼'
                },
                status: 'active',
                last_login: null,
                created_at: new Date().toISOString()
            },
            {
                id: 'viewer_001',
                username: 'viewer',
                password: 'viewer2025',
                role: 'viewer',
                company_id: 'company_001',
                profile: {
                    full_name: 'Visualizador IA South',
                    email: 'viewer@iasouth.tech',
                    avatar: '👁️'
                },
                status: 'active',
                last_login: null,
                created_at: new Date().toISOString()
            },
            {
                id: 'sonho_manager_001',
                username: 'sonho_manager',
                password: 'sonho2025',
                role: 'manager',
                company_id: 'company_002',
                profile: {
                    full_name: 'Gerente Sonho Digital',
                    email: 'manager@sonhodigital.com',
                    avatar: '👩‍💼'
                },
                status: 'active',
                last_login: null,
                created_at: new Date().toISOString()
            },
            {
                id: 'analytics_viewer_001',
                username: 'analytics_viewer',
                password: 'analytics2025',
                role: 'viewer',
                company_id: 'company_003',
                profile: {
                    full_name: 'Analista Analytics Pro',
                    email: 'analyst@analyticspro.com',
                    avatar: '📊'
                },
                status: 'active',
                last_login: null,
                created_at: new Date().toISOString()
            }
        ];
    }

    getDefaultDashboards() {
        return [
            {
                id: 'dashboard_001',
                file: 'dash_sonho.html',
                name: 'Dashboard Sonho',
                company_id: 'company_002',
                description: 'Dashboard principal da Sonho Digital',
                thumbnail: 'sonho_thumb.png',
                status: 'active',
                last_updated: new Date().toISOString(),
                created_at: new Date().toISOString()
            },
            {
                id: 'dashboard_002',
                file: 'dash_analytics.html',
                name: 'Analytics Dashboard',
                company_id: 'company_001',
                description: 'Dashboard de analytics da IA South Tech',
                thumbnail: 'analytics_thumb.png',
                status: 'active',
                last_updated: new Date().toISOString(),
                created_at: new Date().toISOString()
            },
            {
                id: 'dashboard_003',
                file: 'dash_financeiro.html',
                name: 'Dashboard Financeiro',
                company_id: 'company_001',
                description: 'Dashboard financeiro da IA South Tech',
                thumbnail: 'financeiro_thumb.png',
                status: 'active',
                last_updated: new Date().toISOString(),
                created_at: new Date().toISOString()
            },
            {
                id: 'dashboard_004',
                file: 'dash_operacional.html',
                name: 'Dashboard Operacional',
                company_id: 'company_001',
                description: 'Dashboard operacional da IA South Tech',
                thumbnail: 'operacional_thumb.png',
                status: 'active',
                last_updated: new Date().toISOString(),
                created_at: new Date().toISOString()
            },
            {
                id: 'dashboard_005',
                file: 'dash_comercial.html',
                name: 'Dashboard Comercial',
                company_id: 'company_002',
                description: 'Dashboard comercial da Sonho Digital',
                thumbnail: 'comercial_thumb.png',
                status: 'active',
                last_updated: new Date().toISOString(),
                created_at: new Date().toISOString()
            },
            {
                id: 'dashboard_006',
                file: 'dash_rh.html',
                name: 'Dashboard RH',
                company_id: 'company_001',
                description: 'Dashboard de recursos humanos da IA South Tech',
                thumbnail: 'rh_thumb.png',
                status: 'active',
                last_updated: new Date().toISOString(),
                created_at: new Date().toISOString()
            },
            {
                id: 'dashboard_007',
                file: 'dash_marketing.html',
                name: 'Dashboard Marketing',
                company_id: 'company_002',
                description: 'Dashboard de marketing da Sonho Digital',
                thumbnail: 'marketing_thumb.png',
                status: 'active',
                last_updated: new Date().toISOString(),
                created_at: new Date().toISOString()
            },
            {
                id: 'dashboard_008',
                file: 'dash_data_analytics.html',
                name: 'Data Analytics Pro',
                company_id: 'company_003',
                description: 'Dashboard avançado de analytics da Analytics Pro',
                thumbnail: 'data_analytics_thumb.png',
                status: 'active',
                last_updated: new Date().toISOString(),
                created_at: new Date().toISOString()
            }
        ];
    }

    getDefaultRoles() {
        return [
            {
                id: 'super_admin',
                name: 'Super Administrador',
                description: 'Acesso total ao sistema',
                permissions: ['*'],
                created_at: new Date().toISOString()
            },
            {
                id: 'manager',
                name: 'Gerente',
                description: 'Gerencia usuários e dashboards da empresa',
                permissions: [
                    'dashboard:view', 'dashboard:sync', 'dashboard:manage',
                    'users:view', 'users:manage',
                    'reports:view', 'reports:create'
                ],
                created_at: new Date().toISOString()
            },
            {
                id: 'viewer',
                name: 'Visualizador',
                description: 'Visualiza dashboards e relatórios',
                permissions: [
                    'dashboard:view',
                    'reports:view'
                ],
                created_at: new Date().toISOString()
            }
        ];
    }

    getDefaultPermissions() {
        return [
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
    }
}

// Create and export the hybrid auth system
const hybridAuthSystem = new HybridAuthSystem();

// Make it available globally for backward compatibility
if (typeof window !== 'undefined') {
    window.authSystem = hybridAuthSystem;
    window.hybridAuthSystem = hybridAuthSystem;
}
