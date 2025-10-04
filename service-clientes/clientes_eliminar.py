import boto3
import os
import json

def lambda_handler(event, context):
    """
    Borra un cliente por su ID.
    """
    dynamodb = boto3.resource('dynamodb')
    #table_name = os.environ.get('CLIENTS_TABLE_NAME', 'ClientsTable-dev') # Usar una variable de entorno
    table_name = os.environ.get('CLIENTS_TABLE_NAME') # Usar una variable de entorno
    clients_table = dynamodb.Table(table_name)
    # Lee el id de cliente
    body = event['body']
    client_id = body.get('cliente_id')
    # Busca la entrada en la tabla con el id de cliente
    response = clients_table.get_item(Key={'cliente_id': client_id})
    item = response.get('Item')
    if item:
        response = clients_table.delete_item(Key={'cliente_id': client_id})
        return {
            'statusCode': 200,
            'body': response,
            'headers': {'Content-Type': 'application/json'}
        }
    return {
        'statusCode': 404,
        'body': json.dumps({'message': 'Cliente Borrado.'}),
        'headers': {'Content-Type': 'application/json'}
    }