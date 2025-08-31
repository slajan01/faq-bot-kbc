import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    question = req.params.get('q')
    if not question:
        return func.HttpResponse(
             json.dumps({"answer": "Please provide a query."}),
             status_code=400,
             mimetype="application/json"
        )

    # Zde přijde v budoucnu napojení na vaši databázi.
    # Prozatím vracíme testovací odpověď.
    answer = f"Testovací odpověď z Azure Function pro dotaz: '{question}'"

    return func.HttpResponse(
        json.dumps({"answer": answer}),
        status_code=200,
        mimetype="application/json"
    )