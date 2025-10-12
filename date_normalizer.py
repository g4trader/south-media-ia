#!/usr/bin/env python3
"""
Sistema de Normalização de Datas para Google Sheets
Detecta automaticamente formatos brasileiro (DD/MM/YYYY) vs americano (MM/DD/YYYY)
e normaliza para um padrão consistente
"""

import re
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DateNormalizer:
    """Normalizador inteligente de formatos de data"""
    
    def __init__(self):
        self.date_patterns = {
            # Padrões brasileiros (DD/MM/YYYY)
            'brazilian': [
                r'^(\d{1,2})/(\d{1,2})/(\d{4})$',  # DD/MM/YYYY
                r'^(\d{1,2})-(\d{1,2})-(\d{4})$',  # DD-MM-YYYY
                r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', # DD.MM.YYYY
            ],
            # Padrões americanos (MM/DD/YYYY)
            'american': [
                r'^(\d{1,2})/(\d{1,2})/(\d{4})$',  # MM/DD/YYYY
                r'^(\d{1,2})-(\d{1,2})-(\d{4})$',  # MM-DD-YYYY
                r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', # MM.DD.YYYY
            ],
            # Padrões ISO
            'iso': [
                r'^(\d{4})-(\d{1,2})-(\d{1,2})$',  # YYYY-MM-DD
            ]
        }
        
        self.detected_format = None
        self.confidence_score = 0.0
        
    def analyze_date_column(self, dates: List[str]) -> Dict[str, Any]:
        """
        Analisa uma coluna de datas para detectar o formato predominante
        """
        logger.info(f"🔍 Analisando {len(dates)} datas para detectar formato...")
        
        if not dates:
            return {"format": "unknown", "confidence": 0.0, "sample_dates": []}
        
        # Filtrar apenas datas válidas
        valid_dates = [d for d in dates if d and str(d).strip()]
        if not valid_dates:
            return {"format": "unknown", "confidence": 0.0, "sample_dates": []}
        
        logger.info(f"📊 {len(valid_dates)} datas válidas encontradas")
        
        # Analisar cada formato
        format_scores = {
            'brazilian': 0,
            'american': 0,
            'iso': 0
        }
        
        parsed_samples = {
            'brazilian': [],
            'american': [],
            'iso': []
        }
        
        for date_str in valid_dates[:50]:  # Analisar primeiras 50 datas
            date_str = str(date_str).strip()
            
            # Tentar cada formato
            for format_name, patterns in self.date_patterns.items():
                for pattern in patterns:
                    match = re.match(pattern, date_str)
                    if match:
                        try:
                            groups = match.groups()
                            if format_name == 'brazilian':
                                day, month, year = groups
                                parsed_date = datetime(int(year), int(month), int(day))
                                format_scores[format_name] += 1
                                parsed_samples[format_name].append({
                                    'original': date_str,
                                    'parsed': parsed_date.strftime('%Y-%m-%d'),
                                    'day': int(day),
                                    'month': int(month),
                                    'year': int(year)
                                })
                            elif format_name == 'american':
                                month, day, year = groups
                                parsed_date = datetime(int(year), int(month), int(day))
                                format_scores[format_name] += 1
                                parsed_samples[format_name].append({
                                    'original': date_str,
                                    'parsed': parsed_date.strftime('%Y-%m-%d'),
                                    'day': int(day),
                                    'month': int(month),
                                    'year': int(year)
                                })
                            elif format_name == 'iso':
                                year, month, day = groups
                                parsed_date = datetime(int(year), int(month), int(day))
                                format_scores[format_name] += 1
                                parsed_samples[format_name].append({
                                    'original': date_str,
                                    'parsed': parsed_date.strftime('%Y-%m-%d'),
                                    'day': int(day),
                                    'month': int(month),
                                    'year': int(year)
                                })
                            break
                        except ValueError:
                            # Data inválida (ex: 31/02/2025)
                            continue
        
        # Determinar formato predominante
        total_parsed = sum(format_scores.values())
        if total_parsed == 0:
            logger.warning("⚠️ Nenhuma data pôde ser parseada")
            return {"format": "unknown", "confidence": 0.0, "sample_dates": []}
        
        best_format = max(format_scores, key=format_scores.get)
        confidence = format_scores[best_format] / total_parsed
        
        logger.info(f"📊 Formato detectado: {best_format.upper()} (confiança: {confidence:.1%})")
        logger.info(f"📋 Scores: Brasileiro={format_scores['brazilian']}, Americano={format_scores['american']}, ISO={format_scores['iso']}")
        
        # Log de algumas datas de exemplo
        if parsed_samples[best_format]:
            logger.info(f"📅 Exemplos de datas parseadas ({best_format}):")
            for sample in parsed_samples[best_format][:5]:
                logger.info(f"   {sample['original']} → {sample['parsed']}")
        
        self.detected_format = best_format
        self.confidence_score = confidence
        
        return {
            "format": best_format,
            "confidence": confidence,
            "scores": format_scores,
            "sample_dates": parsed_samples[best_format],
            "total_parsed": total_parsed
        }
    
    def normalize_date(self, date_str: str) -> Optional[str]:
        """
        Normaliza uma data individual para o formato ISO (YYYY-MM-DD)
        """
        if not date_str or not str(date_str).strip():
            return None
            
        date_str = str(date_str).strip()
        
        # Se já está no formato ISO, retornar
        if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_str):
            return date_str
        
        # Tentar detectar automaticamente com validação de data
        for format_name, patterns in self.date_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, date_str)
                if match:
                    try:
                        parsed_date = self._parse_with_format(date_str, format_name)
                        if parsed_date and self._is_valid_date(parsed_date):
                            return parsed_date
                    except:
                        continue
        
        logger.warning(f"⚠️ Não foi possível normalizar data: {date_str}")
        return None
    
    def _parse_with_format(self, date_str: str, format_name: str) -> Optional[str]:
        """Parse data com formato específico"""
        patterns = self.date_patterns[format_name]
        
        for pattern in patterns:
            match = re.match(pattern, date_str)
            if match:
                try:
                    groups = match.groups()
                    if format_name == 'brazilian':
                        day, month, year = groups
                        parsed_date = datetime(int(year), int(month), int(day))
                    elif format_name == 'american':
                        month, day, year = groups
                        parsed_date = datetime(int(year), int(month), int(day))
                    elif format_name == 'iso':
                        year, month, day = groups
                        parsed_date = datetime(int(year), int(month), int(day))
                    
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        return None
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Valida se uma data é válida e faz sentido no contexto"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Verificar se a data está em um range razoável (2020-2030)
            if date_obj.year < 2020 or date_obj.year > 2030:
                return False
            
            # Verificar se não é uma data muito no passado ou futuro
            current_year = datetime.now().year
            if abs(date_obj.year - current_year) > 2:
                return False
            
            return True
        except:
            return False
    
    def _smart_format_detection(self, dates: List[str]) -> str:
        """
        Detecção inteligente de formato baseada em contexto
        """
        if not dates:
            return 'brazilian'  # Default para brasileiro
        
        # Analisar padrões nas datas
        sample_dates = dates[:10]  # Analisar primeiras 10 datas
        
        brazilian_score = 0
        american_score = 0
        
        for date_str in sample_dates:
            if not date_str:
                continue
                
            # Tentar ambos os formatos
            for format_name in ['brazilian', 'american']:
                parsed = self._parse_with_format(str(date_str), format_name)
                if parsed and self._is_valid_date(parsed):
                    if format_name == 'brazilian':
                        brazilian_score += 1
                    else:
                        american_score += 1
        
        # Retornar o formato com maior score
        if brazilian_score > american_score:
            return 'brazilian'
        elif american_score > brazilian_score:
            return 'american'
        else:
            return 'brazilian'  # Default
    
    def normalize_dataframe_dates(self, df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """
        Normaliza coluna de datas em um DataFrame
        """
        if date_column not in df.columns:
            logger.error(f"❌ Coluna '{date_column}' não encontrada no DataFrame")
            return df
        
        logger.info(f"🔄 Normalizando datas na coluna '{date_column}'...")
        
        # Analisar formato da coluna
        date_analysis = self.analyze_date_column(df[date_column].astype(str).tolist())
        
        if date_analysis['format'] == 'unknown':
            logger.warning(f"⚠️ Formato de data não detectado, tentando detecção inteligente...")
            smart_format = self._smart_format_detection(df[date_column].astype(str).tolist())
            logger.info(f"🔍 Formato detectado inteligentemente: {smart_format}")
            self.detected_format = smart_format
        
        # Normalizar cada data
        normalized_dates = []
        failed_dates = []
        
        for idx, date_val in df[date_column].items():
            normalized = self.normalize_date(str(date_val))
            if normalized:
                normalized_dates.append(normalized)
            else:
                failed_dates.append(str(date_val))
                normalized_dates.append(None)
        
        # Atualizar DataFrame
        df[date_column] = normalized_dates
        
        # Remover linhas com datas inválidas
        original_count = len(df)
        df = df.dropna(subset=[date_column])
        final_count = len(df)
        
        if failed_dates:
            logger.warning(f"⚠️ {len(failed_dates)} datas não puderam ser normalizadas: {failed_dates[:5]}")
        
        logger.info(f"✅ Datas normalizadas: {original_count} → {final_count} (removidas {original_count - final_count})")
        
        return df
    
    def validate_date_range(self, dates: List[str], expected_start: str = None, expected_end: str = None) -> Dict[str, Any]:
        """
        Valida se o range de datas faz sentido
        """
        if not dates:
            return {"valid": False, "reason": "No dates provided"}
        
        # Normalizar todas as datas
        normalized_dates = [self.normalize_date(d) for d in dates if d]
        valid_dates = [d for d in normalized_dates if d]
        
        if not valid_dates:
            return {"valid": False, "reason": "No valid dates found"}
        
        # Converter para objetos datetime
        date_objects = [datetime.strptime(d, '%Y-%m-%d') for d in valid_dates]
        date_objects.sort()
        
        first_date = date_objects[0]
        last_date = date_objects[-1]
        
        # Verificar se o range faz sentido
        days_span = (last_date - first_date).days
        expected_days = len(valid_dates)
        
        validation_result = {
            "valid": True,
            "first_date": first_date.strftime('%Y-%m-%d'),
            "last_date": last_date.strftime('%Y-%m-%d'),
            "total_days": len(valid_dates),
            "span_days": days_span,
            "gaps": [],
            "warnings": []
        }
        
        # Verificar gaps nas datas
        for i in range(1, len(date_objects)):
            prev_date = date_objects[i-1]
            curr_date = date_objects[i]
            expected_next = prev_date.replace(day=prev_date.day + 1)
            
            if curr_date != expected_next:
                gap_days = (curr_date - prev_date).days - 1
                if gap_days > 0:
                    validation_result["gaps"].append({
                        "after": prev_date.strftime('%Y-%m-%d'),
                        "before": curr_date.strftime('%Y-%m-%d'),
                        "missing_days": gap_days
                    })
        
        # Verificar se há muitos gaps
        if len(validation_result["gaps"]) > 5:
            validation_result["warnings"].append("Many gaps found in date sequence")
        
        # Verificar se o range é muito pequeno para os dados esperados
        if expected_days > 20 and days_span < expected_days * 0.8:
            validation_result["warnings"].append("Date range seems too small for expected data")
        
        return validation_result

def test_date_normalizer():
    """Testar o normalizador de datas"""
    logger.info("🧪 Testando normalizador de datas...")
    
    normalizer = DateNormalizer()
    
    # Teste com datas brasileiras
    brazilian_dates = [
        "02/09/2025", "03/09/2025", "04/09/2025", "05/09/2025", "06/09/2025",
        "07/09/2025", "08/09/2025", "09/09/2025", "10/09/2025", "11/09/2025",
        "12/09/2025", "13/09/2025", "14/09/2025", "15/09/2025", "16/09/2025"
    ]
    
    logger.info("📊 Testando datas brasileiras...")
    result = normalizer.analyze_date_column(brazilian_dates)
    logger.info(f"Resultado: {result['format']} (confiança: {result['confidence']:.1%})")
    
    # Teste com datas americanas
    american_dates = [
        "09/02/2025", "09/03/2025", "09/04/2025", "09/05/2025", "09/06/2025",
        "09/07/2025", "09/08/2025", "09/09/2025", "09/10/2025", "09/11/2025",
        "09/12/2025", "09/13/2025", "09/14/2025", "09/15/2025", "09/16/2025"
    ]
    
    logger.info("📊 Testando datas americanas...")
    result = normalizer.analyze_date_column(american_dates)
    logger.info(f"Resultado: {result['format']} (confiança: {result['confidence']:.1%})")
    
    # Teste de normalização
    test_date = "02/09/2025"
    normalized = normalizer.normalize_date(test_date)
    logger.info(f"Normalização: {test_date} → {normalized}")

if __name__ == "__main__":
    test_date_normalizer()
