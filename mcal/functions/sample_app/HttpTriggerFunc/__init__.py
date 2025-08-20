import logging
import json
import platform
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    return func.HttpResponse(
        body=json.dumps({
            "message": "Hello from the FISO Sample App!",
            "platform": "Azure Functions",
            "python_version": platform.python_version()
        }),
        status_code=200,
        mimetype="application/json"
    )