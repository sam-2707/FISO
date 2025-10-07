"""
FISO Real Cloud Provider API Integration
Enterprise-grade cloud cost data collection with multi-provider support
"""

import asyncio
import aiohttp
import boto3
import azure.mgmt.consumption
import azure.mgmt.costmanagement
from google.cloud import billing
from google.cloud import asset
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class CostRecord:
    """Standardized cost record across all providers"""
    provider: str
    account_id: str
    service_name: str
    resource_id: str
    cost_amount: float
    currency: str
    usage_date: str
    usage_quantity: float
    usage_unit: str
    resource_tags: Dict[str, str]
    region: str
    availability_zone: Optional[str] = None
    instance_type: Optional[str] = None
    billing_period: str = None

@dataclass
class ProviderCredentials:
    """Cloud provider credentials"""
    provider: str
    credentials: Dict[str, Any]
    enabled: bool = True

class CloudProviderBase(ABC):
    """Abstract base class for cloud provider integrations"""
    
    def __init__(self, credentials: ProviderCredentials):
        self.credentials = credentials
        self.provider = credentials.provider
        
    @abstractmethod
    async def get_cost_data(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Fetch cost data for the specified date range"""
        pass
    
    @abstractmethod
    async def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations from the provider"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate provider credentials"""
        pass

class AWSCostProvider(CloudProviderBase):
    """AWS Cost Explorer and Billing API integration"""
    
    def __init__(self, credentials: ProviderCredentials):
        super().__init__(credentials)
        self.session = boto3.Session(
            aws_access_key_id=credentials.credentials['access_key_id'],
            aws_secret_access_key=credentials.credentials['secret_access_key'],
            region_name=credentials.credentials.get('region', 'us-east-1')
        )
        self.cost_explorer = self.session.client('ce')
        self.organizations = self.session.client('organizations')
        
    async def get_cost_data(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Fetch AWS cost data using Cost Explorer API"""
        try:
            # Get cost and usage data
            response = self.cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'},
                    {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}
                ]
            )
            
            cost_records = []
            for result in response['ResultsByTime']:
                usage_date = result['TimePeriod']['Start']
                
                for group in result['Groups']:
                    service_name = group['Keys'][0] if len(group['Keys']) > 0 else 'Unknown'
                    usage_type = group['Keys'][1] if len(group['Keys']) > 1 else 'Unknown'
                    resource_id = group['Keys'][2] if len(group['Keys']) > 2 else 'Unknown'
                    
                    cost_amount = float(group['Metrics']['BlendedCost']['Amount'])
                    usage_quantity = float(group['Metrics']['UsageQuantity']['Amount'])
                    
                    if cost_amount > 0:  # Only include records with actual cost
                        cost_record = CostRecord(
                            provider='aws',
                            account_id=self.credentials.credentials.get('account_id', 'unknown'),
                            service_name=service_name,
                            resource_id=resource_id,
                            cost_amount=cost_amount,
                            currency='USD',
                            usage_date=usage_date,
                            usage_quantity=usage_quantity,
                            usage_unit=group['Metrics']['UsageQuantity']['Unit'],
                            resource_tags={},  # Will be enriched separately
                            region=self._extract_region_from_usage_type(usage_type),
                            billing_period=f"{start_date.strftime('%Y-%m')}"
                        )
                        cost_records.append(cost_record)
            
            # Enrich with resource tags
            await self._enrich_with_resource_tags(cost_records)
            
            logger.info(f"Retrieved {len(cost_records)} AWS cost records from {start_date} to {end_date}")
            return cost_records
            
        except Exception as e:
            logger.error(f"Error fetching AWS cost data: {str(e)}")
            raise
    
    async def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get AWS cost optimization recommendations"""
        try:
            recommendations = []
            
            # Get Reserved Instance recommendations
            ri_response = self.cost_explorer.get_reservation_purchase_recommendation(
                Service='Amazon Elastic Compute Cloud - Compute'
            )
            
            for rec in ri_response.get('Recommendations', []):
                recommendations.append({
                    'type': 'reserved_instance',
                    'service': 'EC2',
                    'recommendation': rec['RecommendationDetails'],
                    'estimated_savings': rec['RecommendationSummary']['TotalEstimatedMonthlySavingsAmount'],
                    'confidence': rec['RecommendationSummary']['CurrencyCode']
                })
            
            # Get Right Sizing recommendations
            rs_response = self.cost_explorer.get_rightsizing_recommendation()
            
            for rec in rs_response.get('RightsizingRecommendations', []):
                recommendations.append({
                    'type': 'rightsizing',
                    'service': 'EC2',
                    'current_instance': rec['CurrentInstance'],
                    'recommended_instance': rec.get('RightsizingType'),
                    'estimated_savings': rec.get('EstimatedMonthlySavings', {}).get('Amount', 0)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching AWS recommendations: {str(e)}")
            return []
    
    async def validate_credentials(self) -> bool:
        """Validate AWS credentials"""
        try:
            sts = self.session.client('sts')
            response = sts.get_caller_identity()
            logger.info(f"AWS credentials valid for account: {response['Account']}")
            return True
        except Exception as e:
            logger.error(f"AWS credential validation failed: {str(e)}")
            return False
    
    def _extract_region_from_usage_type(self, usage_type: str) -> str:
        """Extract region from AWS usage type string"""
        # AWS usage types often contain region info like "USE1-BoxUsage:t3.micro"
        if '-' in usage_type:
            parts = usage_type.split('-')
            if len(parts) > 0:
                region_code = parts[0]
                # Map AWS region codes to standard regions
                region_mapping = {
                    'USE1': 'us-east-1',
                    'USE2': 'us-east-2',
                    'USW1': 'us-west-1',
                    'USW2': 'us-west-2',
                    'EUW1': 'eu-west-1',
                    'EUC1': 'eu-central-1',
                    'APS1': 'ap-southeast-1'
                }
                return region_mapping.get(region_code, 'unknown')
        return 'unknown'
    
    async def _enrich_with_resource_tags(self, cost_records: List[CostRecord]):
        """Enrich cost records with resource tags"""
        # This would require additional AWS API calls to get resource tags
        # For now, we'll leave tags empty but the structure is in place
        pass

class AzureCostProvider(CloudProviderBase):
    """Azure Cost Management API integration"""
    
    def __init__(self, credentials: ProviderCredentials):
        super().__init__(credentials)
        from azure.identity import ClientSecretCredential
        
        self.credential = ClientSecretCredential(
            tenant_id=credentials.credentials['tenant_id'],
            client_id=credentials.credentials['client_id'],
            client_secret=credentials.credentials['client_secret']
        )
        self.subscription_id = credentials.credentials['subscription_id']
        
    async def get_cost_data(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Fetch Azure cost data using Cost Management API"""
        try:
            from azure.mgmt.costmanagement import CostManagementClient
            from azure.mgmt.consumption import ConsumptionManagementClient
            
            cost_client = CostManagementClient(self.credential)
            consumption_client = ConsumptionManagementClient(self.credential, self.subscription_id)
            
            # Query definition for cost data
            query_definition = {
                "type": "Usage",
                "timeframe": "Custom",
                "timePeriod": {
                    "from": start_date.strftime('%Y-%m-%dT00:00:00+00:00'),
                    "to": end_date.strftime('%Y-%m-%dT23:59:59+00:00')
                },
                "dataset": {
                    "granularity": "Daily",
                    "aggregation": {
                        "totalCost": {
                            "name": "PreTaxCost",
                            "function": "Sum"
                        }
                    },
                    "grouping": [
                        {
                            "type": "Dimension",
                            "name": "ResourceId"
                        },
                        {
                            "type": "Dimension", 
                            "name": "ServiceName"
                        },
                        {
                            "type": "Dimension",
                            "name": "ResourceLocation"
                        }
                    ]
                }
            }
            
            # Execute query
            scope = f"/subscriptions/{self.subscription_id}"
            result = cost_client.query.usage(scope, query_definition)
            
            cost_records = []
            for row in result.rows:
                # Azure API returns data in specific column order
                cost_amount = row[0]  # PreTaxCost
                usage_date = row[1]  # Date
                resource_id = row[2] if len(row) > 2 else 'unknown'
                service_name = row[3] if len(row) > 3 else 'unknown'
                resource_location = row[4] if len(row) > 4 else 'unknown'
                
                if cost_amount and cost_amount > 0:
                    cost_record = CostRecord(
                        provider='azure',
                        account_id=self.subscription_id,
                        service_name=service_name,
                        resource_id=resource_id,
                        cost_amount=float(cost_amount),
                        currency='USD',
                        usage_date=usage_date.strftime('%Y-%m-%d') if isinstance(usage_date, datetime) else str(usage_date),
                        usage_quantity=1.0,  # Azure doesn't always provide usage quantity
                        usage_unit='units',
                        resource_tags={},
                        region=resource_location,
                        billing_period=f"{start_date.strftime('%Y-%m')}"
                    )
                    cost_records.append(cost_record)
            
            logger.info(f"Retrieved {len(cost_records)} Azure cost records from {start_date} to {end_date}")
            return cost_records
            
        except Exception as e:
            logger.error(f"Error fetching Azure cost data: {str(e)}")
            raise
    
    async def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get Azure Advisor cost recommendations"""
        try:
            from azure.mgmt.advisor import AdvisorManagementClient
            
            advisor_client = AdvisorManagementClient(self.credential, self.subscription_id)
            
            recommendations = []
            advisor_recommendations = advisor_client.recommendations.list(filter="Category eq 'Cost'")
            
            for rec in advisor_recommendations:
                recommendations.append({
                    'type': rec.category.lower(),
                    'service': rec.impacted_value,
                    'recommendation': rec.short_description.get('solution', ''),
                    'estimated_savings': rec.extended_properties.get('savingsAmount', 0),
                    'impact': rec.impact,
                    'confidence': rec.risk
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching Azure recommendations: {str(e)}")
            return []
    
    async def validate_credentials(self) -> bool:
        """Validate Azure credentials"""
        try:
            from azure.mgmt.resource import ResourceManagementClient
            
            resource_client = ResourceManagementClient(self.credential, self.subscription_id)
            # Try to list resource groups as a credential test
            list(resource_client.resource_groups.list())
            logger.info(f"Azure credentials valid for subscription: {self.subscription_id}")
            return True
        except Exception as e:
            logger.error(f"Azure credential validation failed: {str(e)}")
            return False

class GCPCostProvider(CloudProviderBase):
    """Google Cloud Billing API integration"""
    
    def __init__(self, credentials: ProviderCredentials):
        super().__init__(credentials)
        import os
        
        # Set up GCP credentials
        if 'service_account_key' in credentials.credentials:
            # Write service account key to temporary file
            key_path = '/tmp/gcp_service_account.json'
            with open(key_path, 'w') as f:
                json.dump(credentials.credentials['service_account_key'], f)
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
        
        self.project_id = credentials.credentials['project_id']
        self.billing_account = credentials.credentials.get('billing_account')
        
    async def get_cost_data(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Fetch GCP cost data using Cloud Billing API"""
        try:
            from google.cloud import billing_v1
            from google.cloud import bigquery
            
            # Use BigQuery to query billing export data (more comprehensive)
            if self._has_bigquery_export():
                return await self._get_cost_data_from_bigquery(start_date, end_date)
            
            # Fallback to Cloud Billing API (limited data)
            billing_client = billing_v1.CloudBillingClient()
            
            cost_records = []
            
            # Note: GCP Billing API has limited cost data access
            # Production implementation should use BigQuery billing export
            projects = billing_client.list_project_billing_info(
                name=f"billingAccounts/{self.billing_account}"
            )
            
            for project in projects:
                # This is a simplified implementation
                # Real implementation would query detailed billing data
                cost_record = CostRecord(
                    provider='gcp',
                    account_id=project.project_id,
                    service_name='compute',  # Placeholder
                    resource_id='unknown',
                    cost_amount=0.0,  # Would be fetched from actual billing data
                    currency='USD',
                    usage_date=start_date.strftime('%Y-%m-%d'),
                    usage_quantity=1.0,
                    usage_unit='units',
                    resource_tags={},
                    region='unknown',
                    billing_period=f"{start_date.strftime('%Y-%m')}"
                )
                cost_records.append(cost_record)
            
            logger.info(f"Retrieved {len(cost_records)} GCP cost records from {start_date} to {end_date}")
            return cost_records
            
        except Exception as e:
            logger.error(f"Error fetching GCP cost data: {str(e)}")
            raise
    
    async def _get_cost_data_from_bigquery(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Fetch detailed cost data from BigQuery billing export"""
        try:
            from google.cloud import bigquery
            
            client = bigquery.Client(project=self.project_id)
            
            query = f"""
            SELECT
                service.description as service_name,
                sku.description as sku_description,
                resource.name as resource_name,
                location.location as region,
                cost,
                currency,
                usage_start_time,
                usage_end_time,
                usage.amount as usage_amount,
                usage.unit as usage_unit,
                labels
            FROM `{self.project_id}.billing_export.gcp_billing_export_v1_{self.billing_account.replace('-', '_')}`
            WHERE usage_start_time >= '{start_date.strftime('%Y-%m-%d')}'
              AND usage_end_time <= '{end_date.strftime('%Y-%m-%d')}'
              AND cost > 0
            ORDER BY usage_start_time DESC
            """
            
            results = client.query(query)
            
            cost_records = []
            for row in results:
                cost_record = CostRecord(
                    provider='gcp',
                    account_id=self.project_id,
                    service_name=row.service_name,
                    resource_id=row.resource_name or 'unknown',
                    cost_amount=float(row.cost),
                    currency=row.currency,
                    usage_date=row.usage_start_time.strftime('%Y-%m-%d'),
                    usage_quantity=float(row.usage_amount) if row.usage_amount else 1.0,
                    usage_unit=row.usage_unit or 'units',
                    resource_tags=dict(row.labels) if row.labels else {},
                    region=row.region or 'unknown',
                    billing_period=f"{start_date.strftime('%Y-%m')}"
                )
                cost_records.append(cost_record)
            
            return cost_records
            
        except Exception as e:
            logger.error(f"Error fetching GCP cost data from BigQuery: {str(e)}")
            return []
    
    def _has_bigquery_export(self) -> bool:
        """Check if BigQuery billing export is configured"""
        # This would check if the billing export table exists
        # For now, return False to use basic API
        return False
    
    async def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get GCP cost optimization recommendations"""
        try:
            from google.cloud import recommender_v1
            
            recommender_client = recommender_v1.RecommenderClient()
            
            recommendations = []
            
            # Get Compute Engine recommendations
            parent = f"projects/{self.project_id}/locations/global/recommenders/google.compute.instance.MachineTypeRecommender"
            
            for recommendation in recommender_client.list_recommendations(parent=parent):
                recommendations.append({
                    'type': 'machine_type_optimization',
                    'service': 'Compute Engine',
                    'recommendation': recommendation.description,
                    'estimated_savings': recommendation.primary_impact.cost_projection.cost.units if recommendation.primary_impact else 0,
                    'confidence': recommendation.priority
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching GCP recommendations: {str(e)}")
            return []
    
    async def validate_credentials(self) -> bool:
        """Validate GCP credentials"""
        try:
            from google.cloud import billing_v1
            
            billing_client = billing_v1.CloudBillingClient()
            # Try to list billing accounts as a credential test
            list(billing_client.list_billing_accounts())
            logger.info(f"GCP credentials valid for project: {self.project_id}")
            return True
        except Exception as e:
            logger.error(f"GCP credential validation failed: {str(e)}")
            return False

class MultiCloudCostManager:
    """Unified manager for all cloud provider cost data"""
    
    def __init__(self):
        self.providers: Dict[str, CloudProviderBase] = {}
        self.setup_providers()
    
    def setup_providers(self):
        """Initialize cloud provider connections"""
        # AWS
        aws_creds = ProviderCredentials(
            provider='aws',
            credentials={
                'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                'region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
                'account_id': os.getenv('AWS_ACCOUNT_ID')
            },
            enabled=bool(os.getenv('AWS_ACCESS_KEY_ID'))
        )
        
        if aws_creds.enabled:
            self.providers['aws'] = AWSCostProvider(aws_creds)
        
        # Azure
        azure_creds = ProviderCredentials(
            provider='azure',
            credentials={
                'tenant_id': os.getenv('AZURE_TENANT_ID'),
                'client_id': os.getenv('AZURE_CLIENT_ID'),
                'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
                'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID')
            },
            enabled=bool(os.getenv('AZURE_TENANT_ID'))
        )
        
        if azure_creds.enabled:
            self.providers['azure'] = AzureCostProvider(azure_creds)
        
        # GCP
        gcp_creds = ProviderCredentials(
            provider='gcp',
            credentials={
                'project_id': os.getenv('GCP_PROJECT_ID'),
                'billing_account': os.getenv('GCP_BILLING_ACCOUNT'),
                'service_account_key': json.loads(os.getenv('GCP_SERVICE_ACCOUNT_KEY', '{}'))
            },
            enabled=bool(os.getenv('GCP_PROJECT_ID'))
        )
        
        if gcp_creds.enabled:
            self.providers['gcp'] = GCPCostProvider(gcp_creds)
    
    async def get_unified_cost_data(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Get cost data from all enabled providers"""
        all_cost_records = []
        
        for provider_name, provider in self.providers.items():
            try:
                logger.info(f"Fetching cost data from {provider_name}")
                records = await provider.get_cost_data(start_date, end_date)
                all_cost_records.extend(records)
                logger.info(f"Retrieved {len(records)} records from {provider_name}")
            except Exception as e:
                logger.error(f"Failed to fetch cost data from {provider_name}: {str(e)}")
        
        logger.info(f"Total cost records retrieved: {len(all_cost_records)}")
        return all_cost_records
    
    async def get_unified_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get optimization recommendations from all providers"""
        all_recommendations = {}
        
        for provider_name, provider in self.providers.items():
            try:
                logger.info(f"Fetching recommendations from {provider_name}")
                recommendations = await provider.get_recommendations()
                all_recommendations[provider_name] = recommendations
                logger.info(f"Retrieved {len(recommendations)} recommendations from {provider_name}")
            except Exception as e:
                logger.error(f"Failed to fetch recommendations from {provider_name}: {str(e)}")
                all_recommendations[provider_name] = []
        
        return all_recommendations
    
    async def validate_all_credentials(self) -> Dict[str, bool]:
        """Validate credentials for all providers"""
        validation_results = {}
        
        for provider_name, provider in self.providers.items():
            try:
                is_valid = await provider.validate_credentials()
                validation_results[provider_name] = is_valid
            except Exception as e:
                logger.error(f"Credential validation failed for {provider_name}: {str(e)}")
                validation_results[provider_name] = False
        
        return validation_results
    
    def get_cost_data_as_dataframe(self, cost_records: List[CostRecord]) -> pd.DataFrame:
        """Convert cost records to pandas DataFrame for analysis"""
        data = [asdict(record) for record in cost_records]
        return pd.DataFrame(data)
    
    def calculate_cost_summary(self, cost_records: List[CostRecord]) -> Dict[str, Any]:
        """Calculate cost summary statistics"""
        df = self.get_cost_data_as_dataframe(cost_records)
        
        summary = {
            'total_cost': df['cost_amount'].sum(),
            'cost_by_provider': df.groupby('provider')['cost_amount'].sum().to_dict(),
            'cost_by_service': df.groupby('service_name')['cost_amount'].sum().to_dict(),
            'cost_by_region': df.groupby('region')['cost_amount'].sum().to_dict(),
            'daily_cost_trend': df.groupby('usage_date')['cost_amount'].sum().to_dict(),
            'record_count': len(cost_records),
            'date_range': {
                'start': df['usage_date'].min(),
                'end': df['usage_date'].max()
            }
        }
        
        return summary

# Example usage
if __name__ == "__main__":
    import os
    import asyncio
    
    async def main():
        # Initialize the multi-cloud manager
        manager = MultiCloudCostManager()
        
        # Validate credentials
        validation_results = await manager.validate_all_credentials()
        print("Credential validation results:", validation_results)
        
        # Get cost data for the last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        cost_records = await manager.get_unified_cost_data(start_date, end_date)
        print(f"Retrieved {len(cost_records)} cost records")
        
        # Calculate summary
        if cost_records:
            summary = manager.calculate_cost_summary(cost_records)
            print("Cost summary:", json.dumps(summary, indent=2, default=str))
        
        # Get recommendations
        recommendations = await manager.get_unified_recommendations()
        print("Recommendations:", json.dumps(recommendations, indent=2, default=str))
    
    # Run the example
    asyncio.run(main())