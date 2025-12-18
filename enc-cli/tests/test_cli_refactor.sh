#!/bin/bash
set -e

echo "Testing ENC CLI Refactor..."

# Ensure we are using the installed enc
ENC_CMD=$(which enc)
echo "Using enc at: $ENC_CMD"

# 1. Test basic help
echo "1. Testing 'enc --help'..."
enc --help > /dev/null
echo "   [Pass]"

# 2. Test Set configuration
echo "2. Testing Configuration Setters..."
enc set-url "http://test-server.local:2222" > /dev/null
enc set-username "testuser" > /dev/null
enc set-ssh-key "/tmp/test_key" > /dev/null
echo "   [Pass]"

# 3. Test Show Configuration
echo "3. Testing 'enc show config'..."
OUTPUT=$(enc show config)
if echo "$OUTPUT" | grep -q "test-server.local"; then
    echo "   [Pass] URL verification"
else
    echo "   [Fail] URL not found in config show"
    echo "$OUTPUT"
    exit 1
fi

if echo "$OUTPUT" | grep -q "testuser"; then
    echo "   [Pass] Username verification"
else
    echo "   [Fail] Username not found in config show"
    exit 1
fi

# 4. Test Init (Mock)
echo "4. Testing 'enc init'..."
enc init /tmp/test_project > /dev/null
echo "   [Pass]"

echo "-----------------------------------"
echo "✅ All Client Refactor Tests Passed"
echo "-----------------------------------"
