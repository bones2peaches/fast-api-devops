from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.redis_cache import get_redis
import pytest

router = APIRouter()

pytestmark = pytest.mark.anyio


@router.get("", status_code=status.HTTP_200_OK)
async def healthcheck():
    return "OK"


@router.get("/postgres", status_code=status.HTTP_200_OK)
async def postgres_healthcheck(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(1))
        _ = result.fetchall()
        resp = {"status": "OK"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection error",
        )
    return resp


@router.get("/redis", status_code=status.HTTP_200_OK)
async def redis_healthcheck(redis=Depends(get_redis)):
    try:
        resp = await redis.ping()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    return resp
