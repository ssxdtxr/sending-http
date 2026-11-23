from dataclasses import dataclass
from urllib.parse import urlparse


class RequestError(Exception):
    """Ошибка валидации запроса"""


class InvalidMethod(RequestError):
    pass


class InvalidTimeout(RequestError):
    pass


class NotValidUrl(RequestError):
    pass


@dataclass(frozen=True)
class Request:
    method: str
    url: str
    headers: dict
    body: str
    cookie: str
    timeout: int

    def __post_init__(self):
        self.validate()

    def validate(self):
        allowed_methods = [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
        ]

        if self.method not in allowed_methods:
            raise InvalidMethod(f"Метод {self.method} не валидный")

        if self.timeout <= 0:
            raise InvalidTimeout(f"Таймаут не должен быть равен {self.timeout}")

        try:
            parsed_url = urlparse(self.url)
            host = parsed_url.hostname
        except ValueError:
            raise NotValidUrl(f"{self.url} - URL не валидный")

        if parsed_url.scheme not in {"http", "https"} or host is None:
            raise NotValidUrl(f"{self.url} - URL не валидный")
