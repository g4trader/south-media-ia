/**
 * Sistema de Navegação Moderno
 * Menu lateral responsivo para o sistema multi-tenant
 */

class NavigationMenu {
    constructor() {
        this.isOpen = false;
        this.currentPage = this.getCurrentPage();
        this.init();
    }

    init() {
        this.createMenuHTML();
        this.bindEvents();
        this.updateActiveMenuItem();
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('dashboard-protected.html')) return 'dashboard';
        if (path.includes('dashboard-builder.html')) return 'dashboard-builder';
        if (path.includes('users.html')) return 'users';
        if (path.includes('companies.html')) return 'companies';
        if (path.includes('system-status.html')) return 'system-status';
        if (path.includes('login.html')) return 'login';
        return 'dashboard';
    }

    createMenuHTML() {
        const menuHTML = `
            <!-- Menu Lateral -->
            <div id="navigationMenu" class="nav-menu">
                <div class="nav-header">
                    <div class="nav-logo">
                        <span class="logo-icon">📊</span>
                        <span class="logo-text">Dashboard Pro</span>
                    </div>
                    <button class="nav-close" id="navClose">
                        <span>✕</span>
                    </button>
                </div>
                
                <div class="nav-content">
                    <div class="nav-section">
                        <h3 class="nav-section-title">Principal</h3>
                        <ul class="nav-list">
                            <li class="nav-item">
                                <a href="/dashboard-protected.html" class="nav-link" data-page="dashboard">
                                    <span class="nav-icon">🏠</span>
                                    <span class="nav-text">Dashboard</span>
                                </a>
                            </li>
                        </ul>
                    </div>
                    
                    <div class="nav-section">
                        <h3 class="nav-section-title">Gerenciamento</h3>
                        <ul class="nav-list">
                            <li class="nav-item">
                                <a href="/dashboard-builder.html" class="nav-link" data-page="dashboard-builder">
                                    <span class="nav-icon">🎯</span>
                                    <span class="nav-text">Dashboard Builder</span>
                                </a>
                            </li>
                            <li class="nav-item">
                                <a href="/users.html" class="nav-link" data-page="users">
                                    <span class="nav-icon">👥</span>
                                    <span class="nav-text">Usuários</span>
                                </a>
                            </li>
                            <li class="nav-item">
                                <a href="/companies.html" class="nav-link" data-page="companies">
                                    <span class="nav-icon">🏢</span>
                                    <span class="nav-text">Empresas</span>
                                </a>
                            </li>
                        </ul>
                    </div>
                    
                    <div class="nav-section">
                        <h3 class="nav-section-title">Sistema</h3>
                        <ul class="nav-list">
                            <li class="nav-item">
                                <a href="/system-status.html" class="nav-link" data-page="system-status">
                                    <span class="nav-icon">⚙️</span>
                                    <span class="nav-text">Status do Sistema</span>
                                </a>
                            </li>
                            <li class="nav-item">
                                <a href="#" class="nav-link" id="logoutLink">
                                    <span class="nav-icon">🚪</span>
                                    <span class="nav-text">Sair</span>
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
                
                <div class="nav-footer">
                    <div class="nav-user-info">
                        <div class="nav-user-avatar" id="navUserAvatar">👤</div>
                        <div class="nav-user-details">
                            <div class="nav-user-name" id="navUserName">Usuário</div>
                            <div class="nav-user-role" id="navUserRole">Admin</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Overlay -->
            <div id="navOverlay" class="nav-overlay"></div>
            
            <!-- Botão do Menu -->
            <button id="navToggle" class="nav-toggle">
                <span class="hamburger">
                    <span></span>
                    <span></span>
                    <span></span>
                </span>
            </button>
        `;

        // Adicionar ao body
        document.body.insertAdjacentHTML('beforeend', menuHTML);
        
        // Adicionar CSS
        this.addMenuCSS();
    }

    addMenuCSS() {
        const css = `
            <style>
            /* Menu Lateral */
            .nav-menu {
                position: fixed;
                top: 0;
                left: -300px;
                width: 300px;
                height: 100vh;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: white;
                z-index: 1000;
                transition: left 0.3s ease;
                box-shadow: 2px 0 10px rgba(0,0,0,0.3);
                display: flex;
                flex-direction: column;
            }
            
            .nav-menu.open {
                left: 0;
            }
            
            .nav-header {
                padding: 20px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .nav-logo {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .logo-icon {
                font-size: 24px;
            }
            
            .logo-text {
                font-size: 18px;
                font-weight: bold;
            }
            
            .nav-close {
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                padding: 5px;
                border-radius: 50%;
                transition: background 0.3s ease;
            }
            
            .nav-close:hover {
                background: rgba(255,255,255,0.1);
            }
            
            .nav-content {
                flex: 1;
                padding: 20px 0;
                overflow-y: auto;
            }
            
            .nav-section {
                margin-bottom: 30px;
            }
            
            .nav-section-title {
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: rgba(255,255,255,0.6);
                margin: 0 20px 10px;
                font-weight: 600;
            }
            
            .nav-list {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .nav-item {
                margin: 0;
            }
            
            .nav-link {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 20px;
                color: white;
                text-decoration: none;
                transition: all 0.3s ease;
                border-left: 3px solid transparent;
            }
            
            .nav-link:hover {
                background: rgba(255,255,255,0.1);
                border-left-color: #4CAF50;
            }
            
            .nav-link.active {
                background: rgba(76, 175, 80, 0.2);
                border-left-color: #4CAF50;
            }
            
            .nav-icon {
                font-size: 18px;
                width: 20px;
                text-align: center;
            }
            
            .nav-text {
                font-size: 14px;
                font-weight: 500;
            }
            
            .nav-footer {
                padding: 20px;
                border-top: 1px solid rgba(255,255,255,0.1);
            }
            
            .nav-user-info {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .nav-user-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #4CAF50;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
            }
            
            .nav-user-details {
                flex: 1;
            }
            
            .nav-user-name {
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 2px;
            }
            
            .nav-user-role {
                font-size: 12px;
                color: rgba(255,255,255,0.7);
            }
            
            /* Overlay */
            .nav-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 999;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }
            
            .nav-overlay.show {
                opacity: 1;
                visibility: visible;
            }
            
            /* Botão do Menu */
            .nav-toggle {
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 1001;
                background: #4CAF50;
                border: none;
                border-radius: 8px;
                padding: 12px;
                cursor: pointer;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
            }
            
            .nav-toggle:hover {
                background: #45a049;
                transform: scale(1.05);
            }
            
            .hamburger {
                display: flex;
                flex-direction: column;
                gap: 3px;
            }
            
            .hamburger span {
                width: 20px;
                height: 2px;
                background: white;
                transition: all 0.3s ease;
            }
            
            .nav-toggle.open .hamburger span:nth-child(1) {
                transform: rotate(45deg) translate(5px, 5px);
            }
            
            .nav-toggle.open .hamburger span:nth-child(2) {
                opacity: 0;
            }
            
            .nav-toggle.open .hamburger span:nth-child(3) {
                transform: rotate(-45deg) translate(7px, -6px);
            }
            
            /* Responsivo */
            @media (max-width: 768px) {
                .nav-menu {
                    width: 280px;
                    left: -280px;
                }
                
                .nav-toggle {
                    top: 15px;
                    left: 15px;
                    padding: 10px;
                }
            }
            
            /* Animações */
            @keyframes slideIn {
                from {
                    transform: translateX(-100%);
                }
                to {
                    transform: translateX(0);
                }
            }
            
            .nav-menu.open {
                animation: slideIn 0.3s ease;
            }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', css);
    }

    bindEvents() {
        // Toggle menu
        document.getElementById('navToggle').addEventListener('click', () => {
            this.toggleMenu();
        });

        // Close menu
        document.getElementById('navClose').addEventListener('click', () => {
            this.closeMenu();
        });

        // Close on overlay click
        document.getElementById('navOverlay').addEventListener('click', () => {
            this.closeMenu();
        });

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeMenu();
            }
        });

        // Logout
        document.getElementById('logoutLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.handleLogout();
        });


        // Update user info
        this.updateUserInfo();
    }

    toggleMenu() {
        this.isOpen = !this.isOpen;
        const menu = document.getElementById('navigationMenu');
        const overlay = document.getElementById('navOverlay');
        const toggle = document.getElementById('navToggle');

        if (this.isOpen) {
            menu.classList.add('open');
            overlay.classList.add('show');
            toggle.classList.add('open');
        } else {
            menu.classList.remove('open');
            overlay.classList.remove('show');
            toggle.classList.remove('open');
        }
    }

    closeMenu() {
        this.isOpen = false;
        const menu = document.getElementById('navigationMenu');
        const overlay = document.getElementById('navOverlay');
        const toggle = document.getElementById('navToggle');

        menu.classList.remove('open');
        overlay.classList.remove('show');
        toggle.classList.remove('open');
    }

    updateActiveMenuItem() {
        const links = document.querySelectorAll('.nav-link');
        links.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === this.currentPage) {
                link.classList.add('active');
            }
        });
    }

    async updateUserInfo() {
        try {
            if (window.authSystem) {
                const user = await window.authSystem.getCurrentUser();
                const company = await window.authSystem.getCurrentUserCompany();
                
                if (user) {
                    document.getElementById('navUserName').textContent = 
                        user.profile?.full_name || user.username;
                    document.getElementById('navUserRole').textContent = 
                        user.role === 'super_admin' ? 'Super Admin' : 
                        user.role === 'manager' ? 'Gerente' : 'Visualizador';
                    document.getElementById('navUserAvatar').textContent = 
                        (user.profile?.full_name || user.username).charAt(0).toUpperCase();
                }
            }
        } catch (error) {
            console.error('Erro ao atualizar informações do usuário no menu:', error);
        }
    }

    handleLogout() {
        if (confirm('Tem certeza que deseja sair?')) {
            if (window.authSystem) {
                window.authSystem.logout();
            }
            window.location.href = '/login.html';
        }
    }

}

// Inicializar menu quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    // Só inicializar se não estiver na página de login
    if (!window.location.pathname.includes('login.html')) {
        window.navigationMenu = new NavigationMenu();
    }
});
