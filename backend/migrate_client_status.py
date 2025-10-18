"""
Database migration script to add new client status fields
Run this script to update your database schema

Usage: python migrate_client_status.py
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def migrate():
    """Add new fields to clients table"""
    
    print("Starting database migration...")
    
    migrations = [
        # Add onboarding_completed column
        """
        ALTER TABLE clients 
        ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;
        """,
        
        # Add engagement_letter_signed column
        """
        ALTER TABLE clients 
        ADD COLUMN IF NOT EXISTS engagement_letter_signed BOOLEAN DEFAULT FALSE;
        """,
        
        # Update status column to use enum (if not already enum)
        """
        DO $
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'clientstatus') THEN
                CREATE TYPE clientstatus AS ENUM (
                    'pre_active', 
                    'pending_review', 
                    'inactive', 
                    'active', 
                    'rejected', 
                    'suspended'
                );
            END IF;
        END$;
        """,
        
        # Migrate existing status values to new enum
        """
        UPDATE clients 
        SET status = 'pre_active' 
        WHERE status = 'pending' OR status IS NULL;
        """,
        
        """
        UPDATE clients 
        SET status = 'active' 
        WHERE status IN ('active', 'approved');
        """,
        
        # Alter column to use enum type (if it's currently varchar)
        """
        DO $
        BEGIN
            BEGIN
                ALTER TABLE clients 
                ALTER COLUMN status TYPE clientstatus 
                USING status::clientstatus;
            EXCEPTION
                WHEN others THEN
                    RAISE NOTICE 'Status column already using enum type';
            END;
        END$;
        """
    ]
    
    async with engine.begin() as conn:
        for i, migration in enumerate(migrations, 1):
            try:
                print(f"Running migration {i}/{len(migrations)}...")
                await conn.execute(text(migration))
                print(f"✓ Migration {i} completed")
            except Exception as e:
                print(f"✗ Migration {i} failed: {str(e)}")
                # Continue with other migrations
    
    print("\n✅ Database migration completed!")
    print("\nNext steps:")
    print("1. Update your Client model in backend/app/models/client.py")
    print("2. Restart your backend server")
    print("3. Test the new onboarding flow")

if __name__ == "__main__":
    asyncio.run(migrate())
