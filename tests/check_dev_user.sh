#!/bin/bash
set -e

echo "=== Starting Dev User Test ==="

# Ensure clean slate
rm -rf dev_user
mkdir -p dev_user
cd dev_user

# Detect or create a test SSH key for the dev user setup
DEV_SSH_KEY_PATH="$(pwd)/dev_id_ed25519"
if [ ! -f "$DEV_SSH_KEY_PATH" ]; then
    echo "Creating a temporary test key for dev_user..."
    ssh-keygen -t ed25519 -f "$DEV_SSH_KEY_PATH" -N ""
fi

echo "1. Initializing ENC (Local Config)..."
printf "local\nhttp://localhost:2222\ndev_user\n$DEV_SSH_KEY_PATH\n" | enc init

echo "2. Logging in..."
enc login --password Dev_user

echo "2.5 Setup SSH Key (Authorize)..."
enc setup ssh-key --password Dev_user

echo "3. Showing Config..."
enc show -v

echo "4. Setting up SSH Key..."
# Use --password to automate if key missing
enc setup ssh-key --password Dev_user

echo "5. Creating Dev Project..."
mkdir -p dev_project_test
cat <<EOF > dev_project_test/test.py
print("Welcome to ENC Dev")
EOF

echo "6. Initializing Project 'test_project' (Dev Context)..."
# Name 'test_project' reused.
# Input 'y' for mount.
printf "y\n" | enc project init test_project --directory ./dev_project_test --password Dev_Project_Test

echo "7. Checking Project List..."
enc project list

echo "8. Unmounting..."
enc project unmount test_project

echo "9. Mounting..."
enc project mount test_project ./dev_project_test --password Dev_Project_Test

echo "10. Verification: Access Check..."
if enc user list 2>/dev/null; then
    echo "FAIL: Dev user accessed user list!"
    exit 1
else
    echo "SUCCESS: Dev user denied user list access (Permission Denied expected)."
fi

echo "11. Logout..."
enc logout

echo "=== Dev User Test Complete ==="
