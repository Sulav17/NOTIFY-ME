from sqlalchemy.orm import Session
from app.db import models
from app.schemas.notify import NotificationCreate
from app.services.rabbitmq import publish_to_queue

async def create_and_queue_notification(db: Session, payload: NotificationCreate):
    # Save notification record in DB
    notification = models.Notification(
        recipient=payload.recipient,
        message=payload.message
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Publish to RabbitMQ asynchronously
    await publish_to_queue({
        "id": notification.id,
        "recipient": notification.recipient,
        "message": notification.message
    })

    return notification
