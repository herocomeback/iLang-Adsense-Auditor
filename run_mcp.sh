#!/usr/bin/env bash
# ==============================================================================
# iLang AdSense Auditor — MCP Server 智能启动脚本 (支持 Docker & 本地)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "--------------------------------------------------------"
echo "🚀 启动 iLang AdSense Auditor MCP Server..."
echo "--------------------------------------------------------"

# 检查本地 Python3 版本是否满足 >= 3.10
USE_DOCKER=false

PY_VER_OK=false
if command -v python3 &> /dev/null; then
    PY_VER_OK=$(python3 -c "import sys; print('true' if sys.version_info >= (3, 10) else 'false')" 2>/dev/null || echo "false")
fi

if [ "$PY_VER_OK" = "true" ] && python3 -c "import mcp" &> /dev/null; then
    echo "🟢 检测到本地 Python 版本符合要求 (>= 3.10) 且已安装 mcp，使用本地环境启动..."
    exec python3 "$SCRIPT_DIR/mcp_server.py" "$@"
else
    echo "⚠️ 提示: 本地 Python 版本低于 3.10 或缺少 mcp 依赖。"
    
    if command -v docker &> /dev/null; then
        echo "🐳 检测到系统已安装 Docker，切换为容器隔离环境运行 (Python 3.12 内置)..."
        echo ""
        
        IMAGE_NAME="ilang-adsense-auditor-mcp:latest"
        
        # 检查镜像是否存在，不存在则构建
        if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
            echo "🔨 正在为你首次构建 Docker 镜像，请稍等..."
            docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
            echo "✅ Docker 镜像构建完成！"
            echo "--------------------------------------------------------"
        fi
        
        # 运行容器，通过 Stdio 对接 IDE MCP
        exec docker run -i --rm \
            -v "$SCRIPT_DIR:/app" \
            "$IMAGE_NAME"
    else
        echo "❌ 错误: 本地 Python 版本低于 3.10，且未检测到 Docker。"
        echo "请升级本地 Python 至 3.10+ (如: brew install python@3.11)，或安装 Docker。"
        exit 1
    fi
fi
