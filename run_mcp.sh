#!/usr/bin/env bash
# ==============================================================================
# iLang AdSense Auditor — MCP Server 启动与管理脚本
# ==============================================================================

set -e

# 定位脚本所在的项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "--------------------------------------------------------"
echo "🚀 启动 iLang AdSense Auditor MCP Server..."
echo "--------------------------------------------------------"

# 1. 检查 python3 命令是否存在
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3 命令，请先安装 Python 3。"
    exit 1
fi

# 2. 检查 mcp 依赖库
if ! python3 -c "import mcp" &> /dev/null; then
    echo "⚠️ 提示: 未检测到 Python 'mcp' 依赖库。"
    echo "👉 正在尝试自动为你安装: pip install mcp"
    echo ""
    python3 -m pip install mcp || {
        echo "❌ 自动安装失败，请手动运行: pip install mcp"
        exit 1
    }
    echo "✅ 'mcp' 依赖库安装成功！"
    echo "--------------------------------------------------------"
fi

# 3. 运行 MCP Server
echo "🟢 正在运行 MCP Server (监听 Stdio / MCP 客户端连接)..."
echo "💡 提示: 本程序由 IDE (如 Cursor/Windsurf) 自动调用管理，按 Ctrl+C 可手动退出。"
echo ""

exec python3 "$SCRIPT_DIR/mcp_server.py" "$@"
