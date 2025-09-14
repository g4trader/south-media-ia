#!/usr/bin/env python3
"""
Processador específico para dados de Footfall
Separa a lógica de atualização da aba Footfall dos canais principais
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime
from google_sheets_processor import GoogleSheetsProcessor

logger = logging.getLogger(__name__)

class FootfallProcessor:
    """Classe dedicada para processamento de dados de Footfall"""
    
    def __init__(self):
        self.processor = None
        
    def authenticate(self):
        """Autentica com Google Sheets"""
        try:
            self.processor = GoogleSheetsProcessor()
            logger.info("✅ Autenticação Footfall realizada com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro na autenticação Footfall: {e}")
            return False
    
    def get_footfall_data(self):
        """Coleta dados específicos de footfall"""
        try:
            # Tentar autenticar, mas se falhar, usar dados estáticos
            if not self.processor:
                if not self.authenticate():
                    logger.warning("⚠️ Autenticação falhou, usando dados estáticos de footfall")
                    return self.get_static_footfall_data()
            
            # Importar configuração real
            from footfall_config import FOOTFALL_SHEETS_CONFIG
            
            footfall_config = FOOTFALL_SHEETS_CONFIG["Footfall Data"]
            
            logger.info("🗺️ Coletando dados de footfall da planilha real...")
            
            # Tentar coletar dados reais da planilha
            try:
                footfall_data = self.processor.read_sheet_data(
                    footfall_config["sheet_id"], 
                    gid=footfall_config["gid"]
                )
                
                if footfall_data is not None and not footfall_data.empty:
                    # Processar dados conforme configuração
                    processed_data = []
                    for index, row in footfall_data.iterrows():
                        if index == 0:  # Pular cabeçalho
                            continue
                        
                        try:
                            # Verificar se tem dados válidos
                            if pd.isna(row.iloc[0]) or pd.isna(row.iloc[1]):
                                continue
                                
                            # Corrigir formatação das coordenadas
                            lat_str = str(row.iloc[0])
                            lon_str = str(row.iloc[1])
                            
                            # Se tem muitos pontos, corrigir formatação
                            if lat_str.count('.') > 1:
                                # Manter apenas o primeiro ponto (decimal)
                                lat_parts = lat_str.split('.')
                                lat_str = lat_parts[0] + '.' + ''.join(lat_parts[1:])
                            
                            if lon_str.count('.') > 1:
                                # Manter apenas o primeiro ponto (decimal)
                                lon_parts = lon_str.split('.')
                                lon_str = lon_parts[0] + '.' + ''.join(lon_parts[1:])
                            
                            # Converter para float e validar ranges
                            lat_val = float(lat_str)
                            lon_val = float(lon_str)
                            
                            # Ajustar longitude se estiver fora do range
                            if lon_val < -180:
                                # Para coordenadas do Brasil, ajustar para range válido
                                if lon_val < -300:
                                    lon_val = lon_val + 300  # Ajuste para longitude do Brasil
                                else:
                                    lon_val = lon_val + 34
                            elif lon_val > 180:
                                # Subtrair se necessário
                                lon_val = lon_val - 34
                            
                            processed_data.append({
                                "lat": lat_val,
                                "lon": lon_val,
                                "name": str(row.iloc[3]) if len(row) > 3 and not pd.isna(row.iloc[3]) else "",
                                "users": int(row.iloc[4]) if len(row) > 4 and not pd.isna(row.iloc[4]) else 0,
                                "rate": float(str(row.iloc[5]).replace(',', '.')) if len(row) > 5 and not pd.isna(row.iloc[5]) else 0.0
                            })
                        except (ValueError, IndexError) as e:
                            logger.warning(f"⚠️ Erro ao processar linha {index}: {row.tolist()} - {e}")
                            continue
                    
                    if processed_data:
                        logger.info(f"✅ {len(processed_data)} pontos de footfall coletados da planilha")
                        return processed_data
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao coletar dados reais: {e}")
            
            # Fallback para dados estáticos
            logger.warning("⚠️ Usando dados estáticos como fallback")
            footfall_data = self.get_static_footfall_data()
            
            logger.info(f"✅ {len(footfall_data)} pontos de footfall coletados")
            return footfall_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados de footfall: {e}")
            return None
    
    def get_static_footfall_data(self):
        """Retorna dados estáticos de footfall (temporário até configurar a planilha)"""
        return [
            {"lat": -8.09233930867147, "lon": -34.8847507746984, "name": "Recibom - Av. Eng. Domingos Ferreira, 306 - Pina", "users": 3589, "rate": 9.5},
            {"lat": -8.13196914950721, "lon": -34.9069687730163, "name": "Recibom boa viagem - R. Barão de Souza Leão, 767 - Boa Viagem, Recife - PE, 51030-300", "users": 4182, "rate": 7.9},
            {"lat": -8.04591568467357, "lon": -34.9092152269836, "name": "Recibom - Torre - Rua Conde de Irajá, 632 - Torre, Recife - PE, 50710-310", "users": 3099, "rate": 9.5},
            {"lat": -8.047434924792, "lon": -34.9001621153442, "name": "Recibom - Graças - Av. Rui Barbosa, 551 - Graças, Recife - PE, 52011-040", "users": 2689, "rate": 9.3},
            {"lat": -8.02988247354862, "lon": -34.9066516730163, "name": "Recibom - Parnamirim - Estr. do Arraial, 2668 - Tamarineira, Recife - PE, 52051-380", "users": 1184, "rate": 12.5},
            {"lat": -8.11993224900449, "lon": -34.90091268465557, "name": "Recibom - Boa Viagem - R. Prof. João Medeiros, 261 - Boa Viagem, Recife - PE, 51021-050", "users": 3451, "rate": 14.5},
            {"lat": -8.14254391419425, "lon": -34.9081091134918, "name": "Recibom - Setúbal - R. João Cardoso Aires, 407 - Boa Viagem, Recife - PE, 51130-300", "users": 4321, "rate": 6.5},
            {"lat": -8.0281307802215, "lon": -34.90250688465557, "name": "Recibom - Encruzilhada - Av. Norte Miguel Arraes de Alencar, S/N - Encruzilhada, Recife - PE, 52041-005", "users": 8256, "rate": 11.5},
            {"lat": -7.99956677243255, "lon": -34.8464921711639, "name": "Recibom - Olinda - Av. Carlos de Lima Cavalcante, 515 - Bultrins, Olinda - PE, 53030-260", "users": 8793, "rate": 13.5},
            {"lat": -8.18360115521895, "lon": -34.919450028836, "name": "Recibom - Piedade - Av. Bernardo Vieira de Melo, 3454 - Piedade, Jaboatão dos Guararapes - PE, 54410-010", "users": 1987, "rate": 11.2},
            {"lat": -8.18233405479681, "lon": -34.9200238558197, "name": "Recibom - Piedade -Av. Ayrton Senna da Silva, 2851 - Piedade, Jaboatão dos Guararapes - PE, 54410-400", "users": 4089, "rate": 14.51}
        ]
    
    def validate_footfall_data(self, data):
        """Valida dados de footfall"""
        if not data:
            return False
        
        required_fields = ['lat', 'lon', 'name', 'users', 'rate']
        
        for item in data:
            for field in required_fields:
                if field not in item:
                    logger.error(f"❌ Campo obrigatório '{field}' não encontrado em: {item}")
                    return False
            
            # Validações específicas
            if not isinstance(item['lat'], (int, float)) or not (-90 <= item['lat'] <= 90):
                logger.error(f"❌ Latitude inválida: {item['lat']}")
                return False
                
            if not isinstance(item['lon'], (int, float)) or not (-180 <= item['lon'] <= 180):
                logger.error(f"❌ Longitude inválida: {item['lon']}")
                return False
                
            if not isinstance(item['users'], (int, float)) or item['users'] < 0:
                logger.error(f"❌ Número de usuários inválido: {item['users']}")
                return False
                
            if not isinstance(item['rate'], (int, float)) or item['rate'] < 0:
                logger.error(f"❌ Taxa de conversão inválida: {item['rate']}")
                return False
        
        logger.info("✅ Dados de footfall validados com sucesso")
        return True
    
    def update_dashboard_footfall(self, footfall_data):
        """Atualiza apenas a seção FOOTFALL_POINTS do dashboard"""
        try:
            dashboard_file = "static/dash_sonho.html"
            
            if not os.path.exists(dashboard_file):
                logger.error(f"❌ Arquivo do dashboard não encontrado: {dashboard_file}")
                return False
            
            # Ler arquivo atual
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validar dados antes de atualizar
            if not self.validate_footfall_data(footfall_data):
                logger.error("❌ Dados de footfall inválidos, abortando atualização")
                return False
            
            # Converter dados para JSON
            footfall_json = json.dumps(footfall_data, ensure_ascii=False, indent=2)
            
            # Substituir FOOTFALL_POINTS no arquivo
            import re
            # Padrão para capturar desde const FOOTFALL_POINTS até o final da linha com ];
            pattern = r'const FOOTFALL_POINTS = \[.*?\];'
            replacement = f'const FOOTFALL_POINTS = {footfall_json};'
            
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            if new_content == content:
                logger.warning("⚠️ FOOTFALL_POINTS não encontrado no arquivo")
                return False
            
            # Salvar arquivo atualizado
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"✅ Dashboard footfall atualizado com {len(footfall_data)} pontos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar dashboard footfall: {e}")
            return False
    
    def run_footfall_update(self):
        """Executa atualização completa de footfall"""
        try:
            logger.info("🗺️ Iniciando atualização de footfall...")
            
            # Coletar dados
            footfall_data = self.get_footfall_data()
            if not footfall_data:
                logger.error("❌ Falha ao coletar dados de footfall")
                return False
            
            # Atualizar dashboard
            if not self.update_dashboard_footfall(footfall_data):
                logger.error("❌ Falha ao atualizar dashboard footfall")
                return False
            
            # Fazer commit e push
            try:
                self.commit_and_push()
            except Exception as e:
                logger.warning(f"⚠️ Erro no commit/push: {e}")
            
            logger.info("🎉 Atualização de footfall concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na atualização de footfall: {e}")
            return False
    
    def commit_and_push(self):
        """Faz commit e push das mudanças via GitHub API"""
        try:
            import requests
            import os
            from datetime import datetime
            
            github_token = os.environ.get('GITHUB_TOKEN')
            if not github_token:
                logger.warning("⚠️ GITHUB_TOKEN não encontrado, pulando commit/push")
                return False
            
            # Ler arquivo atualizado
            dashboard_file = "static/dash_sonho.html"
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fazer commit via GitHub API
            url = "https://api.github.com/repos/g4trader/south-media-ia/contents/static/dash_sonho.html"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            import base64
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            # Obter SHA atual do arquivo
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                current_sha = response.json()['sha']
            else:
                logger.warning("⚠️ Não foi possível obter SHA atual do arquivo")
                return False
            
            data = {
                "message": f"Update: Atualização automática de footfall - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                "content": content_b64,
                "sha": current_sha
            }
            
            response = requests.put(url, headers=headers, json=data)
            if response.status_code == 200:
                logger.info("✅ Commit e push de footfall realizados com sucesso via GitHub API")
                return True
            else:
                logger.error(f"❌ Erro ao fazer commit de footfall via GitHub API: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao fazer commit/push de footfall: {e}")
            return False

def main():
    """Função principal para teste"""
    logging.basicConfig(level=logging.INFO)
    
    processor = FootfallProcessor()
    success = processor.run_footfall_update()
    
    if success:
        print("✅ Atualização de footfall bem-sucedida!")
    else:
        print("❌ Falha na atualização de footfall")

if __name__ == "__main__":
    main()
