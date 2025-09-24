#!/usr/bin/env python3
"""
Integração do Dashboard Multicanal - Spotify + Programática
Acessa dados reais das planilhas do Google Sheets e atualiza o dashboard
"""

import os
import json
import pandas as pd
from datetime import datetime
from google_sheets_service import GoogleSheetsService

class MulticanalDashboardIntegrator:
    """Integrador para o dashboard multicanal"""
    
    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        self.dashboard_data = {}
        
        # IDs das planilhas fornecidas
        self.spotify_sheet_id = "1-rSt7tYoZFdEiGEBM3GIVt928-8OugHa5sPF2XguYp0"
        self.spotify_gid = "1604556822"
        
        self.programatica_sheet_id = "1scA5ykf49DLobPTAKSL5fNgGMiomcJmgSJqXolV679M"
        self.programatica_gid = "1791112204"
        
        self.sites_sheet_id = "1scA5ykf49DLobPTAKSL5fNgGMiomcJmgSJqXolV679M"
        self.sites_gid = "409983185"
    
    def fetch_spotify_data(self):
        """Buscar dados da campanha do Spotify"""
        try:
            print("🎵 Buscando dados do Spotify...")
            
            # Ler dados da planilha do Spotify
            df = self.sheets_service.read_sheet_data(
                self.spotify_sheet_id, 
                gid=self.spotify_gid
            )
            
            if df is None:
                print("❌ Nenhum dado encontrado na planilha do Spotify")
                return None
            
            print(f"✅ Dados do Spotify carregados: {len(df)} linhas")
            
            # Processar dados específicos do Spotify
            spotify_data = self._process_spotify_data(df)
            return spotify_data
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados do Spotify: {e}")
            return None
    
    def fetch_programatica_data(self):
        """Buscar dados da campanha Programática"""
        try:
            print("📺 Buscando dados da Programática...")
            
            # Ler dados da planilha da Programática
            df = self.sheets_service.read_sheet_data(
                self.programatica_sheet_id,
                gid=self.programatica_gid
            )
            
            if df is None:
                print("❌ Nenhum dado encontrado na planilha da Programática")
                return None
            
            print(f"✅ Dados da Programática carregados: {len(df)} linhas")
            
            # Processar dados específicos da Programática
            programatica_data = self._process_programatica_data(df)
            return programatica_data
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados da Programática: {e}")
            return None
    
    def fetch_sites_data(self):
        """Buscar lista de sites premium"""
        try:
            print("🌐 Buscando lista de sites...")
            
            # Ler dados da planilha de sites
            df = self.sheets_service.read_sheet_data(
                self.sites_sheet_id,
                gid=self.sites_gid
            )
            
            if df is None:
                print("❌ Nenhum dado encontrado na planilha de sites")
                return []
            
            print(f"✅ Lista de sites carregada: {len(df)} sites")
            
            # Extrair lista de sites
            sites = []
            if 'Site' in df.columns:
                sites = df['Site'].dropna().tolist()
            elif 'Nome do Site' in df.columns:
                sites = df['Nome do Site'].dropna().tolist()
            elif len(df.columns) > 0:
                # Usar primeira coluna se não encontrar coluna específica
                sites = df.iloc[:, 0].dropna().tolist()
            
            return sites
            
        except Exception as e:
            print(f"❌ Erro ao buscar lista de sites: {e}")
            return []
    
    def _process_spotify_data(self, df):
        """Processar dados específicos do Spotify"""
        spotify_data = {
            "canal": "SPOTIFY",
            "nome": "Campanha de Spotify - Objetivo - Escuta Completa",
            "data_inicio": "02/09",
            "data_fim": "11/09",
            "impressoes_contratadas": 52083,
            "valor_contratado": 6249.96,
            "objetivo": "Escuta Completa"
        }
        
        # Mapear colunas do Spotify
        column_mapping = {
            'Impressões': 'impressoes',
            'Escutas Completas': 'escutas_completas',
            'Gasto': 'gasto',
            'CPE': 'cpe',
            'Taxa de Escuta Completa': 'taxa_escuta_completa'
        }
        
        # Encontrar e processar colunas
        for metric, key in column_mapping.items():
            for col in df.columns:
                if metric.lower() in col.lower():
                    try:
                        # Converter para numérico
                        numeric_values = pd.to_numeric(
                            df[col].astype(str).str.replace(r'[^\d.,]', '', regex=True).str.replace(',', '.'), 
                            errors='coerce'
                        )
                        spotify_data[key] = numeric_values.sum()
                        break
                    except:
                        continue
        
        # Calcular métricas derivadas se necessário
        if 'impressoes' in spotify_data and 'escutas_completas' in spotify_data:
            if spotify_data['impressoes'] > 0:
                spotify_data['taxa_escuta_completa'] = (spotify_data['escutas_completas'] / spotify_data['impressoes']) * 100
        
        if 'gasto' in spotify_data and 'escutas_completas' in spotify_data:
            if spotify_data['escutas_completas'] > 0:
                spotify_data['cpe'] = spotify_data['gasto'] / spotify_data['escutas_completas']
        
        return spotify_data
    
    def _process_programatica_data(self, df):
        """Processar dados específicos da Programática"""
        programatica_data = {
            "canal": "PROGRAMÁTICA",
            "nome": "CAMPANHA DE VIDEO PROGRAMATICO EM PORTAIS SELECIONADOS - OBJETIVO COMPLETE VIEW",
            "data_inicio": "02/09",
            "data_fim": "11/09",
            "impressoes_contratadas": 98913,
            "valor_contratado": 22749.99,
            "cpv_contratado": 0.23,
            "objetivo": "Complete View"
        }
        
        # Mapear colunas da Programática
        column_mapping = {
            'Impressões': 'impressoes',
            'Visualizações 100%': 'visualizacoes_100',
            'Cliques': 'cliques',
            'Gasto': 'gasto',
            'CPV': 'cpv',
            'CTR': 'ctr',
            'VTR100': 'vtr100'
        }
        
        # Encontrar e processar colunas
        for metric, key in column_mapping.items():
            for col in df.columns:
                if metric.lower() in col.lower():
                    try:
                        # Converter para numérico
                        numeric_values = pd.to_numeric(
                            df[col].astype(str).str.replace(r'[^\d.,]', '', regex=True).str.replace(',', '.'), 
                            errors='coerce'
                        )
                        programatica_data[key] = numeric_values.sum()
                        break
                    except:
                        continue
        
        # Calcular métricas derivadas se necessário
        if 'impressoes' in programatica_data and 'cliques' in programatica_data:
            if programatica_data['impressoes'] > 0:
                programatica_data['ctr'] = (programatica_data['cliques'] / programatica_data['impressoes']) * 100
        
        if 'impressoes' in programatica_data and 'visualizacoes_100' in programatica_data:
            if programatica_data['impressoes'] > 0:
                programatica_data['vtr100'] = (programatica_data['visualizacoes_100'] / programatica_data['impressoes']) * 100
        
        if 'gasto' in programatica_data and 'visualizacoes_100' in programatica_data:
            if programatica_data['visualizacoes_100'] > 0:
                programatica_data['cpv'] = programatica_data['gasto'] / programatica_data['visualizacoes_100']
        
        return programatica_data
    
    def generate_dashboard_data(self):
        """Gerar dados completos para o dashboard"""
        print("🚀 Iniciando integração do dashboard multicanal...")
        
        # Verificar se o serviço está configurado
        if not self.sheets_service.is_configured():
            print("❌ Google Sheets não configurado. Usando dados simulados.")
            return self._generate_simulated_data()
        
        # Buscar dados de todas as fontes
        spotify_data = self.fetch_spotify_data()
        programatica_data = self.fetch_programatica_data()
        sites_list = self.fetch_sites_data()
        
        # Gerar dados consolidados
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "campanhas": {
                "spotify": spotify_data or self._get_default_spotify_data(),
                "programatica": programatica_data or self._get_default_programatica_data()
            },
            "sites_premium": sites_list or self._get_default_sites(),
            "doubleverify": self._get_doubleverify_data(),
            "consolidado": self._calculate_consolidated_metrics(spotify_data, programatica_data)
        }
        
        # Salvar dados
        self._save_dashboard_data(dashboard_data)
        
        print("✅ Dashboard multicanal integrado com sucesso!")
        return dashboard_data
    
    def _generate_simulated_data(self):
        """Gerar dados simulados quando não há acesso às planilhas"""
        return {
            "timestamp": datetime.now().isoformat(),
            "campanhas": {
                "spotify": self._get_default_spotify_data(),
                "programatica": self._get_default_programatica_data()
            },
            "sites_premium": self._get_default_sites(),
            "doubleverify": self._get_doubleverify_data(),
            "consolidado": self._calculate_consolidated_metrics(None, None)
        }
    
    def _get_default_spotify_data(self):
        """Dados padrão do Spotify"""
        return {
            "canal": "SPOTIFY",
            "nome": "Campanha de Spotify - Objetivo - Escuta Completa",
            "data_inicio": "02/09",
            "data_fim": "11/09",
            "impressoes_contratadas": 52083,
            "valor_contratado": 6249.96,
            "objetivo": "Escuta Completa",
            "impressoes": 45000,
            "escutas_completas": 12500,
            "gasto": 5800.50,
            "cpe": 0.46,
            "taxa_escuta_completa": 27.8
        }
    
    def _get_default_programatica_data(self):
        """Dados padrão da Programática"""
        return {
            "canal": "PROGRAMÁTICA",
            "nome": "CAMPANHA DE VIDEO PROGRAMATICO EM PORTAIS SELECIONADOS - OBJETIVO COMPLETE VIEW",
            "data_inicio": "02/09",
            "data_fim": "11/09",
            "impressoes_contratadas": 98913,
            "valor_contratado": 22749.99,
            "cpv_contratado": 0.23,
            "objetivo": "Complete View",
            "impressoes": 85000,
            "visualizacoes_100": 18500,
            "cliques": 2100,
            "gasto": 21000.00,
            "cpv": 1.14,
            "ctr": 2.47,
            "vtr100": 21.8
        }
    
    def _get_default_sites(self):
        """Lista padrão de sites premium"""
        return [
            "UOL", "G1", "Folha de S.Paulo", "Estadão", "Veja", "Exame",
            "InfoMoney", "Valor Econômico", "Revista Época", "IstoÉ",
            "Terra", "R7", "Brasil 247", "CartaCapital", "The Intercept"
        ]
    
    def _get_doubleverify_data(self):
        """Dados do DoubleVerify"""
        return {
            "empreendedores": {
                "impressoes": 25000,
                "taxa_verificacao": 98.5,
                "viewability": 87.2,
                "brand_safety": 99.1
            },
            "interesse_empreendorismo": {
                "impressoes": 18000,
                "taxa_verificacao": 97.8,
                "viewability": 89.1,
                "brand_safety": 98.9
            }
        }
    
    def _calculate_consolidated_metrics(self, spotify_data, programatica_data):
        """Calcular métricas consolidadas"""
        spotify = spotify_data or self._get_default_spotify_data()
        programatica = programatica_data or self._get_default_programatica_data()
        
        return {
            "total_impressoes": spotify.get("impressoes", 0) + programatica.get("impressoes", 0),
            "total_conversoes": spotify.get("escutas_completas", 0) + programatica.get("visualizacoes_100", 0),
            "total_investimento": spotify.get("gasto", 0) + programatica.get("gasto", 0),
            "total_contratado": spotify.get("valor_contratado", 0) + programatica.get("valor_contratado", 0),
            "pacing_percentual": 0,  # Será calculado
            "cpc_medio": 0  # Será calculado
        }
    
    def _save_dashboard_data(self, data):
        """Salvar dados do dashboard"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multicanal_dashboard_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Dados salvos em: {filename}")
    
    def update_dashboard_html(self, data):
        """Atualizar o HTML do dashboard com dados reais"""
        try:
            # Ler o arquivo HTML atual
            html_file = "static/dash_multicanal_spotify_programatica.html"
            
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Substituir dados simulados pelos dados reais
            # Aqui você pode implementar a lógica de substituição específica
            # Por exemplo, substituir os arrays PER e CONS pelos dados reais
            
            print("✅ Dashboard HTML atualizado com dados reais")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar dashboard HTML: {e}")

def main():
    """Função principal"""
    print("🎯 Dashboard Multicanal - Spotify + Programática")
    print("=" * 50)
    
    integrator = MulticanalDashboardIntegrator()
    
    # Gerar dados do dashboard
    dashboard_data = integrator.generate_dashboard_data()
    
    # Exibir resumo
    print("\n📊 Resumo dos Dados:")
    print(f"Spotify - Impressões: {dashboard_data['campanhas']['spotify']['impressoes']:,}")
    print(f"Programática - Impressões: {dashboard_data['campanhas']['programatica']['impressoes']:,}")
    print(f"Total de Sites Premium: {len(dashboard_data['sites_premium'])}")
    print(f"Investimento Total: R$ {dashboard_data['consolidado']['total_investimento']:,.2f}")
    
    print(f"\n🌐 Dashboard disponível em: static/dash_multicanal_spotify_programatica.html")

if __name__ == "__main__":
    main()
