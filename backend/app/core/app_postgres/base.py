import uuid
from typing import List, TypeVar, Generic, Type, Optional, Any
import logging
from pydantic import BaseModel
from sqlalchemy import select, delete, func, and_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.app_postgres.db_engine import Base

T = TypeVar("T", bound=Base)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseDAO(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("Model must be specified in the child class")

    def _validate_fields(self, filters: dict[str, Any]) -> None:
        valid_fields = self.model.__table__.columns.keys()
        for field in filters.keys():
            if field not in valid_fields:
                raise ValueError(f"Invalid field name: '{field}'")

    async def find_one_or_none_by_id(self, data_id: uuid.UUID | str) -> Optional[T]:
        try:
            return await self._session.get(self.model, data_id)
        except Exception as e:
            logger.error(f"Error finding record by ID {data_id}: {str(e)}")
            await self._session.rollback()
            raise

    async def find_one_or_none(self, filters: dict[str, Any]) -> Optional[T]:
        try:
            self._validate_fields(filters)
            statement = select(self.model)
            if filters:
                conditions = [getattr(self.model, field) == value for field, value in filters.items()]
                statement = statement.where(and_(*conditions))
            result = await self._session.execute(statement)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error finding record with filters {filters}: {str(e)}")
            await self._session.rollback()
            raise

    async def add(self, values: dict | BaseModel) -> T:
        try:
            values_dict = values.model_dump(exclude_unset=True) if isinstance(values, BaseModel) else values
            self._validate_fields(values_dict)
            new_instance = self.model(**values_dict)
            self._session.add(new_instance)
            await self._session.flush()
            await self._session.refresh(new_instance)
            return new_instance
        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error adding record: {str(e)}")
            raise

    async def add_many(self, instances: list[BaseModel]) -> List[T]:
        try:
            values_list = [item.model_dump(exclude_unset=True) for item in instances]
            new_instances = [self.model(**inst) for inst in values_list]
            self._session.add_all(new_instances)
            await self._session.flush()
            for instance in new_instances:
                await self._session.refresh(instance)
            return new_instances
        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error adding multiple records: {str(e)}")
            raise

    async def find_all(self, skip: int = 0, limit: int = 100, filters: Optional[dict[str, Any]] = None, order_by: Optional[str] = None) -> List[T]:
        try:
            if limit > 1000:
                raise ValueError("Limit cannot exceed 1000")
            statement = select(self.model)
            if filters:
                self._validate_fields(filters)
                conditions = []
                for field, value in filters.items():
                    if value is None:
                        continue
                    if isinstance(value, tuple) and len(value) == 2:
                        operator, operand = value
                        column = getattr(self.model, field)
                        match operator:
                            case "in": conditions.append(column.in_(operand))
                            case "not_in": conditions.append(~column.in_(operand))
                            case "ge": conditions.append(column >= operand)
                            case "le": conditions.append(column <= operand)
                            case "gt": conditions.append(column > operand)
                            case "lt": conditions.append(column < operand)
                            case "eq": conditions.append(column == operand)
                            case "ne": conditions.append(column != operand)
                            case "like": conditions.append(column.like(operand))
                            case "ilike": conditions.append(column.ilike(operand))
                            case _: raise ValueError(f"Unsupported operator: {operator}")
                    else:
                        conditions.append(getattr(self.model, field) == value)
                if conditions:
                    statement = statement.where(and_(*conditions))
            if order_by:
                order_column = getattr(self.model, order_by.lstrip('-'))
                statement = statement.order_by(desc(order_column) if order_by.startswith('-') else asc(order_column))
            statement = statement.offset(skip).limit(limit)
            result = await self._session.execute(statement)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching records: {str(e)}")
            await self._session.rollback()
            raise

    async def update(self, filters: dict[str, Any], values: BaseModel | dict) -> T:
        try:
            self._validate_fields(filters)
            values_dict = values.model_dump(exclude_unset=True) if isinstance(values, BaseModel) else values
            self._validate_fields(values_dict)
            entity = await self.find_one_or_none(filters)
            if not entity:
                raise ValueError("Record not found")
            for field, value in values_dict.items():
                setattr(entity, field, value)
            self._session.add(entity)
            await self._session.flush()
            await self._session.refresh(entity)
            return entity
        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error updating record: {str(e)}")
            raise

    async def delete(self, filters: BaseModel | dict[str, Any]) -> int:
        try:
            filters_dict = filters.model_dump(exclude_unset=True) if isinstance(filters, BaseModel) else filters
            if not isinstance(filters_dict, dict) or not filters_dict:
                raise ValueError("Filters must be a non-empty dict or BaseModel")
            self._validate_fields(filters_dict)
            conditions = [getattr(self.model, field) == value for field, value in filters_dict.items()]
            statement = delete(self.model).where(and_(*conditions))
            result = await self._session.execute(statement)
            await self._session.flush()
            return result.rowcount if hasattr(result, 'rowcount') else 0
        except Exception as e:
            await self._session.rollback()
            logger.error(f"Delete error: {str(e)}")
            raise

    async def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        try:
            statement = select(func.count()).select_from(self.model)
            if filters:
                self._validate_fields(filters)
                conditions = [getattr(self.model, field) == value for field, value in filters.items() if value is not None]
                if conditions:
                    statement = statement.where(and_(*conditions))
            result = await self._session.execute(statement)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting records: {str(e)}")
            await self._session.rollback()
            raise
