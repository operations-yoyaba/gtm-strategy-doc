import os
import logging
from typing import Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class ClayService:
    def __init__(self):
        self.api_key = os.getenv("CLAY_API_KEY")
        self.base_url = "https://api.clay.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def enrich_company(self, company_id: int) -> Dict[str, Any]:
        """Enrich company data using Clay API"""
        # This is a placeholder implementation
        # In practice, you would call Clay's actual enrichment API
        url = f"{self.base_url}/enrich/company"
        data = {
            "company_id": company_id,
            "enrichment_types": [
                "funding",
                "competitors", 
                "technologies",
                "social_presence",
                "company_metrics"
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()

    async def get_company_funding(self, domain: str) -> Dict[str, Any]:
        """Get company funding information"""
        url = f"{self.base_url}/company/funding"
        params = {"domain": domain}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def get_company_competitors(self, domain: str) -> Dict[str, Any]:
        """Get company competitors"""
        url = f"{self.base_url}/company/competitors"
        params = {"domain": domain}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json() 