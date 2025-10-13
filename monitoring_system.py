#!/usr/bin/env python3
"""
Sistema de Monitoramento Avançado - South Media IA
Monitora performance, custos e saúde dos serviços
"""

import os
import json
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import subprocess
import psutil

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SouthMediaMonitor:
    """Sistema de monitoramento abrangente"""
    
    def __init__(self, project_id: str = "automatizar-452311"):
        self.project_id = project_id
        self.services = {
            "cloud_run": {
                "name": "dashboard-builder",
                "region": "us-central1",
                "url": "https://mvp-dashboard-builder-609095880025.us-central1.run.app"
            },
            "cloud_sql": {
                "instances": ["south-media-postgres", "concurso-ai-db", "finaflow-postgres"]
            },
            "cloud_storage": {
                "bucket": "south-media-ia-database-452311"
            }
        }
        
        self.metrics = {
            "response_times": [],
            "error_rates": [],
            "cost_tracking": [],
            "resource_usage": []
        }
        
        # Configurações de alertas
        self.alert_thresholds = {
            "response_time_ms": 5000,  # 5 segundos
            "error_rate_percent": 5.0,  # 5%
            "memory_usage_percent": 80.0,  # 80%
            "cpu_usage_percent": 70.0,  # 70%
            "cost_daily_usd": 10.0,  # $10/dia
            "disk_usage_percent": 85.0  # 85%
        }
    
    def check_cloud_run_health(self) -> Dict[str, Any]:
        """Verificar saúde do Cloud Run"""
        health_data = {
            "service": "cloud_run",
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "response_time_ms": 0,
            "error": None,
            "metrics": {}
        }
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.services['cloud_run']['url']}/health", timeout=30)
            response_time = (time.time() - start_time) * 1000
            
            health_data.update({
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": round(response_time, 2),
                "status_code": response.status_code,
                "metrics": response.json() if response.status_code == 200 else {}
            })
            
            # Verificar se está dentro dos limites
            if response_time > self.alert_thresholds["response_time_ms"]:
                health_data["alert"] = f"Response time {response_time}ms exceeds threshold"
            
        except requests.exceptions.RequestException as e:
            health_data.update({
                "status": "error",
                "error": str(e),
                "alert": f"Service unreachable: {str(e)}"
            })
        
        return health_data
    
    def check_cloud_sql_status(self) -> Dict[str, Any]:
        """Verificar status das instâncias Cloud SQL"""
        sql_status = {
            "service": "cloud_sql",
            "timestamp": datetime.now().isoformat(),
            "instances": {},
            "total_cost_estimate": 0.0,
            "alerts": []
        }
        
        for instance in self.services["cloud_sql"]["instances"]:
            try:
                cmd = [
                    "gcloud", "sql", "instances", "describe", instance,
                    "--project", self.project_id,
                    "--format", "json"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    state = info.get("state", "UNKNOWN")
                    tier = info.get("settings", {}).get("tier", "unknown")
                    
                    # Estimar custo (simplificado)
                    cost_estimate = self._estimate_sql_cost(tier)
                    sql_status["total_cost_estimate"] += cost_estimate
                    
                    sql_status["instances"][instance] = {
                        "state": state,
                        "tier": tier,
                        "cost_estimate": cost_estimate,
                        "region": info.get("region", "unknown"),
                        "disk_size": info.get("settings", {}).get("dataDiskSizeGb", 0)
                    }
                    
                    # Verificar se há alertas
                    if state != "RUNNABLE" and tier != "db-f1-micro":
                        sql_status["alerts"].append(f"Instance {instance} is {state}")
                
            except Exception as e:
                sql_status["instances"][instance] = {
                    "state": "error",
                    "error": str(e)
                }
                sql_status["alerts"].append(f"Error checking {instance}: {str(e)}")
        
        return sql_status
    
    def check_cloud_storage_status(self) -> Dict[str, Any]:
        """Verificar status do Cloud Storage"""
        storage_status = {
            "service": "cloud_storage",
            "timestamp": datetime.now().isoformat(),
            "bucket": self.services["cloud_storage"]["bucket"],
            "objects_count": 0,
            "total_size_bytes": 0,
            "alerts": []
        }
        
        try:
            cmd = [
                "gsutil", "ls", "-l", f"gs://{self.services['cloud_storage']['bucket']}",
                "--project", self.project_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('TOTAL:'):
                        # Parse gsutil output
                        parts = line.split()
                        if len(parts) >= 3:
                            try:
                                size = int(parts[0])
                                storage_status["objects_count"] += 1
                                storage_status["total_size_bytes"] += size
                            except ValueError:
                                continue
                
                # Converter para MB
                storage_status["total_size_mb"] = round(storage_status["total_size_bytes"] / (1024 * 1024), 2)
                
                # Verificar se há muitos objetos (possível alerta)
                if storage_status["objects_count"] > 1000:
                    storage_status["alerts"].append(f"High object count: {storage_status['objects_count']}")
                
                # Verificar se o tamanho está muito grande
                if storage_status["total_size_mb"] > 1000:  # 1GB
                    storage_status["alerts"].append(f"Large storage usage: {storage_status['total_size_mb']}MB")
                
            else:
                storage_status["error"] = result.stderr
                storage_status["alerts"].append(f"Error accessing storage: {result.stderr}")
                
        except Exception as e:
            storage_status["error"] = str(e)
            storage_status["alerts"].append(f"Exception accessing storage: {str(e)}")
        
        return storage_status
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Verificar recursos do sistema local (se rodando em VM)"""
        system_status = {
            "service": "system_resources",
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
            "alerts": []
        }
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            system_status["cpu_percent"] = cpu_percent
            
            # Memória
            memory = psutil.virtual_memory()
            system_status["memory_percent"] = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            system_status["disk_percent"] = (disk.used / disk.total) * 100
            
            # Verificar alertas
            if cpu_percent > self.alert_thresholds["cpu_usage_percent"]:
                system_status["alerts"].append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > self.alert_thresholds["memory_usage_percent"]:
                system_status["alerts"].append(f"High memory usage: {memory.percent}%")
            
            if system_status["disk_percent"] > self.alert_thresholds["disk_usage_percent"]:
                system_status["alerts"].append(f"High disk usage: {system_status['disk_percent']}%")
                
        except Exception as e:
            system_status["error"] = str(e)
            system_status["alerts"].append(f"Error checking system resources: {str(e)}")
        
        return system_status
    
    def estimate_daily_costs(self) -> Dict[str, Any]:
        """Estimar custos diários do projeto"""
        cost_estimate = {
            "timestamp": datetime.now().isoformat(),
            "cloud_run_cost": 0.0,
            "cloud_sql_cost": 0.0,
            "cloud_storage_cost": 0.0,
            "total_daily_cost": 0.0,
            "total_monthly_cost": 0.0,
            "alerts": []
        }
        
        # Cloud Run (estimativa baseada em uso)
        # Assumindo 1 instância ativa, 512Mi RAM, uso médio
        cost_estimate["cloud_run_cost"] = 0.50  # ~$0.50/dia
        
        # Cloud SQL (baseado no status atual)
        sql_status = self.check_cloud_sql_status()
        cost_estimate["cloud_sql_cost"] = sql_status["total_cost_estimate"] / 30  # Converter mensal para diário
        
        # Cloud Storage (baseado no tamanho)
        storage_status = self.check_cloud_storage_status()
        storage_gb = storage_status.get("total_size_mb", 0) / 1024
        cost_estimate["cloud_storage_cost"] = storage_gb * 0.026  # $0.026/GB/mês -> diário
        
        # Total
        cost_estimate["total_daily_cost"] = (
            cost_estimate["cloud_run_cost"] +
            cost_estimate["cloud_sql_cost"] +
            cost_estimate["cloud_storage_cost"]
        )
        
        cost_estimate["total_monthly_cost"] = cost_estimate["total_daily_cost"] * 30
        
        # Verificar se excede limite
        if cost_estimate["total_daily_cost"] > self.alert_thresholds["cost_daily_usd"]:
            cost_estimate["alerts"].append(
                f"Daily cost ${cost_estimate['total_daily_cost']:.2f} exceeds threshold"
            )
        
        return cost_estimate
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Gerar relatório completo de saúde"""
        logger.info("🔍 Gerando relatório de saúde do sistema...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_id": self.project_id,
            "overall_status": "unknown",
            "services": {},
            "alerts": [],
            "recommendations": []
        }
        
        # Verificar cada serviço
        services_to_check = [
            ("cloud_run", self.check_cloud_run_health),
            ("cloud_sql", self.check_cloud_sql_status),
            ("cloud_storage", self.check_cloud_storage_status),
            ("system_resources", self.check_system_resources),
            ("costs", self.estimate_daily_costs)
        ]
        
        healthy_services = 0
        total_services = len(services_to_check)
        
        for service_name, check_function in services_to_check:
            try:
                service_data = check_function()
                report["services"][service_name] = service_data
                
                # Coletar alertas
                if "alerts" in service_data:
                    report["alerts"].extend(service_data["alerts"])
                
                # Determinar se o serviço está saudável
                if service_data.get("status") in ["healthy", "optimal"] or service_name in ["costs", "system_resources"]:
                    healthy_services += 1
                
            except Exception as e:
                logger.error(f"❌ Erro ao verificar {service_name}: {e}")
                report["alerts"].append(f"Error checking {service_name}: {str(e)}")
        
        # Determinar status geral
        health_percentage = (healthy_services / total_services) * 100
        if health_percentage >= 80:
            report["overall_status"] = "healthy"
        elif health_percentage >= 60:
            report["overall_status"] = "degraded"
        else:
            report["overall_status"] = "critical"
        
        # Gerar recomendações
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _estimate_sql_cost(self, tier: str) -> float:
        """Estimar custo mensal de uma instância SQL"""
        pricing = {
            "db-f1-micro": 7.67,
            "db-g1-small": 24.27,
            "db-n1-standard-1": 48.54,
            "db-n1-standard-2": 97.08,
            "db-n1-standard-4": 194.16
        }
        return pricing.get(tier, 7.67)
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Gerar recomendações baseadas no relatório"""
        recommendations = []
        
        # Verificar custos
        if "costs" in report["services"]:
            daily_cost = report["services"]["costs"]["total_daily_cost"]
            if daily_cost > 5.0:
                recommendations.append(f"Considerar otimizações de custo - gasto diário: ${daily_cost:.2f}")
        
        # Verificar Cloud SQL
        if "cloud_sql" in report["services"]:
            sql_data = report["services"]["cloud_sql"]
            for instance, info in sql_data.get("instances", {}).items():
                if info.get("state") != "RUNNABLE" and "dev" in instance.lower():
                    recommendations.append(f"Instância de desenvolvimento {instance} pode ser parada para economia")
        
        # Verificar Cloud Run
        if "cloud_run" in report["services"]:
            cloud_run_data = report["services"]["cloud_run"]
            if cloud_run_data.get("response_time_ms", 0) > 3000:
                recommendations.append("Cloud Run com tempo de resposta alto - considerar otimizações")
        
        # Verificar armazenamento
        if "cloud_storage" in report["services"]:
            storage_data = report["services"]["cloud_storage"]
            if storage_data.get("objects_count", 0) > 500:
                recommendations.append("Muitos objetos no Cloud Storage - considerar limpeza")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Salvar relatório em arquivo"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_report_{timestamp}.json"
        
        filepath = os.path.join("logs", filename)
        os.makedirs("logs", exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {filepath}")
        return filepath

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="South Media IA Monitoring System")
    parser.add_argument("--action", choices=["health", "costs", "alerts", "report"], default="health")
    parser.add_argument("--save", action="store_true", help="Salvar relatório em arquivo")
    parser.add_argument("--project", default="automatizar-452311", help="ID do projeto")
    
    args = parser.parse_args()
    
    monitor = SouthMediaMonitor(args.project)
    
    if args.action == "health":
        report = monitor.generate_health_report()
        
        print(f"\n🏥 Relatório de Saúde - {report['timestamp']}")
        print("=" * 60)
        print(f"Status Geral: {report['overall_status'].upper()}")
        print(f"Projeto: {report['project_id']}")
        
        if report['alerts']:
            print(f"\n🚨 Alertas ({len(report['alerts'])}):")
            for alert in report['alerts']:
                print(f"   • {alert}")
        
        if report['recommendations']:
            print(f"\n💡 Recomendações ({len(report['recommendations'])}):")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        if args.save:
            monitor.save_report(report)
    
    elif args.action == "costs":
        costs = monitor.estimate_daily_costs()
        print(f"\n💰 Estimativa de Custos - {costs['timestamp']}")
        print("=" * 50)
        print(f"Cloud Run: ${costs['cloud_run_cost']:.2f}/dia")
        print(f"Cloud SQL: ${costs['cloud_sql_cost']:.2f}/dia")
        print(f"Cloud Storage: ${costs['cloud_storage_cost']:.2f}/dia")
        print(f"Total Diário: ${costs['total_daily_cost']:.2f}")
        print(f"Total Mensal: ${costs['total_monthly_cost']:.2f}")
    
    elif args.action == "alerts":
        report = monitor.generate_health_report()
        if report['alerts']:
            print(f"\n🚨 Alertas Ativos ({len(report['alerts'])}):")
            for alert in report['alerts']:
                print(f"   • {alert}")
        else:
            print("\n✅ Nenhum alerta ativo")
    
    elif args.action == "report":
        report = monitor.generate_health_report()
        filename = monitor.save_report(report)
        print(f"\n📄 Relatório completo salvo em: {filename}")

if __name__ == "__main__":
    main()

