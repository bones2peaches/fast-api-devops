from fastapi import FastAPI
from app.utils.logging import AppLogger
from prometheus_fastapi_instrumentator import Instrumentator
import os


stage = os.getenv("STAGE")

logger = AppLogger().get_logger()

app = FastAPI()
Instrumentator().instrument(app).expose(app)


from app.routers.health import router as health_router
from app.routers.user import router as user_router

app.include_router(health_router, prefix=f"/api/{stage.lower()}/health")
app.include_router(user_router, prefix=f"/api/{stage.lower()}/user")
