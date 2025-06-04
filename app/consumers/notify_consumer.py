import asyncio
import json
from aio_pika import connect_robust, IncomingMessage
from app.services.notify import process_notification
from app.utils.logger import logger
from app.config import settings

async def on_message(message: IncomingMessage):
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            await process_notification(data)
        except Exception as e:
            logger.error(f"Failed to process message: {e}")

async def consume():
    connection = await connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("notify_queue", durable=True)
    await queue.consume(on_message)
    logger.info(" [*] Waiting for messages. To exit press CTRL+C")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume())
    loop.run_forever()
