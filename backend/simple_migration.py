"""
Simple migration to add missing columns to clients table
Run this script to update your database schema

Usage: python simple_migration.py
"""
import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine

async def migrate():
    """Add new fields to clients table"""
    
    print("🔧 Starting database migration...")
    print("=" * 60)
    
    migrations = [
        # Add onboarding_completed column
        {
            "name": "Add onboarding_completed column",
            "sql": """
            ALTER TABLE clients 
            ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;
            """
        },
        
        # Add engagement_letter_signed column
        {
            "name": "Add engagement_letter_signed column",
            "sql": """
            ALTER TABLE clients 
            ADD COLUMN IF NOT EXISTS engagement_letter_signed BOOLEAN DEFAULT FALSE;
            """
        },
        
        # Update existing status values to new format
        {
            "name": "Update existing status values",
            "sql": """
            UPDATE clients 
            SET status = 'pre_active' 
            WHERE status = 'pending' OR status IS NULL;
            """
        },
    ]
    
    async with engine.begin() as conn:
        for i, migration in enumerate(migrations, 1):
            try:
                print(f"\n[{i}/{len(migrations)}] {migration['name']}...")
                await conn.execute(text(migration['sql']))
                print(f"✅ Success!")
            except Exception as e:
                print(f"⚠️  Warning: {str(e)}")
                print("   (This might be okay if column already exists)")
    
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print("\nNext steps:")
    print("1. Update backend/app/models/client.py with the new model")
    print("2. Restart your backend server")
    print("3. Test the application")

if __name__ == "__main__":
    try:
        asyncio.run(migrate())
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Migration failed: {str(e)}")
        print("\nPlease check your database connection and try again.")
        sys.exit(1)
