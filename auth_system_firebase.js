// Firebase Authentication System
import { databaseService } from './firebase_config.js';

class FirebaseAuthSystem {
    constructor() {
        this.sessionKey = 'dashboard_firebase_session';
        this.isInitialized = false;
        this.init();
    }

    async init() {
        try {
            console.log('🔄 Inicializando sistema Firebase...');
            
            // Migrate from localStorage if needed
            await databaseService.migrateFromLocalStorage();
            
            // Initialize default data if needed
            await this.initializeDefaultData();
            
            this.isInitialized = true;
            console.log('✅ Sistema Firebase inicializado com sucesso!');
            
        } catch (error) {
            console.error('❌ Erro ao inicializar sistema Firebase:', error);
            // Fallback to localStorage if Firebase fails
            this.fallbackToLocalStorage();
        }
    }

    async fallbackToLocalStorage() {
        console.log('⚠️ Fallback para localStorage ativado');
        // Import the old system as fallback
        if (typeof window !== 'undefined' && window.authSystem) {
            this.localAuthSystem = window.authSystem;
        }
    }

    async initializeDefaultData() {
        try {
            // Check if we have any companies
            const companies = await databaseService.getAllCompanies();
            if (companies.length === 0) {
                console.log('🔄 Criando dados padrão...');
                await this.createDefaultCompanies();
                await this.createDefaultUsers();
                await this.createDefaultDashboards();
                await this.createDefaultRoles();
                await this.createDefaultPermissions();
            }
        } catch (error) {
            console.error('❌ Erro ao criar dados padrão:', error);
        }
    }

    async createDefaultCompanies() {
        const companies = [
            {
                id: 'company_001',
                name: 'IA South Tech',
                code: 'IASOUTH',
                description: 'Empresa de tecnologia e inteligência artificial',
                settings: {
                    theme: 'dark',
                    timezone: 'America/Sao_Paulo',
                    language: 'pt-BR'
                },
                contact: {
                    email: 'contato@iasouth.tech',
                    phone: '+55 11 99999-9999',
                    address: 'São Paulo, SP, Brasil'
                },
                status: 'active',
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'company_002',
                name: 'Sonho Digital',
                code: 'SONHO',
                description: 'Agência digital especializada em marketing',
                settings: {
                    theme: 'light',
                    timezone: 'America/Sao_Paulo',
                    language: 'pt-BR'
                },
                contact: {
                    email: 'contato@sonhodigital.com',
                    phone: '+55 11 88888-8888',
                    address: 'São Paulo, SP, Brasil'
                },
                status: 'active',
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'company_003',
                name: 'Analytics Pro',
                code: 'ANALYTICS',
                description: 'Especialistas em análise de dados e BI',
                settings: {
                    theme: 'dark',
                    timezone: 'America/Sao_Paulo',
                    language: 'pt-BR'
                },
                contact: {
                    email: 'contato@analyticspro.com',
                    phone: '+55 11 77777-7777',
                    address: 'Rio de Janeiro, RJ, Brasil'
                },
                status: 'active',
                created_at: new Date(),
                updated_at: new Date()
            }
        ];

        for (const company of companies) {
            await databaseService.createCompany(company);
        }
        console.log(`✅ ${companies.length} empresas padrão criadas`);
    }

    async createDefaultUsers() {
        const users = [
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
                created_at: new Date(),
                updated_at: new Date()
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
                created_at: new Date(),
                updated_at: new Date()
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
                created_at: new Date(),
                updated_at: new Date()
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
                created_at: new Date(),
                updated_at: new Date()
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
                created_at: new Date(),
                updated_at: new Date()
            }
        ];

        for (const user of users) {
            await databaseService.createUser(user);
        }
        console.log(`✅ ${users.length} usuários padrão criados`);
    }

    async createDefaultDashboards() {
        const dashboards = [
            {
                id: 'dashboard_001',
                file: 'dash_sonho.html',
                name: 'Dashboard Sonho',
                company_id: 'company_002',
                description: 'Dashboard principal da Sonho Digital',
                thumbnail: 'sonho_thumb.png',
                status: 'active',
                last_updated: new Date(),
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'dashboard_002',
                file: 'dash_analytics.html',
                name: 'Analytics Dashboard',
                company_id: 'company_001',
                description: 'Dashboard de analytics da IA South Tech',
                thumbnail: 'analytics_thumb.png',
                status: 'active',
                last_updated: new Date(),
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'dashboard_003',
                file: 'dash_financeiro.html',
                name: 'Dashboard Financeiro',
                company_id: 'company_001',
                description: 'Dashboard financeiro da IA South Tech',
                thumbnail: 'financeiro_thumb.png',
                status: 'active',
                last_updated: new Date(),
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'dashboard_004',
                file: 'dash_operacional.html',
                name: 'Dashboard Operacional',
                company_id: 'company_001',
                description: 'Dashboard operacional da IA South Tech',
                thumbnail: 'operacional_thumb.png',
                status: 'active',
                last_updated: new Date(),
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'dashboard_005',
                file: 'dash_comercial.html',
                name: 'Dashboard Comercial',
                company_id: 'company_002',
                description: 'Dashboard comercial da Sonho Digital',
                thumbnail: 'comercial_thumb.png',
                status: 'active',
                last_updated: new Date(),
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'dashboard_006',
                file: 'dash_rh.html',
                name: 'Dashboard RH',
                company_id: 'company_001',
                description: 'Dashboard de recursos humanos da IA South Tech',
                thumbnail: 'rh_thumb.png',
                status: 'active',
                last_updated: new Date(),
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'dashboard_007',
                file: 'dash_marketing.html',
                name: 'Dashboard Marketing',
                company_id: 'company_002',
                description: 'Dashboard de marketing da Sonho Digital',
                thumbnail: 'marketing_thumb.png',
                status: 'active',
                last_updated: new Date(),
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'dashboard_008',
                file: 'dash_data_analytics.html',
                name: 'Data Analytics Pro',
                company_id: 'company_003',
                description: 'Dashboard avançado de analytics da Analytics Pro',
                thumbnail: 'data_analytics_thumb.png',
                status: 'active',
                last_updated: new Date(),
                created_at: new Date(),
                updated_at: new Date()
            }
        ];

        for (const dashboard of dashboards) {
            await databaseService.createDashboard(dashboard);
        }
        console.log(`✅ ${dashboards.length} dashboards padrão criados`);
    }

    async createDefaultRoles() {
        const roles = [
            {
                id: 'super_admin',
                name: 'Super Administrador',
                description: 'Acesso total ao sistema',
                permissions: ['*'],
                created_at: new Date(),
                updated_at: new Date()
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
                created_at: new Date(),
                updated_at: new Date()
            },
            {
                id: 'viewer',
                name: 'Visualizador',
                description: 'Visualiza dashboards e relatórios',
                permissions: [
                    'dashboard:view',
                    'reports:view'
                ],
                created_at: new Date(),
                updated_at: new Date()
            }
        ];

        for (const role of roles) {
            await databaseService.create('roles', role);
        }
        console.log(`✅ ${roles.length} roles padrão criados`);
    }

    async createDefaultPermissions() {
        const permissions = [
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

        for (const permission of permissions) {
            await databaseService.create('permissions', permission);
        }
        console.log(`✅ ${permissions.length} permissões padrão criadas`);
    }

    // Authentication methods
    async authenticate(username, password) {
        try {
            if (!this.isInitialized) {
                await this.init();
            }

            const user = await databaseService.getUserByUsername(username);
            
            if (!user) {
                return { success: false, message: 'Usuário não encontrado' };
            }

            if (user.password !== password) {
                return { success: false, message: 'Senha incorreta' };
            }

            if (user.status !== 'active') {
                return { success: false, message: 'Usuário inativo' };
            }

            // Update last login
            await databaseService.updateUser(user.id, { last_login: new Date() });

            // Create session
            const sessionId = this.generateSessionId();
            const sessionData = {
                user_id: user.id,
                username: user.username,
                role: user.role,
                company_id: user.company_id,
                login_time: new Date(),
                expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours
            };

            await databaseService.createSession(sessionData);
            
            // Store session in localStorage for immediate access
            localStorage.setItem(this.sessionKey, JSON.stringify({
                sessionId,
                ...sessionData
            }));

            // Log activity
            await databaseService.logActivity('user_login', user.id, {
                username: user.username,
                ip: await this.getClientIP()
            });

            return {
                success: true,
                user: user,
                session: sessionData
            };

        } catch (error) {
            console.error('❌ Erro na autenticação:', error);
            return { success: false, message: 'Erro interno do servidor' };
        }
    }

    async logout() {
        try {
            const sessionData = this.getCurrentSession();
            if (sessionData) {
                // Delete session from database
                await databaseService.deleteSession(sessionData.sessionId);
                
                // Log activity
                await databaseService.logActivity('user_logout', sessionData.user_id, {
                    username: sessionData.username
                });
            }

            // Clear localStorage
            localStorage.removeItem(this.sessionKey);
            return true;

        } catch (error) {
            console.error('❌ Erro no logout:', error);
            return false;
        }
    }

    isAuthenticated() {
        try {
            const sessionData = this.getCurrentSession();
            if (!sessionData) return false;

            // Check if session is expired
            if (new Date() > new Date(sessionData.expires_at)) {
                this.logout();
                return false;
            }

            return true;
        } catch (error) {
            console.error('❌ Erro ao verificar autenticação:', error);
            return false;
        }
    }

    getCurrentSession() {
        try {
            const sessionData = localStorage.getItem(this.sessionKey);
            return sessionData ? JSON.parse(sessionData) : null;
        } catch (error) {
            console.error('❌ Erro ao obter sessão:', error);
            return null;
        }
    }

    async getCurrentUser() {
        try {
            const session = this.getCurrentSession();
            if (!session) return null;

            const user = await databaseService.getUser(session.user_id);
            return user;
        } catch (error) {
            console.error('❌ Erro ao obter usuário atual:', error);
            return null;
        }
    }

    async getCurrentUserCompany() {
        try {
            const user = await this.getCurrentUser();
            if (!user || !user.company_id) return null;

            const company = await databaseService.getCompany(user.company_id);
            return company;
        } catch (error) {
            console.error('❌ Erro ao obter empresa do usuário:', error);
            return null;
        }
    }

    // Company management
    async getAllCompanies() {
        try {
            return await databaseService.getAllCompanies();
        } catch (error) {
            console.error('❌ Erro ao obter empresas:', error);
            return [];
        }
    }

    async createCompany(companyData) {
        try {
            const companyId = await databaseService.createCompany(companyData);
            
            // Log activity
            const session = this.getCurrentSession();
            if (session) {
                await databaseService.logActivity('company_created', session.user_id, {
                    company_id: companyId,
                    company_name: companyData.name
                });
            }

            return companyId;
        } catch (error) {
            console.error('❌ Erro ao criar empresa:', error);
            throw error;
        }
    }

    // Dashboard management
    async getDashboardsForUser() {
        try {
            const user = await this.getCurrentUser();
            if (!user) return [];

            if (user.role === 'super_admin') {
                // Super admin sees all dashboards
                return await databaseService.getAllDashboards();
            } else if (user.company_id) {
                // Regular users see only their company's dashboards
                return await databaseService.getDashboardsByCompany(user.company_id);
            }

            return [];
        } catch (error) {
            console.error('❌ Erro ao obter dashboards do usuário:', error);
            return [];
        }
    }

    async createDashboard(dashboardData) {
        try {
            const dashboardId = await databaseService.createDashboard(dashboardData);
            
            // Log activity
            const session = this.getCurrentSession();
            if (session) {
                await databaseService.logActivity('dashboard_created', session.user_id, {
                    dashboard_id: dashboardId,
                    dashboard_name: dashboardData.name
                });
            }

            return dashboardId;
        } catch (error) {
            console.error('❌ Erro ao criar dashboard:', error);
            throw error;
        }
    }

    // User management
    async getAllUsers() {
        try {
            return await databaseService.query('users', [], 'username');
        } catch (error) {
            console.error('❌ Erro ao obter usuários:', error);
            return [];
        }
    }

    async createUser(userData) {
        try {
            const userId = await databaseService.createUser(userData);
            
            // Log activity
            const session = this.getCurrentSession();
            if (session) {
                await databaseService.logActivity('user_created', session.user_id, {
                    user_id: userId,
                    username: userData.username
                });
            }

            return userId;
        } catch (error) {
            console.error('❌ Erro ao criar usuário:', error);
            throw error;
        }
    }

    // Utility methods
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async getClientIP() {
        try {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            return data.ip;
        } catch (error) {
            return 'unknown';
        }
    }

    // Permission checking
    hasPermission(permission) {
        try {
            const session = this.getCurrentSession();
            if (!session) return false;

            if (session.role === 'super_admin') return true;

            // Get role permissions from database
            // For now, return true for basic permissions
            const basicPermissions = ['dashboard:view', 'dashboard:sync'];
            return basicPermissions.includes(permission);
        } catch (error) {
            console.error('❌ Erro ao verificar permissão:', error);
            return false;
        }
    }

    // System status
    async getSystemStatus() {
        try {
            const companies = await databaseService.getAllCompanies();
            const users = await databaseService.getAllUsers();
            const dashboards = await databaseService.getAllDashboards();

            return {
                companies: companies.length,
                users: users.length,
                dashboards: dashboards.length,
                isInitialized: this.isInitialized,
                database: 'firebase'
            };
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
}

// Export the Firebase auth system
export const firebaseAuthSystem = new FirebaseAuthSystem();

// Make it available globally for backward compatibility
if (typeof window !== 'undefined') {
    window.firebaseAuthSystem = firebaseAuthSystem;
}
