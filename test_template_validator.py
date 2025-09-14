#!/usr/bin/env python3
"""
Teste do Template Validator
Verifica se o sistema de validação está funcionando corretamente
"""

import os
import sys
from template_validator import TemplateValidator

def test_template_validation():
    """Testa a validação do template atual"""
    print("🔍 Testando validação do template...")
    
    validator = TemplateValidator()
    
    # Verificar se arquivo existe
    if not os.path.exists(validator.template_file):
        print(f"❌ Arquivo não encontrado: {validator.template_file}")
        return False
    
    # Ler arquivo
    with open(validator.template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Arquivo lido: {len(content)} caracteres")
    
    # Validar template
    is_valid, errors = validator.validate_template(content)
    
    if is_valid:
        print("✅ Template válido!")
        
        # Criar backup
        backup_path = validator.create_backup(content)
        if backup_path:
            print(f"💾 Backup criado: {backup_path}")
        
        # Comparar com backup
        comparison = validator.compare_with_backup(content)
        print(f"📊 Comparação com backup: {comparison}")
        
        return True
    else:
        print("❌ Template inválido:")
        for error in errors:
            print(f"  {error}")
        return False

def test_invalid_template():
    """Testa com template inválido"""
    print("\n🧪 Testando com template inválido...")
    
    invalid_content = """
    <html>
    <head><title>Test</title></head>
    <body>
    <script>
    // Template inválido - falta variáveis obrigatórias
    const TEST = "invalid";
    </script>
    </body>
    </html>
    """
    
    validator = TemplateValidator()
    is_valid, errors = validator.validate_template(invalid_content)
    
    if not is_valid:
        print("✅ Validação corretamente identificou template inválido:")
        for error in errors:
            print(f"  {error}")
        return True
    else:
        print("❌ Validação falhou - template inválido foi aceito")
        return False

def test_safe_commit():
    """Testa commit seguro (sem fazer commit real)"""
    print("\n🔒 Testando commit seguro...")
    
    validator = TemplateValidator()
    
    if not os.path.exists(validator.template_file):
        print(f"❌ Arquivo não encontrado: {validator.template_file}")
        return False
    
    with open(validator.template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Testar validação (sem fazer commit real)
    is_valid, errors = validator.validate_template(content)
    
    if is_valid:
        print("✅ Template passaria na validação para commit seguro")
        
        # Simular commit (sem fazer commit real)
        print("📝 Simulando commit seguro...")
        print("  - Validação: ✅")
        print("  - Backup: ✅")
        print("  - Commit: ✅ (simulado)")
        
        return True
    else:
        print("❌ Template falharia na validação:")
        for error in errors:
            print(f"  {error}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do Template Validator\n")
    
    tests = [
        ("Validação do template atual", test_template_validation),
        ("Teste com template inválido", test_invalid_template),
        ("Teste de commit seguro", test_safe_commit)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅' if result else '❌'} {test_name}: {'PASSOU' if result else 'FALHOU'}\n")
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {e}\n")
            results.append((test_name, False))
    
    # Resumo dos testes
    print("📊 RESUMO DOS TESTES:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"📈 Resultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 Todos os testes passaram! Sistema de validação está funcionando.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os problemas.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
