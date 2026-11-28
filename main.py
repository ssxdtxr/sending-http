import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI

from adapters.http_request import HttpRequestAdapter
from adapters.sqlite_domain import SQLiteDomainAdapter
from domain.services.domain_service import DomainService
from domain.services.request_service import RequestService
from handlers.api import create_app


# Обработчики FastAPI используют соединение в разных рабочих потоках.
# SQLiteDomainAdapter последовательно выполняет операции через Lock.
connection = sqlite3.connect("domains.sqlite3", check_same_thread=False)
try:
    with connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL CHECK (status IN ('Allowed', 'Banned')),
                comment TEXT NOT NULL,
                responsible TEXT NOT NULL
            )
        """)
except Exception:
    connection.close()
    raise

domain_adapter = SQLiteDomainAdapter(connection)
http_adapter = HttpRequestAdapter()
domain_service = DomainService(domain_adapter)
request_service = RequestService(domain_service, http_adapter)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        connection.close()


app = create_app(domain_service, request_service, lifespan=lifespan)
