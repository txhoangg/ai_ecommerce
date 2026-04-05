import pika
import json
import logging
import time
import uuid

from app.rabbitmq import publish_command

logger = logging.getLogger(__name__)

def process_shipping(ch, method, properties, body):
    payload = json.loads(body)
    routing_key = method.routing_key
    print(f"[Ship Service] Received: {routing_key}")

    from app.models import Shipping, ShippingTracking

    if routing_key == 'ship.schedule':
        order_id = payload.get('order_id')
        customer_id = payload.get('customer_id')
        address = payload.get('address')
        ship_method = payload.get('ship_method') or payload.get('method', 'standard')

        try:
            tracking_number = f"TRK-{order_id}-{uuid.uuid4().hex[:8].upper()}"

            from decimal import Decimal
            fee_map = {
                'standard': Decimal('5.00'),
                'express': Decimal('15.00'),
                'overnight': Decimal('25.00'),
            }
            fee = fee_map.get(ship_method, Decimal('5.00'))

            shipping = Shipping.objects.create(
                order_id=order_id,
                customer_id=customer_id,
                method=ship_method,
                fee=fee,
                address=address,
                tracking_number=tracking_number,
                status='pending'
            )

            ShippingTracking.objects.create(
                shipping=shipping,
                status='pending',
                location='Warehouse',
                message='Shipping scheduled via Saga'
            )
            
            payload['status'] = 'success'
            payload['tracking_number'] = tracking_number
            print(f"[Ship Service] Scheduled shipping for order {order_id}")
            
        except Exception as e:
            payload['status'] = 'failed'
            print(f"[Ship Service] Failed to schedule shipping for order {order_id}: {e}")
            
        publish_command('ship.result', payload)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    time.sleep(12)
    for _ in range(5):
        try:
            params = pika.URLParameters('amqp://root:12345678@rabbitmq:5672/')
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            channel.exchange_declare(exchange='saga_exchange', exchange_type='topic', durable=True)
            result = channel.queue_declare(queue='ship_saga_queue', durable=True)
            queue_name = result.method.queue
            
            channel.queue_bind(exchange='saga_exchange', queue=queue_name, routing_key='ship.schedule')
            
            channel.basic_consume(queue=queue_name, on_message_callback=process_shipping, auto_ack=False)
            
            print(" [*] Ship Service started consuming...")
            channel.start_consuming()
            break
        except Exception as e:
            print(f"RabbitMQ connection failed: {e}. Retrying...")
            time.sleep(5)
