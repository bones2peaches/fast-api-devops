from typing import Any

from asyncpg import UniqueViolationError
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declared_attr, DeclarativeBase
import logging


class Base(DeclarativeBase):
    id: Any
    __name__: str
    # Generate __tablename__ automatically

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()
