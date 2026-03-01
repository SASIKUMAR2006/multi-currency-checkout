from decimal import Decimal
from .base import FxProvider

class MockFxProvider(FxProvider):

    def __init__(self):
        self.rates = {
            "GBP_USD": Decimal("1.25"),
            "GBP_EUR": Decimal("1.15"),
            "GBP_GBP": Decimal("1.00")
        }

    def get_rate(self, base: str, target: str) -> Decimal:
        key = f"{base}_{target}"
        if key not in self.rates:
            raise ValueError("FX rate unavailable")
        return self.rates[key]
