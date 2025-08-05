#!/bin/bash
set -e

# 启动第一个服务
python3 data/templates/sse-markdown/main.py &
PID1=$!

# 启动第二个服务
python3 data/templates/chat-playground-v1/main.py &
PID2=$!

# 延迟 5s 后启动第三个服务
( sleep 5 && python3 server/main.py ) &
PID3=$!

# 不论正常结束还是收到信号，都执行 cleanup 杀死子进程
cleanup() {
  echo "Cleaning up..."
  kill "$PID1" "$PID2" "$PID3" 2>/dev/null || true
  wait "$PID1" "$PID2" "$PID3" 2>/dev/null || true
}
trap cleanup EXIT

# 等任意一个子进程先退出
# 先关掉 errexit，以确保下面能拿到 exit_code 并执行 cleanup
set +e
wait -n "$PID1" "$PID2" "$PID3"
exit_code=$?
set -e

echo "One of the processes exited with code $exit_code, shutting down."

# 主脚本退出时会走到 trap cleanup
exit $exit_code
