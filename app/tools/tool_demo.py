from ..init_mcp import mcp_echo

@mcp_echo.tool()
async def tool_my_calculator(x: int, y: int) -> int:
    """A simple calculator tool that adds two numbers."""
    print(f"Calculating: {x} + {y}")
    return x + y