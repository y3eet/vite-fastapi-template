from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from app.crud.user import UserCrud
from app.models.lib import Page
from app.models.user import User, UserCreate, UserRead, UserUpdate
from app.core.security import ph


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.user_crud = UserCrud(session)

    def create_user(self, user_create: UserCreate) -> User:
        existing_user = self.user_crud.get_user_by_email(user_create.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = ph.hash(user_create.password)
        user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
        )
        return self.user_crud.create_user(user)

    def get_users_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        threshold: float = 0.2,
    ) -> Page[UserRead]:
        skip = (page - 1) * page_size

        base_statement = select(User)
        count_statement = select(func.count()).select_from(User)

        if q:
            sim_username = func.similarity(User.username, q)
            sim_email = func.similarity(User.email, q)
            score = func.greatest(sim_username, sim_email)
            match_filter = (sim_username > threshold) | (sim_email > threshold)

            base_statement = base_statement.where(match_filter).order_by(score.desc())
            count_statement = count_statement.where(match_filter)

        total = self.session.exec(count_statement).one()
        users = self.session.exec(base_statement.offset(skip).limit(page_size)).all()
        items = [UserRead.model_validate(user) for user in users]

        return Page[UserRead](
            items=items,
            page=page,
            page_size=page_size,
            total=total,
        )

    def get_user_by_id(self, user_id: int):
        user = self.user_crud.get_user_by_id(user_id=user_id)
        if not user:
            raise HTTPException(404, detail="User not found")
        return user

    def update_user(self, user_id: int, user_update: UserUpdate):
        user = self.get_user_by_id(user_id=user_id)
        existing_user = self.user_crud.get_user_by_email(email=user_update.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(403, detail="Email already registered")
        return self.user_crud.update_user(user=user, user_update=user_update)
