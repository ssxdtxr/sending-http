from domain.models.domain import DomainStatus
from domain.models.request import Request, RequestError
from domain.models.response import Response
from domain.ports.request_port import RequestPort
from domain.services.domain_service import DomainService


class DomainForbidden(RequestError):
    status_code = 403


class RequestService:
    def __init__(self, domains: DomainService, transport: RequestPort) -> None:
        self._domains = domains
        self._transport = transport

    def send(self, request: Request) -> Response:
        if self._domains.status(request.url) == DomainStatus.BANNED:
            raise DomainForbidden("Запрос к этому домену запрещён")

        return self._transport.send(request)
