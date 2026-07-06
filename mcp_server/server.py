"""MCP server exposing the Naver Search Open API (news/blog/shop) as tools.

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
def search_shop(query: str, display: int = 5) -> dict:
    """Search Naver Shopping for the given query."""
    return search("shop", query, display)


if __name__ == "__main__":
    mcp.run()
