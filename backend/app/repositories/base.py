# app/repositories/base.py
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.exc import IntegrityError
from app.core.database import Base
import logging

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
        self.logger = logging.getLogger(f"{__name__}.{model.__name__}")
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Get single record by ID"""
        try:
            result = await self.db.get(self.model, id)
            return result
        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} with id {id}: {e}")
            return None
    
    async def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get single record by filters"""
        try:
            query = select(self.model).filter_by(**kwargs)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__}: {e}")
            return None
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """List records with pagination and filtering"""
        try:
            query = select(self.model)
            
            if filters:
                query = query.filter_by(**filters)
            
            if order_by:
                query = query.order_by(getattr(self.model, order_by))
            
            query = query.offset(skip).limit(limit)
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            self.logger.error(f"Error listing {self.model.__name__}: {e}")
            return []
    
    async def create(self, **kwargs) -> ModelType:
        """Create new record"""
        try:
            db_obj = self.model(**kwargs)
            self.db.add(db_obj)
            await self.db.flush()
            await self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.db.rollback()
            self.logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update record"""
        try:
            query = update(self.model).where(
                self.model.id == id
            ).values(**kwargs)
            await self.db.execute(query)
            await self.db.flush()
            return await self.get(id)
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error updating {self.model.__name__}: {e}")
            return None
    
    async def delete(self, id: int) -> bool:
        """Delete record"""
        try:
            query = delete(self.model).where(self.model.id == id)
            result = await self.db.execute(query)
            await self.db.flush()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error deleting {self.model.__name__}: {e}")
            return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records"""
        try:
            query = select(func.count(self.model.id))
            if filters:
                query = query.filter_by(**filters)
            result = await self.db.execute(query)
            return result.scalar() or 0
        except Exception as e:
            self.logger.error(f"Error counting {self.model.__name__}: {e}")
            return 0
