from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Pagination:
    page: int = 1
    limit: int = 20

    def __post_init__(self) -> None:
        if self.page < 1 or self.limit < 1:
            raise ValueError("Номер страницы и размер страницы должны быть положительными")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


@dataclass(frozen=True)
class Page(Generic[T]):
    items: tuple[T, ...]
    total: int
    pagination: Pagination
