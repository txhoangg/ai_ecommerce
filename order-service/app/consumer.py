import datetime
import pika
import json
import logging
import time
import requests
import jwt
from django.conf import settings
from app.rabbitmq import publish_command

logger = logging.getLogger(__name__)

SHARED_SECRET = "super-secret-jwt-key"


def _service_headers():
    payload = {
        'sub': 'order-service',
        'role': 'service',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15),
    }
    token = jwt.encode(payload, SHARED_SECRET, algorithm='HS256')
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }


def _log_purchase_interactions(customer_id, items):
    if not customer_id:
        return

    for item in items or []:
        book_id = item.get('book_id')
        if not book_id:
            continue
        try:
            requests.post(
                f"{settings.AI_SERVICE_URL}/api/graph/interaction/",
                json={
                    'user_id': int(customer_id),
                    'book_id': int(book_id),
                    'event_type': 'purchase',
                },
                headers=_service_headers(),
                timeout=5,
            )
        except Exception as e:
            print(f"[Order Orchestrator] Warning: could not log purchase interaction: {e}")


def callback(ch, method, properties, body):
    payload = json.loads(body)
    routing_key = method.routing_key

    print(f"[Order Orchestrator] Received event: {routing_key} | order_id={payload.get('order_id')}")

    try:
        from app.models import Order
        order_id = payload.get('order_id')
        if not order_id:
            return

        order = Order.objects.get(id=order_id)

        if routing_key == 'payment.result':
            if payload.get('status') == 'success':
                # Payment reserved → update order to processing, then reserve inventory
                order.status = 'processing'
                order.save()
                print(f"[Order Orchestrator] Payment success → order {order_id} = processing. Reserving inventory...")
                publish_command('inventory.reserve', payload)
            else:
                order.status = 'cancelled'
                order.save()
                print(f"[Order Orchestrator] Payment failed → order {order_id} cancelled.")

        elif routing_key == 'inventory.result':
            if payload.get('status') == 'success':
                print(f"[Order Orchestrator] Inventory reserved → scheduling shipping for order {order_id}...")
                publish_command('ship.schedule', payload)
            else:
                order.status = 'cancelled'
                order.save()
                print(f"[Order Orchestrator] Inventory failed → refund payment for order {order_id}.")
                publish_command('payment.refund', payload)

        elif routing_key == 'ship.result':
            if payload.get('status') == 'success':
                # Shipping scheduled successfully → confirm order as shipped
                # (Saga complete: payment reserved, inventory deducted, shipping scheduled)
                order.status = 'shipped'
                order.save()
                print(f"[Order Orchestrator] Shipping scheduled → order {order_id} = shipped. Saga COMPLETE.")

                # NOW it is safe to clear the cart (Saga fully succeeded)
                customer_id = payload.get('customer_id')
                _log_purchase_interactions(customer_id, payload.get('items', []))
                if customer_id:
                    try:
                        requests.delete(
                            f"{settings.CART_SERVICE_URL}/api/carts/{customer_id}/",
                            timeout=5
                        )
                        print(f"[Order Orchestrator] Cart cleared for customer {customer_id}.")
                    except Exception as e:
                        print(f"[Order Orchestrator] Warning: could not clear cart: {e}")
            else:
                # Shipping failed → full compensating rollback
                order.status = 'cancelled'
                order.save()
                print(f"[Order Orchestrator] Shipping failed → reverting inventory + refunding payment for order {order_id}.")
                publish_command('inventory.revert', {'order_id': order.id, 'items': payload.get('items', [])})
                publish_command('payment.refund', {'order_id': order.id})

    except Exception as e:
        print(f"[Order Orchestrator] Error processing {routing_key}: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consuming():
    time.sleep(10)  # Wait for RabbitMQ to start
    for _ in range(5):
        try:
            params = pika.URLParameters('amqp://root:12345678@rabbitmq:5672/')
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.exchange_declare(exchange='saga_exchange', exchange_type='topic', durable=True)

            result = channel.queue_declare(queue='order_saga_queue', durable=True)
            queue_name = result.method.queue

            channel.queue_bind(exchange='saga_exchange', queue=queue_name, routing_key='payment.result')
            channel.queue_bind(exchange='saga_exchange', queue=queue_name, routing_key='inventory.result')
            channel.queue_bind(exchange='saga_exchange', queue=queue_name, routing_key='ship.result')

            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

            print(" [*] Order Orchestrator started consuming Saga results...")
            channel.start_consuming()
            break
        except Exception as e:
            print(f"RabbitMQ connection failed: {e}. Retrying in 5s...")
            time.sleep(5)
