from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.models.user import UserRead, UserCreate, UserUpdate
from app.models.lib import Page
from app.models.user import UserRead
from app.services.user import UserService

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/", response_model=UserRead)
def create_user(
    user_create: UserCreate,
    session: Session = Depends(get_session),
):
    service = UserService(session=session)
    return service.create_user(user_create=user_create)


@user_router.get("/", response_model=Page[UserRead])
def get_users_paginated(
    q: str | None = None,
    page: int = 1,
    page_size: int = 50,
    session: Session = Depends(get_session),
):
    service = UserService(session=session)
    return service.get_users_paginated(page=page, page_size=page_size, q=q)


@user_router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    service = UserService(session=session)
    return service.get_user_by_id(user_id=user_id)


@user_router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_update: UserUpdate, user_id: int, session: Session = Depends(get_session)
):

    service = UserService(session=session)
    return service.update_user(user_id=user_id, user_update=user_update)
