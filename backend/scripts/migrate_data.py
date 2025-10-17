import asyncio
import sqlite3
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# --- Ensure the app module can be found ---
# Adds backend/ to sys.path dynamically
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Add the parent directory (backend/) to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.user import User
from app.core.security import SecurityService


async def migrate_users():
    # Connect to old SQLite database
    old_conn = sqlite3.connect("erano.db")
    old_cursor = old_conn.cursor()

    # Connect to new PostgreSQL
    engine = create_async_engine(
        "postgresql+asyncpg://eranos_user:secure_password_here@localhost/eranos_db"
    )
    async_session = sessionmaker(engine, class_=AsyncSession)

    # Migrate users
    old_cursor.execute("SELECT email, hashed_password, role FROM users")
    users = old_cursor.fetchall()

    async with async_session() as session:
        for email, old_hash, role in users:
            # Note: Users will need to reset passwords due to hash change
            new_user = User(
                email=email,
                hashed_password=old_hash,
                role=role,
                is_verified=False,
                password_changed_at=None,
            )
            session.add(new_user)

        await session.commit()

    old_conn.close()
    print(f"Migrated {len(users)} users successfully!")


if __name__ == "__main__":
    asyncio.run(migrate_users())
