import time
from decimal import Decimal

class FxCache:

    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str):
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Decimal):
        expiry = time.time() + self.ttl
        self.cache[key] = (value, expiry)
