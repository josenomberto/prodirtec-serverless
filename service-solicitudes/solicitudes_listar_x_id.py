import boto3
import os
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    #table_name = os.environ.get('CLIENTS_TABLE_NAME', 'ClientsTable-dev') # Usar una variable de entorno
    table_name = os.environ.get('CLIENTS_TABLE_NAME') # Usar una variable de entorno
    clients_table = dynamodb.Table(table_name)
    # Lee todos los registros
    #response = clients_table.scan()

    path_parameters = event.get('path', {})
    client_id = path_parameters.get('cliente_id')
    response = clients_table.get_item(Key={'cliente_id': client_id})
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