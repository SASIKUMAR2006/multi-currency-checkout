from decimal import Decimal, ROUND_HALF_UP

class CheckoutService:

    BASE_CURRENCY = "GBP"
    ALLOWED = {"GBP", "USD", "EUR"}

    def __init__(self, fx_service):
        self.fx_service = fx_service

    def checkout(self, base_price: Decimal, currency: str):

        if currency not in self.ALLOWED:
            raise ValueError("Invalid currency")

        rate = self.fx_service.get_rate(self.BASE_CURRENCY, currency)

        rate_with_markup = rate * Decimal("1.01")

        raw_converted = base_price * rate_with_markup

        rounded = raw_converted.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        rounding_difference = raw_converted - rounded

        return {
            "base_price": str(base_price),
            "fx_rate_used": str(rate_with_markup),
            "converted_price": str(rounded),
            "rounding_applied": str(rounding_difference)
        }
