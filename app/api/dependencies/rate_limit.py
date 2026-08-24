import time
from fastapi import HTTPException, status, Request
from app.core.config import settings

# A simple in-memory token bucket for rate limiting.
# Note: For multi-worker production deployments, this should be replaced with Redis.

class RateLimiter:
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window
        self.clients = {}

    def is_allowed(self, client_ip: str) -> bool:
        current_time = time.time()
        
        if client_ip not in self.clients:
            self.clients[client_ip] = []
            
        # Clean up old requests
        self.clients[client_ip] = [t for t in self.clients[client_ip] if current_time - t < self.window]
        
        if len(self.clients[client_ip]) >= self.requests:
            return False
            
        self.clients[client_ip].append(current_time)
        return True

limiter = RateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)

async def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
