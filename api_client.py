# api_client.py
import asyncio
import aiohttp
import random
import time
from aiohttp import ClientTimeout

class APIClient:
    def __init__(self):
        self.session = None
        self.mode = "direct"
        self.free_proxies = []
        self.paid_proxies = []
        self.current_free_index = 0
        self.current_paid_index = 0
        self.consecutive_fails = 0
    
    def set_paid_proxies(self, proxies):
        self.paid_proxies = proxies.copy()
    
    def set_free_proxies(self, proxies):
        self.free_proxies = proxies.copy()
        self.current_free_index = 0
    
    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def get_next_proxy(self):
        if self.mode == "free_proxy" and self.free_proxies:
            proxy = self.free_proxies[self.current_free_index % len(self.free_proxies)]
            self.current_free_index += 1
            return f"http://{proxy}"
        elif self.mode == "paid_proxy" and self.paid_proxies:
            proxy = self.paid_proxies[self.current_paid_index % len(self.paid_proxies)]
            self.current_paid_index += 1
            return proxy
        return None
    
    async def check_card(self, card_data: str, retry=0):
        session = await self.get_session()
        proxy = self.get_next_proxy() if self.mode != "direct" else None
        
        try:
            async with session.post(
                "https://api.chkr.cc/",
                json={"data": card_data.strip()},
                proxy=proxy,
                timeout=ClientTimeout(total=8)
            ) as response:
                
                if response.status in [403, 429, 503]:
                    self.consecutive_fails += 1
                    if self.consecutive_fails >= 3:
                        await self.switch_mode()
                    if retry < 2:
                        await asyncio.sleep(2)
                        return await self.check_card(card_data, retry + 1)
                    return {"code": -2, "error": "API blocked"}
                
                self.consecutive_fails = 0
                return await response.json()
                
        except asyncio.TimeoutError:
            self.consecutive_fails += 1
            if self.consecutive_fails >= 3:
                await self.switch_mode()
            if retry < 2:
                await asyncio.sleep(1)
                return await self.check_card(card_data, retry + 1)
            return {"code": -1, "error": "Timeout"}
            
        except Exception as e:
            self.consecutive_fails += 1
            if self.consecutive_fails >= 3:
                await self.switch_mode()
            if retry < 2:
                await asyncio.sleep(1)
                return await self.check_card(card_data, retry + 1)
            return {"code": -1, "error": str(e)}
    
    async def switch_mode(self):
        old_mode = self.mode
        if self.mode == "direct":
            self.mode = "free_proxy"
            print(f"🔄 تبديل الوضع: direct -> free_proxy")
        elif self.mode == "free_proxy":
            self.mode = "paid_proxy"
            print(f"🔄 تبديل الوضع: free_proxy -> paid_proxy")
        elif self.mode == "paid_proxy":
            self.mode = "direct"
            self.consecutive_fails = 0
            print(f"🔄 تبديل الوضع: paid_proxy -> direct")
        self.consecutive_fails = 0

api_client = APIClient()
