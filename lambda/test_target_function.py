import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    Simple test function for FISO orchestration testing
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract data from event
        data = event.get('data', {})
        source = event.get('source', 'unknown')
        
        # Simple processing
        message = f"Hello from FISO target function! Received data from {source}"
        
        response = {
            'status': 'success',
            'message': message,
            'processed_data': data,
            'timestamp': context.aws_request_id,
            'function_name': context.function_name
        }
        
        logger.info(f"Returning response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        logger.error(f"Error in target function: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': context.aws_request_id
        }
