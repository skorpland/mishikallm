from typing import Optional, Union

import httpx

try:
    from mishikallm._version import version
except Exception:
    version = "0.0.0"

headers = {
    "User-Agent": f"mishikallm/{version}",
}


class HTTPHandler:
    def __init__(self, concurrent_limit=1000):
        # Create a client with a connection pool
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=concurrent_limit,
                max_keepalive_connections=concurrent_limit,
            ),
            headers=headers,
        )

    async def close(self):
        # Close the client when you're done with it
        await self.client.aclose()

    async def get(
        self, url: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ):
        response = await self.client.get(url, params=params, headers=headers)
        return response

    async def post(
        self,
        url: str,
        data: Optional[Union[dict, str]] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ):
        try:
            response = await self.client.post(
                url, data=data, params=params, headers=headers  # type: ignore
            )
            return response
        except Exception as e:
            raise e
