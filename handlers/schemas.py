from pydantic import BaseModel, ConfigDict, Field

from domain.models.domain import DomainStatus


class DomainInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    comment: str = ""
    responsible: str = ""


class StatusOutput(BaseModel):
    status: DomainStatus


class RequestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    url: str
    body: str = ""
    headers: dict[str, str] = Field(default_factory=dict)
    cookie: str = ""
    timeout: int = Field(default=10, gt=0)
