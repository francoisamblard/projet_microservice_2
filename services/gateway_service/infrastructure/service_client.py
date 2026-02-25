import httpx
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ServiceClient:
    """Generic service client for inter-service communication"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def get(self, endpoint: str) -> Dict[str, Any]:
        """GET request to service"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error in GET {url}: {e}")
            raise

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST request to service"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error in POST {url}: {e}")
            raise

    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT request to service"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error in PUT {url}: {e}")
            raise

    async def patch(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PATCH request to service"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.patch(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error in PATCH {url}: {e}")
            raise

    async def delete(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """DELETE request to service"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.delete(url)
            response.raise_for_status()
            return response.json() if response.text else None
        except Exception as e:
            logger.error(f"Error in DELETE {url}: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class GatewayServiceRegistry:
    """Registry for all downstream services"""

    def __init__(self):
        self.product_service = ServiceClient(
            os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
        )
        self.customer_service = ServiceClient(
            os.getenv("CUSTOMER_SERVICE_URL", "http://localhost:8002")
        )
        self.inventory_service = ServiceClient(
            os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8003")
        )
        self.pricing_service = ServiceClient(
            os.getenv("PRICING_SERVICE_URL", "http://localhost:8004")
        )
        self.order_service = ServiceClient(
            os.getenv("ORDER_SERVICE_URL", "http://localhost:8005")
        )

    async def close_all(self):
        """Close all client connections"""
        await self.product_service.close()
        await self.customer_service.close()
        await self.inventory_service.close()
        await self.pricing_service.close()
        await self.order_service.close()
