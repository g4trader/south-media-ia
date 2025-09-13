#!/usr/bin/env python3
"""
Script de teste para validar a separação de footfall
"""

import logging
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Testa se todos os imports estão funcionando"""
    try:
        logger.info("🧪 Testando imports...")
        
        # Testar import do processador de footfall
        from footfall_processor import FootfallProcessor
        logger.info("✅ FootfallProcessor importado com sucesso")
        
        # Testar import da configuração de footfall
        from footfall_config import FOOTFALL_SHEETS_CONFIG, FOOTFALL_VALIDATION
        logger.info("✅ Configurações de footfall importadas com sucesso")
        
        # Testar import do app Cloud Run de footfall
        from footfall_cloud_app import app
        logger.info("✅ App Cloud Run de footfall importado com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nos imports: {e}")
        return False

def test_footfall_processor():
    """Testa o processador de footfall"""
    try:
        logger.info("🧪 Testando FootfallProcessor...")
        
        from footfall_processor import FootfallProcessor
        
        # Criar instância
        processor = FootfallProcessor()
        logger.info("✅ Instância do FootfallProcessor criada")
        
        # Testar coleta de dados (dados estáticos)
        footfall_data = processor.get_footfall_data()
        if footfall_data and len(footfall_data) > 0:
            logger.info(f"✅ Dados de footfall coletados: {len(footfall_data)} pontos")
        else:
            logger.error("❌ Falha ao coletar dados de footfall")
            return False
        
        # Testar validação
        if processor.validate_footfall_data(footfall_data):
            logger.info("✅ Validação de dados de footfall passou")
        else:
            logger.error("❌ Validação de dados de footfall falhou")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste do FootfallProcessor: {e}")
        return False

def test_data_structure():
    """Testa a estrutura dos dados de footfall"""
    try:
        logger.info("🧪 Testando estrutura dos dados...")
        
        from footfall_processor import FootfallProcessor
        
        processor = FootfallProcessor()
        footfall_data = processor.get_footfall_data()
        
        if not footfall_data:
            logger.error("❌ Nenhum dado de footfall encontrado")
            return False
        
        # Verificar estrutura do primeiro item
        first_item = footfall_data[0]
        required_fields = ['lat', 'lon', 'name', 'users', 'rate']
        
        for field in required_fields:
            if field not in first_item:
                logger.error(f"❌ Campo obrigatório '{field}' não encontrado")
                return False
        
        logger.info(f"✅ Estrutura dos dados validada - exemplo: {first_item}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de estrutura: {e}")
        return False

def test_configuration():
    """Testa as configurações"""
    try:
        logger.info("🧪 Testando configurações...")
        
        from footfall_config import FOOTFALL_SHEETS_CONFIG, FOOTFALL_VALIDATION, FOOTFALL_UPDATE_CONFIG
        
        # Verificar configurações básicas
        if not FOOTFALL_SHEETS_CONFIG:
            logger.error("❌ Configuração de sheets não encontrada")
            return False
        
        if not FOOTFALL_VALIDATION:
            logger.error("❌ Configuração de validação não encontrada")
            return False
        
        if not FOOTFALL_UPDATE_CONFIG:
            logger.error("❌ Configuração de atualização não encontrada")
            return False
        
        logger.info("✅ Todas as configurações estão presentes")
        logger.info(f"  - Intervalo de atualização: {FOOTFALL_UPDATE_CONFIG.get('update_interval_hours', 'N/A')} horas")
        logger.info(f"  - Campos obrigatórios: {FOOTFALL_VALIDATION.get('required_fields', [])}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de configurações: {e}")
        return False

def main():
    """Função principal de teste"""
    logger.info("🚀 Iniciando testes de separação de footfall...")
    
    tests = [
        ("Imports", test_imports),
        ("Configurações", test_configuration),
        ("Processador", test_footfall_processor),
        ("Estrutura de Dados", test_data_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Executando teste: {test_name}")
        try:
            if test_func():
                logger.info(f"✅ Teste '{test_name}' PASSOU")
                passed += 1
            else:
                logger.error(f"❌ Teste '{test_name}' FALHOU")
        except Exception as e:
            logger.error(f"❌ Teste '{test_name}' ERRO: {e}")
    
    logger.info(f"\n📊 Resultado dos testes:")
    logger.info(f"  - Total: {total}")
    logger.info(f"  - Passou: {passed}")
    logger.info(f"  - Falhou: {total - passed}")
    
    if passed == total:
        logger.info("🎉 Todos os testes passaram! Separação de footfall está funcionando.")
        return True
    else:
        logger.error("❌ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
