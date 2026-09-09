from sqlmodel import Session, select
from app.models.auth import RefreshToken, RefreshTokenUpdate


class RefreshTokenCrud:
    def __init__(self, session: Session):
        self.session = session

    def create_refresh_token(self, refresh_token: RefreshToken):
        self.session.add(refresh_token)
        self.session.commit()  # <-- writes it to the DB, assigns the PK
        self.session.refresh(refresh_token)  # now this works — object is persistent
        return refresh_token

    def update_refresh_token(
        self, refresh_token: RefreshToken, rt_update: RefreshTokenUpdate
    ) -> RefreshToken:
        update_data = rt_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(refresh_token, field, value)

        self.session.add(refresh_token)
        self.session.commit()
        self.session.refresh(refresh_token)
        return refresh_token

    def get_token_by_device(self, user_agent: str, ip_address: str):
        stmt = select(RefreshToken)
        return self.session.exec(
            stmt.where(
                RefreshToken.user_agent == user_agent,
                RefreshToken.ip_address == ip_address,
            )
        ).first()

    def delete_token(self, refresh_token: RefreshToken):
        self.session.delete(refresh_token)
        self.session.commit()
