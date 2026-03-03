from decimal import Decimal
import pytest
from app.services.checkout_service import CheckoutService
from app.services.fx_service import FxService
from app.services.currency_info_service import CurrencyInfoService
from app.providers.mock_provider import MockFxProvider
from app.cache.fx_cache import FxCache


# --- Helper to build a fresh checkout service ---

def _make_checkout():
    provider = MockFxProvider()
    cache = FxCache()
    fx_service = FxService(provider, cache)
    return CheckoutService(fx_service)


# ============================================================
# Conversion tests – value assertions
# ============================================================

def test_conversion_usd():
    checkout = _make_checkout()
    result = checkout.checkout(Decimal("100"), "USD")

    # 100 * 1.25 * 1.01 = 126.25 (exact, no rounding needed)
    assert result["base_price"] == "100"
    assert result["converted_price"] == "126.25"
    assert result["fx_rate_used"] == "1.2625"
    assert result["rounding_applied"] == "0.000000"


def test_conversion_eur():
    checkout = _make_checkout()
    result = checkout.checkout(Decimal("100"), "EUR")

    # 100 * 1.15 * 1.01 = 116.15 (exact)
    assert result["base_price"] == "100"
    assert result["converted_price"] == "116.15"
    assert result["fx_rate_used"] == "1.1615"
    assert result["rounding_applied"] == "0.000000"


def test_conversion_gbp_same_currency():
    checkout = _make_checkout()
    result = checkout.checkout(Decimal("50"), "GBP")

    # 50 * 1.00 * 1.01 = 50.50 (exact)
    assert result["converted_price"] == "50.50"
    assert result["fx_rate_used"] == "1.0100"


def test_conversion_rounding_applied():
    """Verify rounding is applied and tracked for non-round amounts."""
    checkout = _make_checkout()
    # 99.99 * 1.2625 = 126.237375 → rounds to 126.24
    result = checkout.checkout(Decimal("99.99"), "USD")

    assert result["converted_price"] == "126.24"
    # rounding_applied = 126.24 - 126.237375 = 0.002625
    assert Decimal(result["rounding_applied"]) == Decimal("0.002625")


def test_conversion_small_amount():
    checkout = _make_checkout()
    result = checkout.checkout(Decimal("0.01"), "USD")

    # 0.01 * 1.2625 = 0.012625 → rounds to 0.01
    assert result["converted_price"] == "0.01"


def test_conversion_large_amount():
    checkout = _make_checkout()
    result = checkout.checkout(Decimal("999999.99"), "EUR")

    # 999999.99 * 1.1615 = 1161499.988385 → rounds to 1161499.99
    assert result["converted_price"] == "1161499.99"


# ============================================================
# Edge-case tests
# ============================================================

def test_invalid_currency_raises():
    checkout = _make_checkout()
    with pytest.raises(ValueError, match="Invalid currency"):
        checkout.checkout(Decimal("100"), "JPY")


def test_fx_rate_unavailable():
    """Provider raises ValueError for unsupported pairs."""
    provider = MockFxProvider()
    with pytest.raises(ValueError, match="FX rate unavailable"):
        provider.get_rate("GBP", "JPY")


def test_response_contains_all_keys():
    checkout = _make_checkout()
    result = checkout.checkout(Decimal("100"), "USD")

    for key in ("base_price", "fx_rate_used", "converted_price",
                "rounding_applied", "fx_rate_timestamp"):
        assert key in result


# ============================================================
# Cache tests
# ============================================================

def test_cache_returns_cached_rate():
    """FxService should return the same rate on second call (from cache)."""
    provider = MockFxProvider()
    cache = FxCache()
    fx_service = FxService(provider, cache)

    rate1 = fx_service.get_rate("GBP", "USD")
    rate2 = fx_service.get_rate("GBP", "USD")
    assert rate1 == rate2 == Decimal("1.25")


def test_cache_ttl_expiry():
    """Expired cache entries should not be returned."""
    cache = FxCache(ttl_seconds=0)  # Immediate expiry
    cache.set("GBP_USD", Decimal("1.25"))

    import time
    time.sleep(0.01)
    assert cache.get("GBP_USD") is None


def test_currency_status_usd():
    service = CurrencyInfoService()
    status = service.get_currency_status("USD")

    assert status["currency_code"] == "USD"
    assert status["status"] == "strong"
    assert status["strength"] == "high"
    assert "central_bank" in status
    assert "interest_rate" in status
    assert "factors" in status


def test_currency_status_gbp():
    service = CurrencyInfoService()
    status = service.get_currency_status("GBP")

    assert status["currency_code"] == "GBP"
    assert status["status"] == "stable"


def test_currency_status_eur():
    service = CurrencyInfoService()
    status = service.get_currency_status("EUR")

    assert status["currency_code"] == "EUR"
    assert status["status"] == "recovering"


def test_currency_status_invalid():
    service = CurrencyInfoService()
    with pytest.raises(ValueError):
        service.get_currency_status("JPY")


def test_inflation_data_usd():
    service = CurrencyInfoService()
    data = service.get_inflation_data("USD")

    assert data["currency_code"] == "USD"
    assert data["country"] == "United States"
    assert data["current_rate"] == 2.8
    assert data["target_rate"] == 2.0
    assert data["deviation_from_target"] == 0.8
    assert data["direction"] == "decreasing"
    assert "historical" in data
    assert len(data["historical"]) == 5


def test_inflation_data_gbp():
    service = CurrencyInfoService()
    data = service.get_inflation_data("GBP")

    assert data["country"] == "United Kingdom"
    assert data["current_rate"] == 3.2
    assert data["deviation_from_target"] == 1.2


def test_inflation_data_eur():
    service = CurrencyInfoService()
    data = service.get_inflation_data("EUR")

    assert data["country"] == "Eurozone"
    assert data["current_rate"] == 2.4


def test_inflation_data_invalid():
    service = CurrencyInfoService()
    with pytest.raises(ValueError):
        service.get_inflation_data("JPY")


def test_purchasing_power():
    service = CurrencyInfoService()
    pp = service.get_purchasing_power("USD")

    assert pp["currency_code"] == "USD"
    assert pp["big_mac_index"] == 5.69
    assert "basket_cost" in pp
    assert "ppp_rate" in pp


def test_all_currencies_overview():
    service = CurrencyInfoService()
    overview = service.get_all_currencies_overview()

    assert len(overview) == 3
    codes = [c["code"] for c in overview]
    assert "GBP" in codes
    assert "USD" in codes
    assert "EUR" in codes

    for entry in overview:
        assert "name" in entry
        assert "status" in entry
        assert "inflation" in entry
        assert "interest_rate" in entry


def test_full_currency_report():
    service = CurrencyInfoService()
    report = service.get_full_currency_report("GBP")

    assert "status" in report
    assert "inflation" in report
    assert "purchasing_power" in report
    assert report["status"]["currency_code"] == "GBP"
    assert report["inflation"]["currency_code"] == "GBP"
    assert report["purchasing_power"]["currency_code"] == "GBP"
