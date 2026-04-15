from fastapi import APIRouter, Request

router = APIRouter(prefix="/tools")

@router.get("/test")
async def test(request: Request):
    """
    测试接口
    :param request:
    :return:
    """
    return {"message": "MCP Tools test successful!"}