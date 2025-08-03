#!/bin/bash
set -e

python3 server/main.py &
PID1=$!

python3 data/templates/sse-markdown/main.py &
PID2=$!

python3 data/templates/chat-playground-v1/main.py &
PID3=$!

trap 'kill $PID1 $PID2 $PID3; wait' INT TERM

# 等任意一个子进程退出
wait -n

exit_code=$?
echo "One of the processes exited with code $exit_code, shutting down."
kill $PID1 $PID2 $PID3 2>/dev/null || true
wait
exit $exit_code
