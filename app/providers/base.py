from abc import ABC, abstractmethod
from decimal import Decimal

class FxProvider(ABC):

    @abstractmethod
    def get_rate(self, base: str, target: str) -> Decimal:
        pass
