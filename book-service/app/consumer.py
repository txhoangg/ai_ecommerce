import pika
import json
import logging
import time

from app.rabbitmq import publish_command

logger = logging.getLogger(__name__)

def process_inventory(ch, method, properties, body):
    payload = json.loads(body)
    routing_key = method.routing_key
    print(f"[Book Service] Received: {routing_key}")

    order_id = payload.get('order_id')
    items = payload.get('items', [])

    from app.models import Book, BookInventoryHistory
    
    if routing_key == 'inventory.reserve':
        success = True
        # Transaction giả lập
        for item in items:
            try:
                book = Book.objects.get(id=item['book_id'])
                if book.stock >= item['quantity']:
                    book.stock -= item['quantity']
                    book.save()
                    BookInventoryHistory.objects.create(
                        book=book, staff_id=1, action='subtract', quantity=item['quantity'],
                        note=f"Reserved for order {order_id}"
                    )
                else:
                    print(f"Book {book.id} out of stock!")
                    success = False
                    break
            except Book.DoesNotExist:
                success = False
                break
                
        if success:
            payload['status'] = 'success'
            print(f"[Book Service] Reserved inventory for order {order_id}")
        else:
            payload['status'] = 'failed'
            print(f"[Book Service] Failed to reserve inventory for order {order_id}")
            
        publish_command('inventory.result', payload)

    elif routing_key == 'inventory.revert':
        for item in items:
            try:
                book = Book.objects.get(id=item['book_id'])
                book.stock += item['quantity']
                book.save()
                BookInventoryHistory.objects.create(
                    book=book, staff_id=1, action='add', quantity=item['quantity'],
                    note=f"Reverted for cancelled order {order_id}"
                )
            except Book.DoesNotExist:
                pass
        print(f"[Book Service] Reverted inventory for cancelled order {order_id}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    time.sleep(12)
    for _ in range(5):
        try:
            params = pika.URLParameters('amqp://root:12345678@rabbitmq:5672/')
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            channel.exchange_declare(exchange='saga_exchange', exchange_type='topic', durable=True)
            result = channel.queue_declare(queue='book_saga_queue', durable=True)
            queue_name = result.method.queue
            
            channel.queue_bind(exchange='saga_exchange', queue=queue_name, routing_key='inventory.reserve')
            channel.queue_bind(exchange='saga_exchange', queue=queue_name, routing_key='inventory.revert')
            
            channel.basic_consume(queue=queue_name, on_message_callback=process_inventory, auto_ack=False)
            
            print(" [*] Book Service started consuming...")
            channel.start_consuming()
            break
        except Exception as e:
            print(f"RabbitMQ connection failed: {e}. Retrying...")
            time.sleep(5)
