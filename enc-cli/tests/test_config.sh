#!/bin/bash

# tests/test_config.sh
set -e

echo "--- Testing ENC Configuration ---"

# Use installed binary if possible, else symlink
ENC_CMD="$HOME/.local/bin/enc"
if [ ! -x "$ENC_CMD" ]; then
    echo "Warning: ~/.local/bin/enc not found. Installing first..."
    ./install.sh > /dev/null
fi

echo "1. Testing 'config set'..."
"$ENC_CMD" config set url "https://google.com"
"$ENC_CMD" config set username "testuser"
"$ENC_CMD" config set ssh_key "/tmp/id_rsa_test"

echo "2. Testing 'config show'..."
SHOW_OUT=$("$ENC_CMD" config show)
echo "$SHOW_OUT"

if [[ "$SHOW_OUT" != *"https://google.com"* ]]; then
    echo "FAILURE: URL not found in config show"
    exit 1
fi
if [[ "$SHOW_OUT" != *"testuser"* ]]; then
    echo "FAILURE: Username not found in config show"
    exit 1
fi

echo "3. Testing 'check-connection' (Success expected for google.com)..."
if "$ENC_CMD" check-connection | grep -q "Success"; then
    echo "SUCCESS: Connection check passed."
else
    echo "FAILURE: Connection check failed for google.com"
    "$ENC_CMD" check-connection
    exit 1
fi

echo "4. Testing 'check-connection' (Failure expected for invalid host)..."
"$ENC_CMD" config set url "https://invalid.host.test"
if "$ENC_CMD" check-connection | grep -q "Failed"; then
    echo "SUCCESS: Connection check failed as expected."
else
    echo "FAILURE: Connection check succeeded for invalid host?"
    "$ENC_CMD" check-connection
    exit 1
fi

echo "SUCCESS: Config tests passed."
