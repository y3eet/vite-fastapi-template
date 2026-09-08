from math import ceil
from typing import Generic, List, TypeVar
from pydantic import computed_field
from sqlmodel import SQLModel

T = TypeVar("T")


class Page(SQLModel, Generic[T]):
    items: List[T]
    page: int
    page_size: int
    total: int

    @computed_field
    @property
    def total_pages(self) -> int:
        return ceil(self.total / self.page_size)

    @computed_field
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @computed_field
    @property
    def has_previous(self) -> bool:
        return self.page > 1
