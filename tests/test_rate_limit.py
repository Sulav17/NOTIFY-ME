import time
from app.services import rate_limiter

def test_rate_limiter_allows_then_blocks():
    user = "test_user_123"

    # Allow first 5 requests
    for i in range(5):
        assert rate_limiter.allow_request(user) == True

    # 6th request should be blocked
    assert rate_limiter.allow_request(user) == False

    # Wait for rate limit to reset
    time.sleep(60)

    # Should allow again
    assert rate_limiter.allow_request(user) == True
