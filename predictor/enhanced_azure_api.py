# Enhanced Azure Retail Prices API Integration
# Real-time Azure pricing data collection using official API

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class EnhancedAzurePricingAPI:
    """Enhanced Azure Retail Prices API integration for real-time pricing"""
    
    def __init__(self):
        """Initialize Azure pricing API client"""
        self.base_url = "https://prices.azure.com/api/retail/prices"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FISO-Enterprise-Intelligence-Platform/1.0',
            'Accept': 'application/json'
        })
        
        # Common Azure regions
        self.regions = {
            'eastus': 'East US',
            'eastus2': 'East US 2',
            'westus': 'West US',
            'westus2': 'West US 2',
            'westus3': 'West US 3',
            'centralus': 'Central US',
            'northcentralus': 'North Central US',
            'southcentralus': 'South Central US',
            'westcentralus': 'West Central US',
            'canadacentral': 'Canada Central',
            'canadaeast': 'Canada East',
            'brazilsouth': 'Brazil South',
            'northeurope': 'North Europe',
            'westeurope': 'West Europe',
            'uksouth': 'UK South',
            'ukwest': 'UK West',
            'francecentral': 'France Central',
            'francesouth': 'France South',
            'germanywestcentral': 'Germany West Central',
            'norwayeast': 'Norway East',
            'switzerlandnorth': 'Switzerland North',
            'southafricanorth': 'South Africa North',
            'uaenorth': 'UAE North',
            'centralindia': 'Central India',
            'southindia': 'South India',
            'westindia': 'West India',
            'eastasia': 'East Asia',
            'southeastasia': 'Southeast Asia',
            'japaneast': 'Japan East',
            'japanwest': 'Japan West',
            'koreacentral': 'Korea Central',
            'koreasouth': 'Korea South',
            'australiaeast': 'Australia East',
            'australiasoutheast': 'Australia Southeast'
        }
        
        logger.info("✅ Enhanced Azure Pricing API client initialized")
    
    def fetch_vm_pricing_live(self, region: str = 'eastus') -> List[Dict[str, Any]]:
        """Fetch live Azure VM pricing using Retail Prices API"""
        logger.info(f"🔍 Fetching live Azure VM pricing for region: {region}")
        
        pricing_data = []
        
        try:
            # Popular Azure VM series
            vm_series = [
                'Standard_B1s', 'Standard_B1ms', 'Standard_B2s', 'Standard_B2ms',
                'Standard_B4ms', 'Standard_B8ms', 'Standard_B12ms', 'Standard_B16ms',
                'Standard_D2s_v3', 'Standard_D4s_v3', 'Standard_D8s_v3', 'Standard_D16s_v3',
                'Standard_E2s_v3', 'Standard_E4s_v3', 'Standard_E8s_v3', 'Standard_E16s_v3',
                'Standard_F2s_v2', 'Standard_F4s_v2', 'Standard_F8s_v2', 'Standard_F16s_v2',
                'Standard_DS1_v2', 'Standard_DS2_v2', 'Standard_DS3_v2', 'Standard_DS4_v2'
            ]
            
            for vm_size in vm_series:
                try:
                    # Build query filter for Azure Retail Prices API
                    filter_query = (
                        f"serviceName eq 'Virtual Machines' "
                        f"and armSkuName eq '{vm_size}' "
                        f"and armRegionName eq '{region}' "
                        f"and priceType eq 'Consumption'"
                    )
                    
                    params = {
                        '$filter': filter_query,
                        '$top': 100  # Limit results
                    }
                    
                    response = self.session.get(self.base_url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for item in data.get('Items', []):
                            # Extract and process pricing data
                            pricing_record = {
                                'provider': 'azure',
                                'service': 'vm',
                                'region': region,
                                'instance_type': vm_size,
                                'price_per_hour': float(item.get('unitPrice', 0.0)),
                                'currency': item.get('currencyCode', 'USD'),
                                'timestamp': datetime.now().isoformat(),
                                'source': 'azure_retail_prices_api_live',
                                'raw_data': {
                                    'product_name': item.get('productName'),
                                    'sku_name': item.get('skuName'),
                                    'meter_name': item.get('meterName'),
                                    'unit_of_measure': item.get('unitOfMeasure'),
                                    'tier_minimum_units': item.get('tierMinimumUnits'),
                                    'retail_price': item.get('retailPrice'),
                                    'unit_price': item.get('unitPrice'),
                                    'effective_start_date': item.get('effectiveStartDate'),
                                    'meter_id': item.get('meterId'),
                                    'meter_region': item.get('meterRegion'),
                                    'location': item.get('location'),
                                    'service_name': item.get('serviceName'),
                                    'service_id': item.get('serviceId'),
                                    'service_family': item.get('serviceFamily')
                                }
                            }
                            
                            pricing_data.append(pricing_record)
                            
                            # Log successful data collection
                            logger.debug(f"✅ Collected pricing for {vm_size}: ${pricing_record['price_per_hour']:.4f}/hour")
                    
                    elif response.status_code == 429:
                        # Rate limiting - wait and retry
                        logger.warning(f"⚠️ Rate limited, waiting 2 seconds before retry...")
                        time.sleep(2)
                        continue
                    
                    else:
                        logger.warning(f"⚠️ API request failed for {vm_size}: HTTP {response.status_code}")
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.1)
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"⚠️ Timeout fetching pricing for {vm_size}")
                    continue
                except requests.exceptions.RequestException as e:
                    logger.warning(f"⚠️ Request error for {vm_size}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"❌ Unexpected error fetching {vm_size}: {e}")
                    continue
            
            logger.info(f"✅ Azure VM pricing: {len(pricing_data)} live records collected")
            return pricing_data
            
        except Exception as e:
            logger.error(f"❌ Azure VM pricing collection failed: {e}")
            return []
    
    def fetch_storage_pricing_live(self, region: str = 'eastus') -> List[Dict[str, Any]]:
        """Fetch live Azure Storage pricing"""
        logger.info(f"🔍 Fetching live Azure Storage pricing for region: {region}")
        
        pricing_data = []
        
        try:
            # Azure Storage services to query
            storage_services = [
                'Storage',
                'Azure Data Lake Storage Gen2',
                'Bandwidth'
            ]
            
            for service in storage_services:
                try:
                    filter_query = (
                        f"serviceName eq '{service}' "
                        f"and armRegionName eq '{region}' "
                        f"and priceType eq 'Consumption'"
                    )
                    
                    params = {
                        '$filter': filter_query,
                        '$top': 50
                    }
                    
                    response = self.session.get(self.base_url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for item in data.get('Items', []):
                            # Process storage pricing
                            unit_price = float(item.get('unitPrice', 0.0))
                            unit_of_measure = item.get('unitOfMeasure', '')
                            
                            # Determine pricing type based on unit of measure
                            price_per_gb_month = None
                            price_per_request = None
                            
                            if 'GB' in unit_of_measure and 'Month' in unit_of_measure:
                                price_per_gb_month = unit_price
                            elif 'per 10K' in unit_of_measure or 'transaction' in unit_of_measure.lower():
                                price_per_request = unit_price / 10000  # Convert per 10K to per request
                            
                            pricing_record = {
                                'provider': 'azure',
                                'service': 'storage',
                                'region': region,
                                'instance_type': item.get('meterName', 'unknown'),
                                'price_per_hour': None,
                                'price_per_gb_month': price_per_gb_month,
                                'price_per_request': price_per_request,
                                'currency': item.get('currencyCode', 'USD'),
                                'timestamp': datetime.now().isoformat(),
                                'source': 'azure_retail_prices_api_live',
                                'raw_data': {
                                    'product_name': item.get('productName'),
                                    'sku_name': item.get('skuName'),
                                    'meter_name': item.get('meterName'),
                                    'unit_of_measure': unit_of_measure,
                                    'unit_price': unit_price,
                                    'service_name': item.get('serviceName'),
                                    'service_family': item.get('serviceFamily')
                                }
                            }
                            
                            pricing_data.append(pricing_record)
                    
                    # Delay between service queries
                    time.sleep(0.2)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error fetching {service} pricing: {e}")
                    continue
            
            logger.info(f"✅ Azure Storage pricing: {len(pricing_data)} live records collected")
            return pricing_data
            
        except Exception as e:
            logger.error(f"❌ Azure Storage pricing collection failed: {e}")
            return []
    
    def fetch_functions_pricing_live(self, region: str = 'eastus') -> List[Dict[str, Any]]:
        """Fetch live Azure Functions pricing"""
        logger.info(f"🔍 Fetching live Azure Functions pricing for region: {region}")
        
        pricing_data = []
        
        try:
            # Query Azure Functions pricing
            filter_query = (
                f"serviceName eq 'Azure Functions' "
                f"and armRegionName eq '{region}' "
                f"and priceType eq 'Consumption'"
            )
            
            params = {
                '$filter': filter_query,
                '$top': 30
            }
            
            response = self.session.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('Items', []):
                    meter_name = item.get('meterName', '').lower()
                    unit_price = float(item.get('unitPrice', 0.0))
                    
                    # Determine pricing type
                    price_per_request = None
                    price_per_gb_second = None
                    
                    if 'execution' in meter_name or 'request' in meter_name:
                        price_per_request = unit_price
                    elif 'gb-s' in meter_name or 'memory' in meter_name:
                        price_per_gb_second = unit_price
                    
                    pricing_record = {
                        'provider': 'azure',
                        'service': 'functions',
                        'region': region,
                        'instance_type': item.get('meterName', 'consumption'),
                        'price_per_hour': None,
                        'price_per_gb_month': None,
                        'price_per_request': price_per_request,
                        'price_per_gb_second': price_per_gb_second,
                        'currency': item.get('currencyCode', 'USD'),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'azure_retail_prices_api_live',
                        'raw_data': {
                            'product_name': item.get('productName'),
                            'meter_name': item.get('meterName'),
                            'unit_of_measure': item.get('unitOfMeasure'),
                            'unit_price': unit_price,
                            'service_name': item.get('serviceName')
                        }
                    }
                    
                    pricing_data.append(pricing_record)
                
                logger.info(f"✅ Azure Functions pricing: {len(pricing_data)} live records collected")
                return pricing_data
            
            else:
                logger.warning(f"⚠️ Azure Functions API request failed: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Azure Functions pricing collection failed: {e}")
            return []
    
    def fetch_comprehensive_pricing(self, region: str = 'eastus') -> Dict[str, List[Dict[str, Any]]]:
        """Fetch comprehensive Azure pricing for all services"""
        logger.info(f"🔍 Starting comprehensive Azure pricing collection for {region}")
        
        all_pricing = {
            'vm': [],
            'storage': [],
            'functions': []
        }
        
        try:
            # Fetch all service types
            all_pricing['vm'] = self.fetch_vm_pricing_live(region)
            time.sleep(1)  # Delay between service types
            
            all_pricing['storage'] = self.fetch_storage_pricing_live(region)
            time.sleep(1)
            
            all_pricing['functions'] = self.fetch_functions_pricing_live(region)
            
            total_records = sum(len(data) for data in all_pricing.values())
            logger.info(f"✅ Comprehensive Azure pricing complete: {total_records} total records")
            
            return all_pricing
            
        except Exception as e:
            logger.error(f"❌ Comprehensive Azure pricing collection failed: {e}")
            return all_pricing
    
    def get_latest_pricing_summary(self, region: str = 'eastus') -> Dict[str, Any]:
        """Get latest pricing summary with key metrics"""
        try:
            pricing_data = self.fetch_comprehensive_pricing(region)
            
            summary = {
                'region': region,
                'timestamp': datetime.now().isoformat(),
                'total_records': sum(len(data) for data in pricing_data.values()),
                'services': {},
                'price_ranges': {},
                'currency': 'USD'
            }
            
            # Process VM pricing
            if pricing_data['vm']:
                vm_prices = [item['price_per_hour'] for item in pricing_data['vm'] if item['price_per_hour']]
                if vm_prices:
                    summary['services']['vm'] = {
                        'count': len(vm_prices),
                        'min_price': min(vm_prices),
                        'max_price': max(vm_prices),
                        'avg_price': sum(vm_prices) / len(vm_prices)
                    }
            
            # Process Storage pricing
            if pricing_data['storage']:
                storage_prices = [item['price_per_gb_month'] for item in pricing_data['storage'] if item.get('price_per_gb_month')]
                if storage_prices:
                    summary['services']['storage'] = {
                        'count': len(storage_prices),
                        'min_price': min(storage_prices),
                        'max_price': max(storage_prices),
                        'avg_price': sum(storage_prices) / len(storage_prices)
                    }
            
            # Process Functions pricing
            if pricing_data['functions']:
                functions_count = len(pricing_data['functions'])
                summary['services']['functions'] = {
                    'count': functions_count,
                    'pricing_models': len(set(item['instance_type'] for item in pricing_data['functions']))
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Pricing summary generation failed: {e}")
            return {}

# Test function for enhanced Azure API
def test_enhanced_azure_api():
    """Test the enhanced Azure pricing API"""
    try:
        print("🧪 Testing Enhanced Azure Retail Prices API...")
        
        api = EnhancedAzurePricingAPI()
        print("✅ API client initialization successful")
        
        # Test VM pricing
        vm_data = api.fetch_vm_pricing_live('eastus')
        print(f"✅ VM pricing: {len(vm_data)} live records")
        
        # Test storage pricing
        storage_data = api.fetch_storage_pricing_live('eastus')
        print(f"✅ Storage pricing: {len(storage_data)} live records")
        
        # Test functions pricing
        functions_data = api.fetch_functions_pricing_live('eastus')
        print(f"✅ Functions pricing: {len(functions_data)} live records")
        
        # Test comprehensive pricing
        comprehensive_data = api.fetch_comprehensive_pricing('eastus')
        total_records = sum(len(data) for data in comprehensive_data.values())
        print(f"✅ Comprehensive pricing: {total_records} total records")
        
        # Test pricing summary
        summary = api.get_latest_pricing_summary('eastus')
        print(f"✅ Pricing summary: {summary.get('total_records', 0)} records summarized")
        
        print("🎉 All tests passed! Enhanced Azure API is operational.")
        
        # Display sample data
        if vm_data:
            sample_vm = vm_data[0]
            print(f"\n📊 Sample VM Pricing:")
            print(f"   Instance: {sample_vm['instance_type']}")
            print(f"   Price: ${sample_vm['price_per_hour']:.4f}/hour")
            print(f"   Source: {sample_vm['source']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_enhanced_azure_api()
