from fastapi import HTTPException, Request, Response
from sqlmodel import Session
from app.crud.refresh_token import RefreshTokenCrud
from app.models.auth import LoginRequest, RefreshToken
from app.models.user import UserRead
from app.crud.user import UserCrud
from app.core.jwt import Jwt
from app.core.security import ph
import hashlib
from user_agents import parse


def get_current_user(request: Request):
    token = Jwt.get_access_token(request=request)
    return Jwt.decode(token)


class AuthService:
    def __init__(self, session: Session, request: Request, response: Response):
        self.session = session
        self.rt_crud = RefreshTokenCrud(session=session)
        self.user_crud = UserCrud(session=session)
        self.response = response
        self.request = request

    def current_user(self):
        access_token = Jwt.get_access_token(request=self.request)
        if not access_token:
            raise HTTPException(401, detail="No access token found")
        user = Jwt.decode(token=access_token)
        return user

    def login(self, creds: LoginRequest):
        user = self.user_crud.get_user_by_email(email=creds.email)
        if not user:
            raise HTTPException(404, detail="User not found")

        # Verify password
        try:
            ph.verify(password=creds.password, hash=user.hashed_password)
        except Exception:
            raise HTTPException(401, detail="Invalid password")

        ua_string = self.request.headers.get("User-Agent", "")
        xff = self.request.headers.get("X-Forwarded-For")

        device_label = self.build_device_label(ua_string=ua_string)
        ip_address = (
            xff.split(",")[0] if xff else self.request.client.host
        ) or "0.0.0.0"

        access_token, _ = Jwt.create_access_token(user=UserRead.model_validate(user))
        refresh_token, exp = Jwt.create_refresh_token(
            user=UserRead.model_validate(user)
        )

        token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()

        # Save refresh token to db
        self.rt_crud.create_refresh_token(
            refresh_token=RefreshToken(
                user_id=user.id,
                token_hash=token_hash,
                device_label=device_label,
                user_agent=ua_string,
                ip_address=ip_address,
                expires_at=exp,
            )
        )

        # Set tokens to http only cookies
        Jwt.set_tokens(
            response=self.response,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return user

    def refresh(self):
        refresh_token = Jwt.get_refresh_token(request=self.request)
        if not refresh_token:
            raise HTTPException(401, detail="No refresh token found")
        hashed_token = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
        db_token = self.rt_crud.get_token_by_hash(token_hash=hashed_token)
        if not db_token:
            raise HTTPException(401, detail="No refresh token record found")
        user = db_token.user
        new_access_token, _ = Jwt.create_access_token(
            user=UserRead.model_validate(user)
        )
        new_refresh_token, exp = Jwt.create_refresh_token(
            user=UserRead.model_validate(user)
        )
        token_hash = hashlib.sha256(new_refresh_token.encode("utf-8")).hexdigest()
        ua_string = self.request.headers.get("User-Agent", "")
        xff = self.request.headers.get("X-Forwarded-For")
        ip_address = (
            xff.split(",")[0] if xff else self.request.client.host
        ) or "0.0.0.0"
        device_label = self.build_device_label(ua_string=ua_string)
        # Save refresh token to db
        self.rt_crud.create_refresh_token(
            refresh_token=RefreshToken(
                user_id=user.id,
                token_hash=token_hash,
                device_label=device_label,
                user_agent=ua_string,
                ip_address=ip_address,
                expires_at=exp,
            )
        )
        self.rt_crud.delete_token(refresh_token=db_token)
        Jwt.set_tokens(
            response=self.response,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
        return user

    @staticmethod
    def build_device_label(ua_string: str) -> str:
        ua = parse(ua_string)

        if ua.is_bot:
            return "Bot"

        browser = ua.browser.family or "Unknown browser"
        os_name = ua.os.family or "Unknown OS"

        if ua.is_mobile or ua.is_tablet:
            device = ua.device.family or "Mobile device"
            return f"{browser}:{device}"

        return f"{browser}:{os_name}"
