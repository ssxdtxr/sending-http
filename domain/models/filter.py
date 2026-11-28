from dataclasses import dataclass

from domain.models.domain import DomainStatus


@dataclass(frozen=True)
class FilterDomain:
    name: str = ""
    status: DomainStatus | None = None
