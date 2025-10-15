# backend/scripts/create_admin.py
"""
Usage (from backend/):
  source .venv/bin/activate
  python scripts/create_admin.py --email admin@eranoconsulting.local --password 'ChangeMe123!'
"""
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
import asyncio
import argparse
from dotenv import load_dotenv

load_dotenv()

from app.db import AsyncSessionLocal, init_db
from app import crud


async def main(email: str, password: str):
    # ensure DB exists
    await init_db()
    async with AsyncSessionLocal() as db:
        existing = await crud.get_user_by_email(db, email)
        if existing:
            print("Admin user already exists:", email)
            return
        user = await crud.create_user(db, email, password, role="admin")
        print("Created admin:", user.email, "id:", user.id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    asyncio.run(main(args.email, args.password))
