"""Client for interacting with pets-backend GraphQL API."""

import logging
from typing import Any, Dict, Optional

import httpx

from app.core.exceptions import PetsBackendError

_logger = logging.getLogger(__name__)


class PetsBackendClient:
    """Client for pets-backend GraphQL API."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
    ):
        """Initialize pets-backend client.

        Args:
            base_url: Base URL of pets-backend GraphQL server
            timeout: Request timeout in seconds
        """
        self._base_url = base_url.rstrip("/")
        self._graphql_url = f"{self._base_url}/graphql"
        self._timeout = timeout
        self._http_client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._http_client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._http_client:
            await self._http_client.aclose()

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token with pets-backend.

        Args:
            token: JWT token to verify

        Returns:
            User information if token is valid

        Raises:
            PetsBackendError: If verification fails
        """
        query = """
        query VerifyToken($token: String!) {
            verifyToken(token: $token) {
                userId
                email
                valid
            }
        }
        """
        
        variables = {"token": token}
        
        try:
            if not self._http_client:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(
                        self._graphql_url,
                        json={"query": query, "variables": variables},
                        headers=self._headers(),
                    )
            else:
                response = await self._http_client.post(
                    self._graphql_url,
                    json={"query": query, "variables": variables},
                    headers=self._headers(),
                )
            
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                raise PetsBackendError(f"GraphQL errors: {data['errors']}")
            
            return data.get("data", {}).get("verifyToken", {})
            
        except httpx.HTTPStatusError as exc:
            raise PetsBackendError(
                f"pets-backend verification failed: HTTP {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise PetsBackendError(f"pets-backend connection error: {exc}") from exc

    async def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get user information from pets-backend.

        Args:
            token: JWT token

        Returns:
            User information
        """
        query = """
        query GetUser {
            me {
                id
                email
                name
            }
        }
        """
        
        try:
            if not self._http_client:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(
                        self._graphql_url,
                        json={"query": query},
                        headers=self._headers(token=token),
                    )
            else:
                response = await self._http_client.post(
                    self._graphql_url,
                    json={"query": query},
                    headers=self._headers(token=token),
                )
            
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                raise PetsBackendError(f"GraphQL errors: {data['errors']}")
            
            return data.get("data", {}).get("me", {})
            
        except httpx.HTTPStatusError as exc:
            raise PetsBackendError(
                f"pets-backend request failed: HTTP {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise PetsBackendError(f"pets-backend connection error: {exc}") from exc
