from abc import ABC, abstractmethod

from domain.models.request import Request
from domain.models.response import Response


class RequestTransportError(Exception):
    pass


class RequestPort(ABC):
    @abstractmethod
    def send(self, request: Request) -> Response: ...
