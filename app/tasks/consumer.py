import asyncio
import aio_pika
import json
from app.config import settings
from app.db.session import SessionLocal
from app.db.models import Notification
from app.utils.logger import logger
from aiormq.exceptions import AMQPConnectionError

async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        logger.info(f"Processing notification: {data}")

        db = SessionLocal()
        notification = db.query(Notification).get(data["id"])
        if notification:
            notification.status = "sent"
            db.commit()
            logger.info(f"Notification {notification.id} marked as sent.")

async def start_consumer():
    # Retry establishing connection to RabbitMQ
    for attempt in range(10):
        try:
            connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            break
        except AMQPConnectionError:
            logger.warning(f"RabbitMQ connection failed, retrying in 2s (attempt {attempt+1}/10)")
            await asyncio.sleep(2)
    else:
        logger.error("Could not connect to RabbitMQ after 10 retries")
        raise RuntimeError("RabbitMQ connection failed")

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    queue = await channel.declare_queue("notification_queue", durable=True)
    await queue.consume(handle_message)

    logger.info("Notification consumer started")
    return connection

def run_consumer():
    asyncio.run(start_consumer())
