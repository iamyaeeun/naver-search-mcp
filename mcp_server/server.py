"""MCP server exposing the Naver Search Open API (news/blog/image/webkr) as tools.

Run with:
    python3 -m mcp_server.server
    mcp dev mcp_server/server.py
or register it in Claude Code's MCP config pointing at this file.
"""
from mcp.server.fastmcp import FastMCP

try:
    # `python3 -m mcp_server.server` — loaded as part of the mcp_server package.
    from mcp_server.naver_client import search
except ImportError:
    # `mcp dev mcp_server/server.py` — mcp's CLI execs this file standalone and
    # only puts its own directory (mcp_server/) on sys.path, not the project
    # root, so the package-qualified import above isn't resolvable there.
    from naver_client import search

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
def search_img(query: str, display: int = 5, sort: str = "sim", filter: str = "all") -> dict:
    """Search Naver Images for the given query.

    Args:
        query: Search keyword (UTF-8).
        display: Number of results (1-100, default 5).
        sort: "sim" (relevance) or "date".
        filter: Size filter — "all", "large", "medium", or "small".
    """
    return search("image", query, display, sort=sort, filter=filter)


@mcp.tool()
def search_webkr(query: str, display: int = 5) -> dict:
    """Search Naver Korean Web documents for the given query."""
    return search("webkr", query, display)


if __name__ == "__main__":
    mcp.run()
