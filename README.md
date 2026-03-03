# Multi-Currency Checkout System

A currency conversion checkout system built with FastAPI, supporting multi-currency payments with a mock FX provider, in-memory caching, and a web UI.

## Features

- **Multi-currency checkout**: Convert prices from GBP to USD, EUR, or keep in GBP
- **Mock FX provider**: Pluggable provider architecture with a mock implementation
- **In-memory caching**: FX rates cached with 5-minute TTL to reduce provider calls
- **1% FX markup**: Applied transparently on top of the base exchange rate
- **Financial precision**: All calculations use Python's `Decimal` type — no floating-point errors
- **Safe rounding**: `ROUND_HALF_UP` to 2 decimal places with rounding delta tracked
- **Currency dashboard**: View currency status, inflation data, and purchasing power comparisons
- **Web UI**: Interactive checkout form with real-time conversion results

## Setup Instructions

### Prerequisites

- Python 3.10+

### Installation

```bash
# Clone the repository
git clone https://github.com/SASIKUMAR2006/multi-currency-checkout.git
cd multi-currency-checkout

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

### Running Tests

```bash
pytest tests/ -v
```

## Architecture Overview

The system follows a **layered architecture** with clear separation of concerns:

```
Client (Browser)
    │
    ▼
API Layer (FastAPI)
    │
    ▼
Service Layer
    ├── CheckoutService    → Validates currency, applies markup, rounds amount
    ├── FxService          → Checks cache, fetches rate, stores in cache
    └── CurrencyInfoService → Status, inflation, purchasing power data
    │
    ▼
Provider Layer
    ├── FxProvider (ABC)   → Abstract interface for FX rate providers
    └── MockFxProvider     → Hardcoded rates (GBP→USD: 1.25, GBP→EUR: 1.15)
    │
    ▼
Cache Layer
    └── FxCache            → In-memory TTL cache (300 seconds)
```

### Key Design Decisions

- **Dependency Injection**: Services receive dependencies via constructor, making them testable and swappable.
- **Abstract Base Class**: `FxProvider` defines the contract — swap `MockFxProvider` for a real API provider without changing any other code.
- **Decimal everywhere**: `Decimal` is used for all financial values (rates, prices, calculations) to avoid floating-point precision issues.

### Checkout Flow

1. User submits amount + target currency via the form
2. `CheckoutService` validates the currency is in `{GBP, USD, EUR}`
3. `FxService` checks cache → on miss, fetches from `MockFxProvider` → caches result
4. 1% markup is applied to the FX rate
5. Amount is converted and rounded to 2 decimal places (`ROUND_HALF_UP`)
6. Response includes: `base_price`, `fx_rate_used`, `converted_price`, `rounding_applied`

For a detailed architecture diagram (Mermaid), see [ARCHITECTURE.md](ARCHITECTURE.md).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI (checkout form + currency dashboard) |
| POST | `/checkout?amount=100&currency=USD` | Perform currency conversion |
| GET | `/currency/status/{currency}` | Currency strength & status |
| GET | `/currency/inflation/{currency}` | Inflation data with historical trend |
| GET | `/currency/purchasing-power/{currency}` | Purchasing power comparison |
| GET | `/currency/report/{currency}` | Full currency report |
| GET | `/currencies/overview` | Overview of all supported currencies |

## Assumptions

- **Base currency is GBP**: All product prices are stored in British Pounds.
- **Three currencies supported**: GBP, EUR, and USD only.
- **Mock rates are static**: `GBP→USD = 1.25`, `GBP→EUR = 1.15`, `GBP→GBP = 1.00`.
- **1% markup**: Applied as a multiplier (`rate × 1.01`) on top of the base FX rate.
- **Cache TTL is 5 minutes**: Rates are re-fetched from the provider after expiry.
- **Single-threaded cache**: The in-memory cache is not thread-safe (suitable for development/demo).

## Known Limitations

- **No persistent storage**: Cache and rates are in-memory only; lost on restart.
- **No authentication**: Endpoints are publicly accessible with no auth layer.
- **No real FX provider**: Uses hardcoded mock rates, not live market data.
- **No thread safety**: The `FxCache` is not safe for concurrent access in multi-worker deployments.
- **No input sanitization beyond currency validation**: Amount is parsed directly to `Decimal`.
- **No database**: No order history or transaction logging.
- **Single base currency**: Only GBP is supported as the base; extending requires adding more rate pairs.

## Tech Stack

- **FastAPI** — Web framework
- **Jinja2** — HTML templating
- **Uvicorn** — ASGI server
- **Pytest** — Testing
- **Python Decimal** — Financial precision

## License

This project is for educational/assessment purposes.
