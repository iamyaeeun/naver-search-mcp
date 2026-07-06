"""MCP server exposing the Naver Search Open API (news/blog/shop) as tools.

Run with:
    python3 -m mcp_server.server
or register it in Claude Code's MCP config pointing at this file.
"""
from mcp.server.fastmcp import FastMCP

from mcp_server.naver_client import search

mcp = FastMCP("naver-search")


@mcp.tool()
def search_news(query: str, display: int = 5) -> dict:
    """Search Naver News for the given query."""
    return search("news", query, display)


@mcp.tool()
def search_blog(query: str, display: int = 5) -> dict:
    """Search Naver Blog posts for the given query."""
    return search("blog", query, display)


@mcp.tool()
def search_shop(query: str, display: int = 5) -> dict:
    """Search Naver Shopping for the given query."""
    return search("shop", query, display)


if __name__ == "__main__":
    mcp.run()
