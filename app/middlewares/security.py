from fastapi import Request
from app.main import app

@app.middleware("http")
async def security_headers(request: Request, call_next):
    """
    Middleware to add security headers to the response.
    """
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
