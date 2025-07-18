import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class InsightsService:
    def __init__(self):
        self.benchmarks = {
            'ctr': {
                'excellent': 0.25,
                'good': 0.15,
                'average': 0.10,
                'poor': 0.05
            },
            'cpm': {
                'excellent': 2.0,
                'good': 3.0,
                'average': 4.0,
                'poor': 6.0
            },
            'cpc': {
                'excellent': 1.5,
                'good': 2.5,
                'average': 3.5,
                'poor': 5.0
            }
        }
    
    def analyze_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall campaign performance and generate insights"""
        campaign = campaign_data['campaign']
        strategies = campaign_data['strategies']
        device_breakdown = campaign_data['device_breakdown']
        
        insights = {
            'overall_performance': self._analyze_overall_performance(campaign),
            'strategy_insights': self._analyze_strategies(strategies),
            'device_insights': self._analyze_device_performance(device_breakdown),
            'optimization_recommendations': self._generate_recommendations(campaign, strategies),
            'performance_alerts': self._generate_alerts(campaign, strategies),
            'trend_analysis': self._analyze_trends(campaign, strategies),
            'benchmark_comparison': self._compare_with_benchmarks(campaign)
        }
        
        return insights
    
    def _analyze_overall_performance(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall campaign performance"""
        budget_efficiency = (campaign['impressions_delivered'] / campaign['impressions_contracted']) / (campaign['budget_used'] / campaign['budget_contracted'])
        
        performance_score = self._calculate_performance_score(campaign)
        
        return {
            'budget_efficiency': round(budget_efficiency, 2),
            'performance_score': performance_score,
            'impressions_overdelivery': campaign['impressions_delivered'] > campaign['impressions_contracted'],
            'budget_utilization': round((campaign['budget_used'] / campaign['budget_contracted']) * 100, 1),
            'cost_efficiency': 'excellent' if campaign['cpc'] < 2.0 else 'good' if campaign['cpc'] < 3.0 else 'average'
        }
    
    def _analyze_strategies(self, strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze individual strategy performance"""
        if not strategies:
            return {}
        
        # Calculate performance metrics for each strategy
        strategy_performance = []
        for strategy in strategies:
            efficiency_score = (strategy['clicks'] / strategy['impressions']) / (strategy['budget_used'] / 10000)  # Normalized score
            strategy_performance.append({
                'name': strategy['strategy_name'],
                'efficiency_score': round(efficiency_score * 1000, 2),  # Scale for readability
                'ctr': strategy['ctr'],
                'cpc': strategy['cpc'],
                'volume': strategy['impressions']
            })
        
        # Sort by efficiency score
        strategy_performance.sort(key=lambda x: x['efficiency_score'], reverse=True)
        
        # Find best and worst performers
        best_performer = strategy_performance[0]
        worst_performer = strategy_performance[-1]
        
        # Calculate averages
        avg_ctr = statistics.mean([s['ctr'] for s in strategies])
        avg_cpc = statistics.mean([s['cpc'] for s in strategies])
        
        return {
            'best_performer': best_performer,
            'worst_performer': worst_performer,
            'average_ctr': round(avg_ctr, 3),
            'average_cpc': round(avg_cpc, 2),
            'strategy_rankings': strategy_performance,
            'performance_variance': round(statistics.stdev([s['efficiency_score'] for s in strategy_performance]), 2)
        }
    
    def _analyze_device_performance(self, device_breakdown: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze device performance distribution"""
        if not device_breakdown:
            return {}
        
        total_impressions = sum([d['impressions'] for d in device_breakdown])
        
        device_insights = []
        for device in device_breakdown:
            device_insights.append({
                'device': device['device_type'],
                'share': device['percentage'],
                'impressions': device['impressions'],
                'performance': 'high' if device['percentage'] > 50 else 'medium' if device['percentage'] > 20 else 'low'
            })
        
        # Sort by performance
        device_insights.sort(key=lambda x: x['share'], reverse=True)
        
        return {
            'dominant_device': device_insights[0]['device'],
            'device_distribution': device_insights,
            'mobile_dominance': device_insights[0]['device'] == 'Mobile' and device_insights[0]['share'] > 70,
            'diversification_score': len([d for d in device_insights if d['share'] > 10])
        }
    
    def _generate_recommendations(self, campaign: Dict[str, Any], strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Budget optimization
        if campaign['budget_used'] / campaign['budget_contracted'] > 0.9:
            if campaign['impressions_delivered'] / campaign['impressions_contracted'] > 1.05:
                recommendations.append({
                    'type': 'budget',
                    'priority': 'high',
                    'title': 'Otimização de Orçamento',
                    'description': 'Campanha está superentregando impressões. Considere renegociar orçamento ou ajustar targeting.',
                    'impact': 'cost_reduction'
                })
        
        # Strategy optimization
        if strategies:
            high_cpc_strategies = [s for s in strategies if s['cpc'] > 3.0]
            if high_cpc_strategies:
                recommendations.append({
                    'type': 'strategy',
                    'priority': 'medium',
                    'title': 'Otimização de CPC',
                    'description': f'{len(high_cpc_strategies)} estratégias com CPC alto. Revisar targeting e criativos.',
                    'impact': 'performance_improvement'
                })
            
            low_ctr_strategies = [s for s in strategies if s['ctr'] < 0.1]
            if low_ctr_strategies:
                recommendations.append({
                    'type': 'creative',
                    'priority': 'high',
                    'title': 'Melhoria de CTR',
                    'description': f'{len(low_ctr_strategies)} estratégias com CTR baixo. Testar novos criativos.',
                    'impact': 'engagement_improvement'
                })
        
        # Performance recommendations
        if campaign['ctr'] < 0.12:
            recommendations.append({
                'type': 'creative',
                'priority': 'high',
                'title': 'Renovação de Criativos',
                'description': 'CTR geral abaixo da média. Implementar testes A/B com novos formatos.',
                'impact': 'engagement_improvement'
            })
        
        return recommendations
    
    def _generate_alerts(self, campaign: Dict[str, Any], strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate performance alerts"""
        alerts = []
        
        # Budget alerts
        budget_usage = (campaign['budget_used'] / campaign['budget_contracted']) * 100
        if budget_usage > 95:
            alerts.append({
                'type': 'warning',
                'category': 'budget',
                'message': 'Orçamento quase esgotado (>95%)',
                'severity': 'high'
            })
        elif budget_usage > 80:
            alerts.append({
                'type': 'info',
                'category': 'budget',
                'message': 'Orçamento em 80% de utilização',
                'severity': 'medium'
            })
        
        # Performance alerts
        if campaign['ctr'] < 0.08:
            alerts.append({
                'type': 'warning',
                'category': 'performance',
                'message': 'CTR abaixo do esperado (<0.08%)',
                'severity': 'high'
            })
        
        if campaign['cpc'] > 4.0:
            alerts.append({
                'type': 'warning',
                'category': 'cost',
                'message': 'CPC acima da média do mercado (>R$4.00)',
                'severity': 'medium'
            })
        
        # Strategy alerts
        if strategies:
            underperforming = [s for s in strategies if s['ctr'] < 0.05]
            if underperforming:
                alerts.append({
                    'type': 'warning',
                    'category': 'strategy',
                    'message': f'{len(underperforming)} estratégias com performance muito baixa',
                    'severity': 'high'
                })
        
        return alerts
    
    def _analyze_trends(self, campaign: Dict[str, Any], strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends"""
        # Mock trend data - in production, this would analyze historical data
        trend_data = {
            'cpc_trend': 'decreasing',  # CPC is improving over time
            'ctr_trend': 'stable',      # CTR is stable
            'volume_trend': 'increasing', # Impression volume is growing
            'efficiency_trend': 'improving' # Overall efficiency is improving
        }
        
        # Generate trend insights
        trend_insights = []
        
        if trend_data['cpc_trend'] == 'decreasing':
            trend_insights.append({
                'metric': 'CPC',
                'direction': 'positive',
                'description': 'Custo por clique está diminuindo ao longo da campanha'
            })
        
        if trend_data['volume_trend'] == 'increasing':
            trend_insights.append({
                'metric': 'Volume',
                'direction': 'positive',
                'description': 'Volume de impressões está crescendo consistentemente'
            })
        
        return {
            'trends': trend_data,
            'insights': trend_insights,
            'forecast': self._generate_forecast(campaign)
        }
    
    def _generate_forecast(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance forecast"""
        # Simple forecast based on current performance
        days_remaining = 7  # Mock - calculate based on campaign end date
        current_daily_spend = campaign['budget_used'] / 31  # Assuming 31-day campaign
        
        projected_total_spend = current_daily_spend * (31 + days_remaining)
        projected_impressions = (campaign['impressions_delivered'] / campaign['budget_used']) * projected_total_spend
        
        return {
            'projected_total_spend': round(projected_total_spend, 2),
            'projected_impressions': int(projected_impressions),
            'budget_pace': 'on_track' if projected_total_spend <= campaign['budget_contracted'] * 1.05 else 'over_budget',
            'days_remaining': days_remaining
        }
    
    def _compare_with_benchmarks(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Compare campaign performance with industry benchmarks"""
        ctr_benchmark = self._get_benchmark_level(campaign['ctr'], 'ctr')
        cpm_benchmark = self._get_benchmark_level(campaign['cpm'], 'cpm')
        cpc_benchmark = self._get_benchmark_level(campaign['cpc'], 'cpc')
        
        return {
            'ctr_performance': ctr_benchmark,
            'cpm_performance': cpm_benchmark,
            'cpc_performance': cpc_benchmark,
            'overall_benchmark': self._calculate_overall_benchmark(ctr_benchmark, cpm_benchmark, cpc_benchmark)
        }
    
    def _get_benchmark_level(self, value: float, metric: str) -> str:
        """Get benchmark performance level for a metric"""
        benchmarks = self.benchmarks[metric]
        
        if metric in ['ctr']:  # Higher is better
            if value >= benchmarks['excellent']:
                return 'excellent'
            elif value >= benchmarks['good']:
                return 'good'
            elif value >= benchmarks['average']:
                return 'average'
            else:
                return 'poor'
        else:  # Lower is better (cpm, cpc)
            if value <= benchmarks['excellent']:
                return 'excellent'
            elif value <= benchmarks['good']:
                return 'good'
            elif value <= benchmarks['average']:
                return 'average'
            else:
                return 'poor'
    
    def _calculate_overall_benchmark(self, ctr: str, cpm: str, cpc: str) -> str:
        """Calculate overall benchmark performance"""
        scores = {'excellent': 4, 'good': 3, 'average': 2, 'poor': 1}
        
        total_score = scores[ctr] + scores[cpm] + scores[cpc]
        avg_score = total_score / 3
        
        if avg_score >= 3.5:
            return 'excellent'
        elif avg_score >= 2.5:
            return 'good'
        elif avg_score >= 1.5:
            return 'average'
        else:
            return 'poor'
    
    def _calculate_performance_score(self, campaign: Dict[str, Any]) -> int:
        """Calculate overall performance score (0-100)"""
        # Weighted scoring system
        ctr_score = min(campaign['ctr'] / 0.2 * 30, 30)  # Max 30 points
        cpc_score = max(30 - (campaign['cpc'] - 1.5) / 0.5 * 10, 0)  # Max 30 points
        budget_score = min((campaign['impressions_delivered'] / campaign['impressions_contracted']) * 20, 40)  # Max 40 points
        
        total_score = ctr_score + cpc_score + budget_score
        return min(int(total_score), 100)

