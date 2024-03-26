from fastapi import FastAPI
from app.utils.logging import AppLogger
from prometheus_fastapi_instrumentator import Instrumentator
import os
from fastapi.middleware.cors import CORSMiddleware


stage = os.getenv("STAGE", "dev")

logger = AppLogger().get_logger()

app = FastAPI()
Instrumentator().instrument(app).expose(app)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.routers.health import router as health_router
from app.routers.user import router as user_router
from app.routers.chatroom import router as chatroom_router
from app.routers.nchan import router as nchan_router

app.include_router(health_router, prefix=f"/api/health")
app.include_router(user_router, prefix=f"/api/user")
app.include_router(chatroom_router, prefix=f"/api/chatroom")
app.include_router(nchan_router, prefix=f"/api/nchan")
