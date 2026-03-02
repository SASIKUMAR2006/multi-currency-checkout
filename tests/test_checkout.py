from decimal import Decimal
from app.services.checkout_service import CheckoutService
from app.services.fx_service import FxService
from app.services.currency_info_service import CurrencyInfoService
from app.providers.mock_provider import MockFxProvider
from app.cache.fx_cache import FxCache

def test_conversion_usd():
    provider = MockFxProvider()
    cache = FxCache()
    fx_service = FxService(provider, cache)
    checkout = CheckoutService(fx_service)

    result = checkout.checkout(Decimal("100"), "USD")

    assert "converted_price" in result


def test_conversion_eur():
    provider = MockFxProvider()
    cache = FxCache()
    fx_service = FxService(provider, cache)
    checkout = CheckoutService(fx_service)

    result = checkout.checkout(Decimal("100"), "EUR")

    assert "converted_price" in result


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
    try:
        service.get_currency_status("JPY")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


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
    try:
        service.get_inflation_data("JPY")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


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
