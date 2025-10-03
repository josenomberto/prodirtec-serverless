# service-clientes/clientes_lambda.py
import json
import os
import boto3
import uuid
from datetime import datetime

# Inicialización de DynamoDB
# En un entorno Serverless, es mejor inicializar clientes fuera del handler
# para reutilizarlos entre invocaciones (cold start vs warm start)
dynamodb = boto3.resource('dynamodb')
#table_name = os.environ.get('CLIENTS_TABLE_NAME', 'ClientsTable-dev') # Usar una variable de entorno
table_name = os.environ.get('CLIENTS_TABLE_NAME') # Usar una variable de entorno
clients_table = dynamodb.Table(table_name)


def handler(event, context):
    """
    Maneja las solicitudes HTTP para el servicio de gestión de clientes.
    """
    print(f"Received event: {json.dumps(event)}")

    http_method = event.get('httpMethod')
    path_parameters = event.get('pathParameters', {})
    client_id = path_parameters.get('cliente_id') # Usa 'cliente_id' según el path en serverless.yml

    try:
        if http_method == 'POST':
            return create_client(event)
        elif http_method == 'GET' and client_id:
            return get_client(client_id)
        elif http_method == 'GET':
            return get_clients(event)
        elif http_method == 'PUT' and client_id:
            return update_client(client_id, event)
        elif http_method == 'DELETE' and client_id:
            return delete_client(client_id, event)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Método o ruta no soportada.'}),
                'headers': {'Content-Type': 'application/json'}
            }
    except Exception as e:
        print(f"Error processing request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error interno del servidor: {str(e)}'}),
            'headers': {'Content-Type': 'application/json'}
        }


def create_client(event):
    """
    Crea un nuevo cliente.
    """
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


def get_clients(event):
    # Lee todos los registros
    response = clients_table.scan() 
    items = response['Items']
    num_reg = response['Count']
    # Salida (json)
    return {
        'statusCode': 200,
        'body': json.dumps(items),
        'headers': {'Content-Type': 'application/json'}
    }


def get_client(client_id):
    """
    Obtiene los detalles de un cliente por su ID.
    """
    response = clients_table.get_item(Key={'cliente_id': client_id})
    item = response.get('Item')
    if item:
        return {
            'statusCode': 200,
            'body': json.dumps(item),
            'headers': {'Content-Type': 'application/json'}
        }
    return {
        'statusCode': 404,
        'body': json.dumps({'message': 'Cliente no encontrado.'}),
        'headers': {'Content-Type': 'application/json'}
    }


def update_client(client_id, event):
    """
    Actualiza los detalles de un cliente.
    """
    body = json.loads(event['body'])
    update_expression = "SET "
    expression_attribute_values = {}
    expression_attribute_names = {} # Para evitar problemas con nombres reservados como 'name'

    for key, value in body.items():
        if key != 'client_id':
            attr_name_key = f'#{key}' # Usar un nombre de atributo de expresión
            attr_value_key = f':{key}' # Usar un valor de atributo de expresión
            
            update_expression += f"{attr_name_key} = {attr_value_key}, "
            expression_attribute_values[attr_value_key] = value
            expression_attribute_names[attr_name_key] = key # Mapear el nombre real

    update_expression = update_expression.rstrip(', ')

    if not expression_attribute_values:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'No se proporcionaron campos para actualizar.'}),
            'headers': {'Content-Type': 'application/json'}
        }

    response = clients_table.update_item(
        Key={'cliente_id': client_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names,
        ReturnValues='ALL_NEW'
    )
    return {
        'statusCode': 200,
        'body': json.dumps(response['Attributes']),
        'headers': {'Content-Type': 'application/json'}
    }


def delete_client(client_id):
    """
    Borra un cliente por su ID.
    """
    response = clients_table.get_item(Key={'cliente_id': client_id})
    item = response.get('Item')
    if item:
        response = clients_table.delete_item(Key={'cliente_id': client_id})
        return {
            'statusCode': 200,
            'body': json.dumps(response),
            'headers': {'Content-Type': 'application/json'}
        }
    return {
        'statusCode': 404,
        'body': json.dumps({'message': 'Cliente Borrado.'}),
        'headers': {'Content-Type': 'application/json'}
    }
