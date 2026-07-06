"""Thin wrapper around the Naver Search Open API (https://developers.naver.com/docs/serviceapi/search)."""
import os
import urllib.parse
import urllib.request
import json

NAVER_SEARCH_BASE_URL = "https://openapi.naver.com/v1/search"

SUPPORTED_CATEGORIES = ("news", "blog", "shop")

_MOCK_RESULTS = {
    "news": [
        {"title": "샘플 뉴스 제목입니다", "link": "https://example.com/news/1", "description": "네이버 검색 API 키가 설정되지 않아 반환된 목업 데이터입니다."},
    ],
    "blog": [
        {"title": "샘플 블로그 포스트", "link": "https://example.com/blog/1", "description": "네이버 검색 API 키가 설정되지 않아 반환된 목업 데이터입니다."},
    ],
    "shop": [
        {"title": "샘플 쇼핑 상품", "link": "https://example.com/shop/1", "lprice": "10000", "description": "네이버 검색 API 키가 설정되지 않아 반환된 목업 데이터입니다."},
    ],
}


class NaverCredentialsMissing(RuntimeError):
    pass


def _get_credentials() -> tuple[str, str] | None:
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None
    return client_id, client_secret


def search(category: str, query: str, display: int = 5) -> dict:
    """Search Naver's `category` (news/blog/shop) for `query`.

    Falls back to mock data when NAVER_CLIENT_ID / NAVER_CLIENT_SECRET are not set,
    so the MCP server is usable for structural testing before real API keys exist.
    """
    if category not in SUPPORTED_CATEGORIES:
        raise ValueError(f"unsupported category: {category!r}, expected one of {SUPPORTED_CATEGORIES}")

    creds = _get_credentials()
    if creds is None:
        return {"source": "mock", "items": _MOCK_RESULTS[category][:display]}

    client_id, client_secret = creds
    params = urllib.parse.urlencode({"query": query, "display": display})
    url = f"{NAVER_SEARCH_BASE_URL}/{category}.json?{params}"
    req = urllib.request.Request(url, headers={
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    })
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return {"source": "live", "items": body.get("items", [])}
