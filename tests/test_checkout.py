from decimal import Decimal
from app.services.checkout_service import CheckoutService
from app.services.fx_service import FxService
from app.providers.mock_provider import MockFxProvider
from app.cache.fx_cache import FxCache

def test_conversion_usd():
    provider = MockFxProvider()
    cache = FxCache()
    fx_service = FxService(provider, cache)
    checkout = CheckoutService(fx_service)

    result = checkout.checkout(Decimal("100"), "USD")

    assert "converted_price" in result
