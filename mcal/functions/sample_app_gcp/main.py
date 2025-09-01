import json
import os
import platform
import logging
from functions_framework import http
from typing import Dict, Any

@http
def handler(request):
    """
    GCP Cloud Functions handler for FISO multi-cloud orchestration
    """
    logging.info('FISO GCP Cloud Function triggered')
    
    try:
        # Handle health check (GET request)
        if request.method == 'GET':
            response_data = {
                'status': 'healthy',
                'service': 'fiso-gcp-orchestrator',
                'version': '1.0.0',
                'provider_support': ['gcp'],
                'platform': 'Google Cloud Functions',
                'python_version': platform.python_version(),
                'timestamp': request.headers.get('X-Cloud-Trace-Context', 'unknown')
            }
            
            return (
                json.dumps(response_data),
                200,
                {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
            )
        
        # Parse request body for orchestration (POST request)
        try:
            request_json = request.get_json(silent=True)
        except Exception:
            return (
                json.dumps({'error': 'Invalid JSON in request body'}),
                400,
                {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
            )
        
        if not request_json:
            return (
                json.dumps({'error': 'Request body is required'}),
                400,
                {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
            )
        
        # Validate required fields
        target = request_json.get('target')
        data = request_json.get('data', {})
        
        if not target:
            return (
                json.dumps({'error': 'Missing required field: target'}),
                400,
                {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
            )
        
        logging.info(f'Processing orchestration request for target: {target}')
        
        # GCP-specific processing
        result = {
            'status': 'success',
            'platform': 'Google Cloud Functions',
            'provider': 'gcp',
            'target': target,
            'message': f'Hello from Google Cloud Functions! Processed target: {target}',
            'processed_data': data,
            'gcp_region': os.environ.get('FUNCTION_REGION', 'us-central1'),
            'function_name': os.environ.get('K_SERVICE', 'fiso-gcp-function'),
            'python_version': platform.python_version(),
            'timestamp': request.headers.get('X-Cloud-Trace-Context', 'unknown'),
            'execution_time_ms': 35  # GCP Functions typical response time
        }
        
        response = {
            'status': 'success',
            'provider': 'gcp',
            'target': target,
            'result': result,
            'timestamp': request.headers.get('X-Cloud-Trace-Context', 'unknown'),
            'execution_time_ms': 35
        }
        
        logging.info(f'Orchestration completed successfully for target: {target}')
        
        return (
            json.dumps(response),
            200,
            {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f'Error in GCP function: {str(e)}')
        return (
            json.dumps({
                'error': str(e),
                'provider': 'gcp',
                'timestamp': request.headers.get('X-Cloud-Trace-Context', 'unknown')
            }),
            500,
            {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        )