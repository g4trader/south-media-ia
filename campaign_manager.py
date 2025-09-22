#!/usr/bin/env python3
"""
Campaign Manager - Gerenciador de campanhas
Sistema robusto para gerenciar campanhas e seus dados
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class CampaignManager:
    """Gerenciador de campanhas"""
    
    def __init__(self):
        self.campaigns_file = 'campaigns.json'
        self.campaigns = self._load_campaigns()
    
    def _load_campaigns(self) -> List[Dict[str, Any]]:
        """Carregar campanhas do arquivo"""
        if os.path.exists(self.campaigns_file):
            try:
                with open(self.campaigns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar campanhas: {e}")
                return []
        return []
    
    def _save_campaigns(self):
        """Salvar campanhas no arquivo"""
        try:
            with open(self.campaigns_file, 'w', encoding='utf-8') as f:
                json.dump(self.campaigns, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar campanhas: {e}")
    
    def create_campaign(self, campaign_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Criar nova campanha"""
        campaign = {
            "id": campaign_id,
            "name": data.get('campaignName'),
            "start_date": data.get('startDate'),
            "end_date": data.get('endDate'),
            "total_budget": data.get('totalBudget'),
            "kpi_type": data.get('kpiType'),
            "kpi_value": data.get('kpiValue'),
            "report_model": data.get('reportModel'),
            "strategies": data.get('strategies', ''),
            "channels": data.get('channels', []),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "data": {}  # Será preenchido com dados reais das planilhas
        }
        
        # Adicionar à lista de campanhas
        self.campaigns.append(campaign)
        self._save_campaigns()
        
        return campaign
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Obter campanha por ID"""
        for campaign in self.campaigns:
            if campaign.get('id') == campaign_id:
                return campaign
        return None
    
    def update_campaign(self, campaign_id: str, data: Dict[str, Any]) -> bool:
        """Atualizar campanha"""
        for i, campaign in enumerate(self.campaigns):
            if campaign.get('id') == campaign_id:
                # Atualizar campos permitidos
                updatable_fields = ['name', 'start_date', 'end_date', 'total_budget', 'strategies', 'data']
                for field in updatable_fields:
                    if field in data:
                        campaign[field] = data[field]
                
                campaign['updated_at'] = datetime.now().isoformat()
                self.campaigns[i] = campaign
                self._save_campaigns()
                return True
        return False
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """Deletar campanha"""
        for i, campaign in enumerate(self.campaigns):
            if campaign.get('id') == campaign_id:
                del self.campaigns[i]
                self._save_campaigns()
                return True
        return False
    
    def list_campaigns(self) -> List[Dict[str, Any]]:
        """Listar todas as campanhas"""
        return self.campaigns
    
    def get_active_campaigns(self) -> List[Dict[str, Any]]:
        """Obter campanhas ativas"""
        return [campaign for campaign in self.campaigns if campaign.get('status') == 'active']
    
    def update_campaign_data(self, campaign_id: str, data: Dict[str, Any]) -> bool:
        """Atualizar dados de uma campanha"""
        for i, campaign in enumerate(self.campaigns):
            if campaign.get('id') == campaign_id:
                campaign['data'] = data
                campaign['updated_at'] = datetime.now().isoformat()
                self.campaigns[i] = campaign
                self._save_campaigns()
                return True
        return False
    
    def get_campaigns_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Obter campanhas por período"""
        filtered_campaigns = []
        for campaign in self.campaigns:
            campaign_start = campaign.get('start_date', '')
            campaign_end = campaign.get('end_date', '')
            
            # Verificar se há sobreposição de datas
            if (campaign_start <= end_date and campaign_end >= start_date):
                filtered_campaigns.append(campaign)
        
        return filtered_campaigns
    
    def get_campaigns_by_channel(self, channel_name: str) -> List[Dict[str, Any]]:
        """Obter campanhas por canal"""
        filtered_campaigns = []
        for campaign in self.campaigns:
            channels = campaign.get('channels', [])
            for channel in channels:
                if channel.get('name', '').lower() == channel_name.lower():
                    filtered_campaigns.append(campaign)
                    break
        return filtered_campaigns
    
    def get_campaign_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas das campanhas"""
        total_campaigns = len(self.campaigns)
        active_campaigns = len(self.get_active_campaigns())
        
        total_budget = sum(campaign.get('total_budget', 0) for campaign in self.campaigns)
        
        # Contar canais por tipo
        channel_counts = {}
        for campaign in self.campaigns:
            for channel in campaign.get('channels', []):
                channel_name = channel.get('name', '')
                channel_counts[channel_name] = channel_counts.get(channel_name, 0) + 1
        
        return {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_budget": total_budget,
            "channel_distribution": channel_counts,
            "last_updated": datetime.now().isoformat()
        }
