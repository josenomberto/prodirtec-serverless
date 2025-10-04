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

    path_parameters = event.get('pathParameters', {})
    client_id = path_parameters.get('cliente_id')
    response = clients_table.get_item(Key={'cliente_id': client_id})
    items = response['Items']
    num_reg = response['Count']
    # Salida (json)
    return {
        'statusCode': 200,
        'body': items,
        # 'body': json.dumps(items),
        'headers': {'Content-Type': 'application/json'}
    }