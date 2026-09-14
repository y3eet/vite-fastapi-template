from fastapi import APIRouter, Depends, Request, Response
from sqlmodel import Session
from app.db.session import get_session
from app.models.auth import LoginRequest
from app.services.auth import AuthService
from app.models.user import UserRead, UserPayload

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/current-user", response_model=UserPayload)
def current_user(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
):
    service = AuthService(request=request, response=response, session=session)
    return service.current_user()


@auth_router.post("/login", response_model=UserRead)
def login(
    request: Request,
    response: Response,
    credentials: LoginRequest,
    session: Session = Depends(get_session),
):
    service = AuthService(session=session, request=request, response=response)
    return service.login(creds=credentials)


@auth_router.post("/refresh", response_model=UserRead)
def refresh(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
):
    service = AuthService(session=session, request=request, response=response)
    return service.refresh()
