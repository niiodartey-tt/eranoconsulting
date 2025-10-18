# app/main.py - Updated router includes
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import redis.asyncio as redis
import logging
import uuid
from app.core.config import settings
from app.core.database import init_db
from app.middleware.security import SecurityHeadersMiddleware, RateLimitMiddleware

# Import all API routers
from app.api.v1 import auth, users, files, admin, messages

# Import new routers for the fixes
from app.api.v1.client_onboarding import router as onboarding_router
from app.api.v1.admin_users import router as admin_users_router

import uvicorn

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting application...")
    await init_db()

    if settings.REDIS_URL:
        app.state.redis = await redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    yield

    logger.info("Shutting down application...")
    if hasattr(app.state, "redis"):
        await app.state.redis.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

if settings.REDIS_URL:
    app.add_middleware(RateLimitMiddleware, redis_client=app.state.redis)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Include all API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])

# Include new routers for fixes
app.include_router(
    onboarding_router, prefix="/api/v1/clients/onboarding", tags=["onboarding"]
)
app.include_router(admin_users_router, prefix="/api/v1/admin", tags=["admin-users"])


@app.get("/")
async def root():
    return {
        "message": "Eranos Consulting API",
        "version": settings.VERSION,
        "docs": "/api/docs" if settings.DEBUG else None,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
