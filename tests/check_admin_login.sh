#!/bin/bash
set -e

echo "=== Starting Admin Login Test ==="

# Ensure clean slate
# Ensure clean slate
# Load password from .env
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_FILE="$SCRIPT_DIR/../enc-server/.env"
if [ -f "$ENV_FILE" ]; then
    echo "DEBUG: Loading .env from $ENV_FILE"
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "DEBUG: .env file not found at $ENV_FILE"
fi
TEST_PASS=${ADMIN_PASSWORD:-"admin"}
echo "DEBUG: Using password: $TEST_PASS"

rm -rf admin_user
mkdir -p admin_user
cd admin_user

# Detect or create a test SSH key
SSH_KEY_PATH="$HOME/.ssh/id_ed25519"
if [ ! -f "$SSH_KEY_PATH" ]; then
    SSH_KEY_PATH="$HOME/.ssh/id_rsa"
fi
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "Warning: No standard SSH key found. Creating a temporary test key..."
    ssh-keygen -t ed25519 -f ./test_key -N ""
    SSH_KEY_PATH="$(pwd)/test_key"
fi

echo "1. Initializing ENC (Local Config)..."
printf "local\nhttp://localhost:2222\nadmin\n$SSH_KEY_PATH\n" | enc init

echo "2. Logging in..."
enc login --password "$TEST_PASS"

echo "2.5 Setup SSH Key (Authorize)..."
enc setup ssh-key --password "$TEST_PASS"

echo "3. Showing Config..."
enc show -v

echo "4. Listing Projects..."
enc project list

echo "5. Creating Project Test Directory..."
mkdir -p project_test
cat <<EOF > project_test/test.py
print("Welcome to ENC")
EOF

echo "6. Initializing Project 'test_project'..."
# Inputs: 
# 1. 'y' to confirm remaining mounted (from interactive_unmount_timer)
printf "y\n" | enc project init test_project --directory ./project_test --password Project_Test

echo "7. Checking Project List (Mounted)..."
enc project list

echo "8. Unmounting..."
enc project unmount test_project

echo "9. Mounting Again..."
enc project mount test_project ./project_test --password Project_Test

echo "10. Logout..."
enc logout

echo "11. Login again and List Users..."
# Re-login as admin
enc login --password "$TEST_PASS"
enc user list

echo "12. Creating Developer User..."
# Inputs:
# 1. SSH Key Path (optional) -> Enter to skip
printf "\n" | enc user create dev_user --role user --password Dev_user

echo "=== Admin Test Complete ==="
