#!/bin/bash
# 启动企业微信机器人定时任务服务

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "============================================"
echo "启动企业微信机器人定时任务服务"
echo "============================================"

# Kill any existing wxwork processes
echo "检查现有的wxwork服务..."
pkill -f "wxwork.py" 2>/dev/null || true
sleep 1

# Start wxwork service using Server's virtual environment
echo "启动wxwork服务..."
cd AliData/hooks

# 使用Server的虚拟环境并设置正确的PYTHONPATH
source ../../Server/venv/bin/activate
export PYTHONPATH="$PROJECT_DIR/AliData:$PYTHONPATH"

# 启动服务
nohup python3 wxwork.py > "$PROJECT_DIR/wxwork.log" 2>&1 &
WXWORK_PID=$!
echo "WXWORK服务启动成功，PID: $WXWORK_PID"
cd "$PROJECT_DIR"

# Save PID
echo "$WXWORK_PID" > wxwork.pid

echo ""
echo "============================================"
echo "✓ WXWORK定时任务服务启动成功！"
echo "  定时任务：每日 00:03 执行销售汇算"
echo ""
echo "  日志文件: $PROJECT_DIR/wxwork.log"
echo "  停止服务: ./stop_wxwork.sh"
echo "============================================"

# 等待几秒检查服务是否正常运行
sleep 3
if ps -p $WXWORK_PID > /dev/null; then
    echo "✓ 服务运行正常"
else
    echo "✗ 服务可能异常退出，请检查日志"
fi
