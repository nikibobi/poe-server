import logging
import json
import azure.functions as func

from .fetch import fetch
from .compute import compute

def main(req: func.HttpRequest) -> func.HttpResponse:

    params = req.get_json() if req.method == 'POST' else req.params

    if not params.get('user'):
        logging.warn('missing user parameter')
        return func.HttpResponse(
             'Please pass a user on the query string',
             status_code=400
        )

    try:
        items = fetch(**params)
        results = compute(items, **params)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse('Error processing data', status_code=500)
    else:
        headers = {
            'Content-type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
        return func.HttpResponse(json.dumps(results), headers = headers)
