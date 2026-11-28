from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.types import Lifespan

from domain.models.domain import DomainError, DomainStatus
from domain.models.request import RequestError
from domain.ports.domain_port import DomainAlreadyExists, DomainNotFound
from domain.ports.request_port import RequestTransportError
from domain.services.domain_service import DomainService
from domain.services.request_service import DomainForbidden, RequestService
from handlers.domains import create_domain_list_router, create_domain_status_router
from handlers.requests import create_request_router


def create_app(
    domains: DomainService,
    requests: RequestService,
    *,
    lifespan: Lifespan[FastAPI] | None = None,
) -> FastAPI:
    """Собрать HTTP-слой из готовых сервисов.

    Синхронные обработчики выполняются в рабочих потоках FastAPI.
    Передаваемые сервисы и их адаптеры должны поддерживать такой вызов.
    """
    app = FastAPI(title="Сервис безопасных HTTP-запросов", lifespan=lifespan)
    app.include_router(
        create_domain_list_router("/api/allowed-domains", DomainStatus.ALLOWED, domains)
    )
    app.include_router(
        create_domain_list_router("/api/banned-domains", DomainStatus.BANNED, domains)
    )
    app.include_router(create_domain_status_router(domains))
    app.include_router(create_request_router(requests))

    @app.exception_handler(DomainAlreadyExists)
    async def already_exists(_request: Request, exc: DomainAlreadyExists) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(DomainNotFound)
    async def not_found(_request: Request, exc: DomainNotFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(DomainForbidden)
    async def forbidden(_request: Request, exc: DomainForbidden) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(RequestTransportError)
    async def transport_error(_request: Request, exc: RequestTransportError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(DomainError)
    @app.exception_handler(RequestError)
    async def invalid_input(_request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    return app
