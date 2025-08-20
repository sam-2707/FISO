import json
import platform
from functions_framework import http

@http
def handler(request):
    """
    A simple handler for Google Cloud Functions that returns a welcome message.
    """
    print("FISO Sample App (GCP) was invoked!")

    data = {
        "message": "Hello from the FISO Sample App!",
        "platform": "Google Cloud Functions",
        "python_version": platform.python_version()
    }

    return (json.dumps(data), 200, {'Content-Type': 'application/json'})