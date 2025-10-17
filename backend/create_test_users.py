import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session, engine
from app.models.base import Base
from app.models.user import User, UserRole
from app.core.security import SecurityService

async def create_test_users():
    """Create test users for development"""
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Test users data
        test_users = [
            {
                "email": "admin@eranoconsulting.com",
                "password": "Admin123!",
                "full_name": "Admin User",
                "role": UserRole.ADMIN
            },
            {
                "email": "consultant@eranoconsulting.com",
                "password": "Consultant123!",
                "full_name": "Sarah Johnson",
                "role": UserRole.STAFF
            },
            {
                "email": "accountant@eranoconsulting.com",
                "password": "Staff123!",
                "full_name": "Michael Chen",
                "role": UserRole.STAFF
            },
            {
                "email": "taxadvisor@eranoconsulting.com",
                "password": "Staff123!",
                "full_name": "Emily Davis",
                "role": UserRole.STAFF
            },
            {
                "email": "client1@example.com",
                "password": "Client123!",
                "full_name": "John Doe",
                "role": UserRole.CLIENT
            },
            {
                "email": "client2@example.com",
                "password": "Client123!",
                "full_name": "Jane Smith",
                "role": UserRole.CLIENT
            }
        ]
        
        created_count = 0
        
        for user_data in test_users:
            # Check if user already exists
            from sqlalchemy import select
            stmt = select(User).where(User.email == user_data["email"])
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✓ User already exists: {user_data['email']}")
                continue
            
            # Create new user
            hashed_password = SecurityService.hash_password(user_data["password"])
            new_user = User(
                email=user_data["email"],
                hashed_password=hashed_password,
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
                is_verified=True
            )
            
            session.add(new_user)
            created_count += 1
            print(f"✓ Created user: {user_data['email']} ({user_data['role'].value})")
        
        await session.commit()
        
        print(f"\n{'='*50}")
        print(f"✅ Test user creation complete!")
        print(f"📊 Created {created_count} new users")
        print(f"{'='*50}\n")
        
        # Display login credentials
        print("🔑 LOGIN CREDENTIALS:\n")
        for user_data in test_users:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Role: {user_data['role'].value}")
            print(f"Name: {user_data['full_name']}")
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(create_test_users())
