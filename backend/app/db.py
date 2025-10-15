# backend/app/db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./erano.db")

# create async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


# helper to create DB from code
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
