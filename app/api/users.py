# app/api/v1/items.py
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.user import Item

router = APIRouter()


@router.get("/items")
def list_items(
    session: Session = Depends(get_session),
    q: str | None = Query(None, description="Search by name"),
    is_active: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Item)

    if q:
        stmt = stmt.where(Item.name.ilike(f"%{q}%"))
    if is_active is not None:
        stmt = stmt.where(Item.is_active == is_active)

    stmt = stmt.offset(skip).limit(limit)
    return session.exec(stmt).all()
