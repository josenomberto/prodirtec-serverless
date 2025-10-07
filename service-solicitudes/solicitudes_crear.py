import json
import os
import boto3
import uuid
from datetime import datetime


def lambda_handler(event, context):
    """
    Crea una nueva solicitud de cotización y emite un evento.
    """

    dynamodb = boto3.resource('dynamodb')
    #table_name = os.environ.get('REQUESTS_TABLE_NAME', 'QuoteRequests-dev')
    table_name = os.environ.get('REQUESTS_TABLE_NAME')
    requests_table = dynamodb.Table(table_name)

    # eventbridge = boto3.client('events')
    # #event_bus_name = os.environ.get('EVENT_BUS_NAME', 'ProdirtecBus-dev')
    # event_bus_name = os.environ.get('EVENT_BUS_NAME')

    # body = json.loads(event['body'])
    body = event['body']
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

    # # Publicar evento a EventBridge
    # eventbridge.put_events(
    #     Entries=[
    #         {
    #             'Source': 'prodirtec.cotizaciones.solicitudes',
    #             'DetailType': 'CotizacionSolicitada',
    #             'Detail': json.dumps({'solicitud_id': new_solicitud_id, 'client_id': item['client_id'], 'servicio_solicitado': item['servicio_solicitado']}),
    #             'EventBusName': event_bus_name
    #         }
    #     ]
    # )

    return {
        'statusCode': 202,
        'body': json.dumps({'solicitud_id': new_solicitud_id, 'message': 'Su solicitud ha sido recibida y está siendo procesada.'}),
        'headers': {'Content-Type': 'application/json'}
    }
