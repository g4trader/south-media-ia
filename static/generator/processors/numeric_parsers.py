#!/usr/bin/env python3
"""
Parsers numéricos seguros para converter strings em números
"""

def safe_float(value, default=0.0):
    """
    Converte um valor para float de forma segura
    
    Args:
        value: Valor a ser convertido
        default: Valor padrão se a conversão falhar
        
    Returns:
        float: Valor convertido ou default
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove espaços e caracteres especiais
            value = value.strip().replace(',', '.').replace(' ', '')
            # Remove caracteres não numéricos (exceto ponto e sinal negativo)
            value = ''.join(c for c in value if c.isdigit() or c in '.-')
            if value:
                return float(value)
        
        return default
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """
    Converte um valor para int de forma segura
    
    Args:
        value: Valor a ser convertido
        default: Valor padrão se a conversão falhar
        
    Returns:
        int: Valor convertido ou default
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, int):
            return value
        
        if isinstance(value, float):
            return int(value)
        
        if isinstance(value, str):
            # Remove espaços e caracteres não numéricos
            value = value.strip().replace(',', '.').replace(' ', '')
            # Remove tudo exceto dígitos e sinal negativo
            value = ''.join(c for c in value if c.isdigit() or c == '-')
            if value:
                # Converte para float primeiro e depois para int (para lidar com decimais)
                return int(float(value))
        
        return default
    except (ValueError, TypeError):
        return default

