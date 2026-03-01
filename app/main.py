from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from decimal import Decimal

from app.providers.mock_provider import MockFxProvider
from app.cache.fx_cache import FxCache
from app.services.fx_service import FxService
from app.services.checkout_service import CheckoutService

app = FastAPI(title="Multi-Currency Checkout API")

templates = Jinja2Templates(directory="app/templates")

provider = MockFxProvider()
cache = FxCache()
fx_service = FxService(provider, cache)
checkout_service = CheckoutService(fx_service)

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
