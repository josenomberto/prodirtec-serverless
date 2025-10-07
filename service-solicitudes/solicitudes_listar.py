import json
import os
import boto3
import uuid
from datetime import datetime


def lambda_handler(event, context):
    """
    Listar todas las solicitude de cotización.
    """
    dynamodb = boto3.resource('dynamodb')
    #table_name = os.environ.get('REQUESTS_TABLE_NAME', 'QuoteRequests-dev')
    table_name = os.environ.get('REQUESTS_TABLE_NAME')
    requests_table = dynamodb.Table(table_name)

    # eventbridge = boto3.client('events')
    # #event_bus_name = os.environ.get('EVENT_BUS_NAME', 'ProdirtecBus-dev')
    # event_bus_name = os.environ.get('EVENT_BUS_NAME')

    # Lee todos los registros
    response = requests_table.scan() 
    items = response['Items']
    num_reg = response['Count']
    # Salida (json)
    return {
        'statusCode': 200,
        'body': items,
        # 'body': json.dumps(items),
        'headers': {'Content-Type': 'application/json'}
    }

