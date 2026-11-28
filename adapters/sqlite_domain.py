from contextlib import closing
from dataclasses import replace
from sqlite3 import SQLITE_CONSTRAINT_UNIQUE, Connection, IntegrityError, Row

from domain.models.domain import Domain, DomainStatus
from domain.models.filter import FilterDomain
from domain.models.pagination import Page, Pagination
from domain.ports.domain_port import DomainAlreadyExists, DomainNotFound, DomainPort


class SQLiteDomainAdapter(DomainPort):
    """Адаптер SQLite, получающий соединение от вызывающего кода."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(self, domain: Domain) -> Domain:
        """Сохранить домен и вернуть его с присвоенным ID.

        Столбец id должен быть INTEGER PRIMARY KEY, а name иметь ограничение UNIQUE.
        Если имя уже занято, вызвать DomainAlreadyExists.
        """
        with (
            self._connection,
            closing(self._connection.cursor()) as cursor,
        ):
            cursor.execute(
                """
                INSERT INTO domains (name, status, comment, responsible)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """,
                (
                    domain.name,
                    domain.status.value,
                    domain.comment,
                    domain.responsible,
                ),
            )
            row = cursor.fetchone()
            if row is None:
                raise DomainAlreadyExists(domain.name)

            return replace(domain, id=row[0])

    def read_list(self, filter_: FilterDomain, pagination: Pagination) -> Page[Domain]:
        """Получить страницу доменов с фильтрацией по имени и статусу.

        В Page.total вернуть количество всех записей, подходящих под фильтр,
        а в Page.items — записи запрошенной страницы.
        """
        name = Domain.normalize_name(filter_.name)
        status = None
        if filter_.status is not None:
            status = filter_.status.value

        with self._connection, closing(self._connection.cursor()) as cursor:
            cursor.row_factory = Row
            # Количество и страница должны читаться из одного снимка данных.
            if not self._connection.in_transaction:
                cursor.execute("BEGIN")

            cursor.execute(
                """
                SELECT count(*) AS total FROM domains
                WHERE instr(name, ?) > 0 AND status = COALESCE(?, status)
                """,
                (name, status),
            )
            total = cursor.fetchone()["total"]

            cursor.execute(
                """
                SELECT id, name, status, comment, responsible FROM domains
                WHERE instr(name, ?) > 0 AND status = COALESCE(?, status)
                ORDER BY name
                LIMIT ? OFFSET ?
                """,
                (name, status, pagination.limit, pagination.offset),
            )
            domains = []
            for row in cursor:
                domains.append(self._to_domain(row))

            return Page(items=tuple(domains), total=total, pagination=pagination)

    def find_by_names(self, names: tuple[str, ...]) -> tuple[Domain, ...]:
        """Получить записи с именами из переданного набора.

        Если совпадений нет, вернуть пустой кортеж.
        Выбор ближайшего родительского домена выполняет DomainService.
        """
        if not names:
            return ()

        placeholders = ", ".join(["?"] * len(names))
        with closing(self._connection.cursor()) as cursor:
            cursor.row_factory = Row
            cursor.execute(
                f"""
                SELECT id, name, status, comment, responsible FROM domains
                WHERE name IN ({placeholders})
                ORDER BY name
                """,
                names,
            )
            domains = []
            for row in cursor:
                domains.append(self._to_domain(row))

            return tuple(domains)

    def update(
        self, domain: Domain, *, expected_status: DomainStatus | None = None
    ) -> Domain:
        """Обновить запись по ID и вернуть обновлённый домен.

        При заданном expected_status изменять запись только при совпадении
        её текущего статуса. Если подходящей записи нет, вызвать DomainNotFound.
        Если новое имя занято другим доменом, вызвать DomainAlreadyExists.
        """
        status = None
        if expected_status is not None:
            status = expected_status.value

        try:
            with self._connection, closing(self._connection.cursor()) as cursor:
                cursor.execute(
                    """
                    UPDATE domains
                    SET name = ?, status = ?, comment = ?, responsible = ?
                    WHERE id = ? AND status = COALESCE(?, status)
                    """,
                    (
                        domain.name,
                        domain.status.value,
                        domain.comment,
                        domain.responsible,
                        domain.id,
                        status,
                    ),
                )
                if cursor.rowcount == 0:
                    raise DomainNotFound(domain.id)

                return domain
        except IntegrityError as exc:
            if exc.sqlite_errorcode == SQLITE_CONSTRAINT_UNIQUE:
                raise DomainAlreadyExists(domain.name) from exc
            raise

    def delete(
        self, domain_id: int, *, expected_status: DomainStatus | None = None
    ) -> None:
        """Удалить запись по ID.

        При заданном expected_status удалять запись только при совпадении
        её текущего статуса. Если подходящей записи нет, вызвать DomainNotFound.
        """
        status = None
        if expected_status is not None:
            status = expected_status.value

        with self._connection, closing(self._connection.cursor()) as cursor:
            cursor.execute(
                "DELETE FROM domains WHERE id = ? AND status = COALESCE(?, status)",
                (domain_id, status),
            )
            if cursor.rowcount == 0:
                raise DomainNotFound(domain_id)

    @staticmethod
    def _to_domain(row: Row) -> Domain:
        """Преобразовать строку таблицы в доменную модель."""
        return Domain(
            id=row["id"],
            name=row["name"],
            status=DomainStatus(row["status"]),
            comment=row["comment"],
            responsible=row["responsible"],
        )
