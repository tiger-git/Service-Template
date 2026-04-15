# Web+MCP Service Template

## Getting started
### 配置
* update .env,参考.env copy

### 启动/部署
### Local
#### 启动web
``` shell
poetry install --no-root
uvicorn main:app
```

> **如果存在挂载mcp节点，对应节点访问类似如下：**
> - http://127.0.0.1:8000/mcp/echo
> - http://127.0.0.1:8000/mcp/weather
> - ...

#### 启动mcp【单节点启动】
``` shell
poetry install --no-root
uvicorn main.py:mcp_web_app --transport=http --host=127.0.0.1 --port=8000
```
更多部署启动方式，参考 https://gofastmcp.com/cli/running

### Docker
根据最终架构策略调整`compose.yaml`
```shell
docker compose up -d
```
* 针对mcp docker部署,仅需启动命令同步调整即可参考本地

## 开发调试【MCP】

### 功能逻辑postman or MCP inspector
step1 启动mcp server
```shell
fastmcp run main.py:mcp_web_app --transport=http --host=0.0.0.0
```
step2 基于官方MCP Inspector可视化界面
```shell
npx @modelcontextprotocol/inspector fastmcp run main.py:mcp_web_app --transport=http --host=0.0.0.0 # or npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```
or postman
```json
{
    "mcpServers": {
        "mcp server": {
            "url": "http://0.0.0.0:8000/mcp"
        }
    }
}
```
### LLM集成训练
- 主流AI 客户端工具，如calude code、copilot等，此处以免费的qwen code为例
``` shell
qwen
qwen mcp add --transport http demo-server http://localhost:8000/mcp
```
- 参考文档 https://qwenlm.github.io/qwen-code-docs/zh/users/features/mcp/

## 版本说明

- 多数情况mcp/web不会共生，至少不会挤在一个服务，此处只为调研
    -  web+mcp 同时提供HTTP/MCP协议，支持挂载多个mcp节点
    - 支持基于已有web server,拓展支持MCP【fastapi/openapi.json依赖】
        - 官方不建议挤在一起
        - 支持指定接口转化，需自定义路由规则
- lifespan共享生命周期，即redis、DB初始化一次即可
- 有待探索...

