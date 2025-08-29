import json
import platform

def handler(event, context):
    """
    AWS Lambda handler for the FISO Sample App.
    """
    print("FISO Sample App (AWS Lambda) was invoked!")
    
    # Log the incoming event for debugging
    print(f"Event: {json.dumps(event)}")
    
    response_data = {
        "message": "Hello from the FISO Sample App!",
        "platform": "AWS Lambda", 
        "python_version": platform.python_version()
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response_data)
    }
