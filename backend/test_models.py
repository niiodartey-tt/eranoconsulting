# test_models.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import User, Client, KYCDocument, Payment

async def test_models():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:password@localhost:5432/eranos_db"
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create test user
        user = User(
            email="test@example.com",
            hashed_password="dummy",
            full_name="Test User",
            role="client"
        )
        session.add(user)
        await session.commit()
        
        # Create test client
        client = Client(
            user_id=user.id,
            business_name="Test Business",
            phone="+233123456789",
            onboarding_status="pending_verification"
        )
        session.add(client)
        await session.commit()
        
        print("✅ Models work correctly!")
        print(f"Created user: {user.email}")
        print(f"Created client: {client.business_name}")
        
        # Clean up
        await session.delete(client)
        await session.delete(user)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(test_models())
