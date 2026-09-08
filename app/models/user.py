from pydantic import EmailStr
from sqlmodel import Column, SQLModel, Field, String
from datetime import datetime


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


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserUpdate(SQLModel):
    email: EmailStr | None = None
    username: str | None = None
