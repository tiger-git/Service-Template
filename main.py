from fastmcp.server import FastMCP
from fastmcp.server.providers.openapi.routing import MCPType, RouteMap
import httpx

from app.init_app import app
from app.router import routers
from app.init_mcp import mcp_echo_app, mcp_weather_app
from app.tools import tool_demo

app.include_router(routers)
app.mount("/echo", app=mcp_echo_app)
app.mount("/weather", app=mcp_weather_app)

# =========================Generate MCP app from FastAPI app============================
mcp_web_app = FastMCP.from_fastapi(
    app,
    route_maps=[
        # RouteMap(pattern=r"test.*", mcp_type=MCPType.TOOL), # TODO 不生效,why?
        RouteMap(mcp_type=MCPType.EXCLUDE, tags={"Demo"})
    ],
)

# ==========================Generate MCP app from OpenAPI spec==========================
# openapi_spec = httpx.get("https://api.example.com/openapi.json").json()
# client = httpx.AsyncClient(base_url="https://api.example.com")
# mcp_web_app = FastMCP.from_openapi(
#     openapi_spec=openapi_spec,
#     client=client,
#     route_maps=[
#         RouteMap(mcp_type=MCPType.EXCLUDE,tags={"Demo"})
#     ],
# )


if __name__ == "__main__":
    pass
    # ==========================Start the MCP apps==========================
    # mcp_echo_app.run(transport="stdio")
    # mcp_echo_app.run(transport="streamable-http")
    # mcp_weather_app.run(transport="streamable-http")

    # ==========================Start the FastAPI app==========================
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
