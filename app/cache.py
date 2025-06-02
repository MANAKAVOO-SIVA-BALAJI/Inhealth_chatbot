# # app/cache.py

import time

class CacheManager:
    def __init__(self, max_size=100, ttl=300):  
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl

    def _normalize_key(self, key: str) -> str:
        return ' '.join(key.strip().lower().split())

    def get(self, key: str):
        key = self._normalize_key(key)
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp <= self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value):
        key = self._normalize_key(key)
        self.cache[key] = (value, time.time())

        # Clean up if cache is too large
        if len(self.cache) > self.max_size:
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
            for old_key, _ in sorted_items[:len(self.cache) - self.max_size]:
                del self.cache[old_key]

        return value

cache = CacheManager(max_size=200, ttl=3600)  # 1 hour TTL
