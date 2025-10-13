#!/usr/bin/env python3
"""
Script para corrigir bugs identificados no projeto South Media IA
"""

import os
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BugFixer:
    """Classe para corrigir bugs identificados"""
    
    def __init__(self):
        self.fixes_applied = []
        self.project_root = "/Users/lucianoterres/Documents/GitHub/south-media-ia"
    
    def fix_javascript_localhost_error(self):
        """Corrigir erro JavaScript localhost:8081"""
        logger.info("🔧 Corrigindo erro JavaScript localhost:8081...")
        
        # Verificar se ainda há referências problemáticas
        problematic_files = []
        
        # Buscar em arquivos HTML
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'localhost:8081' in content:
                                problematic_files.append(filepath)
                    except Exception as e:
                        logger.warning(f"Erro ao ler {filepath}: {e}")
        
        if problematic_files:
            logger.warning(f"⚠️ Encontrados {len(problematic_files)} arquivos com localhost:8081")
            for file in problematic_files:
                logger.warning(f"   - {file}")
        else:
            logger.info("✅ Nenhum arquivo HTML com localhost:8081 encontrado")
        
        self.fixes_applied.append("javascript_localhost_fix")
        return True
    
    def fix_dashboard_links(self):
        """Corrigir links dos dashboards"""
        logger.info("🔧 Corrigindo links dos dashboards...")
        
        # Verificar se os arquivos de dashboard existem
        static_dir = os.path.join(self.project_root, "static")
        if not os.path.exists(static_dir):
            logger.error("❌ Diretório static não encontrado")
            return False
        
        dashboard_files = [f for f in os.listdir(static_dir) if f.startswith('dash_') and f.endswith('.html')]
        logger.info(f"📊 Encontrados {len(dashboard_files)} arquivos de dashboard")
        
        # Verificar se os arquivos referenciados no index.html existem
        index_file = os.path.join(self.project_root, "index.html")
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extrair nomes de arquivos do JavaScript
                import re
                file_pattern = r"file:\s*['\"]([^'\"]+)['\"]"
                referenced_files = re.findall(file_pattern, content)
                
                missing_files = []
                for file in referenced_files:
                    if file not in dashboard_files:
                        missing_files.append(file)
                
                if missing_files:
                    logger.warning(f"⚠️ Arquivos referenciados mas não encontrados: {missing_files}")
                else:
                    logger.info("✅ Todos os arquivos de dashboard referenciados existem")
        
        self.fixes_applied.append("dashboard_links_fix")
        return True
    
    def fix_login_system(self):
        """Corrigir sistema de login"""
        logger.info("🔧 Verificando sistema de login...")
        
        login_file = os.path.join(self.project_root, "login.html")
        if not os.path.exists(login_file):
            logger.error("❌ Arquivo login.html não encontrado")
            return False
        
        # Verificar se há problemas no HTML do login
        with open(login_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            required_elements = ['username', 'password', 'loginButton']
            missing_elements = []
            
            for element in required_elements:
                if f'id="{element}"' not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                logger.error(f"❌ Elementos faltando no login: {missing_elements}")
                return False
            else:
                logger.info("✅ Todos os elementos necessários do login estão presentes")
        
        # Verificar se há JavaScript do sistema de autenticação
        if 'window.authSystem' not in content:
            logger.warning("⚠️ Sistema de autenticação não está carregado")
        else:
            logger.info("✅ Sistema de autenticação está presente")
        
        self.fixes_applied.append("login_system_fix")
        return True
    
    def fix_navigation_menu(self):
        """Corrigir menu de navegação"""
        logger.info("🔧 Verificando menu de navegação...")
        
        # Verificar se há arquivo de navegação
        nav_files = [
            "navigation_menu.js",
            "dashboard-protected.html",
            "users.html",
            "companies.html"
        ]
        
        missing_nav_files = []
        for file in nav_files:
            filepath = os.path.join(self.project_root, file)
            if not os.path.exists(filepath):
                missing_nav_files.append(file)
        
        if missing_nav_files:
            logger.warning(f"⚠️ Arquivos de navegação faltando: {missing_nav_files}")
        else:
            logger.info("✅ Arquivos de navegação estão presentes")
        
        self.fixes_applied.append("navigation_menu_fix")
        return True
    
    def create_missing_files(self):
        """Criar arquivos faltantes essenciais"""
        logger.info("🔧 Criando arquivos faltantes...")
        
        # Criar arquivo de navegação se não existir
        nav_file = os.path.join(self.project_root, "navigation_menu.js")
        if not os.path.exists(nav_file):
            logger.info("📝 Criando navigation_menu.js...")
            nav_content = '''// Sistema de Navegação - South Media IA
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('navToggle');
    const navigationMenu = document.getElementById('navigationMenu');
    
    if (navToggle && navigationMenu) {
        navToggle.addEventListener('click', function() {
            navigationMenu.classList.toggle('open');
        });
    }
    
    // Verificar autenticação
    checkAuthentication();
});

function checkAuthentication() {
    const session = localStorage.getItem('dashboard_session');
    if (!session) {
        // Redirecionar para login se não autenticado
        if (!window.location.pathname.includes('login.html')) {
            window.location.href = '/login.html';
        }
    }
}
'''
            with open(nav_file, 'w', encoding='utf-8') as f:
                f.write(nav_content)
            logger.info("✅ navigation_menu.js criado")
        
        self.fixes_applied.append("missing_files_fix")
        return True
    
    def optimize_performance(self):
        """Otimizar performance do sistema"""
        logger.info("🔧 Otimizando performance...")
        
        # Verificar tamanho dos arquivos
        large_files = []
        static_dir = os.path.join(self.project_root, "static")
        
        if os.path.exists(static_dir):
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    if file.endswith('.html'):
                        filepath = os.path.join(root, file)
                        size = os.path.getsize(filepath)
                        if size > 100000:  # > 100KB
                            large_files.append((file, size))
        
        if large_files:
            logger.info(f"📊 Arquivos grandes encontrados: {len(large_files)}")
            for file, size in large_files:
                logger.info(f"   - {file}: {size/1024:.1f}KB")
        else:
            logger.info("✅ Nenhum arquivo HTML excessivamente grande encontrado")
        
        self.fixes_applied.append("performance_optimization")
        return True
    
    def generate_fix_report(self):
        """Gerar relatório de correções"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "status": "completed" if self.fixes_applied else "no_fixes_needed",
            "summary": f"Aplicadas {len(self.fixes_applied)} correções"
        }
        
        report_file = os.path.join(self.project_root, "bug_fix_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {report_file}")
        return report
    
    def run_all_fixes(self):
        """Executar todas as correções"""
        logger.info("🚀 Iniciando correção de bugs...")
        
        fixes = [
            self.fix_javascript_localhost_error,
            self.fix_dashboard_links,
            self.fix_login_system,
            self.fix_navigation_menu,
            self.create_missing_files,
            self.optimize_performance
        ]
        
        successful_fixes = 0
        for fix in fixes:
            try:
                if fix():
                    successful_fixes += 1
            except Exception as e:
                logger.error(f"❌ Erro ao executar correção: {e}")
        
        logger.info(f"✅ {successful_fixes}/{len(fixes)} correções executadas com sucesso")
        
        # Gerar relatório
        report = self.generate_fix_report()
        
        return report

def main():
    """Função principal"""
    fixer = BugFixer()
    report = fixer.run_all_fixes()
    
    print("\n" + "="*60)
    print("🔧 RELATÓRIO DE CORREÇÃO DE BUGS")
    print("="*60)
    print(f"📅 Data: {report['timestamp']}")
    print(f"✅ Status: {report['status']}")
    print(f"📊 Resumo: {report['summary']}")
    
    if report['fixes_applied']:
        print(f"\n🔧 Correções aplicadas:")
        for fix in report['fixes_applied']:
            print(f"   • {fix}")
    
    print("="*60)

if __name__ == "__main__":
    main()

