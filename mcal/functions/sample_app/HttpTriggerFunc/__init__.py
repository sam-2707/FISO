import json
import logging
import os
import platform
import azure.functions as func
from typing import Dict, Any

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Functions handler for FISO multi-cloud orchestration
    """
    logging.info('FISO Azure Function triggered')
    
    try:
        # Handle health check (GET request)
        if req.method == 'GET':
            response_data = {
                'status': 'healthy',
                'service': 'fiso-azure-orchestrator',
                'version': '1.0.0',
                'provider_support': ['azure'],
                'platform': 'Azure Functions',
                'python_version': platform.python_version(),
                'timestamp': req.headers.get('x-ms-request-id', 'unknown')
            }
            
            return func.HttpResponse(
                json.dumps(response_data),
                status_code=200,
                headers={'Content-Type': 'application/json'}
            )
        
        # Parse request body for orchestration (POST request)
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({'error': 'Invalid JSON in request body'}),
                status_code=400,
                headers={'Content-Type': 'application/json'}
            )
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({'error': 'Request body is required'}),
                status_code=400,
                headers={'Content-Type': 'application/json'}
            )
        
        # Validate required fields
        target = req_body.get('target')
        data = req_body.get('data', {})
        
        if not target:
            return func.HttpResponse(
                json.dumps({'error': 'Missing required field: target'}),
                status_code=400,
                headers={'Content-Type': 'application/json'}
            )
        
        logging.info(f'Processing orchestration request for target: {target}')
        
        # Azure-specific processing
        result = {
            'status': 'success',
            'platform': 'Azure Functions',
            'provider': 'azure',
            'target': target,
            'message': f'Hello from Azure Functions! Processed target: {target}',
            'processed_data': data,
            'azure_region': os.environ.get('WEBSITE_SITE_NAME', 'azure-eastus'),
            'function_name': os.environ.get('WEBSITE_SITE_NAME', 'fiso-azure-function'),
            'python_version': platform.python_version(),
            'timestamp': req.headers.get('x-ms-request-id', 'unknown'),
            'execution_time_ms': 45  # Azure Functions typical response time
        }
        
        response = {
            'status': 'success',
            'provider': 'azure',
            'target': target,
            'result': result,
            'timestamp': req.headers.get('x-ms-request-id', 'unknown'),
            'execution_time_ms': 45
        }
        
        logging.info(f'Orchestration completed successfully for target: {target}')
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except Exception as e:
        logging.error(f'Error in Azure function: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                'error': str(e),
                'provider': 'azure',
                'timestamp': req.headers.get('x-ms-request-id', 'unknown')
            }),
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )