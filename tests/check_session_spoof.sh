#!/bin/bash
set -e

# Setup
TEST_USER="admin"
# Load password from .env
ENV_FILE="../enc-server/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi
TEST_PASS=${ADMIN_PASSWORD:-"admin"}
CONFIG_DIR="$HOME/.enc"
CONFIG_FILE="$CONFIG_DIR/config.json"

echo "========================================"
echo "SESSION SPOOFING TEST"
echo "========================================"

# 1. Login (Valid)
echo "1. Logging in as $TEST_USER..."
enc login --password "$TEST_PASS" > /dev/null
echo "Login successful."

# 2. Verify Access (Valid)
echo "2. Verifying valid access..."
if enc project list > /dev/null 2>&1; then
    echo "Valid session working."
else
    echo "FAILED: Valid session rejected."
    exit 1
fi

# 3. Tamper with Config (Inject Fake Session)
echo "3. Injecting FAKE session ID into $CONFIG_FILE..."
# Backup
cp "$CONFIG_FILE" "$CONFIG_FILE.bak"
# Inject fake ID using sed or jq. We'll use sed for simplicity/robustness if jq missing key
# Assuming "session_id": "..." format
sed -i.tmp 's/"session_id": ".*"/"session_id": "fake-session-123"/' "$CONFIG_FILE"

# 4. Attempt Access
echo "4. Attempting command with FAKE session..."
OUTPUT=$(enc project list 2>&1 || true)
echo "Output: $OUTPUT"

if echo "$OUTPUT" | grep -q -E "Session Verification Failed|Invalid or expired session|Session Error|Please login first|Server Error"; then
    echo "SUCCESS: Server rejected fake session."
else
    echo "FAILED: Server accepted fake session or gave wrong error."
    # Restore config
    mv "$CONFIG_FILE.bak" "$CONFIG_FILE"
    exit 1
fi

# 5. Restore Config
mv "$CONFIG_FILE.bak" "$CONFIG_FILE"
echo "Restored valid config."

echo "========================================"
echo "✅ SESSION VERIFICATION WORKING"
echo "========================================"
