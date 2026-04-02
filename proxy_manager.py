# proxy_manager.py
import asyncio
import aiohttp
import re
import time

class ProxyManager:
    def __init__(self):
        self.free_proxies = []
        self.last_update = 0
    
    async def fetch_free_proxies(self):
        """جلب بروكسيات مجانية من الإنترنت"""
        sources = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        ]
        
        proxies = []
        for source in sources:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(source, timeout=10) as response:
                        text = await response.text()
                        found = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', text)
                        proxies.extend(found)
            except:
                continue
        
        # إزالة التكرار
        self.free_proxies = list(set(proxies))
        self.last_update = time.time()
        return self.free_proxies
    
    async def update_proxies(self):
        """تحديث قائمة البروكسيات المجانية"""
        print("🔄 جلب بروكسيات مجانية...")
        proxies = await self.fetch_free_proxies()
        print(f"✅ تم جلب {len(proxies)} بروكسي مجاني")
        return proxies
    
    def get_free_proxies(self):
        return self.free_proxies

proxy_manager = ProxyManager()
