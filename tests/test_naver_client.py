import os

import pytest

from mcp_server.naver_client import search, SUPPORTED_CATEGORIES


@pytest.fixture(autouse=True)
def no_credentials(monkeypatch):
    monkeypatch.delenv("NAVER_CLIENT_ID", raising=False)
    monkeypatch.delenv("NAVER_CLIENT_SECRET", raising=False)


def test_mock_fallback_when_no_credentials():
    result = search("news", "테스트")
    assert result["source"] == "mock"
    assert len(result["items"]) >= 1


def test_display_limits_mock_items():
    result = search("blog", "테스트", display=0)
    assert result["items"] == []


def test_unsupported_category_raises():
    with pytest.raises(ValueError):
        search("weather", "테스트")


def test_all_supported_categories_have_mock_data():
    for category in SUPPORTED_CATEGORIES:
        result = search(category, "쿼리")
        assert result["items"]
