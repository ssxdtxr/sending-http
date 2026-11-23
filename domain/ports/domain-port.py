from abc import ABC, abstractmethod

from domain.models.filter import FilterDomain
from domain.models.pagination import Pagination


class DomainPort(ABC):
    @abstractmethod
    def read_list(self, filter_: FilterDomain, pagination: Pagination):
        """Страницу с списком доменов по фильтрам и пагинации"""
        ...
