import pika
import json
import logging
import time

from app.rabbitmq import publish_command

logger = logging.getLogger(__name__)

def process_payment(ch, method, properties, body):
    payload = json.loads(body)
    routing_key = method.routing_key
    print(f"[Pay Service] Received: {routing_key}")

    from app.models import Payment, PaymentTransaction

    if routing_key == 'order.created':
        order_id = payload.get('order_id')
        amount = payload.get('amount')
        pay_method = payload.get('method')

        payment = Payment.objects.create(
            order_id=order_id,
            amount=amount,
            method=pay_method,
            status='processing'
        )

        if pay_method in ('cash', 'cash_on_delivery'):
            payment.status = 'pending'
            transaction_status = 'pending'
        else:
            payment.status = 'completed'
            transaction_status = 'success'

        payment.save()

        PaymentTransaction.objects.create(
            payment=payment,
            transaction_type='charge',
            amount=amount,
            status=transaction_status,
            message=f'Processed via {pay_method}'
        )

        payload['status'] = 'success'
        print(f"[Pay Service] Processed payment for order {order_id}. Emitting payment.result")

        publish_command('payment.result', payload)

    elif routing_key == 'payment.refund':
        order_id = payload.get('order_id')
        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.status = 'refunded'
            payment.save()
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='refund',
                amount=payment.amount,
                status='success',
                message='Payment automatically refunded due to Saga rollback'
            )
            print(f"[Pay Service] Refunded payment for order {order_id}")
        except Exception as e:
            print(f"[Pay Service] Payment for order {order_id} not found for refund: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    time.sleep(12)
    for _ in range(5):
        try:
            params = pika.URLParameters('amqp://root:12345678@rabbitmq:5672/')
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            channel.exchange_declare(exchange='saga_exchange', exchange_type='topic', durable=True)
            result = channel.queue_declare(queue='pay_saga_queue', durable=True)
            queue_name = result.method.queue
            
            channel.queue_bind(exchange='saga_exchange', queue=queue_name, routing_key='order.created')
            channel.queue_bind(exchange='saga_exchange', queue=queue_name, routing_key='payment.refund')
            
            channel.basic_consume(queue=queue_name, on_message_callback=process_payment, auto_ack=False)
            
            print(" [*] Pay Service started consuming...")
            channel.start_consuming()
            break
        except Exception as e:
            print(f"RabbitMQ connection failed: {e}. Retrying...")
            time.sleep(5)
