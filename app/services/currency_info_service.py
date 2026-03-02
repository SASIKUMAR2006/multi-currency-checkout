from decimal import Decimal
from datetime import datetime


class CurrencyInfoService:
    """
    Provides currency status, inflation data, and economic indicators
    for supported currencies.
    """

    # Inflation rates (annual %) - simulated data as of early 2026
    INFLATION_DATA = {
        "GBP": {
            "country": "United Kingdom",
            "current_rate": 3.2,
            "previous_rate": 3.5,
            "target_rate": 2.0,
            "trend": "falling",
            "last_updated": "2026-02-01",
            "historical": [
                {"period": "2025-Q4", "rate": 3.5},
                {"period": "2025-Q3", "rate": 3.8},
                {"period": "2025-Q2", "rate": 4.1},
                {"period": "2025-Q1", "rate": 4.5},
                {"period": "2024-Q4", "rate": 4.2},
            ],
        },
        "USD": {
            "country": "United States",
            "current_rate": 2.8,
            "previous_rate": 3.0,
            "target_rate": 2.0,
            "trend": "falling",
            "last_updated": "2026-02-01",
            "historical": [
                {"period": "2025-Q4", "rate": 3.0},
                {"period": "2025-Q3", "rate": 3.3},
                {"period": "2025-Q2", "rate": 3.5},
                {"period": "2025-Q1", "rate": 3.7},
                {"period": "2024-Q4", "rate": 3.4},
            ],
        },
        "EUR": {
            "country": "Eurozone",
            "current_rate": 2.4,
            "previous_rate": 2.6,
            "target_rate": 2.0,
            "trend": "falling",
            "last_updated": "2026-02-01",
            "historical": [
                {"period": "2025-Q4", "rate": 2.6},
                {"period": "2025-Q3", "rate": 2.9},
                {"period": "2025-Q2", "rate": 3.1},
                {"period": "2025-Q1", "rate": 3.4},
                {"period": "2024-Q4", "rate": 3.1},
            ],
        },
    }

    # Currency status and strength indicators
    CURRENCY_STATUS = {
        "GBP": {
            "name": "British Pound Sterling",
            "symbol": "£",
            "central_bank": "Bank of England",
            "interest_rate": 4.25,
            "status": "stable",
            "strength": "moderate",
            "volatility": "low",
            "trading_volume": "high",
            "year_high": 1.32,
            "year_low": 1.21,
            "sentiment": "neutral",
            "factors": [
                "BoE maintaining restrictive monetary policy",
                "Inflation trending toward target",
                "Brexit trade adjustments stabilizing",
            ],
        },
        "USD": {
            "name": "US Dollar",
            "symbol": "$",
            "central_bank": "Federal Reserve",
            "interest_rate": 4.50,
            "status": "strong",
            "strength": "high",
            "volatility": "low",
            "trading_volume": "very high",
            "year_high": 1.00,
            "year_low": 1.00,
            "sentiment": "bullish",
            "factors": [
                "Federal Reserve hawkish stance",
                "Strong labor market data",
                "Safe-haven demand persists",
            ],
        },
        "EUR": {
            "name": "Euro",
            "symbol": "€",
            "central_bank": "European Central Bank",
            "interest_rate": 3.75,
            "status": "recovering",
            "strength": "moderate",
            "volatility": "moderate",
            "trading_volume": "high",
            "year_high": 1.18,
            "year_low": 1.08,
            "sentiment": "cautiously optimistic",
            "factors": [
                "ECB rate cuts expected mid-2026",
                "Manufacturing recovery in Germany",
                "Energy prices stabilizing",
            ],
        },
    }

    # Purchasing power index (relative to GBP basket of goods)
    PURCHASING_POWER = {
        "GBP": {"big_mac_index": 4.19, "basket_cost": 100.00, "ppp_rate": 1.00},
        "USD": {"big_mac_index": 5.69, "basket_cost": 128.50, "ppp_rate": 1.285},
        "EUR": {"big_mac_index": 4.65, "basket_cost": 117.30, "ppp_rate": 1.173},
    }

    def get_currency_status(self, currency: str) -> dict:
        """Get the current status and strength indicators for a currency."""
        if currency not in self.CURRENCY_STATUS:
            raise ValueError(f"Currency status unavailable for {currency}")

        status = self.CURRENCY_STATUS[currency].copy()
        status["currency_code"] = currency
        status["last_checked"] = datetime.now().isoformat()
        return status

    def get_inflation_data(self, currency: str) -> dict:
        """Get inflation data for a currency's country/region."""
        if currency not in self.INFLATION_DATA:
            raise ValueError(f"Inflation data unavailable for {currency}")

        data = self.INFLATION_DATA[currency].copy()
        data["currency_code"] = currency

        # Calculate inflation difference from target
        data["deviation_from_target"] = round(
            data["current_rate"] - data["target_rate"], 2
        )

        # Inflation direction indicator
        change = data["current_rate"] - data["previous_rate"]
        if change < -0.1:
            data["direction"] = "decreasing"
            data["direction_icon"] = "↓"
        elif change > 0.1:
            data["direction"] = "increasing"
            data["direction_icon"] = "↑"
        else:
            data["direction"] = "stable"
            data["direction_icon"] = "→"

        return data

    def get_purchasing_power(self, currency: str) -> dict:
        """Get purchasing power comparison data for a currency."""
        if currency not in self.PURCHASING_POWER:
            raise ValueError(f"Purchasing power data unavailable for {currency}")

        data = self.PURCHASING_POWER[currency].copy()
        data["currency_code"] = currency
        return data

    def get_all_currencies_overview(self) -> list:
        """Get a complete overview of all supported currencies."""
        overview = []
        for currency in self.CURRENCY_STATUS:
            entry = {
                "code": currency,
                "name": self.CURRENCY_STATUS[currency]["name"],
                "symbol": self.CURRENCY_STATUS[currency]["symbol"],
                "status": self.CURRENCY_STATUS[currency]["status"],
                "strength": self.CURRENCY_STATUS[currency]["strength"],
                "inflation": self.INFLATION_DATA[currency]["current_rate"],
                "inflation_trend": self.INFLATION_DATA[currency]["trend"],
                "interest_rate": self.CURRENCY_STATUS[currency]["interest_rate"],
                "sentiment": self.CURRENCY_STATUS[currency]["sentiment"],
            }
            overview.append(entry)
        return overview

    def get_full_currency_report(self, currency: str) -> dict:
        """Get a comprehensive report combining status, inflation, and purchasing power."""
        return {
            "status": self.get_currency_status(currency),
            "inflation": self.get_inflation_data(currency),
            "purchasing_power": self.get_purchasing_power(currency),
        }
