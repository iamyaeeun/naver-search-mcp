"""Thin wrapper around the Naver Search API as exposed through NAVER API HUB
(https://api.ncloud-docs.com/docs/naver-api-hub-search-news), not the legacy
developers.naver.com console — the two issue different credentials and use
different auth headers, and API HUB keys are rejected by the legacy ones."""
from __future__ import annotations

import os
import urllib.error
import urllib.parse
import urllib.request
import json
from pathlib import Path

from dotenv import load_dotenv

# Resolve relative to this file, not the process cwd, so credentials load
# consistently whether run via `python3 -m mcp_server.server`, `mcp dev`
# (which execs this file standalone from a different sys.path root), or pytest.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

NAVER_SEARCH_BASE_URL = "https://naverapihub.apigw.ntruss.com/search/v1"

# "shop" isn't confirmed against API HUB's docs (only news/blog are) — it's
# also absent from API HUB apps that haven't done the separate shopping
# business verification, so this path is a best-effort guess pending an
# app that actually has it enabled.
SUPPORTED_CATEGORIES = ("news", "blog", "image", "webkr")

_MOCK_RESULTS = {
    "news": [
        {"title": "샘플 뉴스 제목입니다", "link": "https://example.com/news/1", "description": "네이버 검색 API 키가 설정되지 않아 반환된 목업 데이터입니다."},
    ],
    "blog": [
        {"title": "샘플 블로그 포스트", "link": "https://example.com/blog/1", "description": "네이버 검색 API 키가 설정되지 않아 반환된 목업 데이터입니다."},
    ],
    "image": [
        {"title": "샘플 이미지", "link": "https://example.com/image/1", "thumbnail": "https://example.com/thumb/1.jpg", "sizeheight": "300", "sizewidth": "400"},
    ],
    "webkr": [
        {"title": "샘플 <b>웹</b> 문서", "link": "https://example.com/web/1", "description": "네이버 검색 API 키가 설정되지 않아 반환된 목업 데이터입니다."},
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


def search(category: str, query: str, display: int = 5, **extra_params) -> dict:
    """Search Naver's `category` (news/blog/image) for `query`.

    Falls back to mock data when NAVER_CLIENT_ID / NAVER_CLIENT_SECRET are not set,
    so the MCP server is usable for structural testing before real API keys exist.
    """
    if category not in SUPPORTED_CATEGORIES:
        raise ValueError(f"unsupported category: {category!r}, expected one of {SUPPORTED_CATEGORIES}")

    creds = _get_credentials()
    if creds is None:
        return {"source": "mock", "items": _MOCK_RESULTS[category][:display]}

    client_id, client_secret = creds
    params = urllib.parse.urlencode({"query": query, "display": display, "format": "json", **extra_params})
    url = f"{NAVER_SEARCH_BASE_URL}/{category}?{params}"
    req = urllib.request.Request(url, headers={
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    })
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # Naver's error body (errorCode/errorMessage) is far more actionable
        # than urllib's generic "HTTP Error 401: Unauthorized".
        detail = e.read().decode("utf-8", errors="replace")
        raise urllib.error.HTTPError(e.url, e.code, f"{e.reason}: {detail}", e.headers, None) from None
    return {"source": "live", "items": body.get("items", [])}
