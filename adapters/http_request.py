from contextlib import closing
from http.client import HTTPConnection, HTTPException, HTTPSConnection
from urllib.parse import urlsplit

from domain.models.request import Request
from domain.models.response import Response
from domain.ports.request_port import RequestPort, RequestTransportError


class HttpRequestAdapter(RequestPort):
    """Выполняет один HTTP-запрос. Перенаправления возвращает вызывающему коду."""

    def send(self, request: Request) -> Response:
        try:
            url = urlsplit(request.url)
            host = url.hostname
            if host is None:
                raise RequestTransportError("В URL не указан хост")

            connection_type = (
                HTTPSConnection if url.scheme == "https" else HTTPConnection
            )
            target = url.path or "/"
            if url.query:
                target += "?" + url.query

            headers = dict(request.headers)
            if request.cookie:
                new_headers = {}

                for name, value in headers.items():
                    if name.lower() != "cookie":
                        new_headers[name] = value

                headers = new_headers
                headers["Cookie"] = request.cookie

            with closing(
                connection_type(host, url.port, timeout=request.timeout)
            ) as connection:
                """Отправляется запрос"""
                connection.request(
                    request.method,
                    target,
                    body=request.body.encode("utf-8"),
                    headers=headers,
                )

                """Получить ответ"""
                with connection.getresponse() as response:
                    content = response.read()
                    encoding = response.headers.get_content_charset() or "utf-8"
                    try:
                        body = content.decode(encoding, errors="replace")
                    except LookupError:
                        body = content.decode("utf-8", errors="replace")

                    return Response(
                        status_code=response.status,
                        body=body,
                        headers=dict(response.getheaders()),
                    )
        except (OSError, HTTPException, ValueError) as exc:
            raise RequestTransportError("Не удалось выполнить HTTP-запрос") from exc
