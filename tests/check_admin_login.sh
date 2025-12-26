#!/bin/bash
set -e

echo "=== Starting Admin Login Test ==="

# Ensure clean slate
rm -rf admin_user
mkdir -p admin_user
cd admin_user

echo "1. Initializing ENC (Local Config)..."
# Inputs: config_type=local, url, username, ssh_key
# The CLI prompts for: 
# 1. Global/Local? -> local
# 2. URL -> http://localhost:2222
# 3. Username -> admin
# 4. SSH Key Path -> /Users/pranjalbhaskare/.ssh/enc_key
printf "local\nhttp://localhost:2222\nadmin\n/Users/pranjalbhaskare/.ssh/enc_key\n" | enc init

echo "2. Logging in..."
enc login

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
enc login
enc user list

echo "12. Creating Developer User..."
# Inputs:
# 1. SSH Key Path (optional) -> Enter to skip
printf "\n" | enc user create dev_user --role user --password Dev_user

echo "=== Admin Test Complete ==="
