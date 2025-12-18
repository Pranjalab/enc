#!/bin/bash
set -e

echo "Testing ENC Session Login..."

# 1. Configure for Test
enc set-url "http://localhost:2222" > /dev/null
enc set-username "admin" > /dev/null
enc set-ssh-key "/tmp/test_admin_key" > /dev/null

# 2. Run Login (should be non-interactive now)
echo "Running 'enc login'..."
OUTPUT=$(enc login)
echo "$OUTPUT"

# 3. Verify Session File
SESSION_ID=$(echo "$OUTPUT" | grep "Session ID" | awk '{print $NF}')

if [ -z "$SESSION_ID" ]; then
    echo "❌ Fail: No Session ID returned."
    exit 1
fi

SESSION_FILE="$HOME/.enc/sessions/$SESSION_ID.json"
if [ -f "$SESSION_FILE" ]; then
    echo "✅ Success: Session file created at $SESSION_FILE"
    cat "$SESSION_FILE"
else
    echo "❌ Fail: Session file not found."
    exit 1
fi

echo "-----------------------------------"
echo "✅ Session Test Passed"
echo "-----------------------------------"
