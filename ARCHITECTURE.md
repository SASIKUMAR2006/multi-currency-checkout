# Multi-Currency Checkout System - Architecture Diagram

## System Architecture

```mermaid
graph TB
    subgraph Client["🌐 Client Layer"]
        Browser["Web Browser"]
        Form["Checkout Form"]
    end

    subgraph FastAPI["📡 API Layer - FastAPI"]
        Home["GET / - Home Route"]
        Checkout["POST /checkout - Checkout Endpoint"]
    end

    subgraph Templates["📄 Presentation Layer"]
        HTML["index.html<br/>Jinja2 Template"]
    end

    subgraph Services["⚙️ Business Logic Layer"]
        CheckoutSvc["CheckoutService<br/>- Validate Currency<br/>- Apply Markup 1%<br/>- Round Amount"]
        FxSvc["FxService<br/>- Check Cache<br/>- Fetch Rate<br/>- Store in Cache"]
    end

    subgraph Providers["🔌 Provider Layer"]
        FxProviderBase["FxProvider<br/>Abstract Base Class"]
        MockFxProvider["MockFxProvider<br/>- GBP_USD: 1.25<br/>- GBP_EUR: 1.15<br/>- GBP_GBP: 1.00"]
    end

    subgraph Cache["💾 Cache Layer"]
        FxCache["FxCache<br/>- TTL: 300 seconds<br/>- Key-Value Store"]
    end

    subgraph DataFlow["📊 Data Flow"]
        Response["Response JSON<br/>- base_price<br/>- fx_rate_used<br/>- converted_price<br/>- rounding_applied"]
    end

    %% Client interactions
    Browser -->|"1. Load Page"| Home
    Home -->|"2. Return HTML"| HTML
    Browser -->|"3. Submit Form<br/>(amount, currency)"| Checkout

    %% API to Service
    Checkout -->|"4. Call checkout()<br/>(amount, currency)"| CheckoutSvc

    %% CheckoutService workflow
    CheckoutSvc -->|"5a. Validate currency<br/>GBP, USD, EUR"| CheckoutSvc
    CheckoutSvc -->|"5b. Get exchange rate"| FxSvc

    %% FxService caching logic
    FxSvc -->|"6a. Check for cached rate"| FxCache
    FxCache -->|"Cache HIT"| FxSvc
    FxCache -->|"Cache MISS"| FxSvc

    %% Provider hierarchy
    FxSvc -->|"6b. Fetch from provider"| FxProviderBase
    FxProviderBase -->|"Implements"| MockFxProvider

    %% Response generation
    MockFxProvider -->|"7. Return rate"| FxSvc
    FxSvc -->|"8. Cache rate"| FxCache
    FxSvc -->|"9. Return rate"| CheckoutSvc

    %% Calculation and response
    CheckoutSvc -->|"10. Apply markup<br/>Convert & Round"| CheckoutSvc
    CheckoutSvc -->|"11. Return result"| Response
    Response -->|"12. JSON Response"| Browser
    Browser -->|"13. Display Result"| Form

    %% Styling
    classDef clientLayer fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef apiLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serviceLayer fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef providerLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef cacheLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef dataLayer fill:#f1f8e9,stroke:#33691e,stroke-width:2px

    class Browser,Form clientLayer
    class Home,Checkout apiLayer
    class HTML clientLayer
    class CheckoutSvc,FxSvc serviceLayer
    class FxProviderBase,MockFxProvider providerLayer
    class FxCache cacheLayer
    class Response dataLayer
```

## Layer Overview

### 1. **Client Layer** 🌐
- **Web Browser**: Client application
- **Checkout Form**: User interface for entering amount and currency

### 2. **API Layer** 📡
- **FastAPI Framework**: Modern web framework for building APIs
- **GET /**: Serves home page with HTML template
- **POST /checkout**: Processes currency conversion requests

### 3. **Presentation Layer** 📄
- **index.html**: Jinja2 template rendering the checkout form interface

### 4. **Business Logic Layer** ⚙️
- **CheckoutService**: 
  - Validates currency (allowed: GBP, USD, EUR)
  - Applies 1% markup to exchange rate
  - Rounds converted amount to 2 decimal places
  
- **FxService**: 
  - Checks cache for exchange rates
  - Fetches rates from provider if not cached
  - Stores rates in cache for reuse

### 5. **Provider Layer** 🔌
- **FxProvider**: Abstract base class defining the exchange rate provider interface
- **MockFxProvider**: Concrete implementation with hardcoded rates:
  - GBP → USD: 1.25
  - GBP → EUR: 1.15
  - GBP → GBP: 1.00
  
*Extensible design allows replacing MockFxProvider with real external providers*

### 6. **Cache Layer** 💾
- **FxCache**: In-memory time-to-live (TTL) cache
  - Default TTL: 300 seconds (5 minutes)
  - Key format: `BASE_TARGET` (e.g., `GBP_USD`)
  - Prevents redundant provider calls for the same currency pairs

## Data Flow

1. **Client Request**: Browser submits checkout form with amount and currency
2. **API Routing**: FastAPI receives POST request to `/checkout` endpoint
3. **Validation**: CheckoutService validates the requested currency
4. **Rate Lookup**: CheckoutService requests exchange rate from FxService
5. **Cache Check**: FxService checks if rate is already cached
6. **Provider Fetch**: If cache miss, FxService fetches rate from FxProvider
7. **Cache Store**: Rate is stored in FxCache with TTL
8. **Conversion**: CheckoutService applies 1% markup and converts amount
9. **Rounding**: Amount is rounded to 2 decimal places (HALF_UP)
10. **Response**: JSON response with base price, rate used, converted price, and rounding difference
11. **Display**: Browser renders the conversion result to user

## Project Structure

```
multi_currency_checkout_with_ui/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── cache/
│   │   └── fx_cache.py         # FxCache implementation
│   ├── providers/
│   │   ├── base.py             # FxProvider abstract base class
│   │   └── mock_provider.py    # MockFxProvider implementation
│   ├── services/
│   │   ├── checkout_service.py # CheckoutService implementation
│   │   └── fx_service.py       # FxService implementation
│   └── templates/
│       └── index.html          # Checkout form template
├── tests/
│   └── test_checkout.py        # Test suite
├── requirements.txt            # Python dependencies
└── ARCHITECTURE.md             # This file
```

## Key Design Patterns

### Dependency Injection
All services receive their dependencies via constructor, making them testable and flexible:
```python
fx_service = FxService(provider, cache)
checkout_service = CheckoutService(fx_service)
```

### Abstract Base Classes
`FxProvider` defines the contract for exchange rate providers, allowing easy swapping of implementations:
```python
class FxProvider(ABC):
    @abstractmethod
    def get_rate(self, base: str, target: str) -> Decimal:
        pass
```

### Caching Strategy
TTL-based caching reduces external provider calls while ensuring data freshness:
- Cache validates expiry before returning cached values
- Automatic cleanup of expired entries

### Layered Architecture
Clear separation of concerns:
- **API Layer**: HTTP handling
- **Service Layer**: Business logic
- **Provider Layer**: External data sources
- **Cache Layer**: Performance optimization

## Extension Points

To integrate a real FX provider (e.g., external API):

1. Create a new provider class extending `FxProvider`:
```python
class RealFxProvider(FxProvider):
    def get_rate(self, base: str, target: str) -> Decimal:
        # Call real API
        pass
```

2. Swap the provider in `main.py`:
```python
provider = RealFxProvider()  # Instead of MockFxProvider()
```

The rest of the system remains unchanged due to abstraction!
