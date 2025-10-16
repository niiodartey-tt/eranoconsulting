import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .db import init_db
from .api import auth, onboarding, admin, messages, test_protected

load_dotenv()

app = FastAPI(title="Eranos Consulting API")

# CORS setup
cors_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,"
    "http://www.eranoconsultinggh.local,"
    "http://clients.eranoconsultinggh.local,"
    "http://admin.eranoconsultinggh.local",
)
origins = [o.strip() for o in cors_raw.split(",") if o.strip()]
print("Loaded CORS origins:", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])
app.include_router(test_protected.router)  # Already has prefix="/protected" in router


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def root():
    return {"msg": "Eranos Consulting API (backend) - running"}
