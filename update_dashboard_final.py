#!/usr/bin/env python3
"""
Script para atualizar o dashboard com os dados corrigidos
"""

import json

def main():
    # Dados de contratação (já corretos)
    contract_data = [
        {'Canal': 'CTV', 'Budget Contratado (R$)': 11895.55, 'CPV (R$)': 0.2, 'Views Contratadas': 59477},
        {'Canal': 'Disney', 'Budget Contratado (R$)': 23145.9, 'CPV (R$)': 0.46, 'Views Contratadas': 50045},
        {'Canal': 'Footfall Display', 'Budget Contratado (R$)': 10229.36, 'CPM (R$)': 21.0, 'Impressões Contratadas': 481382},
        {'Canal': 'Netflix', 'Budget Contratado (R$)': 23145.7, 'CPV (R$)': 0.33, 'Views Contratadas': 68579},
        {'Canal': 'TikTok', 'Budget Contratado (R$)': 16898.09, 'CPM (R$)': 15.2, 'Impressões Contratadas': 898373},
        {'Canal': 'YouTube', 'Budget Contratado (R$)': 24166.65, 'CPV (R$)': 0.03, 'Views Contratadas': 644444}
    ]
    
    # Carregar dados de entrega corrigidos
    with open('/Users/lucianoterres/Documents/GitHub/south-media-ia/corrected_delivery_data.js', 'r', encoding='utf-8') as f:
        content = f.read()
        # Extrair apenas o JSON
        json_start = content.find('[')
        json_end = content.rfind(']') + 1
        daily_data = json.loads(content[json_start:json_end])
    
    # Calcular dados consolidados
    total_budget_contratado = sum([c['Budget Contratado (R$)'] for c in contract_data])
    total_budget_utilizado = sum([d['spend'] for d in daily_data])
    total_impressions = sum([d['impressions'] for d in daily_data if d['impressions']])
    total_clicks = sum([d['clicks'] for d in daily_data if d['clicks']])
    total_vc = sum([d['q100'] for d in daily_data if d['q100']])
    
    # Calcular métricas consolidadas
    ctr_cons = (total_clicks / total_impressions) if total_impressions > 0 else 0
    vtr_cons = (total_vc / total_impressions) if total_impressions > 0 else 0
    cpm_cons = (total_budget_utilizado / total_impressions * 1000) if total_impressions > 0 else 0
    cpv_cons = (total_budget_utilizado / total_vc) if total_vc > 0 else 0
    
    cons_data = {
        'Budget Contratado (R$)': total_budget_contratado,
        'Budget Utilizado (R$)': total_budget_utilizado,
        'Impressões': total_impressions,
        'Cliques': total_clicks,
        'CTR (cons.)': ctr_cons,
        'VC (100%)': total_vc,
        'VTR (cons.)': vtr_cons,
        'CPM (R$) cons.': cpm_cons,
        'CPV (R$) cons.': cpv_cons,
        'Visitas (Footfall)': 0,
        'Custo/Visita (R$) cons.': None
    }
    
    # Calcular dados por canal
    per_data = []
    for contract in contract_data:
        channel = contract['Canal']
        
        # Calcular dados de entrega para este canal
        channel_delivery = [d for d in daily_data if d['channel'] == channel]
        budget_utilizado = sum([d['spend'] for d in channel_delivery])
        impressions = sum([d['impressions'] for d in channel_delivery if d['impressions']])
        clicks = sum([d['clicks'] for d in channel_delivery if d['clicks']])
        vc = sum([d['q100'] for d in channel_delivery if d['q100']])
        
        # Calcular métricas
        ctr = (clicks / impressions) if impressions > 0 else None
        vtr = (vc / impressions) if impressions > 0 else None
        cpm = (budget_utilizado / impressions * 1000) if impressions > 0 else None
        cpv = (budget_utilizado / vc) if vc > 0 else None
        pacing = (budget_utilizado / contract['Budget Contratado (R$)']) if contract['Budget Contratado (R$)'] > 0 else 0
        
        per_data.append({
            'Canal': channel,
            'Budget Contratado (R$)': contract['Budget Contratado (R$)'],
            'Budget Utilizado (R$)': budget_utilizado,
            'Impressões': impressions if impressions > 0 else None,
            'Cliques': clicks if clicks > 0 else None,
            'CTR': ctr,
            'VC (100%)': vc if vc > 0 else None,
            'VTR (100%)': vtr,
            'CPV (R$)': contract.get('CPV (R$)'),
            'CPM (R$)': contract.get('CPM (R$)'),
            'Visitas (Footfall)': 0,
            'Custo/Visita (R$)': None,
            'Pacing (%)': pacing
        })
    
    # Dados de footfall (mantidos)
    footfall_points = [
        {"lat": -8.09233930867147, "lon": -34.8847507746984, "name": "Recibom - Av. Eng. Domingos Ferreira, 306 - Pina", "users": 1740.0, "rate": 3.0},
        {"lat": -8.13196914950721, "lon": -34.9069687730163, "name": "Recibom boa viagem - R. Barão de Souza Leão, 767 - Boa Viagem, Recife - PE, 51030-300", "users": 1892.0, "rate": 7.0},
        {"lat": -8.04591568467357, "lon": -34.9092152269836, "name": "Recibom - Torre - Rua Conde de Irajá, 632 - Torre, Recife - PE, 50710-310", "users": 211.0, "rate": 9.0},
        {"lat": -8.047434924792, "lon": -34.9001621153442, "name": "Recibom - Graças - Av. Rui Barbosa, 551 - Graças, Recife - PE, 52011-040", "users": 548.0, "rate": 8.0},
        {"lat": -8.02988247354862, "lon": -34.9066516730163, "name": "Recibom - Parnamirim - Estr. do Arraial, 2668 - Tamarineira, Recife - PE, 52051-380", "users": 555.0, "rate": 11.0},
        {"lat": -8.11993224900449, "lon": -34.9009126846557, "name": "Recibom - Boa Viagem - R. Prof. João Medeiros, 261 - Boa Viagem, Recife - PE, 51021-050", "users": 1020.0, "rate": 6.0},
        {"lat": -8.14254391419425, "lon": -34.9081091134918, "name": "Recibom - Setúbal - R. João Cardoso Aires, 407 - Boa Viagem, Recife - PE, 51130-300", "users": 1089.0, "rate": 5.0},
        {"lat": -8.0281307802215, "lon": -34.9025068846557, "name": "Recibom - Encruzilhada - Av. Norte Miguel Arraes de Alencar, S/N - Encruzilhada, Recife - PE, 52041-005", "users": 4328.0, "rate": 11.0},
        {"lat": -7.99956677243255, "lon": -34.8464921711639, "name": "Recibom - Olinda - Av. Carlos de Lima Cavalcante, 515 - Bultrins, Olinda - PE, 53030-260", "users": 5121.0, "rate": 12.0},
        {"lat": -8.18360115521895, "lon": -34.919450028836, "name": "Recibom - Piedade - Av. Bernardo Vieira de Melo, 3454 - Piedade, Jaboatão dos Guararapes - PE, 54410-010", "users": 1212.0, "rate": 11.0},
        {"lat": -8.18233405479681, "lon": -34.9200238558197, "name": "Recibom - Piedade -Av. Ayrton Senna da Silva, 2851 - Piedade, Jaboatão dos Guararapes - PE, 54410-400", "users": 1573.0, "rate": 14.0},
        {"lat": -8.01836781970679, "lon": -34.9962135137705, "name": "Recibom - Timbi, Camaragibe - PE, 54765-290", "users": None, "rate": None}
    ]
    
    # Gerar JavaScript
    js_content = f"""// Dados finais corrigidos do dashboard
const CONS = {json.dumps(cons_data, ensure_ascii=False, indent=2)};
const PER = {json.dumps(per_data, ensure_ascii=False, indent=2)};
const DAILY = {json.dumps(daily_data, ensure_ascii=False, indent=2)};
const FOOTFALL_POINTS = {json.dumps(footfall_points, ensure_ascii=False, indent=2)};"""
    
    # Salvar arquivo
    with open('/Users/lucianoterres/Documents/GitHub/south-media-ia/final_dashboard_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("✅ Dashboard atualizado com dados corrigidos!")
    print(f"📊 Total contratado: R$ {cons_data['Budget Contratado (R$)']:,.2f}")
    print(f"💰 Total utilizado: R$ {cons_data['Budget Utilizado (R$)']:,.2f}")
    print(f"📈 Pacing geral: {(cons_data['Budget Utilizado (R$)'] / cons_data['Budget Contratado (R$)'] * 100):.1f}%")
    print(f"📊 Total de registros diários: {len(daily_data)}")
    
    return cons_data, per_data, daily_data

if __name__ == "__main__":
    main()
