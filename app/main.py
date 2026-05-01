"""
FastAPI application entry point.
Configures CORS, Rate Limiting, Middleware, and API Routers.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import jwt

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.routers import auth, patients
from app.config import settings
from app.database import engine
from app.models import Base

# ---------- Rate Limiting Setup ----------
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# ---------- Role Enforcement Middleware ----------
class RoleBasedAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Normalize path to handle trailing slash
        normalized_path = request.url.path.rstrip("/")
        if request.method == "GET" and normalized_path == "/patients":
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                role = payload.get("role")
                # Explicit allowlist – only admin/clinician
                if role not in ["admin", "clinician"]:
                    return JSONResponse(status_code=403, content={"detail": "Forbidden: Insufficient permissions"})
                request.state.user = payload
            except jwt.PyJWTError:
                return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})
        response = await call_next(request)
        return response

# ---------- Security Headers Middleware ----------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds standard HTTP security headers to all responses.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

# ---------- FastAPI App Initialization ----------
app = FastAPI(title="Healthcare Platform API", version="1.0.0")

# Apply Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Apply Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Apply strict CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Apply Role Middleware
app.add_middleware(RoleBasedAccessMiddleware)

# Include Routers
app.include_router(auth.router)
app.include_router(patients.router)

# ---------- Database Initialization ----------
@app.on_event("startup")
async def init_db():
    """
    Creates database tables on startup. 
    Note: In a true production environment, use Alembic for migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
