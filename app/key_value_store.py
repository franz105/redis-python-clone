import asyncio

class KeyValueStore:
    def __init__(self):
        self.data = {}
        self.loop = asyncio.get_running_loop()

    async def set(self, key, value, px = None):
        self.data[key] = value
        if px:
            self.loop.call_later(px/1000, self.expire, key)

    def get(self, key):
        return self.data.get(key, b"")
    
    def expire(self, key): 
        self.data.pop(key, None)