import json
import boto3
import subprocess
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS clients
lambda_client = boto3.client('lambda')

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    AWS Lambda handler for FISO multi-cloud orchestration
    """
    try:
        # Handle health check requests
        if 'httpMethod' in event and event['httpMethod'] == 'GET':
            if event.get('path') == '/health':
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'status': 'healthy',
                        'service': 'fiso-lambda-orchestrator',
                        'version': '1.0.0',
                        'provider_support': ['aws'],
                        'timestamp': getattr(context, 'aws_request_id', 'unknown')
                    })
                }
        
        # Extract request data for orchestration
        if 'body' in event:
            # API Gateway event
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct Lambda invocation
            body = event
        
        # Validate required fields
        required_fields = ['target', 'data']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': f'Missing required field: {field}',
                        'timestamp': getattr(context, 'aws_request_id', 'unknown')
                    })
                }
        
        target = body['target']
        data = body['data']
        
        logger.info(f"Processing orchestration request for target: {target}")
        
        # Get policy from environment or use default
        policy = {
            'default_provider': os.getenv('DEFAULT_PROVIDER', 'aws'),
            'cost_threshold': float(os.getenv('COST_THRESHOLD', '0.10')),
            'latency_threshold': int(os.getenv('LATENCY_THRESHOLD', '5000'))
        }
        
        # Intelligent routing logic
        selected_provider = intelligent_routing(policy)
        
        # Execute the function based on selected provider
        if selected_provider == 'aws':
            result = invoke_aws_function(target, data)
        elif selected_provider == 'azure':
            result = invoke_azure_function(target, data)
        elif selected_provider == 'gcp':
            result = invoke_gcp_function(target, data)
        else:
            # Default to AWS if provider not recognized
            logger.warning(f"Unknown provider {selected_provider}, defaulting to AWS")
            result = invoke_aws_function(target, data)
        
        # Prepare response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'success',
                'provider': selected_provider,
                'target': target,
                'result': result,
                'timestamp': getattr(context, 'aws_request_id', 'unknown'),
                'execution_time_ms': result.get('execution_time', 0)
            })
        }
        
        logger.info(f"Orchestration completed successfully for target: {target}")
        return response
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'timestamp': getattr(context, 'aws_request_id', 'unknown')
            })
        }

def intelligent_routing(policy: Dict[str, Any]) -> str:
    """
    Determine the best cloud provider based on policy and current conditions
    """
    # For this Lambda version, we'll use AWS by default
    # In the future, this could include cost analysis, latency checking, etc.
    default_provider = policy.get('default_provider', 'aws')
    
    logger.info(f"Intelligent routing selected: {default_provider}")
    return default_provider

def invoke_aws_function(target: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke an AWS Lambda function
    """
    try:
        # Get the AWS function name from environment or use target
        function_name = os.getenv('AWS_TARGET_FUNCTION', target)
        
        # Prepare payload
        payload = {
            'data': data,
            'source': 'fiso-orchestrator'
        }
        
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Parse response
        response_payload = json.loads(response['Payload'].read())
        
        return {
            'status': 'success',
            'data': response_payload,
            'execution_time': response.get('Duration', 0),
            'provider': 'aws'
        }
        
    except Exception as e:
        logger.error(f"Error invoking AWS function {target}: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'provider': 'aws'
        }

def invoke_azure_function(target: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke an Azure Function
    """
    try:
        import requests
        
        # Get Azure function URL from environment
        azure_function_url = os.getenv('AZURE_FUNCTION_URL', 'https://your-azure-function.azurewebsites.net/api/HttpTriggerFunc')
        
        # Prepare payload
        payload = {
            'data': data,
            'source': 'fiso-orchestrator',
            'target': target
        }
        
        # Set headers
        headers = {
            'Content-Type': 'application/json',
            'x-functions-key': os.getenv('AZURE_FUNCTION_KEY', '')
        }
        
        # Make HTTP request to Azure Function
        response = requests.post(
            azure_function_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        return {
            'status': 'success',
            'data': response_data,
            'execution_time': response.elapsed.total_seconds() * 1000,
            'provider': 'azure'
        }
        
    except Exception as e:
        logger.error(f"Error invoking Azure function {target}: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'provider': 'azure'
        }

def invoke_gcp_function(target: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke a Google Cloud Function
    """
    try:
        import requests
        
        # Get GCP function URL from environment
        gcp_function_url = os.getenv('GCP_FUNCTION_URL', 'https://your-region-your-project.cloudfunctions.net/fiso-function')
        
        # Prepare payload
        payload = {
            'data': data,
            'source': 'fiso-orchestrator',
            'target': target
        }
        
        # Set headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add authentication if available
        gcp_token = os.getenv('GCP_FUNCTION_TOKEN')
        if gcp_token:
            headers['Authorization'] = f'Bearer {gcp_token}'
        
        # Make HTTP request to GCP Function
        response = requests.post(
            gcp_function_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        return {
            'status': 'success',
            'data': response_data,
            'execution_time': response.elapsed.total_seconds() * 1000,
            'provider': 'gcp'
        }
        
    except Exception as e:
        logger.error(f"Error invoking GCP function {target}: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'provider': 'gcp'
        }
