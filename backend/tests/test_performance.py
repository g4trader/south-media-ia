"""
Testes de Performance e Carga para sistema South Media IA
Inclui testes de throughput, latência, concorrência e estresse
"""

import pytest
import time
import asyncio
import aiohttp
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from datetime import datetime, timedelta
import psutil
import os

from src.main import app
from fastapi.testclient import TestClient


class TestPerformanceBasics:
    """Testes básicos de performance"""
    
    def test_api_response_time_basic(self, test_client: TestClient):
        """Testar tempo de resposta básico da API"""
        start_time = time.time()
        
        response = test_client.get("/health")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0, f"Resposta muito lenta: {response_time:.3f}s"
    
    def test_database_query_performance(self, test_client: TestClient, mock_auth_headers):
        """Testar performance de queries do banco de dados"""
        # Simular múltiplas requisições para testar cache e performance
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            
            with patch('src.services.company_service.CompanyService.list_companies') as mock_list:
                mock_list.return_value = []
                
                response = test_client.get("/api/companies/", headers=mock_auth_headers)
            
            end_time = time.time()
            response_times.append(end_time - start_time)
            
            assert response.status_code == 200
        
        # Calcular estatísticas
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # Verificar se a performance está dentro dos limites aceitáveis
        assert avg_response_time < 0.5, f"Tempo médio de resposta muito alto: {avg_response_time:.3f}s"
        assert max_response_time < 1.0, f"Tempo máximo de resposta muito alto: {max_response_time:.3f}s"
        assert min_response_time < 0.1, f"Tempo mínimo de resposta muito alto: {min_response_time:.3f}s"
    
    def test_memory_usage_basic(self):
        """Testar uso básico de memória"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simular algumas operações
        test_data = []
        for i in range(1000):
            test_data.append({
                "id": f"test-{i}",
                "name": f"Test Item {i}",
                "data": "x" * 100
            })
        
        memory_after_operations = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after_operations - initial_memory
        
        # Verificar se o aumento de memória é razoável
        assert memory_increase < 100, f"Aumento de memória muito alto: {memory_increase:.2f}MB"
        
        # Limpar dados de teste
        del test_data
        
        # Verificar se a memória foi liberada
        memory_after_cleanup = process.memory_info().rss / 1024 / 1024  # MB
        memory_after_cleanup_increase = memory_after_cleanup - initial_memory
        
        assert memory_after_cleanup_increase < 50, f"Memória não foi liberada adequadamente: {memory_after_cleanup_increase:.2f}MB"


class TestConcurrency:
    """Testes de concorrência e simultaneidade"""
    
    def test_concurrent_api_requests(self, test_client: TestClient):
        """Testar múltiplas requisições simultâneas"""
        num_requests = 50
        response_times = []
        successful_requests = 0
        
        def make_request():
            start_time = time.time()
            try:
                response = test_client.get("/health")
                end_time = time.time()
                if response.status_code == 200:
                    return end_time - start_time, True
                else:
                    return end_time - start_time, False
            except Exception:
                return time.time() - start_time, False
        
        # Executar requisições em paralelo
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                response_time, success = future.result()
                response_times.append(response_time)
                if success:
                    successful_requests += 1
        
        # Verificar resultados
        assert successful_requests >= num_requests * 0.95, f"Muitas falhas: {successful_requests}/{num_requests}"
        
        # Verificar performance
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 2.0, f"Tempo médio de resposta muito alto: {avg_response_time:.3f}s"
        assert max_response_time < 5.0, f"Tempo máximo de resposta muito alto: {max_response_time:.3f}s"
    
    def test_concurrent_database_operations(self, test_client: TestClient, mock_auth_headers):
        """Testar operações concorrentes no banco de dados"""
        num_operations = 30
        response_times = []
        successful_operations = 0
        
        def make_database_request():
            start_time = time.time()
            try:
                with patch('src.services.company_service.CompanyService.list_companies') as mock_list:
                    mock_list.return_value = []
                    
                    response = test_client.get("/api/companies/", headers=mock_auth_headers)
                
                end_time = time.time()
                if response.status_code == 200:
                    return end_time - start_time, True
                else:
                    return end_time - start_time, False
            except Exception:
                return time.time() - start_time, False
        
        # Executar operações em paralelo
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_database_request) for _ in range(num_operations)]
            
            for future in as_completed(futures):
                response_time, success = future.result()
                response_times.append(response_time)
                if success:
                    successful_operations += 1
        
        # Verificar resultados
        assert successful_operations >= num_operations * 0.9, f"Muitas falhas: {successful_operations}/{num_operations}"
        
        # Verificar performance
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 1.0, f"Tempo médio de resposta muito alto: {avg_response_time:.3f}s"
        assert max_response_time < 3.0, f"Tempo máximo de resposta muito alto: {max_response_time:.3f}s"


class TestLoadTesting:
    """Testes de carga e estresse"""
    
    def test_high_load_scenario(self, test_client: TestClient):
        """Testar cenário de alta carga"""
        num_requests = 200
        response_times = []
        successful_requests = 0
        error_count = 0
        
        def make_request():
            start_time = time.time()
            try:
                response = test_client.get("/health")
                end_time = time.time()
                if response.status_code == 200:
                    return end_time - start_time, True, None
                else:
                    return end_time - start_time, False, f"HTTP {response.status_code}"
            except Exception as e:
                return time.time() - start_time, False, str(e)
        
        # Executar requisições em paralelo com alta concorrência
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                response_time, success, error = future.result()
                response_times.append(response_time)
                if success:
                    successful_requests += 1
                else:
                    error_count += 1
        
        # Verificar resultados
        success_rate = successful_requests / num_requests
        assert success_rate >= 0.8, f"Taxa de sucesso muito baixa: {success_rate:.2%}"
        
        # Verificar performance sob carga
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        assert avg_response_time < 3.0, f"Tempo médio de resposta muito alto sob carga: {avg_response_time:.3f}s"
        assert max_response_time < 10.0, f"Tempo máximo de resposta muito alto sob carga: {max_response_time:.3f}s"
        assert p95_response_time < 5.0, f"P95 de resposta muito alto: {p95_response_time:.3f}s"
        
        # Verificar se não há muitas falhas
        assert error_count < num_requests * 0.2, f"Muitas falhas sob carga: {error_count}/{num_requests}"
    
    def test_memory_leak_under_load(self, test_client: TestClient):
        """Testar vazamento de memória sob carga"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Executar operações repetitivas
        for cycle in range(5):
            response_times = []
            
            # Ciclo de 50 requisições
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(test_client.get, "/health") for _ in range(50)]
                
                for future in as_completed(futures):
                    start_time = time.time()
                    response = future.result()
                    end_time = time.time()
                    
                    response_times.append(end_time - start_time)
                    assert response.status_code == 200
            
            # Verificar memória após cada ciclo
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            # Verificar se não há vazamento significativo
            assert memory_increase < 200, f"Possível vazamento de memória no ciclo {cycle}: {memory_increase:.2f}MB"
            
            # Pequena pausa entre ciclos
            time.sleep(0.1)
        
        # Verificar memória final
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_memory_increase = final_memory - initial_memory
        
        assert total_memory_increase < 100, f"Vazamento de memória significativo: {total_memory_increase:.2f}MB"


class TestScalability:
    """Testes de escalabilidade"""
    
    def test_scalability_with_data_volume(self, test_client: TestClient, mock_auth_headers):
        """Testar escalabilidade com diferentes volumes de dados"""
        data_sizes = [10, 50, 100, 200]
        response_times = {}
        
        for size in data_sizes:
            # Simular diferentes tamanhos de resposta
            mock_data = [{"id": f"item-{i}", "name": f"Item {i}"} for i in range(size)]
            
            start_time = time.time()
            
            with patch('src.services.company_service.CompanyService.list_companies') as mock_list:
                mock_list.return_value = mock_data
                
                response = test_client.get("/api/companies/", headers=mock_auth_headers)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            response_times[size] = response_time
            assert response.status_code == 200
        
        # Verificar se o tempo de resposta escala linearmente ou melhor
        for i in range(1, len(data_sizes)):
            current_size = data_sizes[i]
            previous_size = data_sizes[i-1]
            
            current_time = response_times[current_size]
            previous_time = response_times[previous_size]
            
            # O tempo não deve aumentar mais que proporcionalmente ao tamanho dos dados
            expected_ratio = current_size / previous_size
            actual_ratio = current_time / previous_time
            
            assert actual_ratio <= expected_ratio * 1.5, f"Escalabilidade ruim: {current_size} items ({current_time:.3f}s) vs {previous_size} items ({previous_time:.3f}s)"
    
    def test_concurrent_users_scalability(self, test_client: TestClient):
        """Testar escalabilidade com diferentes números de usuários concorrentes"""
        user_counts = [5, 10, 20, 30]
        response_times = {}
        
        for user_count in user_counts:
            response_times_cycle = []
            
            # Simular usuários concorrentes
            with ThreadPoolExecutor(max_workers=user_count) as executor:
                futures = [executor.submit(test_client.get, "/health") for _ in range(user_count * 2)]
                
                for future in as_completed(futures):
                    start_time = time.time()
                    response = future.result()
                    end_time = time.time()
                    
                    response_times_cycle.append(end_time - start_time)
                    assert response.status_code == 200
            
            # Calcular tempo médio para este número de usuários
            avg_time = statistics.mean(response_times_cycle)
            response_times[user_count] = avg_time
        
        # Verificar se a performance não degrada drasticamente
        for i in range(1, len(user_counts)):
            current_users = user_counts[i]
            previous_users = user_counts[i-1]
            
            current_time = response_times[current_users]
            previous_time = response_times[previous_users]
            
            # O tempo não deve aumentar mais que proporcionalmente ao número de usuários
            expected_ratio = current_users / previous_users
            actual_ratio = current_time / previous_time
            
            assert actual_ratio <= expected_ratio * 2.0, f"Escalabilidade ruim com usuários: {current_users} users ({current_time:.3f}s) vs {previous_users} users ({previous_time:.3f}s)"


class TestResourceUsage:
    """Testes de uso de recursos"""
    
    def test_cpu_usage_under_load(self, test_client: TestClient):
        """Testar uso de CPU sob carga"""
        process = psutil.Process(os.getpid())
        
        # Medir CPU em idle
        cpu_idle = process.cpu_percent(interval=1)
        
        # Executar carga
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(test_client.get, "/health") for _ in range(100)]
            
            # Medir CPU durante a carga
            cpu_under_load = process.cpu_percent(interval=1)
            
            # Aguardar conclusão
            for future in as_completed(futures):
                response = future.result()
                assert response.status_code == 200
        
        # Verificar se o uso de CPU é razoável
        assert cpu_under_load < 80, f"Uso de CPU muito alto sob carga: {cpu_under_load:.1f}%"
        
        # Verificar se o CPU volta ao normal
        time.sleep(2)
        cpu_after_load = process.cpu_percent(interval=1)
        
        assert cpu_after_load < cpu_idle * 2, f"CPU não voltou ao normal após carga: {cpu_after_load:.1f}% vs {cpu_idle:.1f}%"
    
    def test_disk_io_under_load(self, test_client: TestClient):
        """Testar I/O de disco sob carga"""
        # Este teste seria mais relevante com um banco de dados real
        # Por enquanto, vamos simular operações de arquivo
        
        import tempfile
        import json
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # Medir I/O antes
            disk_io_before = psutil.disk_io_counters()
            
            # Executar operações de I/O
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                
                for i in range(50):
                    future = executor.submit(self._write_test_data, temp_file, i)
                    futures.append(future)
                
                # Aguardar conclusão
                for future in as_completed(futures):
                    future.result()
            
            # Medir I/O depois
            disk_io_after = psutil.disk_io_counters()
            
            # Calcular diferença
            read_bytes = disk_io_after.read_bytes - disk_io_before.read_bytes
            write_bytes = disk_io_after.write_bytes - disk_io_before.write_bytes
            
            # Verificar se as operações de I/O foram realizadas
            assert write_bytes > 0, "Nenhuma operação de escrita detectada"
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def _write_test_data(self, filename: str, index: int):
        """Escrever dados de teste no arquivo"""
        data = {
            "index": index,
            "timestamp": datetime.utcnow().isoformat(),
            "data": "x" * 100
        }
        
        with open(filename, 'a') as f:
            json.dump(data, f)
            f.write('\n')


class TestPerformanceMonitoring:
    """Testes de monitoramento de performance"""
    
    def test_response_time_distribution(self, test_client: TestClient):
        """Testar distribuição dos tempos de resposta"""
        num_requests = 100
        response_times = []
        
        # Coletar tempos de resposta
        for _ in range(num_requests):
            start_time = time.time()
            response = test_client.get("/health")
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            assert response.status_code == 200
        
        # Calcular estatísticas
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        std_dev = statistics.stdev(response_times)
        
        # Calcular percentis
        p50 = statistics.quantiles(response_times, n=2)[0]  # 50th percentile
        p90 = statistics.quantiles(response_times, n=10)[8]  # 90th percentile
        p95 = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        
        # Verificar se as estatísticas fazem sentido
        assert avg_time > 0, "Tempo médio deve ser positivo"
        assert median_time > 0, "Mediana deve ser positiva"
        assert std_dev >= 0, "Desvio padrão deve ser não-negativo"
        
        # Verificar se os percentis estão em ordem
        assert p50 <= p90 <= p95 <= p99, "Percentis devem estar em ordem crescente"
        
        # Verificar se a distribuição é razoável
        assert p95 < avg_time * 3, "P95 muito alto em relação à média"
        assert p99 < avg_time * 5, "P99 muito alto em relação à média"
    
    def test_error_rate_monitoring(self, test_client: TestClient):
        """Testar monitoramento de taxa de erro"""
        num_requests = 200
        successful_requests = 0
        error_requests = 0
        response_times = []
        
        # Fazer requisições (algumas válidas, algumas inválidas)
        for i in range(num_requests):
            start_time = time.time()
            
            try:
                if i % 10 == 0:  # A cada 10 requisições, fazer uma inválida
                    response = test_client.get("/invalid-endpoint")
                    if response.status_code == 404:
                        successful_requests += 1  # 404 é esperado para endpoint inválido
                    else:
                        error_requests += 1
                else:
                    response = test_client.get("/health")
                    if response.status_code == 200:
                        successful_requests += 1
                    else:
                        error_requests += 1
                
                end_time = time.time()
                response_times.append(end_time - start_time)
                
            except Exception:
                error_requests += 1
                response_times.append(0)
        
        # Calcular taxas
        total_requests = successful_requests + error_requests
        success_rate = successful_requests / total_requests
        error_rate = error_requests / total_requests
        
        # Verificar se as taxas fazem sentido
        assert success_rate > 0.8, f"Taxa de sucesso muito baixa: {success_rate:.2%}"
        assert error_rate < 0.2, f"Taxa de erro muito alta: {error_rate:.2%}"
        assert abs(success_rate + error_rate - 1.0) < 0.01, "Taxas devem somar 1.0"
        
        # Verificar se há dados suficientes para análise
        assert len(response_times) > 0, "Nenhum tempo de resposta coletado"
        
        # Calcular estatísticas dos tempos de resposta válidos
        valid_response_times = [t for t in response_times if t > 0]
        if valid_response_times:
            avg_valid_time = statistics.mean(valid_response_times)
            assert avg_valid_time < 1.0, f"Tempo médio de resposta válida muito alto: {avg_valid_time:.3f}s"


class TestPerformanceRegression:
    """Testes de regressão de performance"""
    
    def test_performance_baseline(self, test_client: TestClient):
        """Estabelecer baseline de performance para comparação futura"""
        num_requests = 50
        response_times = []
        
        # Coletar dados de baseline
        for _ in range(num_requests):
            start_time = time.time()
            response = test_client.get("/health")
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            assert response.status_code == 200
        
        # Calcular métricas de baseline
        baseline_metrics = {
            "avg_response_time": statistics.mean(response_times),
            "p95_response_time": statistics.quantiles(response_times, n=20)[18],
            "max_response_time": max(response_times),
            "min_response_time": min(response_times),
            "std_dev": statistics.stdev(response_times),
            "timestamp": datetime.utcnow().isoformat(),
            "num_requests": num_requests
        }
        
        # Salvar baseline (em um sistema real, isso seria persistido)
        # Por enquanto, vamos apenas verificar se as métricas são razoáveis
        
        assert baseline_metrics["avg_response_time"] < 1.0, "Baseline: tempo médio muito alto"
        assert baseline_metrics["p95_response_time"] < 2.0, "Baseline: P95 muito alto"
        assert baseline_metrics["max_response_time"] < 3.0, "Baseline: tempo máximo muito alto"
        
        # Retornar métricas para comparação futura
        return baseline_metrics
    
    def test_performance_consistency(self, test_client: TestClient):
        """Testar consistência da performance ao longo do tempo"""
        num_cycles = 5
        cycle_metrics = []
        
        for cycle in range(num_cycles):
            # Fazer um ciclo de testes
            response_times = []
            
            for _ in range(20):
                start_time = time.time()
                response = test_client.get("/health")
                end_time = time.time()
                
                response_times.append(end_time - start_time)
                assert response.status_code == 200
            
            # Calcular métricas do ciclo
            cycle_avg = statistics.mean(response_times)
            cycle_metrics.append(cycle_avg)
            
            # Pequena pausa entre ciclos
            time.sleep(0.5)
        
        # Verificar consistência entre ciclos
        overall_avg = statistics.mean(cycle_metrics)
        overall_std = statistics.stdev(cycle_metrics)
        
        # O coeficiente de variação deve ser baixo (performance consistente)
        cv = overall_std / overall_avg if overall_avg > 0 else 0
        
        assert cv < 0.3, f"Performance muito inconsistente entre ciclos: CV = {cv:.3f}"
        
        # Verificar se não há degradação significativa
        for i, metric in enumerate(cycle_metrics):
            assert metric < overall_avg * 1.5, f"Degradação significativa no ciclo {i}: {metric:.3f}s vs {overall_avg:.3f}s"


# Configurações de teste de performance
@pytest.mark.performance
class TestPerformanceConfig:
    """Configurações e utilitários para testes de performance"""
    
    @pytest.fixture(scope="class")
    def performance_config(self):
        """Configuração para testes de performance"""
        return {
            "max_response_time": 2.0,  # segundos
            "max_avg_response_time": 1.0,  # segundos
            "max_memory_usage": 500,  # MB
            "max_cpu_usage": 80,  # percentual
            "min_success_rate": 0.95,  # 95%
            "max_concurrent_users": 50,
            "load_test_duration": 60,  # segundos
            "warmup_requests": 10
        }
    
    def test_performance_thresholds(self, test_client: TestClient, performance_config):
        """Testar se a aplicação atende aos thresholds de performance"""
        # Fazer requisições de aquecimento
        for _ in range(performance_config["warmup_requests"]):
            response = test_client.get("/health")
            assert response.status_code == 200
        
        # Teste de performance principal
        num_requests = 100
        response_times = []
        successful_requests = 0
        
        start_time = time.time()
        
        for _ in range(num_requests):
            request_start = time.time()
            
            try:
                response = test_client.get("/health")
                request_end = time.time()
                
                if response.status_code == 200:
                    response_times.append(request_end - request_start)
                    successful_requests += 1
                else:
                    response_times.append(request_end - request_start)
                    
            except Exception:
                response_times.append(time.time() - request_start)
        
        end_time = time.time()
        
        # Calcular métricas
        total_time = end_time - start_time
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        success_rate = successful_requests / num_requests
        throughput = num_requests / total_time
        
        # Verificar thresholds
        assert avg_response_time <= performance_config["max_avg_response_time"], \
            f"Tempo médio de resposta excedeu threshold: {avg_response_time:.3f}s > {performance_config['max_avg_response_time']}s"
        
        assert max_response_time <= performance_config["max_response_time"], \
            f"Tempo máximo de resposta excedeu threshold: {max_response_time:.3f}s > {performance_config['max_response_time']}s"
        
        assert success_rate >= performance_config["min_success_rate"], \
            f"Taxa de sucesso abaixo do threshold: {success_rate:.2%} < {performance_config['min_success_rate']:.2%}"
        
        # Verificar se o throughput é razoável
        assert throughput >= 10, f"Throughput muito baixo: {throughput:.1f} req/s"
        
        # Verificar uso de recursos
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent(interval=1)
        
        assert memory_usage <= performance_config["max_memory_usage"], \
            f"Uso de memória excedeu threshold: {memory_usage:.1f}MB > {performance_config['max_memory_usage']}MB"
        
        assert cpu_usage <= performance_config["max_cpu_usage"], \
            f"Uso de CPU excedeu threshold: {cpu_usage:.1f}% > {performance_config['max_cpu_usage']}%"



