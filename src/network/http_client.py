from dataclasses import dataclass
from typing import Optional, Dict, Any
import httpx  # 只使用 httpx

@dataclass
class HttpResponse:
    ##响应结构体
    status_code: int
    headers: dict
    body: str
    elapsed: float
    exception: Exception = None
class HttpClient:
    def __init__(self, timeout: int = 30, verify_ssl: bool = True):
        self._client = httpx.Client(
            timeout=timeout,
            verify=verify_ssl
        )

    def request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        body: Optional[Dict[str, Any]] = None
    ) -> HttpResponse:
        try:
            response = self._client.request(
                method,
                url,
                headers=headers,
                json=body
            )
            return HttpResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                elapsed=response.elapsed.total_seconds(),
                body=response.text,
                exception=None
            )
        except Exception as e:
            return HttpResponse(
                status_code=-1,
                headers={},
                body="",
                elapsed=0,
                exception=e
            )

    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
        return self.request('GET', url, headers=headers)

    def post(self, url: str, headers: Optional[Dict[str, str]] = None, body: Optional[Dict[str, Any]] = None) -> HttpResponse:
        return self.request('POST', url, headers=headers, body=body)

    def close(self):
        self._client.close()