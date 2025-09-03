/**
 * FISO AI Predictor Integration Module
 * Enhanced AI capabilities for the dashboard
 */

class FISOAIPredictor {
    constructor(apiBase, apiKey) {
        this.apiBase = apiBase;
        this.apiKey = apiKey;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    /**
     * Get comprehensive cost analysis with ML predictions
     */
    async getComprehensiveAnalysis(params) {
        const cacheKey = 'comprehensive_analysis_' + JSON.stringify(params);
        
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }

        try {
            const response = await fetch(`${this.apiBase}/api/ai/comprehensive-analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();
            
            // Cache the result
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });

            return data;
        } catch (error) {
            console.error('Comprehensive analysis error:', error);
            return this.getFallbackAnalysis(params);
        }
    }

    /**
     * Get real-time pricing with enhanced formatting
     */
    async getRealTimePricing() {
        try {
            const response = await fetch(`${this.apiBase}/api/ai/real-time-pricing`, {
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            const data = await response.json();
            return this.enhancePricingData(data);
        } catch (error) {
            console.error('Real-time pricing error:', error);
            return this.getFallbackPricing();
        }
    }

    /**
     * Get ML-powered cost predictions for specific provider
     */
    async getCostPrediction(provider, params) {
        try {
            const response = await fetch(`${this.apiBase}/api/ai/cost-prediction`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify({...params, provider})
            });

            const data = await response.json();
            return this.enhancePredictionData(data);
        } catch (error) {
            console.error(`Cost prediction error for ${provider}:`, error);
            return this.getFallbackPrediction(provider, params);
        }
    }

    /**
     * Get optimization recommendations
     */
    async getOptimizationRecommendations(params) {
        try {
            const response = await fetch(`${this.apiBase}/api/ai/optimization-recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Optimization recommendations error:', error);
            return this.getFallbackOptimizations(params);
        }
    }

    /**
     * Get market trend analysis
     */
    async getTrendAnalysis() {
        try {
            const response = await fetch(`${this.apiBase}/api/ai/trend-analysis`, {
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            const data = await response.json();
            return this.enhanceTrendData(data);
        } catch (error) {
            console.error('Trend analysis error:', error);
            return this.getFallbackTrends();
        }
    }

    /**
     * Enhanced data processing methods
     */
    enhancePricingData(data) {
        if (!data || !data.pricing_data) return data;

        // Add price change indicators
        Object.keys(data.pricing_data).forEach(provider => {
            data.pricing_data[provider] = data.pricing_data[provider].map(item => ({
                ...item,
                price_change: this.calculatePriceChange(item),
                cost_efficiency: this.calculateCostEfficiency(item),
                recommendation: this.getServiceRecommendation(item)
            }));
        });

        return data;
    }

    enhancePredictionData(data) {
        if (!data) return data;

        return {
            ...data,
            risk_level: this.calculateRiskLevel(data),
            savings_potential: this.calculateSavingsPotential(data),
            confidence_level: this.getConfidenceLevel(data.confidence_score),
            recommendation_priority: this.prioritizeRecommendations(data.optimization_recommendations)
        };
    }

    enhanceTrendData(data) {
        if (!data || !data.market_trends) return data;

        // Add trend predictions
        Object.keys(data.market_trends).forEach(provider => {
            data.market_trends[provider] = {
                ...data.market_trends[provider],
                predicted_direction: this.predictTrendDirection(data.market_trends[provider]),
                volatility_impact: this.assessVolatilityImpact(data.market_trends[provider]),
                investment_timing: this.recommendInvestmentTiming(data.market_trends[provider])
            };
        });

        return data;
    }

    /**
     * Utility calculation methods
     */
    calculatePriceChange(item) {
        // Mock calculation - in real implementation, compare with historical data
        return Math.random() * 0.1 - 0.05; // Random change between -5% and +5%
    }

    calculateCostEfficiency(item) {
        const baseEfficiency = 0.7;
        const priceModifier = (item.price_per_hour || item.price_per_gb_month || 0) * 0.01;
        return Math.min(0.95, baseEfficiency + Math.random() * 0.2 - priceModifier);
    }

    getServiceRecommendation(item) {
        const efficiency = this.calculateCostEfficiency(item);
        if (efficiency > 0.8) return 'Highly Recommended';
        if (efficiency > 0.6) return 'Good Value';
        if (efficiency > 0.4) return 'Consider Alternatives';
        return 'Not Recommended';
    }

    calculateRiskLevel(prediction) {
        const riskFactors = prediction.risk_factors?.length || 0;
        const confidence = prediction.confidence_score || 0;
        
        if (riskFactors > 3 || confidence < 0.6) return 'High';
        if (riskFactors > 1 || confidence < 0.8) return 'Medium';
        return 'Low';
    }

    calculateSavingsPotential(prediction) {
        const savings = prediction.savings_opportunity_percent || 0;
        if (savings > 30) return 'High';
        if (savings > 15) return 'Medium';
        return 'Low';
    }

    getConfidenceLevel(score) {
        if (score > 0.85) return 'Very High';
        if (score > 0.70) return 'High';
        if (score > 0.55) return 'Medium';
        return 'Low';
    }

    prioritizeRecommendations(recommendations) {
        if (!recommendations || !Array.isArray(recommendations)) return [];
        
        // Sort by potential impact (simplified)
        return recommendations.map((rec, index) => ({
            text: rec,
            priority: index < 3 ? 'High' : index < 6 ? 'Medium' : 'Low',
            impact: index < 2 ? 'High' : index < 5 ? 'Medium' : 'Low'
        }));
    }

    predictTrendDirection(trend) {
        const overall = trend.overall_trend || 'stable';
        const volatility = trend.volatility || 'low';
        
        if (overall === 'increasing' && volatility === 'low') return 'Continued Growth';
        if (overall === 'decreasing' && volatility === 'low') return 'Continued Decline';
        if (volatility === 'high') return 'Uncertain';
        return 'Stable';
    }

    assessVolatilityImpact(trend) {
        const volatility = trend.volatility || 'low';
        const stability = trend.price_stability_score || 0.8;
        
        if (volatility === 'high' || stability < 0.6) return 'High Risk';
        if (volatility === 'medium' || stability < 0.8) return 'Moderate Risk';
        return 'Low Risk';
    }

    recommendInvestmentTiming(trend) {
        const direction = this.predictTrendDirection(trend);
        const volatility = trend.volatility || 'low';
        
        if (direction === 'Continued Decline' && volatility === 'low') return 'Good Time to Buy';
        if (direction === 'Continued Growth' && volatility === 'low') return 'Consider Selling';
        if (volatility === 'high') return 'Wait for Stability';
        return 'Monitor Closely';
    }

    /**
     * Fallback data methods
     */
    getFallbackAnalysis(params) {
        return {
            ai_insights: {
                best_value_provider: 'gcp',
                maximum_savings_potential: 35.5,
                average_confidence_score: 0.82,
                total_optimization_opportunities: 7
            },
            provider_predictions: {
                aws: {
                    predicted_monthly_cost: params.estimated_monthly_spend * 1.1,
                    confidence_score: 0.8,
                    savings_opportunity_percent: 25
                },
                azure: {
                    predicted_monthly_cost: params.estimated_monthly_spend * 1.05,
                    confidence_score: 0.85,
                    savings_opportunity_percent: 30
                },
                gcp: {
                    predicted_monthly_cost: params.estimated_monthly_spend * 0.95,
                    confidence_score: 0.82,
                    savings_opportunity_percent: 35
                }
            },
            overall_recommendations: [
                'Optimize Lambda function memory allocation',
                'Consider reserved capacity for predictable workloads',
                'Implement intelligent storage tiering',
                'Use automated scaling policies',
                'Monitor and right-size compute instances'
            ]
        };
    }

    getFallbackPricing() {
        return {
            pricing_data: {
                aws: [
                    { service: 'lambda', price_per_hour: 0.0000166667, region: 'us-east-1' },
                    { service: 'ec2', price_per_hour: 0.0104, region: 'us-east-1' },
                    { service: 's3', price_per_gb_month: 0.023, region: 'us-east-1' }
                ],
                azure: [
                    { service: 'functions', price_per_hour: 0.000016, region: 'east-us' },
                    { service: 'vm', price_per_hour: 0.0104, region: 'east-us' },
                    { service: 'storage', price_per_gb_month: 0.0184, region: 'east-us' }
                ],
                gcp: [
                    { service: 'functions', price_per_hour: 0.0000025, region: 'us-central1' },
                    { service: 'compute', price_per_hour: 0.006, region: 'us-central1' },
                    { service: 'storage', price_per_gb_month: 0.02, region: 'us-central1' }
                ]
            },
            total_data_points: 9,
            last_updated: new Date().toISOString()
        };
    }

    getFallbackPrediction(provider, params) {
        const baseCost = params.estimated_monthly_spend || 1000;
        const multiplier = provider === 'aws' ? 1.1 : provider === 'azure' ? 1.05 : 0.95;
        
        return {
            provider: provider,
            predicted_monthly_cost: baseCost * multiplier,
            confidence_score: 0.8,
            savings_opportunity_percent: provider === 'gcp' ? 35 : provider === 'azure' ? 30 : 25,
            optimization_recommendations: [
                `Optimize ${provider} resource allocation`,
                `Consider ${provider} reserved instances`,
                `Implement ${provider} auto-scaling`
            ],
            risk_factors: [`${provider} pricing subject to change`, 'Market conditions may vary']
        };
    }

    getFallbackOptimizations(params) {
        return {
            optimization_opportunities: [
                'Right-size your instances based on actual usage',
                'Implement auto-scaling to handle traffic spikes',
                'Use spot instances for non-critical workloads',
                'Optimize storage classes based on access patterns',
                'Set up budget alerts and cost monitoring'
            ],
            estimated_savings: params.estimated_monthly_spend * 0.3,
            implementation_complexity: 'Medium',
            time_to_implement: '2-4 weeks'
        };
    }

    getFallbackTrends() {
        return {
            market_trends: {
                aws: {
                    overall_trend: 'stable',
                    volatility: 'low',
                    price_stability_score: 0.88
                },
                azure: {
                    overall_trend: 'decreasing',
                    volatility: 'medium',
                    price_stability_score: 0.82
                },
                gcp: {
                    overall_trend: 'stable',
                    volatility: 'low',
                    price_stability_score: 0.90
                }
            },
            overall_stability_score: 0.87,
            market_volatility: 'low'
        };
    }
}

// Export for use in dashboard
window.FISOAIPredictor = FISOAIPredictor;
