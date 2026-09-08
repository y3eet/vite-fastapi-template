from pydantic import EmailStr
from sqlmodel import Column, Relationship, SQLModel, Field
from datetime import datetime

from app.models import auth


class UserBase(SQLModel):
    username: str | None = Field(max_length=50)
    email: EmailStr = Field(unique=True)


class User(UserBase, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    blocked: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column("updated_at", default=datetime.now, onupdate=datetime.now),
    )
    refresh_tokens: list["auth.RefreshToken"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserUpdate(SQLModel):
    email: EmailStr | None = None
    username: str | None = None
