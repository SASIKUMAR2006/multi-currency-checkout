from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from decimal import Decimal

from app.providers.mock_provider import MockFxProvider
from app.cache.fx_cache import FxCache
from app.services.fx_service import FxService
from app.services.checkout_service import CheckoutService
from app.services.currency_info_service import CurrencyInfoService

app = FastAPI(title="Multi-Currency Checkout API")

templates = Jinja2Templates(directory="app/templates")

provider = MockFxProvider()
cache = FxCache()
fx_service = FxService(provider, cache)
checkout_service = CheckoutService(fx_service)
currency_info_service = CurrencyInfoService()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/checkout")
def checkout(amount: str, currency: str):
    try:
        result = checkout_service.checkout(
            Decimal(amount),
            currency
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/currency/status/{currency}")
def currency_status(currency: str):
    """Get current status and strength indicators for a currency."""
    try:
        return currency_info_service.get_currency_status(currency.upper())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/currency/inflation/{currency}")
def currency_inflation(currency: str):
    """Get inflation data for a currency's country/region."""
    try:
        return currency_info_service.get_inflation_data(currency.upper())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/currency/purchasing-power/{currency}")
def currency_purchasing_power(currency: str):
    """Get purchasing power comparison for a currency."""
    try:
        return currency_info_service.get_purchasing_power(currency.upper())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/currency/report/{currency}")
def currency_full_report(currency: str):
    """Get comprehensive report combining status, inflation, and purchasing power."""
    try:
        return currency_info_service.get_full_currency_report(currency.upper())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/currencies/overview")
def currencies_overview():
    """Get an overview of all supported currencies."""
    return currency_info_service.get_all_currencies_overview()
