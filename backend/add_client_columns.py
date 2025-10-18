import asyncio
from sqlalchemy import text
from app.core.database import engine

async def migrate():
    print("Adding missing columns to clients table...")
    
    migrations = [
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS engagement_letter_signed BOOLEAN DEFAULT FALSE;",
        "UPDATE clients SET status = 'pre_active' WHERE status = 'pending' OR status IS NULL;",
    ]
    
    async with engine.begin() as conn:
        for sql in migrations:
            try:
                await conn.execute(text(sql))
                print(f"✅ {sql[:50]}...")
            except Exception as e:
                print(f"⚠️  {str(e)}")
    
    print("✅ Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())
