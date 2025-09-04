#!/usr/bin/env python3
"""
Script principal para execução de testes do sistema South Media IA
Inclui testes unitários, integração, E2E, performance e relatórios
"""

import os
import sys
import subprocess
import argparse
import time
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Executor principal de testes"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.coverage_dir = self.project_root / "htmlcov"
        
        # Criar diretórios de relatórios se não existirem
        self.reports_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)
    
    def run_command(self, command: list, description: str) -> bool:
        """Executar comando e retornar sucesso/falha"""
        print(f"\n{'='*60}")
        print(f"🚀 {description}")
        print(f"{'='*60}")
        print(f"Comando: {' '.join(command)}")
        print(f"Diretório: {self.project_root}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                check=True,
                capture_output=False,
                text=True
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n✅ {description} concluído com sucesso em {duration:.2f}s")
            return True
            
        except subprocess.CalledProcessError as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n❌ {description} falhou após {duration:.2f}s")
            print(f"Código de saída: {e.returncode}")
            return False
    
    def run_unit_tests(self) -> bool:
        """Executar testes unitários"""
        command = [
            "python", "-m", "pytest",
            "tests/test_models.py",
            "-v",
            "--tb=short",
            "--cov=src/models",
            "--cov-report=html:htmlcov/models",
            "--cov-report=term-missing"
        ]
        
        return self.run_command(command, "Testes Unitários - Modelos")
    
    def run_integration_tests(self) -> bool:
        """Executar testes de integração"""
        command = [
            "python", "-m", "pytest",
            "tests/test_integration_api.py",
            "-v",
            "--tb=short",
            "--cov=src/routes",
            "--cov-report=html:htmlcov/routes",
            "--cov-report=term-missing"
        ]
        
        return self.run_command(command, "Testes de Integração - API")
    
    def run_performance_tests(self) -> bool:
        """Executar testes de performance"""
        command = [
            "python", "-m", "pytest",
            "tests/test_performance.py",
            "-v",
            "--tb=short",
            "-m", "performance",
            "--durations=10"
        ]
        
        return self.run_command(command, "Testes de Performance")
    
    def run_selenium_tests(self) -> bool:
        """Executar testes E2E com Selenium"""
        command = [
            "python", "-m", "pytest",
            "tests/test_e2e_selenium.py",
            "-v",
            "--tb=short",
            "-m", "selenium",
            "--headless"
        ]
        
        return self.run_command(command, "Testes E2E - Selenium")
    
    def run_all_tests(self) -> bool:
        """Executar todos os testes"""
        command = [
            "python", "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--cov=src",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=80",
            "--durations=10",
            "--junitxml=test_reports/junit.xml"
        ]
        
        return self.run_command(command, "Todos os Testes")
    
    def run_coverage_report(self) -> bool:
        """Gerar relatório de cobertura detalhado"""
        command = [
            "python", "-m", "coverage",
            "report",
            "--show-missing",
            "--fail-under=80"
        ]
        
        return self.run_command(command, "Relatório de Cobertura")
    
    def run_linting(self) -> bool:
        """Executar verificação de código"""
        commands = [
            (["python", "-m", "black", "--check", "src/"], "Verificação Black (formatação)"),
            (["python", "-m", "flake8", "src/"], "Verificação Flake8 (estilo)"),
            (["python", "-m", "isort", "--check-only", "src/"], "Verificação isort (imports)"),
            (["python", "-m", "mypy", "src/"], "Verificação MyPy (tipos)"),
            (["python", "-m", "bandit", "-r", "src/"], "Verificação Bandit (segurança)")
        ]
        
        all_passed = True
        for command, description in commands:
            if not self.run_command(command, description):
                all_passed = False
        
        return all_passed
    
    def run_smoke_tests(self) -> bool:
        """Executar testes de fumaça (críticos)"""
        command = [
            "python", "-m", "pytest",
            "tests/",
            "-v",
            "-m", "smoke",
            "--tb=short"
        ]
        
        return self.run_command(command, "Testes de Fumaça")
    
    def run_regression_tests(self) -> bool:
        """Executar testes de regressão"""
        command = [
            "python", "-m", "pytest",
            "tests/",
            "-v",
            "-m", "regression",
            "--tb=short"
        ]
        
        return self.run_command(command, "Testes de Regressão")
    
    def generate_test_report(self, results: dict):
        """Gerar relatório resumido dos testes"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_content = f"""
# Relatório de Testes - South Media IA
**Data/Hora:** {timestamp}

## Resumo dos Resultados

### Testes Unitários
- Status: {'✅ PASSOU' if results['unit'] else '❌ FALHOU'}

### Testes de Integração
- Status: {'✅ PASSOU' if results['integration'] else '❌ FALHOU'}

### Testes de Performance
- Status: {'✅ PASSOU' if results['performance'] else '❌ FALHOU'}

### Testes E2E (Selenium)
- Status: {'✅ PASSOU' if results['selenium'] else '❌ FALHOU'}

### Verificação de Código
- Status: {'✅ PASSOU' if results['linting'] else '❌ FALHOU'}

### Cobertura de Código
- Status: {'✅ PASSOU' if results['coverage'] else '❌ FALHOU'}

## Estatísticas
- Total de Testes: {sum(results.values())}/{len(results)}
- Taxa de Sucesso: {(sum(results.values()) / len(results)) * 100:.1f}%

## Próximos Passos
{'🎉 Todos os testes passaram! O sistema está pronto para produção.' if all(results.values()) else '⚠️ Alguns testes falharam. Verifique os logs e corrija os problemas antes de prosseguir.'}

---
*Relatório gerado automaticamente pelo sistema de testes*
"""
        
        # Salvar relatório
        report_file = self.reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📊 Relatório salvo em: {report_file}")
        
        # Exibir relatório no console
        print(report_content)
    
    def run_test_suite(self, test_type: str = "all"):
        """Executar suite de testes específica"""
        results = {}
        
        if test_type == "all" or test_type == "unit":
            results['unit'] = self.run_unit_tests()
        
        if test_type == "all" or test_type == "integration":
            results['integration'] = self.run_integration_tests()
        
        if test_type == "all" or test_type == "performance":
            results['performance'] = self.run_performance_tests()
        
        if test_type == "all" or test_type == "selenium":
            results['selenium'] = self.run_selenium_tests()
        
        if test_type == "all" or test_type == "linting":
            results['linting'] = self.run_linting()
        
        if test_type == "all" or test_type == "coverage":
            results['coverage'] = self.run_coverage_report()
        
        if test_type == "all":
            # Executar todos os testes juntos para cobertura completa
            results['all'] = self.run_all_tests()
        
        # Gerar relatório
        if results:
            self.generate_test_report(results)
        
        return results


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Executor de testes para South Media IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_tests.py                    # Executar todos os testes
  python run_tests.py --type unit        # Apenas testes unitários
  python run_tests.py --type integration # Apenas testes de integração
  python run_tests.py --type performance # Apenas testes de performance
  python run_tests.py --type selenium    # Apenas testes E2E
  python run_tests.py --type linting     # Apenas verificação de código
  python run_tests.py --type smoke       # Testes de fumaça
  python run_tests.py --type regression  # Testes de regressão
        """
    )
    
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "performance", "selenium", "linting", "coverage", "smoke", "regression"],
        default="all",
        help="Tipo de teste a executar"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Executar testes em paralelo (quando suportado)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verboso"
    )
    
    args = parser.parse_args()
    
    # Configurar runner
    runner = TestRunner()
    
    # Executar testes
    print(f"🧪 Iniciando execução de testes: {args.type.upper()}")
    print(f"📁 Diretório do projeto: {runner.project_root}")
    print(f"📁 Diretório de testes: {runner.test_dir}")
    print(f"📊 Diretório de relatórios: {runner.reports_dir}")
    
    try:
        results = runner.run_test_suite(args.type)
        
        # Verificar se todos os testes passaram
        if results and all(results.values()):
            print("\n🎉 SUCCESS: Todos os testes passaram!")
            sys.exit(0)
        else:
            print("\n❌ FAILURE: Alguns testes falharam!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Erro durante execução dos testes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

