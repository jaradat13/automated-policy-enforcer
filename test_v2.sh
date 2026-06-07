#!/bin/bash

echo "======================================================"
echo "⚡ V2.0 Event-Driven Architecture - Zero Latency Test"
echo "======================================================"
echo ""

# Pre-flight cleanup
docker rm -f instant_rogue > /dev/null 2>&1 || true

# 1. Start the event-driven daemon
echo "[1] Starting Event-Driven Daemon in the background..."
> v2_output.log
python3 -u auditor/agent.py > v2_output.log 2>&1 &
DAEMON_PID=$!

# 2. Dynamically wait for the daemon to be ready
echo "[2] Waiting for daemon to initialize Python..."
while ! grep -q "Listening for live container" v2_output.log; do
    sleep 0.5
done

# Give the underlying 'docker events' subprocess time to bind to the socket!
echo "      ⏳ Allowing socket connection to establish (2s)..."
sleep 2
echo "      ✅ Daemon is fully bound to the event stream!"

# 3. Stream the logs live
echo "[3] Streaming logs. Watch how fast it reacts..."
echo "------------------- LIVE ACTION -------------------"
tail -f v2_output.log &
TAIL_PID=$!

# 4. Trigger the event (PORT CHANGED TO 8081 to avoid http_violator)
echo -e "\n>>> [SYSTEM] Deploying rogue container NOW..."
docker run -d --name instant_rogue -p 8081:80 alpine sleep infinity > /dev/null 2>&1

# 5. Wait for the daemon to react and kill it (Max 15s)
TIMEOUT=15
ELAPSED=0
while docker ps --format '{{.Names}}' | grep -q "^instant_rogue$" && [ $ELAPSED -lt $TIMEOUT ]; do
    sleep 1
    ELAPSED=$((ELAPSED+1))
done

# Clean up processes
kill $TAIL_PID
echo "---------------------------------------------------"

# 6. Validate the actual state
if docker ps -a --format '{{.Names}}' | grep -q "^instant_rogue$"; then
    echo "      ❌ Demo Failed: Container survived. Daemon missed it!"
else
    echo "      ✅ SUCCESS: Daemon detected and assassinated the container instantly!"
fi

echo ""
echo "🧹 Cleaning up..."
kill $DAEMON_PID
docker rm -f instant_rogue > /dev/null 2>&1 || true
echo "======================================================"
