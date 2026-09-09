from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship

from app.models import user


class TokenStatus(str, Enum):
    active = "active"  # currently valid, not yet rotated
    rotated = "rotated"  # consumed normally during refresh
    revoked = "revoked"  # explicitly killed by user/admin (e.g. logout, manual session revoke)
    compromised = "compromised"  # killed due to detected reuse/theft


class RefreshTokenUpdate(SQLModel):
    status: Optional[TokenStatus]
    used_at: Optional[datetime] = Field(default=None)
    revoked_at: Optional[datetime] = Field(default=None)


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(index=True, nullable=False, foreign_key="users.id")
    user: "user.User" = Relationship(back_populates="refresh_tokens")

    # SHA-256 hash of the raw token — never store the raw value.
    token_hash: str = Field(index=True, unique=True, nullable=False)

    status: TokenStatus = Field(default=TokenStatus.active, index=True)

    # Device/session metadata — for "active sessions" UI, not for lookup or auth decisions.
    device_label: Optional[str] = Field(default=None)  # e.g. "Chrome on macOS"
    user_agent: Optional[str] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    expires_at: datetime = Field(nullable=False)
    used_at: Optional[datetime] = Field(default=None)  # when rotated away
    revoked_at: Optional[datetime] = Field(default=None)  # when explicitly killed

    revoked_reason: Optional[str] = Field(
        default=None
    )  # "user_logout", "reuse_detected", "security_reset", etc.

    def is_valid(self) -> bool:
        """Check if this token can currently be used to refresh."""
        return self.status == TokenStatus.active and self.expires_at > datetime.now()


class LoginRequest(SQLModel):
    email: EmailStr
    password: str
