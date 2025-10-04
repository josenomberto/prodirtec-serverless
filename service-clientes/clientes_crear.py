import boto3
import os
import json
import uuid
from datetime import datetime

def lambda_handler(event):
    """
    Crea un nuevo cliente.
    """
    dynamodb = boto3.resource('dynamodb')
    #table_name = os.environ.get('CLIENTS_TABLE_NAME', 'ClientsTable-dev') # Usar una variable de entorno
    table_name = os.environ.get('CLIENTS_TABLE_NAME') # Usar una variable de entorno
    clients_table = dynamodb.Table(table_name)

    body = json.loads(event['body'])
    new_client_id = str(uuid.uuid4())
    item = {
        'cliente_id': new_client_id,
        'nombre': body.get('nombre'),
        'apellido': body.get('apellido'),
        'email': body.get('email'),
        'telefono': body.get('telefono'),
        'empresa_razon_social': body.get('empresa_razon_social'),
        'cargo': body.get('cargo'),
        'fecha_registro': datetime.now().isoformat()
    }
    clients_table.put_item(Item=item)
    return {
        'statusCode': 201,
        'body': json.dumps({'cliente_id': new_client_id, 'message': 'Cliente creado exitosamente.'}),
        'headers': {'Content-Type': 'application/json'}
    }