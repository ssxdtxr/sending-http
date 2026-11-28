from abc import ABC, abstractmethod

from domain.models.domain import Domain, DomainError, DomainStatus
from domain.models.filter import FilterDomain
from domain.models.pagination import Page, Pagination


class DomainAlreadyExists(DomainError):
    pass


class DomainNotFound(DomainError):
    pass


class DomainPort(ABC):
    @abstractmethod
    def create(self, domain: Domain) -> Domain: ...

    @abstractmethod
    def read_list(self, filter_: FilterDomain, pagination: Pagination) -> Page[Domain]: ...

    @abstractmethod
    def find_by_names(self, names: tuple[str, ...]) -> tuple[Domain, ...]: ...

    @abstractmethod
    def update(
        self, domain: Domain, *, expected_status: DomainStatus | None = None
    ) -> Domain: ...

    @abstractmethod
    def delete(
        self, domain_id: int, *, expected_status: DomainStatus | None = None
    ) -> None: ...
