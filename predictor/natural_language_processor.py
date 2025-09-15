"""
Natural Language Query Interface for FISO
Enables AI-powered natural language interactions with the dashboard
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3

class NaturalLanguageProcessor:
    """Process natural language queries for cloud cost analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_patterns()
        
    def setup_patterns(self):
        """Setup regex patterns for query understanding"""
        self.patterns = {
            'cost_query': [
                r'(?:show|display|get|find)\s+(?:me\s+)?(?:the\s+)?costs?\s+for\s+(\w+)',
                r'(?:what|how much)\s+(?:is|are|did|does)\s+(\w+)\s+cost',
                r'(\w+)\s+costs?\s+(?:for|in|during)\s+(.+)',
                r'total\s+(?:cost|spending|expenses?)\s+(?:for|on|in)\s+(\w+)'
            ],
            'comparison_query': [
                r'compare\s+(\w+)\s+(?:and|vs|versus|with)\s+(\w+)',
                r'(?:which|what)\s+is\s+cheaper\s+(\w+)\s+or\s+(\w+)',
                r'difference\s+between\s+(\w+)\s+and\s+(\w+)'
            ],
            'time_period': [
                r'(?:in|during|for)\s+(?:the\s+)?(?:last|past)\s+(\d+)\s+(days?|weeks?|months?|years?)',
                r'(?:this|last)\s+(week|month|year|quarter)',
                r'(?:yesterday|today|last\s+week|last\s+month)',
                r'from\s+(.+)\s+to\s+(.+)'
            ],
            'optimization_query': [
                r'(?:optimize|improve|reduce)\s+(?:costs?|spending|expenses?)',
                r'(?:how\s+)?(?:can\s+i|to)\s+(?:save|reduce)\s+(?:money|costs?)',
                r'recommendations?\s+for\s+(\w+)',
                r'best\s+(?:practices|options)\s+for\s+(\w+)'
            ],
            'prediction_query': [
                r'(?:predict|forecast|estimate)\s+(?:costs?|spending|expenses?)',
                r'(?:what\s+will|how\s+much\s+will)\s+(\w+)\s+cost',
                r'future\s+(?:costs?|spending)\s+for\s+(\w+)',
                r'next\s+(week|month|quarter|year)\s+(?:costs?|spending)'
            ],
            'provider_names': [
                r'\b(aws|amazon|ec2|lambda|s3|rds)\b',
                r'\b(azure|microsoft|vm|functions|blob|sql)\b',
                r'\b(gcp|google|compute|cloud\s+sql|storage)\b',
                r'\b(oracle|oci)\b'
            ],
            'service_types': [
                r'\b(compute|vm|ec2|instances?)\b',
                r'\b(storage|s3|blob|disk)\b',
                r'\b(database|db|sql|rds)\b',
                r'\b(serverless|lambda|functions?)\b',
                r'\b(networking|vpc|bandwidth)\b'
            ]
        }
        
    def parse_query(self, query: str) -> Dict:
        """Parse natural language query and extract intent and entities"""
        query = query.lower().strip()
        
        result = {
            'intent': 'unknown',
            'entities': {},
            'confidence': 0.0,
            'query_type': 'general',
            'parameters': {}
        }
        
        # Detect query intent
        intent, confidence = self._detect_intent(query)
        result['intent'] = intent
        result['confidence'] = confidence
        
        # Extract entities
        entities = self._extract_entities(query)
        result['entities'] = entities
        
        # Extract time period
        time_period = self._extract_time_period(query)
        if time_period:
            result['parameters']['time_period'] = time_period
            
        # Extract providers and services
        providers = self._extract_providers(query)
        services = self._extract_services(query)
        
        if providers:
            result['entities']['providers'] = providers
        if services:
            result['entities']['services'] = services
            
        return result
        
    def _detect_intent(self, query: str) -> Tuple[str, float]:
        """Detect the main intent of the query"""
        intents = [
            ('cost_query', self.patterns['cost_query']),
            ('comparison_query', self.patterns['comparison_query']),
            ('optimization_query', self.patterns['optimization_query']),
            ('prediction_query', self.patterns['prediction_query'])
        ]
        
        best_intent = 'general'
        best_confidence = 0.0
        
        for intent_name, patterns in intents:
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    # Calculate confidence based on pattern match quality
                    match = re.search(pattern, query, re.IGNORECASE)
                    confidence = len(match.group(0)) / len(query)
                    
                    if confidence > best_confidence:
                        best_intent = intent_name
                        best_confidence = confidence
                        
        return best_intent, min(best_confidence * 2, 1.0)  # Scale up confidence
        
    def _extract_entities(self, query: str) -> Dict:
        """Extract named entities from the query"""
        entities = {}
        
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', query)
        if numbers:
            entities['numbers'] = [float(n) for n in numbers]
            
        # Extract currency amounts
        currency = re.findall(r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
        if currency:
            entities['currency'] = [float(c.replace(',', '')) for c in currency]
            
        return entities
        
    def _extract_time_period(self, query: str) -> Optional[Dict]:
        """Extract time period information"""
        for pattern in self.patterns['time_period']:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:  # Number + unit
                    try:
                        amount = int(groups[0])
                        unit = groups[1].rstrip('s')  # Remove plural
                        return {
                            'amount': amount,
                            'unit': unit,
                            'type': 'relative'
                        }
                    except ValueError:
                        continue
                elif len(groups) == 1:  # Single period
                    period = groups[0]
                    return {
                        'period': period,
                        'type': 'named'
                    }
                        
        return None
        
    def _extract_providers(self, query: str) -> List[str]:
        """Extract cloud provider names"""
        providers = []
        
        provider_mapping = {
            'aws': ['aws', 'amazon', 'ec2', 'lambda', 's3', 'rds'],
            'azure': ['azure', 'microsoft', 'vm', 'functions', 'blob'],
            'gcp': ['gcp', 'google', 'compute', 'cloud sql', 'storage'],
            'oracle': ['oracle', 'oci']
        }
        
        for provider, keywords in provider_mapping.items():
            for keyword in keywords:
                if re.search(r'\b' + keyword + r'\b', query, re.IGNORECASE):
                    if provider not in providers:
                        providers.append(provider)
                        
        return providers
        
    def _extract_services(self, query: str) -> List[str]:
        """Extract service types"""
        services = []
        
        service_mapping = {
            'compute': ['compute', 'vm', 'ec2', 'instances', 'virtual machine'],
            'storage': ['storage', 's3', 'blob', 'disk', 'bucket'],
            'database': ['database', 'db', 'sql', 'rds', 'mysql', 'postgres'],
            'serverless': ['serverless', 'lambda', 'functions', 'function'],
            'networking': ['networking', 'vpc', 'bandwidth', 'network']
        }
        
        for service, keywords in service_mapping.items():
            for keyword in keywords:
                if re.search(r'\b' + keyword + r'\b', query, re.IGNORECASE):
                    if service not in services:
                        services.append(service)
                        
        return services
        
    def generate_response(self, query_result: Dict, data_result: Dict) -> Dict:
        """Generate natural language response based on query and data"""
        intent = query_result['intent']
        entities = query_result['entities']
        
        if intent == 'cost_query':
            return self._generate_cost_response(entities, data_result)
        elif intent == 'comparison_query':
            return self._generate_comparison_response(entities, data_result)
        elif intent == 'optimization_query':
            return self._generate_optimization_response(entities, data_result)
        elif intent == 'prediction_query':
            return self._generate_prediction_response(entities, data_result)
        else:
            return self._generate_general_response(data_result)
            
    def _generate_cost_response(self, entities: Dict, data: Dict) -> Dict:
        """Generate response for cost queries"""
        providers = entities.get('providers', [])
        services = entities.get('services', [])
        
        if providers and len(providers) == 1:
            provider = providers[0].upper()
            if 'total_cost' in data:
                response = f"Your {provider} costs are currently ${data['total_cost']:.2f} per month."
                
                if services:
                    service = services[0]
                    response += f" For {service} services specifically, you're spending approximately ${data.get('service_cost', data['total_cost'] * 0.3):.2f}."
                    
                return {
                    'response': response,
                    'type': 'cost_summary',
                    'data': data
                }
                
        return {
            'response': f"Your total cloud costs are ${data.get('total_cost', 0):.2f} per month across all providers.",
            'type': 'cost_summary',
            'data': data
        }
        
    def _generate_comparison_response(self, entities: Dict, data: Dict) -> Dict:
        """Generate response for comparison queries"""
        providers = entities.get('providers', [])
        
        if len(providers) >= 2:
            prov1, prov2 = providers[0].upper(), providers[1].upper()
            
            # Mock comparison data
            comparison = {
                prov1: data.get('total_cost', 0) * 0.4,
                prov2: data.get('total_cost', 0) * 0.6
            }
            
            cheaper = min(comparison, key=comparison.get)
            savings = abs(comparison[prov1] - comparison[prov2])
            
            response = f"Comparing {prov1} vs {prov2}: {cheaper} is cheaper by approximately ${savings:.2f} per month. "
            response += f"{prov1} costs ${comparison[prov1]:.2f} while {prov2} costs ${comparison[prov2]:.2f}."
            
            return {
                'response': response,
                'type': 'comparison',
                'data': {'comparison': comparison, 'cheaper': cheaper, 'savings': savings}
            }
            
        return {
            'response': "I need two providers to compare. Try asking 'Compare AWS and Azure costs'.",
            'type': 'clarification',
            'data': {}
        }
        
    def _generate_optimization_response(self, entities: Dict, data: Dict) -> Dict:
        """Generate response for optimization queries"""
        potential_savings = data.get('potential_savings', 0)
        
        recommendations = [
            f"Switch to reserved instances to save up to ${potential_savings * 0.4:.2f}",
            f"Optimize unused resources to save ${potential_savings * 0.3:.2f}",
            f"Consider spot instances for non-critical workloads to save ${potential_savings * 0.3:.2f}"
        ]
        
        response = f"I found ${potential_savings:.2f} in potential monthly savings. Here are my top recommendations: "
        response += "; ".join(recommendations)
        
        return {
            'response': response,
            'type': 'optimization',
            'data': {'recommendations': recommendations, 'total_savings': potential_savings}
        }
        
    def _generate_prediction_response(self, entities: Dict, data: Dict) -> Dict:
        """Generate response for prediction queries"""
        current_cost = data.get('total_cost', 0)
        predicted_growth = 1.15  # 15% growth assumption
        
        next_month = current_cost * predicted_growth
        
        response = f"Based on current trends, I predict your costs will be approximately ${next_month:.2f} next month, "
        response += f"representing a {((predicted_growth - 1) * 100):.1f}% increase from the current ${current_cost:.2f}."
        
        return {
            'response': response,
            'type': 'prediction',
            'data': {'predicted_cost': next_month, 'growth_rate': predicted_growth - 1}
        }
        
    def _generate_general_response(self, data: Dict) -> Dict:
        """Generate general response"""
        total_cost = data.get('total_cost', 0)
        active_resources = data.get('active_resources', 0)
        
        response = f"Your cloud infrastructure currently costs ${total_cost:.2f} per month with {active_resources} active resources. "
        response += "I can help you analyze costs, compare providers, optimize spending, or predict future costs. "
        response += "Try asking: 'Show me AWS costs', 'Compare Azure and GCP', or 'How can I optimize costs?'"
        
        return {
            'response': response,
            'type': 'general',
            'data': data
        }

class QueryProcessor:
    """Main query processing engine"""
    
    def __init__(self):
        self.nlp = NaturalLanguageProcessor()
        self.logger = logging.getLogger(__name__)
        
    def process_query(self, query: str, context_data: Dict) -> Dict:
        """Process a natural language query and return results"""
        try:
            # Parse the query
            query_result = self.nlp.parse_query(query)
            
            # Generate appropriate data based on intent
            data_result = self._get_relevant_data(query_result, context_data)
            
            # Generate natural language response
            response = self.nlp.generate_response(query_result, data_result)
            
            return {
                'success': True,
                'query': query,
                'parsed_query': query_result,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query '{query}': {str(e)}")
            return {
                'success': False,
                'query': query,
                'error': str(e),
                'response': {
                    'response': "I'm sorry, I couldn't understand your question. Please try rephrasing it.",
                    'type': 'error',
                    'data': {}
                },
                'timestamp': datetime.now().isoformat()
            }
            
    def _get_relevant_data(self, query_result: Dict, context_data: Dict) -> Dict:
        """Get relevant data based on the parsed query"""
        intent = query_result['intent']
        entities = query_result['entities']
        
        # Start with context data
        result = dict(context_data)
        
        # Filter by providers if specified
        if 'providers' in entities:
            providers = entities['providers']
            # Filter pricing data by providers
            if 'pricing_data' in context_data:
                filtered_pricing = {}
                for provider in providers:
                    if provider in context_data['pricing_data']:
                        filtered_pricing[provider] = context_data['pricing_data'][provider]
                result['pricing_data'] = filtered_pricing
                
        # Add intent-specific data
        if intent == 'prediction_query':
            # Add prediction data
            result['predictions'] = self._generate_sample_predictions()
        elif intent == 'optimization_query':
            # Add optimization recommendations
            result['recommendations'] = self._generate_sample_recommendations()
            
        return result
        
    def _generate_sample_predictions(self) -> Dict:
        """Generate sample prediction data"""
        return {
            'next_week': {
                'predicted_cost': 650.00,
                'confidence': 0.85
            },
            'next_month': {
                'predicted_cost': 2900.00,
                'confidence': 0.75
            }
        }
        
    def _generate_sample_recommendations(self) -> List[Dict]:
        """Generate sample optimization recommendations"""
        return [
            {
                'type': 'Reserved Instances',
                'description': 'Switch to 1-year reserved instances for EC2',
                'potential_savings': 342.50,
                'effort': 'Low',
                'impact': 'High'
            },
            {
                'type': 'Resource Rightsizing',
                'description': 'Downsize underutilized t3.large instances',
                'potential_savings': 156.00,
                'effort': 'Medium',
                'impact': 'Medium'
            }
        ]

# Global instance
query_processor = QueryProcessor()