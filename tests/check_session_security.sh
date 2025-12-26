#!/bin/bash
set -e

# Configuration
ENC_SERVER="localhost"
ENC_PORT="2222"
ADMIN_USER="admin"

echo "========================================"
echo "SESSION SECURITY & HIJACKING TEST"
echo "========================================"

# 1. Login to get a valid session
echo "1. Logging in as admin..."
LOGIN_OUTPUT=$(ssh -p $ENC_PORT $ADMIN_USER@$ENC_SERVER "server-login $ADMIN_USER" 2>/dev/null)
SESSION_ID=$(echo "$LOGIN_OUTPUT" | jq -r '.session_id')
echo "Valid Session ID: $SESSION_ID"

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" == "null" ]; then
    echo "FAILED: Valid login returned no session ID."
    exit 1
fi

# 2. Verify Valid Session Works
echo "2. Verifying valid session access..."
 ssh -p $ENC_PORT $ADMIN_USER@$ENC_SERVER "server-project-list --session-id $SESSION_ID" > /dev/null
if [ $? -eq 0 ]; then
    echo "SUCCESS: Valid session accepted."
else
    echo "FAILED: Valid session rejected."
    exit 1
fi

# 3. Attempt Access with Invalid Session ID
FAKE_SESSION_ID="fake-session-uuid-1234"
echo "3. Attempting access with FAKE session ID: $FAKE_SESSION_ID"
OUTPUT=$(ssh -p $ENC_PORT $ADMIN_USER@$ENC_SERVER "server-project-list --session-id $FAKE_SESSION_ID" 2>&1 || true)

if echo "$OUTPUT" | grep -q "Session Verification Failed"; then
    echo "SUCCESS: Fake session rejected with correct error message."
else
    echo "FAILED: Fake session was NOT rejected or error message mismatch."
    echo "Output: $OUTPUT"
    exit 1
fi

# 4. Logout (Invalidate Session)
echo "4. Logging out..."
ssh -p $ENC_PORT $ADMIN_USER@$ENC_SERVER "server-logout $SESSION_ID" > /dev/null

# 5. Attempt Access with Expired Session
echo "5. Attempting access with EXPIRED session ID..."
OUTPUT=$(ssh -p $ENC_PORT $ADMIN_USER@$ENC_SERVER "server-project-list --session-id $SESSION_ID" 2>&1 || true)

if echo "$OUTPUT" | grep -q "Session Verification Failed"; then
    echo "SUCCESS: Expired session rejected."
else
    echo "FAILED: Expired session was NOT rejected."
    echo "Output: $OUTPUT"
    exit 1
fi

echo "========================================"
echo "✅ SESSION SECURITY VERIFIED"
echo "========================================"
