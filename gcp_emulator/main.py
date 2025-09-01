import json
import logging
import os
import platform
from typing import Dict, Any
import functions_framework
from flask import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def handler(request: Request) -> str:
    """
    GCP Cloud Functions handler for FISO multi-cloud orchestration (Local Emulator)
    """
    logging.info('FISO GCP Function (Emulator) triggered')
    
    try:
        # Handle health check (GET request)
        if request.method == 'GET':
            response_data = {
                'status': 'healthy',
                'service': 'fiso-gcp-orchestrator-emulator',
                'version': '1.0.0',
                'provider_support': ['gcp'],
                'platform': 'GCP Cloud Functions (Local Emulator)',
                'python_version': platform.python_version(),
                'emulator': True,
                'timestamp': 'emulator-timestamp'
            }
            
            return json.dumps(response_data)
        
        # Parse request body for orchestration (POST request)
        try:
            req_body = request.get_json()
        except ValueError:
            return json.dumps({
                'error': 'Invalid JSON in request body',
                'emulator': True
            }), 400
        
        if not req_body:
            return json.dumps({
                'error': 'Request body is required',
                'emulator': True
            }), 400
        
        # Validate required fields
        target = req_body.get('target')
        data = req_body.get('data', {})
        
        if not target:
            return json.dumps({
                'error': 'Missing required field: target',
                'emulator': True
            }), 400
        
        logging.info(f'Processing orchestration request for target: {target}')
        
        # GCP-specific processing (emulated)
        result = {
            'status': 'success',
            'platform': 'GCP Cloud Functions (Local Emulator)',
            'provider': 'gcp',
            'target': target,
            'message': f'Hello from GCP Cloud Functions Emulator! Processed target: {target}',
            'processed_data': data,
            'gcp_region': 'us-central1-emulator',
            'function_name': 'fiso-gcp-function-emulator',
            'python_version': platform.python_version(),
            'emulator': True,
            'timestamp': 'emulator-timestamp',
            'execution_time_ms': 25  # Emulated response time
        }
        
        response = {
            'status': 'success',
            'provider': 'gcp',
            'target': target,
            'result': result,
            'emulator': True,
            'timestamp': 'emulator-timestamp',
            'execution_time_ms': 25
        }
        
        logging.info(f'Orchestration completed successfully for target: {target}')
        
        return json.dumps(response)
        
    except Exception as e:
        logging.error(f'Error in GCP function emulator: {str(e)}')
        return json.dumps({
            'error': str(e),
            'provider': 'gcp',
            'emulator': True,
            'timestamp': 'emulator-timestamp'
        }), 500

if __name__ == '__main__':
    # For local testing
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/', methods=['GET', 'POST'])
    def local_handler():
        from flask import request
        return handler(request)
    
    print("Starting GCP Functions Emulator on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
