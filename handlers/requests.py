from fastapi import APIRouter

from domain.models.request import Request
from domain.models.response import Response
from domain.services.request_service import RequestService
from handlers.schemas import RequestInput


def create_request_router(service: RequestService) -> APIRouter:
    router = APIRouter(prefix="/api/requests", tags=["Requests"])

    @router.post("")
    def send(payload: RequestInput) -> Response:
        request = Request(
            method=payload.method,
            url=payload.url,
            body=payload.body,
            headers=payload.headers,
            cookie=payload.cookie,
            timeout=payload.timeout,
        )

        return service.send(request)

    return router
