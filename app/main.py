from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.users import user_router
from app.api.auth import auth_router
from app.core.config import settings

app = FastAPI()

origins = [settings.FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_router = APIRouter(prefix="/api")
api_router.include_router(user_router)
api_router.include_router(auth_router)
app.include_router(api_router)
