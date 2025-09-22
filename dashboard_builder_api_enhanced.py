#!/usr/bin/env python3
"""
API aprimorada para criação de dashboards - Interface amigável
"""

import json
import os
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import traceback

# Configurar logging
logger = logging.getLogger(__name__)

# Importar processador de planilhas
try:
    from google_sheets_processor import GoogleSheetsProcessor
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False
    print("⚠️ GoogleSheetsProcessor não disponível - usando dados simulados")

app = Flask(__name__)
CORS(app)

class DashboardBuilderEnhanced:
    def __init__(self):
        self.dashboards_file = 'dynamic_dashboards_enhanced.json'
        self.templates_dir = 'templates'
        self.output_dir = 'static'
        self.sheets_processor = None
        
        # Inicializar processador de planilhas se disponível
        if SHEETS_AVAILABLE:
            try:
                self.sheets_processor = GoogleSheetsProcessor()
                self.sheets_processor.authenticate()
                print("✅ GoogleSheetsProcessor inicializado com sucesso")
            except Exception as e:
                print(f"⚠️ Erro ao inicializar GoogleSheetsProcessor: {e}")
                self.sheets_processor = None

    def load_dashboards(self):
        """Carregar dashboards existentes"""
        if os.path.exists(self.dashboards_file):
            with open(self.dashboards_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_dashboards(self, dashboards):
        """Salvar dashboards"""
        with open(self.dashboards_file, 'w', encoding='utf-8') as f:
            json.dump(dashboards, f, ensure_ascii=False, indent=2)

    def validate_campaign_data(self, data):
        """Validar dados da campanha"""
        errors = []
        
        # Campos obrigatórios
        required_fields = ['campaignName', 'startDate', 'endDate', 'totalBudget', 'kpiType', 'kpiValue', 'reportModel']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Campo obrigatório: {field}")
        
        # Validação de datas
        if data.get('startDate') and data.get('endDate'):
            try:
                start_date = datetime.strptime(data['startDate'], '%Y-%m-%d')
                end_date = datetime.strptime(data['endDate'], '%Y-%m-%d')
                if start_date >= end_date:
                    errors.append("Data de início deve ser anterior à data de fim")
            except ValueError:
                errors.append("Formato de data inválido")
        
        # Validação de orçamento
        try:
            total_budget = float(data.get('totalBudget', 0))
            if total_budget <= 0:
                errors.append("Orçamento total deve ser maior que zero")
        except (ValueError, TypeError):
            errors.append("Orçamento total deve ser um número válido")
        
        # Validação de canais
        channels = data.get('channels', [])
        if not channels:
            errors.append("Pelo menos um canal deve ser selecionado")
        
        total_channel_budget = 0
        for channel in channels:
            try:
                channel_budget = float(channel.get('budget', 0))
                if channel_budget < 0:
                    errors.append(f"Orçamento do canal {channel.get('name')} não pode ser negativo")
                total_channel_budget += channel_budget
            except (ValueError, TypeError):
                errors.append(f"Orçamento inválido para o canal {channel.get('name')}")
        
        if total_channel_budget > total_budget:
            errors.append("Soma dos orçamentos dos canais não pode exceder o orçamento total")
        
        return {'valid': len(errors) == 0, 'errors': errors}

    def load_real_sheets_data(self):
        """Carregar dados reais das planilhas processadas"""
        try:
            # Procurar por arquivos de dados processados
            import glob
            
            # Buscar arquivos de dados mais recentes
            data_files = glob.glob('data_pt_br_formatted_*.json')
            if not data_files:
                data_files = glob.glob('quartis_corrected_*.json')
            if not data_files:
                data_files = glob.glob('used_data_*.json')
            
            if data_files:
                # Pegar o arquivo mais recente
                latest_file = max(data_files, key=os.path.getctime)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
        except Exception as e:
            print(f"Erro ao carregar dados reais: {e}")
            return None

    def get_real_channel_data(self, channel, real_data):
        """Usar dados reais das planilhas"""
        channel_name = channel.get('name', '').lower()
        
        if 'youtube' in channel_name:
            return {
                'name': 'YouTube',
                'impressions': real_data.get('YOUTUBE_TOTAL_IMPRESSIONS', 0),
                'clicks': real_data.get('YOUTUBE_TOTAL_CLICKS', 0),
                'spend': real_data.get('YOUTUBE_TOTAL_SPEND', 0),
                'ctr': real_data.get('YOUTUBE_CTR', 0),
                'cpv': real_data.get('YOUTUBE_CPV', 0),
                'completion_rate': real_data.get('YOUTUBE_COMPLETION_RATE', 0)
            }
        elif 'programatica' in channel_name and 'video' in channel_name:
            return {
                'name': 'Programática Video',
                'impressions': real_data.get('PROG_TOTAL_IMPRESSIONS', 0),
                'clicks': real_data.get('PROG_TOTAL_CLICKS', 0),
                'spend': real_data.get('PROG_TOTAL_SPEND', 0),
                'ctr': real_data.get('PROG_CTR', 0),
                'cpv': real_data.get('PROG_CPV', 0),
                'completion_rate': real_data.get('PROG_COMPLETION_RATE', 0)
            }
        elif 'programatica' in channel_name and 'display' in channel_name:
            return {
                'name': 'Programática Display',
                'impressions': real_data.get('PROG_DISPLAY_IMPRESSIONS', 0),
                'clicks': real_data.get('PROG_DISPLAY_CLICKS', 0),
                'spend': real_data.get('PROG_DISPLAY_SPEND', 0),
                'ctr': real_data.get('PROG_DISPLAY_CTR', 0),
                'cpv': real_data.get('PROG_DISPLAY_CPV', 0),
                'completion_rate': real_data.get('PROG_DISPLAY_COMPLETION_RATE', 0)
            }
        else:
            return self.get_simulated_channel_data(channel)

    def process_channel_data(self, channel):
        """Processar dados de um canal"""
        try:
            # SEMPRE tentar usar dados reais das planilhas
            if not self.sheets_processor:
                raise Exception("Google Sheets não configurado - configure as credenciais")
            
            sheet_id = channel.get('sheetId') or channel.get('sheet_id')
            gid = channel.get('gid')
            
            # Debug logging
            print(f"🔍 DEBUG - Canal: {channel.get('name')}")
            print(f"🔍 DEBUG - sheetId (camelCase): {channel.get('sheetId')}")
            print(f"🔍 DEBUG - sheet_id (snake_case): {channel.get('sheet_id')}")
            print(f"🔍 DEBUG - sheet_id final: {sheet_id}")
            print(f"🔍 DEBUG - gid: {gid}")
            
            if not sheet_id:
                raise Exception(f"ID da planilha obrigatório para {channel.get('name')}")
            
            # Validar acesso à planilha
            if not self.sheets_processor.validate_sheet_access(sheet_id, gid):
                raise Exception(f"Não foi possível acessar a planilha {sheet_id}")
            
            # Ler dados reais da planilha
            data = self.sheets_processor.read_sheet_data(sheet_id, sheet_name=None, gid=gid)
            if not data:
                raise Exception(f"Nenhum dado encontrado na planilha {sheet_id}")
            
            # Processar dados reais
            return self.calculate_channel_metrics(data, channel)
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar canal {channel.get('name')}: {e}")
            logger.error(f"❌ Tipo do erro: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise Exception(f"Erro ao processar dados do canal {channel.get('name')}: {e}")

    def get_simulated_channel_data(self, channel):
        """Dados simulados para um canal"""
        channel_name = channel.get('name', '')
        budget = float(channel.get('budget', 0))
        quantity = int(channel.get('quantity', 0))
        
        # Simular métricas baseadas no tipo de canal
        if 'YouTube' in channel_name:
            return {
                'total_views': quantity,
                'total_clicks': int(quantity * 0.02),  # 2% CTR
                'total_spend': budget * 0.5,  # 50% do orçamento usado
                'avg_ctr': 2.0,
                'avg_cpv': budget * 0.5 / quantity if quantity > 0 else 0
            }
        elif 'Programática' in channel_name:
            return {
                'total_impressions': quantity,
                'total_clicks': int(quantity * 0.015),  # 1.5% CTR
                'total_spend': budget * 0.6,  # 60% do orçamento usado
                'avg_ctr': 1.5,
                'avg_cpm': budget * 0.6 / (quantity / 1000) if quantity > 0 else 0
            }
        else:
            return {
                'total_impressions': quantity,
                'total_clicks': int(quantity * 0.01),
                'total_spend': budget * 0.4,
                'avg_ctr': 1.0,
                'avg_cpm': 0
            }

    def calculate_channel_metrics(self, data, channel):
        """Calcular métricas de um canal baseado nos dados da planilha"""
        try:
            logger.info(f"🧮 Calculando métricas para {channel.get('name')}")
            logger.info(f"📊 Tipo dos dados: {type(data)}")
            
            # Verificar se é DataFrame ou lista
            if hasattr(data, 'empty'):  # É um DataFrame
                logger.info(f"📊 DataFrame com {len(data)} linhas")
                if data.empty:
                    raise Exception("DataFrame vazio - dados insuficientes na planilha")
                
                # Converter DataFrame para lista
                headers = data.columns.tolist()
                rows = data.values.tolist()
                logger.info(f"📊 DataFrame convertido para lista com {len(rows)} linhas")
            else:  # É uma lista
                logger.info(f"📊 Lista com {len(data) if data else 0} elementos")
                if not data or len(data) < 2:
                    raise Exception("Dados insuficientes na planilha")
                
                # Extrair cabeçalhos e dados
                headers = data[0] if data else []
                rows = data[1:] if len(data) > 1 else []
            
            logger.info(f"📋 Cabeçalhos: {headers}")
            logger.info(f"📋 Número de linhas: {len(rows)}")
            
            # Debug: verificar estrutura das primeiras linhas
            if rows:
                logger.info(f"🔍 Primeira linha: {rows[0] if rows else 'Nenhuma'}")
                logger.info(f"🔍 Tipo da primeira linha: {type(rows[0])}")
                if rows[0]:
                    logger.info(f"🔍 Primeira linha é lista: {isinstance(rows[0], list)}")
                    if isinstance(rows[0], list):
                        logger.info(f"🔍 Tamanho da primeira linha: {len(rows[0])}")
            
            # Calcular métricas básicas
            metrics = {
                'name': channel.get('name', 'Unknown'),
                'budget': float(channel.get('budget', 0)),
                'quantity': int(channel.get('quantity', 0)),
                'sheet_id': channel.get('sheet_id'),
                'gid': channel.get('gid'),
                'data_rows': len(rows),
                'headers': headers
            }
            
            # Calcular totais se houver colunas numéricas
            if rows and headers:
                for i, header in enumerate(headers):
                    if header and any(keyword in header.lower() for keyword in ['spend', 'gasto', 'custo', 'impress', 'view', 'click']):
                        try:
                            # Verificar se a linha é uma lista antes de acessar por índice
                            total = 0
                            for row in rows:
                                if isinstance(row, list) and i < len(row) and row[i] is not None:
                                    try:
                                        # Tentar converter para float, removendo vírgulas e pontos
                                        value_str = str(row[i]).replace(',', '').replace('.', '')
                                        if value_str.isdigit():
                                            total += float(row[i])
                                    except (ValueError, TypeError):
                                        continue
                            metrics[f'total_{header.lower().replace(" ", "_")}'] = total
                            logger.info(f"📊 Total calculado para {header}: {total}")
                        except (ValueError, IndexError, TypeError) as e:
                            logger.warning(f"⚠️ Erro ao calcular total para {header}: {e}")
                            continue
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular métricas do canal {channel.get('name')}: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise Exception(f"Erro ao processar dados do canal: {str(e)}")

    def generate_dashboard_html(self, config):
        """Gerar HTML do dashboard"""
        try:
            # Determinar template baseado no modelo
            template_file = 'template_simple.html'
            if config.get('report_model') == 'multichannel':
                template_file = 'template_multichannel.html'
            
            template_path = os.path.join(self.templates_dir, template_file)
            
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template não encontrado: {template_path}")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Processar dados dos canais
            channel_data = {}
            for channel in config.get('channels', []):
                channel_name = channel.get('name', '')
                channel_data[channel_name] = self.process_channel_data(channel)
            
            # Substituir variáveis no template
            html_content = self.replace_template_variables(template_content, config, channel_data)
            
            return html_content
            
        except Exception as e:
            print(f"Erro ao gerar HTML: {e}")
            raise

    def replace_template_variables(self, template_content, config, channel_data):
        """Substituir variáveis no template"""
        # Dados básicos da campanha
        replacements = {
            '{{CAMPAIGN_NAME}}': config.get('campaignName', ''),
            '{{START_DATE}}': self.format_date_to_dd_mm_aa(config.get('startDate', '')),
            '{{END_DATE}}': self.format_date_to_dd_mm_aa(config.get('endDate', '')),
            '{{STATUS}}': 'Ativa',
            '{{TOTAL_BUDGET}}': f"R$ {float(config.get('totalBudget', 0)):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            '{{KPI_VALUE}}': f"R$ {float(config.get('kpiValue', 0)):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        }
        
        # Aplicar substituições
        for placeholder, value in replacements.items():
            template_content = template_content.replace(placeholder, str(value))
        
        # Substituir dados dos canais (implementar lógica específica)
        # Por enquanto, usar valores padrão
        default_replacements = {
            '{{TOTAL_SPEND_USED}}': 'R$ 0,00',
            '{{TOTAL_IMPRESSIONS_USED}}': '0',
            '{{TOTAL_CLICKS_USED}}': '0',
            '{{TOTAL_CPV_USED}}': 'R$ 0,00',
            '{{TOTAL_CTR_USED}}': '0,00%',
            '{{BUDGET_UTILIZATION_PERCENTAGE}}': '0,00%',
            '{{IMPRESSIONS_UTILIZATION_PERCENTAGE}}': '0,00%'
        }
        
        for placeholder, value in default_replacements.items():
            template_content = template_content.replace(placeholder, str(value))
        
        return template_content

    def format_date_to_dd_mm_aa(self, date_str):
        """Formatar data para dd/mm/aa"""
        try:
            if not date_str:
                return ''
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%y')
        except:
            return date_str

# Inicializar builder
builder = DashboardBuilderEnhanced()

@app.route('/health', methods=['GET'])
def health_check():
    """Verificar saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'sheets_available': SHEETS_AVAILABLE,
        'version': '2.0.0'
    })

@app.route('/api/dashboards', methods=['GET'])
def list_dashboards():
    """Listar todos os dashboards"""
    try:
        dashboards = builder.load_dashboards()
        return jsonify({
            'success': True,
            'dashboards': dashboards,
            'count': len(dashboards)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboards', methods=['POST'])
def create_dashboard():
    """Criar novo dashboard"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Validar dados
        validation_errors = builder.validate_campaign_data(data)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Dados inválidos',
                'details': validation_errors
            }), 400
        
        # Gerar ID único
        dashboard_id = str(uuid.uuid4())
        
        # Criar configuração do dashboard
        dashboard_config = {
            'id': dashboard_id,
            'name': data.get('campaignName'),
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'config': data
        }
        
        # Gerar HTML
        try:
            html_content = builder.generate_dashboard_html(data)
            
            # Salvar arquivo HTML
            filename = f"dash_{data.get('campaignName', 'campaign').lower().replace(' ', '_')}.html"
            filepath = os.path.join(builder.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            dashboard_config['html_file'] = filename
            dashboard_config['html_path'] = filepath
            
        except Exception as e:
            print(f"Erro ao gerar HTML: {e}")
            dashboard_config['html_error'] = str(e)
        
        # Salvar dashboard
        dashboards = builder.load_dashboards()
        dashboards.append(dashboard_config)
        builder.save_dashboards(dashboards)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_config,
            'message': 'Dashboard criado com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro ao criar dashboard: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

@app.route('/api/dashboards/<dashboard_id>/validate', methods=['POST'])
def validate_dashboard(dashboard_id):
    """Validar dashboard"""
    try:
        dashboards = builder.load_dashboards()
        dashboard = next((d for d in dashboards if d['id'] == dashboard_id), None)
        
        if not dashboard:
            return jsonify({
                'success': False,
                'error': 'Dashboard não encontrado'
            }), 404
        
        dashboard['status'] = 'validated'
        dashboard['validated_at'] = datetime.now().isoformat()
        
        builder.save_dashboards(dashboards)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard,
            'message': 'Dashboard validado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboards/<dashboard_id>/activate', methods=['POST'])
def activate_dashboard(dashboard_id):
    """Ativar dashboard"""
    try:
        dashboards = builder.load_dashboards()
        dashboard = next((d for d in dashboards if d['id'] == dashboard_id), None)
        
        if not dashboard:
            return jsonify({
                'success': False,
                'error': 'Dashboard não encontrado'
            }), 404
        
        dashboard['status'] = 'active'
        dashboard['activated_at'] = datetime.now().isoformat()
        
        builder.save_dashboards(dashboards)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard,
            'message': 'Dashboard ativado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboards/<dashboard_id>', methods=['GET'])
def get_dashboard(dashboard_id):
    """Obter dashboard específico"""
    try:
        dashboards = builder.load_dashboards()
        dashboard = next((d for d in dashboards if d['id'] == dashboard_id), None)
        
        if not dashboard:
            return jsonify({
                'success': False,
                'error': 'Dashboard não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'dashboard': dashboard
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboards/<dashboard_id>/download', methods=['GET'])
def download_dashboard(dashboard_id):
    """Download do arquivo HTML do dashboard"""
    try:
        dashboards = builder.load_dashboards()
        dashboard = next((d for d in dashboards if d['id'] == dashboard_id), None)
        
        if not dashboard:
            return jsonify({
                'success': False,
                'error': 'Dashboard não encontrado'
            }), 404
        
        html_file = dashboard.get('html_file')
        if not html_file:
            return jsonify({
                'success': False,
                'error': 'Arquivo HTML não encontrado'
            }), 404
        
        filepath = os.path.join(builder.output_dir, html_file)
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Arquivo HTML não existe no sistema'
            }), 404
        
        return send_file(filepath, as_attachment=True, download_name=html_file)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/templates', methods=['GET'])
def list_templates():
    """Listar templates disponíveis"""
    try:
        templates = []
        if os.path.exists(builder.templates_dir):
            for file in os.listdir(builder.templates_dir):
                if file.endswith('.html'):
                    templates.append({
                        'name': file,
                        'path': os.path.join(builder.templates_dir, file)
                    })
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando Dashboard Builder API Enhanced...")
    print(f"📁 Templates: {builder.templates_dir}")
    print(f"📁 Output: {builder.output_dir}")
    print(f"📊 Google Sheets: {'✅ Disponível' if SHEETS_AVAILABLE else '❌ Não disponível'}")
    
    app.run(host='0.0.0.0', port=8084, debug=True)
