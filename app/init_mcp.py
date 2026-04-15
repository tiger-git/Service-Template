from dataclasses import dataclass
import logging

from fastmcp.server import FastMCP
from core.handler.handle_context_manager import mcp_app_context
from core.handler.handle_service_redis import redis_handler

logger = logging.getLogger(__name__)

mcp_echo = FastMCP("Echo", lifespan=mcp_app_context)
mcp_echo_app = mcp_echo.http_app("/mcp")

mcp_weather = FastMCP("Weather", lifespan=mcp_app_context)
mcp_weather_app = mcp_weather.http_app("/mcp")


@mcp_echo.tool()
async def tool_echo(message: str) -> str:
    """A simple echo tool that returns the input message."""
    current_time = await redis_handler.redis_cli.get("current_time")
    print(f"Echoing message: {message}. Current time: {current_time}")
    return message


@mcp_weather.tool()
async def tool_get_weather(city: str) -> str:
    """A simple weather tool that returns a fake weather report for a given city."""
    print(f"Getting weather for city: {city}")
    current_time = await redis_handler.redis_cli.get("current_time")
    return f"The current weather in {city} is sunny with a high of 25°C. Current time: {current_time}"
