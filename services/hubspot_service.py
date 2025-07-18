import os
import logging
from typing import Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class HubSpotService:
    def __init__(self):
        self.access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_company_data(self, company_id: int) -> Dict[str, Any]:
        """Fetch company data from HubSpot"""
        url = f"{self.base_url}/crm/v3/objects/companies/{company_id}"
        params = {
            "properties": "name,domain,industry,numberofemployees,annualrevenue,city,state,country"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_deal_data(self, deal_id: int) -> Dict[str, Any]:
        """Fetch deal data from HubSpot"""
        url = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"
        params = {
            "properties": "amount,dealstage,dealname,closedate"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def update_deal_status(self, deal_id: int, status: str, timestamp: str) -> None:
        """Update deal status in HubSpot"""
        url = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"
        data = {
            "properties": {
                "gtm_doc_status": status,
                "gtm_last_processed_ts": timestamp
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def update_deal_properties(self, deal_id: int, properties: Dict[str, Any]) -> None:
        """Update multiple deal properties in HubSpot"""
        url = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"
        data = {"properties": properties}
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, json=data)
            response.raise_for_status() 