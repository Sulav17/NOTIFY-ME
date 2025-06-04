import redis
from app.config import settings

r = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True
)

LIMIT = 5  # 5 requests
WINDOW = 60  # per 60 seconds

def allow_request(user_id: str) -> bool:
    key = f"rate_limit:{user_id}"
    current = r.get(key)
    
    if current and int(current) >= LIMIT:
        return False
    else:
        pipe = r.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, WINDOW)
        pipe.execute()
        return True
