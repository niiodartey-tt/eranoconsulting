import asyncio
from app.core.database import async_session
from app.models.user import User, UserRole
from app.core.security import SecurityService

async def create_admin():
    async with async_session() as db:
        # Check if admin exists
        from sqlalchemy import select
        query = select(User).where(User.email == "admin@eranoconsulting.com")
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            print("✅ Admin already exists: admin@eranoconsulting.com")
            return
        
        # Create admin
        admin = User(
            email="admin@eranoconsulting.com",
            hashed_password=SecurityService.hash_password("Admin123!"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin)
        await db.commit()
        
        print("✅ Admin account created successfully!")
        print("\n📧 Email: admin@eranoconsulting.com")
        print("🔑 Password: Admin123!")
        print("\n⚠️  Please change this password after first login!")

if __name__ == "__main__":
    asyncio.run(create_admin())
