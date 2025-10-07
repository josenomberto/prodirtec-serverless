import boto3
import os
import json

def lambda_handler(event, context):
    """
    Listar solicitud de cotización por id de solicitud.
    """
    dynamodb = boto3.resource('dynamodb')
    #table_name = os.environ.get('REQUESTS_TABLE_NAME', 'QuoteRequests-dev')
    table_name = os.environ.get('REQUESTS_TABLE_NAME')
    requests_table = dynamodb.Table(table_name)

    # eventbridge = boto3.client('events')
    # #event_bus_name = os.environ.get('EVENT_BUS_NAME', 'ProdirtecBus-dev')
    # event_bus_name = os.environ.get('EVENT_BUS_NAME')

    path_parameters = event.get('path', {})
    request_id = path_parameters.get('solicitud_id')
    response = requests_table.get_item(Key={'solicitud_id': request_id})
    item = response['Item']
    # Salida (json)
    return {
        'statusCode': 200,
        'body': item,
        # 'body': json.dumps(items),
        # 'headers': {'Content-Type': 'application/json'}
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Or specific origin like 'http://localhost:3000'
            #'Access-Control-Allow-Credentials': True, # If using credentials like cookies
        }
    }
