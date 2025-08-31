import azure.functions as func
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Cesta k swagger.json, který je o úroveň výš
    swagger_file_path = os.path.join(os.path.dirname(__file__), '..', 'swagger.json')

    try:
        with open(swagger_file_path, 'r') as f:
            swagger_content = f.read()
        
        return func.HttpResponse(
            body=swagger_content,
            status_code=200,
            mimetype="application/json"
        )
    except FileNotFoundError:
        return func.HttpResponse(
            "swagger.json not found",
            status_code=404,
            mimetype="text/plain"
        )