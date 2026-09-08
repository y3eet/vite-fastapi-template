from sqlmodel import Session, select

from app.models.user import User, UserCreate, UserUpdate


class UserCrud:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.exec(select(User).where(User.email == email)).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.session.exec(select(User).where(User.id == user_id)).first()

    def create_user(self, user_create: UserCreate) -> User:
        user = User.model_validate(user_create)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_user(self, user: User, user_update: UserUpdate) -> User:
        update_data = user_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
