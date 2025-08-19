import json
import platform

def handler(event, context):
    """
    A simple handler that returns a welcome message.
    """
    print("FISO Sample App was invoked!")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Hello from the FISO Sample App!",
            "platform": "AWS Lambda", # We will make this dynamic later
            "python_version": platform.python_version()
        })
    }