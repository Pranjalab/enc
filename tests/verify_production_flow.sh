#!/bin/bash
set -e

echo "=== ENC PRODUCTION VERIFICATION FLOW ==="
echo "This script verifies the entire ecosystem from Docker Registry to Local CLI."

# Ensure we are in the tests directory
cd "$(dirname "$0")"

# 1. Cleanup
echo "1. Cleaning up local environment..."
pkill -f "enc logout" || true
docker stop enc_ssh_server || true
docker rm enc_ssh_server || true
ssh-keygen -R "[localhost]:2222" || true
rm -rf ~/.enc
rm -rf admin_user
rm -rf dev_user

# 2. Rebuild Server Locally (To ensure latest fixes are tested immediately)
echo "2. Rebuilding server from local source (v0.1.10 fixes)..."
cd ../enc-server && docker build -q -t pranjalab/enc-server:latest . && cd ../tests

echo "3. Starting hardened server container with short timeout for monitoring tests..."
docker run -d --name enc_ssh_server -p 2222:22 --cap-add SYS_ADMIN --device /dev/fuse -e ENC_SESSION_TIMEOUT=30 pranjalab/enc-server:latest

# 3. Wait for Server
echo "4. Waiting for SSHD to be ready (port 2222)..."
for i in {1..30}; do
    if nc -z localhost 2222; then
        echo "Server is UP!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# 4. Install Client (Local Fixed Version)
# IMPORTANT: We use local version to include the NameError fix
echo "5. Installing latest ENC CLI (Local Fix)..."
cd .. && pip install -q -e ./enc-cli

echo "6. Running 'enc install' to verify setup logic..."
printf "n\n" | enc install

echo "7. Initializing Global ENC Config (Bootstrap)..."
# Detect or create a test SSH key for global admin
GLOBAL_SSH_KEY_PATH="$HOME/.ssh/id_ed25519"
if [ ! -f "$GLOBAL_SSH_KEY_PATH" ]; then
    GLOBAL_SSH_KEY_PATH="$HOME/.ssh/id_rsa"
fi
printf "global\nhttp://localhost:2222\nadmin\n$GLOBAL_SSH_KEY_PATH\n" | enc init
enc login --password admin
enc setup ssh-key --password admin

cd tests

# 5. Run Test Suite
echo "6. Running full test suite..."
chmod +x *.sh
./test_all.sh

echo "=== PRODUCTION VERIFICATION COMPLETE ==="
