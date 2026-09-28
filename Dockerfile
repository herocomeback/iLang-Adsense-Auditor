# 使用自带 Python 3.12 的官方轻量镜像
FROM python:3.12-slim

WORKDIR /app

# 设置环境变量，确保输出实时不缓冲
ENV PYTHONUNBUFFERED=1

# 安装 mcp 基础依赖
RUN pip install --no-cache-dir mcp

# 复制工程源代码
COPY . /app

# 默认启动 MCP Server (Stdio 模式)
CMD ["python", "-u", "mcp_server.py"]
