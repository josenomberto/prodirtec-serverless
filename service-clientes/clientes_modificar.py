import boto3
import os
import json

def lambda_handler(event, context):
    """
    Actualiza los detalles de un cliente.
    """
    dynamodb = boto3.resource('dynamodb')
    #table_name = os.environ.get('CLIENTS_TABLE_NAME', 'ClientsTable-dev') # Usar una variable de entorno
    table_name = os.environ.get('CLIENTS_TABLE_NAME') # Usar una variable de entorno
    clients_table = dynamodb.Table(table_name)

    body = event['body']
    client_id = body.get('cliente_id')

    update_expression = "SET "
    expression_attribute_values = {}
    expression_attribute_names = {} # Para evitar problemas con nombres reservados como 'name'

    for key, value in body.items():
        if key != 'cliente_id':
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
        'body': response['Attributes'],
        'headers': {'Content-Type': 'application/json'}
    }