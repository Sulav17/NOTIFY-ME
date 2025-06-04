from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.notify import NotificationCreate, NotificationOut
from app.db import session as db_session
from app.services import notification, rate_limiter

router = APIRouter(prefix="/api/v1/notify", tags=["Notification"])

def get_db():
    db = db_session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=NotificationOut)
async def send_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db)
):
    # Rate limiting: block if exceeded
    if not rate_limiter.allow_request(payload.recipient):
        # Too many requests
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    # Create notification record and publish to queue
    new_notif = await notification.create_and_queue_notification(db, payload)
    return new_notif
