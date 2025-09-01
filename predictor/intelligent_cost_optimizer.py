import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class ProviderMetrics:
    name: str
    response_time: float
    cost_per_invocation: float
    success_rate: float
    availability: float
    region: str

class IntelligentCostOptimizer:
    def __init__(self):
        self.providers = {
            'aws': {
                'endpoint': 'https://krls9u88od.execute-api.us-east-1.amazonaws.com/prod',
                'base_cost': 0.0000002,  # $0.0000002 per invocation
                'gb_second_cost': 0.0000166667  # $0.0000166667 per GB-second
            },
            'azure': {
                'endpoint': 'https://fiso-sample-function-app-cmcks5.azurewebsites.net/api/httptriggerfunc',
                'base_cost': 0.0000002,  # Similar to AWS
                'execution_cost': 0.0000125  # Per GB-second
            },
            'gcp': {
                'endpoint': 'http://localhost:8080',
                'base_cost': 0.0000004,  # $0.0000004 per invocation
                'gb_second_cost': 0.0000025  # Per GB-second
            }
        }
        self.historical_data = []
        
    async def test_provider_performance(self, provider: str, endpoint: str) -> ProviderMetrics:
        """Test a single provider's performance and calculate metrics"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Health check
                async with session.get(f"{endpoint}/health" if provider == 'aws' else endpoint, 
                                     timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    success = response.status == 200
                    
                    return ProviderMetrics(
                        name=provider,
                        response_time=response_time,
                        cost_per_invocation=self.providers[provider]['base_cost'],
                        success_rate=100.0 if success else 0.0,
                        availability=100.0 if success else 0.0,
                        region=self._get_region(provider)
                    )
                    
        except Exception as e:
            print(f"Error testing {provider}: {e}")
            return ProviderMetrics(
                name=provider,
                response_time=9999.0,
                cost_per_invocation=self.providers[provider]['base_cost'],
                success_rate=0.0,
                availability=0.0,
                region=self._get_region(provider)
            )
    
    def _get_region(self, provider: str) -> str:
        regions = {
            'aws': 'us-east-1',
            'azure': 'East US',
            'gcp': 'us-central1 (emulator)'
        }
        return regions.get(provider, 'unknown')
    
    async def collect_real_time_metrics(self) -> List[ProviderMetrics]:
        """Collect performance metrics from all providers simultaneously"""
        tasks = []
        
        for provider, config in self.providers.items():
            task = self.test_provider_performance(provider, config['endpoint'])
            tasks.append(task)
        
        metrics = await asyncio.gather(*tasks)
        
        # Store historical data
        timestamp = datetime.now()
        for metric in metrics:
            self.historical_data.append({
                'timestamp': timestamp,
                'provider': metric.name,
                'response_time': metric.response_time,
                'cost': metric.cost_per_invocation,
                'success_rate': metric.success_rate,
                'availability': metric.availability
            })
        
        # Keep only last 100 data points per provider
        if len(self.historical_data) > 300:
            self.historical_data = self.historical_data[-300:]
        
        return metrics
    
    def calculate_cost_efficiency_score(self, metric: ProviderMetrics) -> float:
        """Calculate a cost efficiency score (higher is better)"""
        if metric.response_time == 0 or metric.success_rate == 0:
            return 0.0
        
        # Normalize metrics (lower response time and cost are better)
        response_time_score = max(0, (5000 - metric.response_time) / 5000)  # 5 seconds max
        cost_score = max(0, (0.001 - metric.cost_per_invocation) / 0.001)  # $0.001 max
        availability_score = metric.availability / 100.0
        
        # Weighted score
        efficiency_score = (
            response_time_score * 0.4 +  # 40% weight on performance
            cost_score * 0.3 +            # 30% weight on cost
            availability_score * 0.3      # 30% weight on availability
        )
        
        return efficiency_score * 100  # Convert to percentage
    
    def recommend_optimal_provider(self, metrics: List[ProviderMetrics]) -> Tuple[str, Dict]:
        """Recommend the best provider based on current metrics"""
        recommendations = []
        
        for metric in metrics:
            if metric.success_rate > 0:  # Only consider working providers
                efficiency_score = self.calculate_cost_efficiency_score(metric)
                recommendations.append({
                    'provider': metric.name,
                    'efficiency_score': efficiency_score,
                    'response_time': metric.response_time,
                    'cost': metric.cost_per_invocation,
                    'reasoning': self._generate_reasoning(metric, efficiency_score)
                })
        
        if not recommendations:
            return 'none', {'error': 'No providers available'}
        
        # Sort by efficiency score
        recommendations.sort(key=lambda x: x['efficiency_score'], reverse=True)
        best_provider = recommendations[0]
        
        return best_provider['provider'], {
            'recommendation': best_provider,
            'all_options': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_reasoning(self, metric: ProviderMetrics, efficiency_score: float) -> str:
        """Generate human-readable reasoning for the recommendation"""
        reasons = []
        
        if metric.response_time < 1000:
            reasons.append("excellent response time")
        elif metric.response_time < 2000:
            reasons.append("good response time")
        else:
            reasons.append("acceptable response time")
        
        if metric.cost_per_invocation < 0.0001:
            reasons.append("very cost-effective")
        elif metric.cost_per_invocation < 0.0005:
            reasons.append("cost-effective")
        else:
            reasons.append("higher cost but acceptable")
        
        if metric.availability >= 99:
            reasons.append("excellent availability")
        elif metric.availability >= 95:
            reasons.append("good availability")
        
        return f"Recommended due to {', '.join(reasons)} (efficiency score: {efficiency_score:.1f}%)"
    
    def get_cost_trend_analysis(self) -> Dict:
        """Analyze cost trends over time"""
        if len(self.historical_data) < 10:
            return {'error': 'Insufficient data for trend analysis'}
        
        df = pd.DataFrame(self.historical_data)
        
        # Calculate average metrics per provider
        provider_stats = df.groupby('provider').agg({
            'response_time': ['mean', 'std', 'min', 'max'],
            'cost': ['mean', 'std'],
            'success_rate': 'mean',
            'availability': 'mean'
        }).round(4)
        
        # Calculate cost savings potential
        costs = df.groupby('provider')['cost'].mean()
        cheapest_cost = costs.min()
        cost_savings = {}
        
        for provider in costs.index:
            if costs[provider] > cheapest_cost:
                savings = ((costs[provider] - cheapest_cost) / costs[provider]) * 100
                cost_savings[provider] = f"{savings:.1f}% potential savings"
        
        return {
            'provider_statistics': provider_stats.to_dict(),
            'cost_savings_opportunities': cost_savings,
            'data_points': len(self.historical_data),
            'analysis_period': f"Last {len(self.historical_data)} measurements"
        }

async def main():
    """Main function to demonstrate the cost optimizer"""
    optimizer = IntelligentCostOptimizer()
    
    print("🚀 FISO Intelligent Cost Optimizer")
    print("=" * 50)
    
    # Collect real-time metrics
    print("📊 Collecting real-time metrics from all providers...")
    metrics = await optimizer.collect_real_time_metrics()
    
    # Display current metrics
    print("\\nCurrent Provider Metrics:")
    print("-" * 30)
    for metric in metrics:
        print(f"{metric.name.upper():>6}: {metric.response_time:>6.0f}ms | "
              f"${metric.cost_per_invocation:.6f} | {metric.success_rate:>5.1f}% success")
    
    # Get recommendation
    print("\\n🎯 Intelligent Recommendation:")
    print("-" * 30)
    best_provider, recommendation_data = optimizer.recommend_optimal_provider(metrics)
    
    if 'error' not in recommendation_data:
        best = recommendation_data['recommendation']
        print(f"Recommended Provider: {best['provider'].upper()}")
        print(f"Efficiency Score: {best['efficiency_score']:.1f}%")
        print(f"Reasoning: {best['reasoning']}")
        
        print("\\n📈 All Provider Rankings:")
        for i, option in enumerate(recommendation_data['all_options'], 1):
            print(f"{i}. {option['provider'].upper()} - {option['efficiency_score']:.1f}% efficiency")
    else:
        print(f"Error: {recommendation_data['error']}")

if __name__ == "__main__":
    asyncio.run(main())
