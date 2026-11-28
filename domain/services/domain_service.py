from urllib.parse import urlsplit

from domain.models.domain import Domain, DomainStatus, InvalidDomainName
from domain.models.filter import FilterDomain
from domain.models.pagination import Page, Pagination
from domain.ports.domain_port import DomainPort


class DomainService:
    def __init__(self, domains: DomainPort) -> None:
        self._domains = domains

    def create(self, domain: Domain) -> Domain:
        return self._domains.create(domain)

    def read_list(
        self,
        filter_: FilterDomain,
        pagination: Pagination,
    ) -> Page[Domain]:
        return self._domains.read_list(filter_, pagination)

    def update(
        self, domain: Domain, *, expected_status: DomainStatus | None = None
    ) -> Domain:
        if domain.id is None:
            raise ValueError("Для изменения нужен ID домена")

        if expected_status is None:
            return self._domains.update(domain)
        return self._domains.update(domain, expected_status=expected_status)

    def delete(
        self, domain_id: int, *, expected_status: DomainStatus | None = None
    ) -> None:
        if expected_status is None:
            self._domains.delete(domain_id)
        else:
            self._domains.delete(domain_id, expected_status=expected_status)

    def status(self, name_or_url: str) -> DomainStatus:
        value = name_or_url.strip()

        if "://" in value:
            try:
                url = urlsplit(value)
                host = url.hostname
            except ValueError as exc:
                raise InvalidDomainName(value) from exc
            if url.scheme not in {"http", "https"} or host is None:
                raise InvalidDomainName(value)
            value = host

        name = Domain(name=value, status=DomainStatus.ALLOWED).name
        labels = name.split(".")
        candidates = tuple(".".join(labels[index:]) for index in range(len(labels) - 1))
        statuses = {
            domain.name: domain.status
            for domain in self._domains.find_by_names(candidates)
        }

        for candidate in candidates:
            if candidate in statuses:
                return statuses[candidate]
        return DomainStatus.ALLOWED
