import pika
import json
import logging
import time

logger = logging.getLogger(__name__)

def get_connection():
    for _ in range(5):
        try:
            params = pika.URLParameters('amqp://root:12345678@rabbitmq:5672/')
            return pika.BlockingConnection(params)
        except Exception:
            time.sleep(2)
    return None

def publish_command(routing_key, payload):
    try:
        connection = get_connection()
        if not connection: return False
        channel = connection.channel()
        channel.exchange_declare(exchange='saga_exchange', exchange_type='topic', durable=True)
        channel.basic_publish(
            exchange='saga_exchange',
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return True
    except Exception as e:
        logger.error(f"Failed to publish {routing_key}: {e}")
        return False
