#!/bin/bash
# 停止企业微信机器人定时任务服务

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "停止企业微信机器人定时任务服务..."

# Stop wxwork service
if [ -f wxwork.pid ]; then
    WXWORK_PID=$(cat wxwork.pid)
    if kill -0 $WXWORK_PID 2>/dev/null; then
        kill $WXWORK_PID
        echo "WXWORK服务已停止 (PID: $WXWORK_PID)"
    fi
    rm -f wxwork.pid
fi

# Kill any remaining processes
pkill -f "wxwork.py" 2>/dev/null || true

echo "WXWORK定时任务服务已停止。"
