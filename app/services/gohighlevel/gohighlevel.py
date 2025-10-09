import aiohttp

from app.core.config.config import settings
from app.core.mixins import LogMixin

class GoHighLevelService(LogMixin):    
    def __init__(self):
        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Authorization": f"Bearer {settings.gohighlevel.TOKEN_GOHIGHLEVEL}",
            "Version": "2021-07-28",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def send_request(self, method: str, url: str, payload: dict | None = None, headers: dict | None = None, return_status: bool = False
    ) -> dict | tuple[dict, int, str]:
        async with aiohttp.ClientSession(base_url=self.base_url, headers=self.headers) as session:
            async with session.request(method, url, json=payload, headers=headers) as response:
                status_code = response.status
                text = await response.text()
                try:
                    response_json = await response.json()
                except Exception:
                    response_json = {}

                self.log(f"[API] {method} {url} -> {status_code}")
                if text:
                    self.log(f"[API] Response: {text}") 

                if return_status:
                    return response_json, status_code, text
                return response_json
