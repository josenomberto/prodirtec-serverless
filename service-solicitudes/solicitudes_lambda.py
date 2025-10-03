# service-solicitudes/solicitudes_lambda.py
import json
import os
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
#table_name = os.environ.get('REQUESTS_TABLE_NAME', 'QuoteRequests-dev')
table_name = os.environ.get('REQUESTS_TABLE_NAME')
requests_table = dynamodb.Table(table_name)

eventbridge = boto3.client('events')
#event_bus_name = os.environ.get('EVENT_BUS_NAME', 'ProdirtecBus-dev')
event_bus_name = os.environ.get('EVENT_BUS_NAME')

def handler(event, context):
    """
    Maneja las solicitudes HTTP para el servicio de solicitud de cotización.
    """
    print(f"Received event: {json.dumps(event)}")

    http_method = event.get('httpMethod')
    path_parameters = event.get('pathParameters', {})
    solicitud_id = path_parameters.get('solicitud_id')

    try:
        if http_method == 'POST':
            return create_quote_request(event)
        elif http_method == 'GET' and solicitud_id:
            return get_quote_request(solicitud_id)
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


def create_quote_request(event):
    """
    Crea una nueva solicitud de cotización y emite un evento.
    """
    body = json.loads(event['body'])
    new_solicitud_id = str(uuid.uuid4())
    item = {
        'solicitud_id': new_solicitud_id,
        'client_id': body.get('client_id'), # Usar client_id consistente con el servicio de clientes
        'servicio_solicitado': body.get('servicio_solicitado'),
        'detalles': body.get('detalles'),
        'presupuesto_estimado': body.get('presupuesto_estimado'),
        'fecha_requerida': body.get('fecha_requerida'),
        'estado': 'PENDIENTE_COTIZACION',
        'fecha_solicitud': datetime.now().isoformat(),
        'fecha_ultima_actualizacion': datetime.now().isoformat()
    }
    requests_table.put_item(Item=item)

    # Publicar evento a EventBridge
    eventbridge.put_events(
        Entries=[
            {
                'Source': 'prodirtec.cotizaciones.solicitudes',
                'DetailType': 'CotizacionSolicitada',
                'Detail': json.dumps({'solicitud_id': new_solicitud_id, 'client_id': item['client_id'], 'servicio_solicitado': item['servicio_solicitado']}),
                'EventBusName': event_bus_name
            }
        ]
    )

    return {
        'statusCode': 202,
        'body': json.dumps({'solicitud_id': new_solicitud_id, 'message': 'Su solicitud ha sido recibida y está siendo procesada.'}),
        'headers': {'Content-Type': 'application/json'}
    }


def get_quote_request(solicitud_id):
    """
    Obtiene el estado de una solicitud de cotización.
    """
    response = requests_table.get_item(Key={'solicitud_id': solicitud_id})
    item = response.get('Item')
    if item:
        return {
            'statusCode': 200,
            'body': json.dumps(item),
            'headers': {'Content-Type': 'application/json'}
        }
    return {
        'statusCode': 404,
        'body': json.dumps({'message': 'Solicitud de cotización no encontrada.'}),
        'headers': {'Content-Type': 'application/json'}
    }