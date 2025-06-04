from fastapi import FastAPI
from app.api.v1 import notify
from app.db.base import Base
from app.db.session import engine
from app.tasks.consumer import start_consumer
import asyncio
from sqlalchemy.exc import OperationalError

app = FastAPI(title="NotifyMe", version="1.0.0")

app.include_router(notify.router)

@app.on_event("startup")
async def startup_event():
    # Ensure DB is ready and create tables with retries
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            await asyncio.sleep(2)
    else:
        raise RuntimeError("Could not connect to MySQL after 10 retries")
    # Start background consumer task
    asyncio.create_task(start_consumer())
