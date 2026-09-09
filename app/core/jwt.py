from fastapi import Request, Response
from app.core.config import settings
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from app.models.user import UserPayload, UserRead
from datetime import datetime, timedelta

ACCESS_SECRET_KEY = settings.JWT_ACCESS_SECRET_KEY
REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY

ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
ALGORITHM = "HS256"


class Jwt:
    @staticmethod
    def get_access_token(request: Request):
        return request.cookies.get("access_token")

    @staticmethod
    def get_refresh_token(request: Request):
        return request.cookies.get("refresh_token")

    @staticmethod
    def create_access_token(user: UserRead):
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = UserPayload(
            sub=str(user.id),
            iat=now,
            exp=exp,
            jti=str(uuid.uuid4()),
            claims=user,
        )
        return (
            jwt.encode(payload.model_dump(), ACCESS_SECRET_KEY, algorithm=ALGORITHM),
            exp,
        )

    @staticmethod
    def create_refresh_token(user: UserRead):
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        payload = UserPayload(
            sub=str(user.id),
            iat=now,
            exp=exp,
            jti=str(uuid.uuid4()),
            claims=user,
        )
        return (
            jwt.encode(payload.model_dump(), REFRESH_SECRET_KEY, algorithm=ALGORITHM),
            exp,
        )

    @staticmethod
    def decode(token, token_type="access"):
        secret_key = ACCESS_SECRET_KEY
        if token_type == "refresh":
            secret_key = REFRESH_SECRET_KEY
        decoded_token = jwt.decode(token, secret_key, algorithms=[Jwt.ALGORITHM])
        return UserPayload.model_validate(decoded_token)

    @staticmethod
    def set_tokens(response: Response, access_token: str, refresh_token: str):
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=int(timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
            path="/",
            domain=settings.COOKIE_DOMAIN,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=int(
                timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES).total_seconds()
            ),
            path="/",
            domain=settings.COOKIE_DOMAIN,
        )

    @staticmethod
    def delete_tokens(response: Response):
        response.delete_cookie("access_token", path="/", domain=settings.COOKIE_DOMAIN)
        response.delete_cookie("refresh_token", path="/", domain=settings.COOKIE_DOMAIN)
