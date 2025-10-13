#!/usr/bin/env python3
"""
Cloud SQL Optimizer - Sistema avançado de otimização de custos e performance
Projeto: automatizar-452311
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import subprocess
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudSQLOptimizer:
    """Otimizador avançado para Cloud SQL"""
    
    def __init__(self, project_id: str = "automatizar-452311"):
        self.project_id = project_id
        self.instances = {
            "production": ["south-media-postgres"],  # Instâncias críticas
            "development": ["concurso-ai-db", "finaflow-postgres"],  # Instâncias de dev
            "backup": []  # Instâncias de backup
        }
        
        # Configurações de otimização
        self.optimization_config = {
            "auto_stop_dev": True,
            "backup_retention_days": 7,
            "maintenance_window": "sun:03:00",
            "cpu_utilization_threshold": 70,
            "memory_utilization_threshold": 80,
            "cost_alert_threshold": 50.0  # USD por mês
        }
    
    def get_instance_info(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """Obter informações detalhadas de uma instância"""
        try:
            cmd = [
                "gcloud", "sql", "instances", "describe", instance_name,
                "--project", self.project_id,
                "--format", "json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Erro ao obter info da instância {instance_name}: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao executar comando gcloud: {e}")
            return None
    
    def get_all_instances_status(self) -> Dict[str, Dict[str, Any]]:
        """Obter status de todas as instâncias"""
        instances_status = {}
        
        for category, instances in self.instances.items():
            for instance in instances:
                info = self.get_instance_info(instance)
                if info:
                    instances_status[instance] = {
                        "category": category,
                        "state": info.get("state", "UNKNOWN"),
                        "tier": info.get("settings", {}).get("tier", "unknown"),
                        "region": info.get("region", "unknown"),
                        "disk_size": info.get("settings", {}).get("dataDiskSizeGb", 0),
                        "disk_type": info.get("settings", {}).get("dataDiskType", "unknown"),
                        "backup_enabled": info.get("settings", {}).get("backupConfiguration", {}).get("enabled", False),
                        "maintenance_window": info.get("settings", {}).get("maintenanceWindow", {}),
                        "created_at": info.get("createTime", ""),
                        "last_updated": datetime.now().isoformat()
                    }
        
        return instances_status
    
    def estimate_monthly_cost(self, instance_name: str) -> float:
        """Estimar custo mensal de uma instância"""
        info = self.get_instance_info(instance_name)
        if not info:
            return 0.0
        
        tier = info.get("settings", {}).get("tier", "db-f1-micro")
        disk_size = info.get("settings", {}).get("dataDiskSizeGb", 10)
        
        # Preços aproximados (USD/mês) - atualizados para 2024
        pricing = {
            "db-f1-micro": 7.67,
            "db-g1-small": 24.27,
            "db-n1-standard-1": 48.54,
            "db-n1-standard-2": 97.08,
            "db-n1-standard-4": 194.16,
            "db-n1-standard-8": 388.32,
            "db-n1-standard-16": 776.64,
            "db-n1-highmem-2": 146.88,
            "db-n1-highmem-4": 293.76,
            "db-n1-highmem-8": 587.52,
            "db-n1-highmem-16": 1175.04
        }
        
        # Custo base da instância
        base_cost = pricing.get(tier, 7.67)
        
        # Custo do disco (SSD: ~$0.17/GB/mês)
        disk_cost = disk_size * 0.17
        
        # Backup (se habilitado): ~$0.08/GB/mês
        backup_cost = 0.0
        if info.get("settings", {}).get("backupConfiguration", {}).get("enabled", False):
            backup_cost = disk_size * 0.08
        
        total_cost = base_cost + disk_cost + backup_cost
        return round(total_cost, 2)
    
    def optimize_development_instances(self) -> Dict[str, Any]:
        """Otimizar instâncias de desenvolvimento"""
        optimization_results = {
            "stopped_instances": [],
            "savings": 0.0,
            "errors": []
        }
        
        for instance in self.instances["development"]:
            try:
                info = self.get_instance_info(instance)
                if not info:
                    continue
                
                if info.get("state") == "RUNNABLE":
                    # Calcular economia
                    monthly_cost = self.estimate_monthly_cost(instance)
                    optimization_results["savings"] += monthly_cost
                    
                    # Parar instância
                    cmd = [
                        "gcloud", "sql", "instances", "patch", instance,
                        "--project", self.project_id,
                        "--activation-policy=NEVER",
                        "--quiet"
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        optimization_results["stopped_instances"].append({
                            "name": instance,
                            "monthly_savings": monthly_cost,
                            "stopped_at": datetime.now().isoformat()
                        })
                        logger.info(f"✅ Instância de desenvolvimento {instance} parada (economia: ${monthly_cost}/mês)")
                    else:
                        optimization_results["errors"].append({
                            "instance": instance,
                            "error": result.stderr
                        })
                        logger.error(f"❌ Erro ao parar {instance}: {result.stderr}")
                
            except Exception as e:
                optimization_results["errors"].append({
                    "instance": instance,
                    "error": str(e)
                })
                logger.error(f"❌ Erro ao otimizar {instance}: {e}")
        
        return optimization_results
    
    def start_instance_on_demand(self, instance_name: str) -> bool:
        """Iniciar instância sob demanda"""
        try:
            cmd = [
                "gcloud", "sql", "instances", "patch", instance_name,
                "--project", self.project_id,
                "--activation-policy=ALWAYS",
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Instância {instance_name} iniciada com sucesso")
                return True
            else:
                logger.error(f"❌ Erro ao iniciar {instance_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar {instance_name}: {e}")
            return False
    
    def optimize_backup_settings(self) -> Dict[str, Any]:
        """Otimizar configurações de backup"""
        backup_optimizations = {
            "optimized_instances": [],
            "savings": 0.0,
            "errors": []
        }
        
        for category, instances in self.instances.items():
            for instance in instances:
                try:
                    info = self.get_instance_info(instance)
                    if not info:
                        continue
                    
                    backup_config = info.get("settings", {}).get("backupConfiguration", {})
                    
                    # Se backup está habilitado, verificar se pode ser otimizado
                    if backup_config.get("enabled", False):
                        retention_days = backup_config.get("pointInTimeRecoveryEnabled", 7)
                        
                        # Se retenção > 7 dias e é instância de dev, reduzir
                        if retention_days > 7 and category == "development":
                            cmd = [
                                "gcloud", "sql", "instances", "patch", instance,
                                "--project", self.project_id,
                                "--backup-start-time=03:00",
                                "--retained-backups-count=7",
                                "--quiet"
                            ]
                            
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            if result.returncode == 0:
                                backup_optimizations["optimized_instances"].append({
                                    "name": instance,
                                    "old_retention": retention_days,
                                    "new_retention": 7,
                                    "optimized_at": datetime.now().isoformat()
                                })
                                
                                # Calcular economia (aproximada)
                                disk_size = info.get("settings", {}).get("dataDiskSizeGb", 10)
                                savings = (retention_days - 7) * disk_size * 0.08 / 30  # Por mês
                                backup_optimizations["savings"] += savings
                                
                                logger.info(f"✅ Backup otimizado para {instance} (economia: ${savings:.2f}/mês)")
                            else:
                                backup_optimizations["errors"].append({
                                    "instance": instance,
                                    "error": result.stderr
                                })
                
                except Exception as e:
                    backup_optimizations["errors"].append({
                        "instance": instance,
                        "error": str(e)
                    })
                    logger.error(f"❌ Erro ao otimizar backup de {instance}: {e}")
        
        return backup_optimizations
    
    def generate_cost_report(self) -> Dict[str, Any]:
        """Gerar relatório detalhado de custos"""
        instances_status = self.get_all_instances_status()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "project_id": self.project_id,
            "total_monthly_cost": 0.0,
            "instances": {},
            "recommendations": [],
            "potential_savings": 0.0
        }
        
        for instance, status in instances_status.items():
            monthly_cost = self.estimate_monthly_cost(instance)
            report["total_monthly_cost"] += monthly_cost
            
            report["instances"][instance] = {
                **status,
                "monthly_cost": monthly_cost,
                "optimization_status": "optimal" if status["state"] == "RUNNABLE" and status["category"] == "production" else "suboptimal"
            }
            
            # Gerar recomendações
            if status["category"] == "development" and status["state"] == "RUNNABLE":
                report["recommendations"].append({
                    "type": "cost_optimization",
                    "instance": instance,
                    "action": "stop_development_instance",
                    "potential_savings": monthly_cost,
                    "description": f"Parar instância de desenvolvimento {instance} pode economizar ${monthly_cost}/mês"
                })
                report["potential_savings"] += monthly_cost
        
        return report
    
    def auto_optimize(self) -> Dict[str, Any]:
        """Executar otimização automática completa"""
        logger.info("🚀 Iniciando otimização automática do Cloud SQL...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "development_optimization": self.optimize_development_instances(),
            "backup_optimization": self.optimize_backup_settings(),
            "cost_report": self.generate_cost_report()
        }
        
        total_savings = (
            results["development_optimization"]["savings"] +
            results["backup_optimization"]["savings"]
        )
        
        results["total_monthly_savings"] = round(total_savings, 2)
        
        logger.info(f"✅ Otimização concluída! Economia total: ${total_savings:.2f}/mês")
        
        return results

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cloud SQL Optimizer")
    parser.add_argument("--action", choices=["status", "optimize", "start", "report"], default="status")
    parser.add_argument("--instance", help="Nome da instância (para comando start)")
    parser.add_argument("--project", default="automatizar-452311", help="ID do projeto")
    
    args = parser.parse_args()
    
    optimizer = CloudSQLOptimizer(args.project)
    
    if args.action == "status":
        status = optimizer.get_all_instances_status()
        print("\n📊 Status das Instâncias Cloud SQL:")
        print("=" * 50)
        for instance, info in status.items():
            cost = optimizer.estimate_monthly_cost(instance)
            print(f"🔸 {instance}")
            print(f"   Categoria: {info['category']}")
            print(f"   Estado: {info['state']}")
            print(f"   Tier: {info['tier']}")
            print(f"   Custo: ${cost}/mês")
            print()
    
    elif args.action == "optimize":
        results = optimizer.auto_optimize()
        print("\n🚀 Resultados da Otimização:")
        print("=" * 50)
        print(f"💰 Economia total: ${results['total_monthly_savings']}/mês")
        print(f"🛑 Instâncias paradas: {len(results['development_optimization']['stopped_instances'])}")
        print(f"💾 Backups otimizados: {len(results['backup_optimization']['optimized_instances'])}")
    
    elif args.action == "start":
        if not args.instance:
            print("❌ Especifique a instância com --instance")
            return
        success = optimizer.start_instance_on_demand(args.instance)
        if success:
            print(f"✅ Instância {args.instance} iniciada com sucesso")
        else:
            print(f"❌ Erro ao iniciar instância {args.instance}")
    
    elif args.action == "report":
        report = optimizer.generate_cost_report()
        print("\n📋 Relatório de Custos:")
        print("=" * 50)
        print(f"💰 Custo total mensal: ${report['total_monthly_cost']}")
        print(f"💡 Economia potencial: ${report['potential_savings']}")
        print(f"📊 Total de instâncias: {len(report['instances'])}")
        
        if report['recommendations']:
            print("\n💡 Recomendações:")
            for rec in report['recommendations']:
                print(f"   • {rec['description']}")

if __name__ == "__main__":
    main()

