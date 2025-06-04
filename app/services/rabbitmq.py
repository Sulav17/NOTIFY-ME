import json
import aio_pika
from app.config import settings

RABBITMQ_URL = settings.rabbitmq_url
QUEUE_NAME = "notification_queue"

async def publish_to_queue(message: dict):
    """
    Publish a message to the RabbitMQ notification queue.
    """
    # Establish a robust connection to RabbitMQ and publish
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=QUEUE_NAME
        )
