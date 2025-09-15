/**
 * Middleware de Autenticação
 * Sistema de proteção de rotas e controle de acesso
 */

class AuthMiddleware {
    constructor() {
        this.protectedRoutes = [
            '/dashboard-protected.html',
            '/admin.html',
            '/users.html'
        ];
        
        this.publicRoutes = [
            '/login.html',
            '/index.html',
            '/static/'
        ];
    }

    /**
     * Verificar se rota está protegida
     */
    isProtectedRoute(path) {
        return this.protectedRoutes.some(route => path.includes(route));
    }

    /**
     * Verificar se rota é pública
     */
    isPublicRoute(path) {
        return this.publicRoutes.some(route => path.includes(route));
    }

    /**
     * Middleware principal de autenticação
     */
    checkAuthentication() {
        const currentPath = window.location.pathname;
        
        // Se é rota pública, permitir acesso
        if (this.isPublicRoute(currentPath)) {
            return true;
        }

        // Se é rota protegida, verificar autenticação
        if (this.isProtectedRoute(currentPath)) {
            if (!window.authSystem.isAuthenticated()) {
                this.redirectToLogin();
                return false;
            }
            
            // Verificar permissões específicas por rota
            if (!this.checkRoutePermissions(currentPath)) {
                this.redirectToUnauthorized();
                return false;
            }
        }

        return true;
    }

    /**
     * Verificar permissões específicas da rota
     */
    checkRoutePermissions(path) {
        const routePermissions = {
            '/admin.html': ['users:manage', 'system:config'],
            '/users.html': ['users:view'],
            '/dashboard-protected.html': ['dashboard:view']
        };

        const requiredPermissions = routePermissions[path];
        if (!requiredPermissions) return true;

        return requiredPermissions.some(permission => 
            window.authSystem.hasPermission(permission)
        );
    }

    /**
     * Redirecionar para login
     */
    redirectToLogin() {
        const currentPath = encodeURIComponent(window.location.pathname);
        window.location.href = `/login.html?redirect=${currentPath}`;
    }

    /**
     * Redirecionar para página de não autorizado
     */
    redirectToUnauthorized() {
        window.location.href = '/unauthorized.html';
    }

    /**
     * Aplicar middleware em todas as páginas
     */
    applyMiddleware() {
        // Verificar autenticação ao carregar a página
        if (!this.checkAuthentication()) {
            return false;
        }

        // Configurar proteção para navegação
        this.setupNavigationProtection();
        
        // Configurar logout automático
        this.setupAutoLogout();
        
        return true;
    }

    /**
     * Configurar proteção de navegação
     */
    setupNavigationProtection() {
        // Interceptar cliques em links
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (!link) return;

            const href = link.getAttribute('href');
            if (!href) return;

            // Se é rota protegida, verificar permissões
            if (this.isProtectedRoute(href)) {
                if (!window.authSystem.isAuthenticated()) {
                    e.preventDefault();
                    this.redirectToLogin();
                    return;
                }

                if (!this.checkRoutePermissions(href)) {
                    e.preventDefault();
                    this.redirectToUnauthorized();
                    return;
                }
            }
        });

        // Interceptar mudanças de hash (SPA navigation)
        window.addEventListener('hashchange', () => {
            const newPath = window.location.pathname + window.location.hash;
            if (this.isProtectedRoute(newPath)) {
                if (!window.authSystem.isAuthenticated()) {
                    this.redirectToLogin();
                    return;
                }

                if (!this.checkRoutePermissions(newPath)) {
                    this.redirectToUnauthorized();
                    return;
                }
            }
        });
    }

    /**
     * Configurar logout automático
     */
    setupAutoLogout() {
        // Verificar sessão a cada 5 minutos
        setInterval(() => {
            if (!window.authSystem.isAuthenticated()) {
                this.redirectToLogin();
            }
        }, 5 * 60 * 1000);

        // Logout automático em caso de inatividade (30 minutos)
        let inactivityTimer;
        const resetInactivityTimer = () => {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(() => {
                if (window.authSystem.isAuthenticated()) {
                    window.authSystem.logout();
                    alert('Sessão expirada por inatividade');
                    this.redirectToLogin();
                }
            }, 30 * 60 * 1000);
        };

        // Resetar timer em atividade do usuário
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, resetInactivityTimer, true);
        });

        resetInactivityTimer();
    }

    /**
     * Decorator para funções que requerem autenticação
     */
    requireAuth(fn) {
        return (...args) => {
            if (!window.authSystem.isAuthenticated()) {
                this.redirectToLogin();
                return;
            }
            return fn(...args);
        };
    }

    /**
     * Decorator para funções que requerem permissão específica
     */
    requirePermission(permission) {
        return (fn) => {
            return (...args) => {
                if (!window.authSystem.hasPermission(permission)) {
                    this.redirectToUnauthorized();
                    return;
                }
                return fn(...args);
            };
        };
    }

    /**
     * Decorator para funções que requerem role específica
     */
    requireRole(role) {
        return (fn) => {
            return (...args) => {
                if (!window.authSystem.hasRole(role)) {
                    this.redirectToUnauthorized();
                    return;
                }
                return fn(...args);
            };
        };
    }
}

// Instância global do middleware
window.authMiddleware = new AuthMiddleware();

// Aplicar middleware automaticamente
document.addEventListener('DOMContentLoaded', () => {
    window.authMiddleware.applyMiddleware();
});

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthMiddleware;
}
