#!/bin/bash
set -e

# 要启动的命令列表
COMMANDS=(
    "python data/templates/sse-markdown/main.py"
    "sleep 3 && python data/templates/chat-playground-v1/main.py"
    "sleep 5 && python server/main.py"
)

PIDS=()

# 启动所有命令
for cmd in "${COMMANDS[@]}"; do
    echo "Starting: $cmd"
    bash -c "$cmd" &
    PIDS+=($!)
done

# 定义清理函数
cleanup() {
    echo "Cleaning up..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait "${PIDS[@]}" 2>/dev/null || true
}
trap cleanup EXIT

# 等待任意一个子进程退出
set +e
wait -n "${PIDS[@]}"
exit_code=$?
set -e

echo "One of the processes exited with code $exit_code, shutting down."

# 主脚本退出时会自动触发 trap cleanup
exit $exit_code
