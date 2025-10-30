#!/usr/bin/env python3
"""
Gerenciador de dados da aba Footfall Out
Permite atualizar dados diretamente do Google Sheets ou de arquivo local
"""

import json
import os
import re
from datetime import datetime
import requests
from typing import List, Dict, Any

class FootfallDataManager:
    def __init__(self):
        self.html_file = "static/dash_sonho_v2.html"
        self.data_file = "footfall_out_data.json"
        self.google_sheets_url = "https://docs.google.com/spreadsheets/d/1etGnblqr5YZIqXIweKj5qTMGqmWlxL9OLbN_Ss5tzlQ/edit?gid=120680471#gid=120680471"
    
    def load_current_data(self) -> Dict[str, Any]:
        """Carregar dados atuais do arquivo JSON"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_data(self, data: List[Dict], source: str = "manual") -> None:
        """Salvar dados no arquivo JSON"""
        total_users = sum(store['users'] for store in data)
        active_stores = len([store for store in data if store['users'] > 0])
        avg_conversion = sum(store['rate'] for store in data) / len(data) if data else 0
        best_store = max(data, key=lambda x: x['users']) if data else None
        
        data_package = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
            "google_sheets_url": self.google_sheets_url,
            "data": data,
            "metrics": {
                "total_users": total_users,
                "active_stores": active_stores,
                "avg_conversion": round(avg_conversion, 1),
                "best_store": best_store['name'] if best_store else "N/A",
                "best_store_users": best_store['users'] if best_store else 0
            }
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data_package, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Dados salvos em: {self.data_file}")
        print(f"📊 Métricas atualizadas:")
        print(f"   Total de usuários: {total_users:,}")
        print(f"   Lojas ativas: {active_stores}")
        print(f"   Taxa de conversão média: {avg_conversion:.1f}%")
        if best_store:
            print(f"   Melhor loja: {best_store['name']} ({best_store['users']:,} usuários)")
    
    def update_html_file(self, footfall_data: List[Dict]) -> bool:
        """Atualizar o arquivo HTML com os novos dados"""
        
        if not os.path.exists(self.html_file):
            print(f"❌ Arquivo {self.html_file} não encontrado!")
            return False
        
        # Ler o arquivo HTML
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Criar novo FOOTFALL_POINTS
        new_footfall_points = "const FOOTFALL_POINTS = [\n"
        for store in footfall_data:
            new_footfall_points += f'  {{\n    "lat": {store["lat"]},\n    "lon": {store["lon"]},\n    "name": "{store["name"]}",\n    "users": {store["users"]},\n    "rate": {store["rate"]}\n  }},\n'
        new_footfall_points += "];"
        
        # Substituir FOOTFALL_POINTS no arquivo
        pattern = r'const FOOTFALL_POINTS = \[.*?\];'
        content = re.sub(pattern, new_footfall_points, content, flags=re.DOTALL)
        
        # Salvar arquivo atualizado
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Arquivo {self.html_file} atualizado com sucesso!")
        return True
    
    def update_from_google_sheets(self) -> bool:
        """Atualizar dados do Google Sheets (requer implementação da API)"""
        print("⚠️  Atualização do Google Sheets requer implementação da API")
        print("💡 Use update_from_file() para atualizar via arquivo JSON")
        return False
    
    def update_from_file(self, file_path: str = None) -> bool:
        """Atualizar dados de arquivo JSON"""
        if file_path is None:
            file_path = self.data_file
        
        if not os.path.exists(file_path):
            print(f"❌ Arquivo {file_path} não encontrado!")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data_package = json.load(f)
        
        footfall_data = data_package.get('data', [])
        if not footfall_data:
            print("❌ Nenhum dado encontrado no arquivo!")
            return False
        
        print(f"📂 Carregando dados de: {file_path}")
        print(f"📅 Última atualização: {data_package.get('last_updated', 'N/A')}")
        
        # Atualizar HTML
        if self.update_html_file(footfall_data):
            print("🎉 Dados atualizados com sucesso!")
            return True
        
        return False
    
    def add_new_store(self, lat: float, lon: float, name: str, users: int, rate: float) -> None:
        """Adicionar nova loja aos dados"""
        current_data = self.load_current_data()
        footfall_data = current_data.get('data', [])
        
        new_store = {
            "lat": lat,
            "lon": lon,
            "name": name,
            "users": users,
            "rate": rate
        }
        
        footfall_data.append(new_store)
        self.save_data(footfall_data, "manual_addition")
        self.update_html_file(footfall_data)
        print(f"✅ Nova loja adicionada: {name}")
    
    def remove_store(self, store_name: str) -> None:
        """Remover loja dos dados"""
        current_data = self.load_current_data()
        footfall_data = current_data.get('data', [])
        
        original_count = len(footfall_data)
        footfall_data = [store for store in footfall_data if store['name'] != store_name]
        
        if len(footfall_data) < original_count:
            self.save_data(footfall_data, "manual_removal")
            self.update_html_file(footfall_data)
            print(f"✅ Loja removida: {store_name}")
        else:
            print(f"❌ Loja não encontrada: {store_name}")
    
    def list_stores(self) -> None:
        """Listar todas as lojas atuais"""
        current_data = self.load_current_data()
        footfall_data = current_data.get('data', [])
        
        if not footfall_data:
            print("❌ Nenhuma loja encontrada!")
            return
        
        print(f"📋 Lojas cadastradas ({len(footfall_data)}):")
        for i, store in enumerate(footfall_data, 1):
            print(f"   {i:2d}. {store['name']}")
            print(f"       Usuários: {store['users']:,} | Taxa: {store['rate']}%")
    
    def show_status(self) -> None:
        """Mostrar status atual dos dados"""
        current_data = self.load_current_data()
        
        if not current_data:
            print("❌ Nenhum dado carregado!")
            return
        
        print("📊 Status dos dados:")
        print(f"   📅 Última atualização: {current_data.get('last_updated', 'N/A')}")
        print(f"   📂 Fonte: {current_data.get('source', 'N/A')}")
        
        metrics = current_data.get('metrics', {})
        print(f"   👥 Total de usuários: {metrics.get('total_users', 0):,}")
        print(f"   🏪 Lojas ativas: {metrics.get('active_stores', 0)}")
        print(f"   📈 Taxa de conversão média: {metrics.get('avg_conversion', 0)}%")
        print(f"   🏆 Melhor loja: {metrics.get('best_store', 'N/A')}")

def main():
    """Função principal do gerenciador"""
    manager = FootfallDataManager()
    
    print("🏪 Gerenciador de Dados - Footfall Out")
    print("=" * 50)
    
    while True:
        print("\n📋 Opções disponíveis:")
        print("1. Atualizar do arquivo JSON")
        print("2. Adicionar nova loja")
        print("3. Remover loja")
        print("4. Listar lojas")
        print("5. Mostrar status")
        print("6. Sair")
        
        choice = input("\nEscolha uma opção (1-6): ").strip()
        
        if choice == "1":
            manager.update_from_file()
        
        elif choice == "2":
            try:
                lat = float(input("Latitude: "))
                lon = float(input("Longitude: "))
                name = input("Nome da loja: ")
                users = int(input("Número de usuários: "))
                rate = float(input("Taxa de conversão (%): "))
                manager.add_new_store(lat, lon, name, users, rate)
            except ValueError:
                print("❌ Dados inválidos!")
        
        elif choice == "3":
            name = input("Nome da loja para remover: ")
            manager.remove_store(name)
        
        elif choice == "4":
            manager.list_stores()
        
        elif choice == "5":
            manager.show_status()
        
        elif choice == "6":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()

