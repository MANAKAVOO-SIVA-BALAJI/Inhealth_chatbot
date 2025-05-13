# app/cache.py
from functools import lru_cache
import hashlib
import json
import time

class CacheManager:
    def __init__(self, max_size=100, ttl=300):  # ttl in seconds
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def _generate_key(self, *args, **kwargs):
        """Generate a unique cache key based on inputs"""
        key_dict = {
            'args': args,
            'kwargs': {k: v for k, v in kwargs.items() if k != 'self'}
        }
        key_str = json.dumps(key_dict, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, *args, **kwargs):
        """Get an item from cache if it exists and is not expired"""
        key = self._generate_key(*args, **kwargs)
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp <= self.ttl:
                return value
            else:
                # Expired item
                del self.cache[key]
        return None
    
    def set(self, value, *args, **kwargs):
        """Store an item in the cache"""
        key = self._generate_key(*args, **kwargs)
        self.cache[key] = (value, time.time())
        
        # Clean up if cache is too large
        if len(self.cache) > self.max_size:
            # Remove oldest items
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
            for old_key, _ in sorted_items[:len(self.cache) - self.max_size]:
                del self.cache[old_key]
        
        return value

# Create global cache instance
cache = CacheManager(max_size=200, ttl=3600)  # 1 hour TTL
