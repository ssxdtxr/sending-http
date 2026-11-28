from fastapi import APIRouter, HTTPException, Path, Query, Response

from domain.models.domain import Domain, DomainStatus
from domain.models.filter import FilterDomain
from domain.models.pagination import Page, Pagination
from domain.services.domain_service import DomainService
from handlers.schemas import DomainInput, StatusOutput

MAX_ID = 2**63 - 1


def create_domain_list_router(
    prefix: str, status: DomainStatus, service: DomainService
) -> APIRouter:
    """Создать одинаковые CRUD-маршруты для выбранного списка."""
    router = APIRouter(prefix=prefix, tags=[status.value])

    @router.get("")
    def read_list(
        name: str = "",
        page: int = Query(default=1, ge=1, le=MAX_ID),
        limit: int = Query(default=20, ge=1, le=MAX_ID),
    ) -> Page[Domain]:
        pagination = Pagination(page=page, limit=limit)
        if pagination.offset > MAX_ID:
            raise HTTPException(
                status_code=422, detail="Слишком большой номер страницы"
            )

        filters = FilterDomain(name=name, status=status)
        return service.read_list(filters, pagination)

    @router.post("", status_code=201)
    def create(payload: DomainInput) -> Domain:
        domain = Domain(
            name=payload.name,
            status=status,
            comment=payload.comment,
            responsible=payload.responsible,
        )
        return service.create(domain)

    @router.put("/{domain_id}")
    def update(
        payload: DomainInput,
        domain_id: int = Path(ge=1, le=MAX_ID),
    ) -> Domain:
        domain = Domain(
            id=domain_id,
            name=payload.name,
            status=status,
            comment=payload.comment,
            responsible=payload.responsible,
        )
        return service.update(domain, expected_status=status)

    @router.delete("/{domain_id}", status_code=204)
    def delete(domain_id: int = Path(ge=1, le=MAX_ID)) -> Response:
        service.delete(domain_id, expected_status=status)
        return Response(status_code=204)

    return router


def create_domain_status_router(service: DomainService) -> APIRouter:
    router = APIRouter(prefix="/api/domains", tags=["Domains"])

    @router.get("/status")
    def get_status(name: str = Query(min_length=1)) -> StatusOutput:
        return StatusOutput(status=service.status(name))

    return router
