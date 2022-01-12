# stdlib
from abc import ABC, abstractmethod


class Exporter(ABC):
    @abstractmethod
    def __init__(self, table):
        pass

    @abstractmethod
    def to_file(self, filepath):
        pass
