import time
from typing import Dict, Tuple

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 100,
        burst_size: int = 50
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.requests: Dict[str, Tuple[int, float]] = {}  # {ip: (count, timestamp)}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        # Check rate limit
        if not self.check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        # Add rate limit headers
        response = await call_next(request)
        remaining, reset_time = self.get_rate_limit_info(client_ip)
        
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))
        
        return response

    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = (1, now)
            return True
            
        count, timestamp = self.requests[client_ip]
        
        # Reset counter if window has passed
        if now - timestamp >= 60:
            self.requests[client_ip] = (1, now)
            return True
            
        # Check if within limits
        if count >= self.requests_per_minute:
            return False
            
        # Increment counter
        self.requests[client_ip] = (count + 1, timestamp)
        return True

    def get_rate_limit_info(self, client_ip: str) -> Tuple[int, float]:
        """Get remaining requests and reset time."""
        now = time.time()
        
        if client_ip not in self.requests:
            return self.requests_per_minute, now + 60
            
        count, timestamp = self.requests[client_ip]
        
        if now - timestamp >= 60:
            return self.requests_per_minute, now + 60
            
        remaining = max(0, self.requests_per_minute - count)
        reset_time = timestamp + 60
        
        return remaining, reset_time
