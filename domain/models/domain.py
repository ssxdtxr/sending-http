import ipaddress
import re
from dataclasses import dataclass
from enum import Enum


class DomainError(Exception):
    """Ошибка валидации домена"""


class IPAddressForbidden(DomainError):
    pass


class NotSecondDomainLevel(DomainError):
    pass


class HostNotExist(DomainError):
    pass


class InvalidDomainName(DomainError):
    pass


class InvalidDomainStatus(DomainError):
    pass


class DomainStatus(Enum):
    BANNED = "Banned"
    ALLOWED = "Allowed"


@dataclass(frozen=True, kw_only=True)
class Domain:
    id: int | None = None
    name: str
    status: DomainStatus
    comment: str = ""
    responsible: str = ""

    def __post_init__(self):
        self.validate()

        normalized_name = self.normalize_name(self.name)
        object.__setattr__(self, "name", normalized_name)

    def validate(self) -> None:
        if not isinstance(self.name, str):
            raise InvalidDomainName(f"{self.name} - некорректное доменное имя")

        host = self.normalize_name(self.name)

        if not host:
            raise HostNotExist("Хост не объявлен")

        if self.is_ip_address(host):
            raise IPAddressForbidden(f"{host} - IP-адреса запрещены")

        if not self.is_valid_domain_name(host):
            raise InvalidDomainName(f"{host} - некорректное доменное имя")

        if self.domain_level(host) < 2:
            raise NotSecondDomainLevel(
                f"Домен {host} не соответствует домену 2-го уровня"
            )

        if not isinstance(self.status, DomainStatus):
            raise InvalidDomainStatus(f"{self.status} - недопустимый статус домена")

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip().lower()

    @staticmethod
    def is_ip_address(address: str) -> bool:
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    @staticmethod
    def domain_level(domain: str) -> int:
        name = domain.lower()
        parts = name.split(".")

        return len(parts)

    @staticmethod
    def is_valid_domain_name(domain: str) -> bool:
        if len(domain) > 253:
            return False

        label_pattern = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")
        labels = domain.lower().split(".")

        return all(label_pattern.fullmatch(label) for label in labels)
