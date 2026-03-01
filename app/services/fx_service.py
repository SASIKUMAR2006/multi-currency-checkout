class FxService:

    def __init__(self, provider, cache):
        self.provider = provider
        self.cache = cache

    def get_rate(self, base: str, target: str):
        key = f"{base}_{target}"
        cached = self.cache.get(key)
        if cached:
            return cached

        rate = self.provider.get_rate(base, target)
        self.cache.set(key, rate)
        return rate
