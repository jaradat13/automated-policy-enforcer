#!/bin/bash

echo "======================================================"
echo "🛡️  Automated Policy Enforcer - Live Demo Initializing"
echo "======================================================"
echo ""

# 0. PRE-FLIGHT CLEANUP (Destroy ghosts from previous runs)
docker rm -f rogue_demo > /dev/null 2>&1 || true

# 1. Provision the base infrastructure
echo "[1/4] 🏗️  Provisioning test infrastructure via Terraform..."
cd infrastructure
terraform apply -auto-approve > /dev/null 2>&1
cd ..
echo "      ✅ Infrastructure active."

# 2. Start the daemon in the background
echo "[2/4] 🧠 Starting Continuous Security Daemon in background..."
> demo_output.log # Clear the old log
python3 -u auditor/agent.py > demo_output.log 2>&1 &
DAEMON_PID=$!
sleep 3
echo "      ✅ Daemon is monitoring."

# 3. Simulate the attack 
echo "[3/4] 😈 Simulating rogue deployment (Exposing port 22)..."
docker run -d --name rogue_demo -p 2223:22 alpine sleep infinity > /dev/null 2>&1

# 4. Dynamically wait and show live action
echo "[4/4] ⏳ Daemon is active. Streaming live enforcement logs (Max 60s)..."
echo "------------------- LIVE ACTION -------------------"

TIMEOUT=60
ELAPSED=0

# Stream the log to the terminal in the background
tail -f demo_output.log &
TAIL_PID=$!

# Loop until rogue_demo is completely wiped off the system
while docker ps -a --format '{{.Names}}' | grep -q "^rogue_demo$" && [ $ELAPSED -lt $TIMEOUT ]; do
    sleep 2
    ELAPSED=$((ELAPSED+2))
done

# Kill the live stream
kill $TAIL_PID
echo "---------------------------------------------------"

# Check the final state
if docker ps -a --format '{{.Names}}' | grep -q "^rogue_demo$"; then
    echo "      ❌ Demo Failed: Rogue container survived the 60s timeout."
else
    echo "      ✅ SUCCESS: Daemon successfully detected and assassinated rogue_demo!"
fi

# Cleanup
echo ""
echo "🧹 Cleaning up background processes and test artifacts..."
kill $DAEMON_PID
docker rm -f rogue_demo > /dev/null 2>&1 || true
echo "======================================================"
echo "🎯 Demo Complete."
echo "======================================================"
