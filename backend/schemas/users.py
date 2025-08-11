import re
from datetime import datetime
from typing import Optional

from pydantic import field_validator
from sqlmodel import SQLModel, Field

from backend.mixins import BaseModelMixin
from backend.schemas.common import PaginatedList


class UserBase(SQLModel):
    username: str
    full_name: Optional[str] = None
    require_password_change: bool = Field(default=True)


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*_+]", value):
            raise ValueError("Password must contain at least one special character")
        return value


class UserUpdate(UserBase):
    password: Optional[str] = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*_+]", value):
            raise ValueError("Password must contain at least one special character")
        return value


class User(UserBase, BaseModelMixin, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class UserPublic(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


UsersPublic = PaginatedList[UserPublic]
