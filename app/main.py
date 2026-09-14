from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
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


class EndpointFilter(logging.Filter):
    def __init__(self, excluded_paths: list[str]):
        super().__init__()
        self.excluded_paths = excluded_paths

    def filter(self, record: logging.LogRecord) -> bool:
        # uvicorn access log records have args like (client_addr, method, path, http_version, status_code)
        if record.args and len(record.args) >= 3:
            path = record.args[2]
            return not any(path.startswith(p) for p in self.excluded_paths)
        return True


logging.getLogger("uvicorn.access").addFilter(
    EndpointFilter(excluded_paths=["/openapi.json", "/health"])
)

api_router = APIRouter(prefix="/api")
api_router.include_router(user_router)
api_router.include_router(auth_router)
app.include_router(api_router)
