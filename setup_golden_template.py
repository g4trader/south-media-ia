#!/usr/bin/env python3
"""
Setup Golden Template - Define o template de referência
Cria um backup especial que serve como template "golden" (referência)
"""

import os
import shutil
from datetime import datetime
from template_validator import TemplateValidator

def setup_golden_template():
    """Define o template atual como golden template"""
    print("🏆 Configurando Golden Template...")
    
    validator = TemplateValidator()
    
    # Verificar se arquivo existe
    if not os.path.exists(validator.template_file):
        print(f"❌ Arquivo não encontrado: {validator.template_file}")
        return False
    
    # Ler arquivo atual
    with open(validator.template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Validar template atual
    is_valid, errors = validator.validate_template(content)
    
    if not is_valid:
        print("❌ Template atual é inválido, não pode ser usado como golden template:")
        for error in errors:
            print(f"  {error}")
        return False
    
    print("✅ Template atual é válido")
    
    # Criar diretório golden se não existir
    golden_dir = "golden_templates"
    os.makedirs(golden_dir, exist_ok=True)
    
    # Criar golden template
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    golden_filename = f"dash_sonho_golden_{timestamp}.html"
    golden_path = os.path.join(golden_dir, golden_filename)
    
    # Copiar template atual como golden
    shutil.copy2(validator.template_file, golden_path)
    
    # Criar link simbólico para o golden atual
    golden_current = os.path.join(golden_dir, "dash_sonho_golden_current.html")
    if os.path.exists(golden_current):
        os.remove(golden_current)
    os.symlink(golden_filename, golden_current)
    
    print(f"🏆 Golden template criado: {golden_path}")
    print(f"🔗 Link atual: {golden_current}")
    
    # Criar arquivo de metadados
    metadata = {
        "created_at": datetime.now().isoformat(),
        "source_file": validator.template_file,
        "golden_file": golden_filename,
        "validation_status": "valid",
        "description": "Template de referência validado e funcionando"
    }
    
    import json
    metadata_path = os.path.join(golden_dir, "golden_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Metadados salvos: {metadata_path}")
    
    return True

def validate_against_golden():
    """Valida template atual contra golden template"""
    print("🔍 Validando contra Golden Template...")
    
    validator = TemplateValidator()
    golden_dir = "golden_templates"
    golden_current = os.path.join(golden_dir, "dash_sonho_golden_current.html")
    
    if not os.path.exists(golden_current):
        print("❌ Golden template não encontrado. Execute setup_golden_template() primeiro.")
        return False
    
    # Ler template atual
    with open(validator.template_file, 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    # Ler golden template
    with open(golden_current, 'r', encoding='utf-8') as f:
        golden_content = f.read()
    
    # Validar template atual
    is_valid, errors = validator.validate_template(current_content)
    
    if not is_valid:
        print("❌ Template atual é inválido:")
        for error in errors:
            print(f"  {error}")
        return False
    
    # Comparar com golden
    if current_content == golden_content:
        print("✅ Template atual é idêntico ao golden template")
        return True
    else:
        print("⚠️ Template atual difere do golden template")
        
        # Mostrar diferenças básicas
        current_lines = current_content.split('\n')
        golden_lines = golden_content.split('\n')
        
        if len(current_lines) != len(golden_lines):
            print(f"  - Número de linhas: atual={len(current_lines)}, golden={len(golden_lines)}")
        
        # Verificar se as diferenças são apenas em dados (não em estrutura)
        current_structure = [line for line in current_lines if not line.strip().startswith('//') and '=' in line]
        golden_structure = [line for line in golden_lines if not line.strip().startswith('//') and '=' in line]
        
        if len(current_structure) == len(golden_structure):
            print("✅ Estrutura do template mantida (apenas dados atualizados)")
            return True
        else:
            print("❌ Estrutura do template foi alterada")
            return False

def restore_from_golden():
    """Restaura template a partir do golden template"""
    print("🔄 Restaurando do Golden Template...")
    
    validator = TemplateValidator()
    golden_dir = "golden_templates"
    golden_current = os.path.join(golden_dir, "dash_sonho_golden_current.html")
    
    if not os.path.exists(golden_current):
        print("❌ Golden template não encontrado")
        return False
    
    # Fazer backup do template atual
    if os.path.exists(validator.template_file):
        backup_path = validator.create_backup(open(validator.template_file, 'r', encoding='utf-8').read())
        if backup_path:
            print(f"💾 Backup do template atual criado: {backup_path}")
    
    # Restaurar do golden
    shutil.copy2(golden_current, validator.template_file)
    
    print("✅ Template restaurado do golden template")
    
    # Validar template restaurado
    is_valid, errors = validator.validate_template(open(validator.template_file, 'r', encoding='utf-8').read())
    
    if is_valid:
        print("✅ Template restaurado é válido")
        return True
    else:
        print("❌ Template restaurado é inválido:")
        for error in errors:
            print(f"  {error}")
        return False

def main():
    """Função principal"""
    print("🏆 Golden Template Manager")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Uso: python setup_golden_template.py [setup|validate|restore]")
        print("  setup    - Define template atual como golden")
        print("  validate - Valida template atual contra golden")
        print("  restore  - Restaura template do golden")
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        success = setup_golden_template()
    elif command == "validate":
        success = validate_against_golden()
    elif command == "restore":
        success = restore_from_golden()
    else:
        print(f"❌ Comando inválido: {command}")
        success = False
    
    if success:
        print("🎉 Operação concluída com sucesso!")
    else:
        print("❌ Operação falhou!")

if __name__ == "__main__":
    import sys
    main()
