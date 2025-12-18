#!/bin/bash
set -e
set -x

echo "Testing End-to-End Project Workflow..."
PROJECT_NAME="new_project_$(date +%s)"
PASSWORD="client_secret_pass"

# 1. Login Logic
# Use existing session or force login
# We assume existing session from previous test is valid, OR we re-login.
# Since we might have lost session logic if we re-installed? No, session is in ~/.enc/sessions.
# Let's check session status first.

echo "Checking login status..."
SESSION_FILE=$(ls ~/.enc/sessions/*.json | head -n 1)
if [ -z "$SESSION_FILE" ]; then
    echo "No session found. Running simple login..."
    enc set-url "http://localhost:2222" > /dev/null
    enc set-username "admin" > /dev/null
    enc set-ssh-key "/tmp/test_admin_key" > /dev/null
    # SSH trust handled?
    enc login
fi

# 2. Init Project
echo "Initializing Project '$PROJECT_NAME' (via Client)..."
# Pass password to Click prompt via input redirection?
# Click password_option usually reads from tty or stdin.
# We pipe it.
# NOTE: cli.py uses @click.password_option() which reads securely.
printf "$PASSWORD\n$PASSWORD\n" | enc project init "$PROJECT_NAME" --password "$PASSWORD" > /tmp/client_init.txt 2>&1

cat /tmp/client_init.txt

if grep -q "initialized successfully" /tmp/client_init.txt; then
    echo "✅ Client Project Init Success"
else
    echo "❌ Client Project Init Failed"
    exit 1
fi

# 3. Mount Project (Dev)
echo "Mounting Project '$PROJECT_NAME'..."
# enc project dev <name> --password <pass>
# Why prompt? I added @click.password_option() which ADDS --password arg automatically.
# So I can pass it directly.
enc project dev "$PROJECT_NAME" --password "$PASSWORD" > /tmp/client_mount.txt 2>&1

cat /tmp/client_mount.txt

if grep -q "Project mounted" /tmp/client_mount.txt; then
    echo "✅ Client Project Mount Success"
else
    echo "❌ Client Project Mount Failed"
    exit 1
fi

# 4. Verify Server Mount Point
echo "Verifying Server Mount..."
# Check if /home/admin/.enc/run/master/$PROJECT_NAME exists
docker exec enc_ssh_server ls -ld /home/admin/.enc/run/master/$PROJECT_NAME
if [ $? -eq 0 ]; then
    echo "✅ Server Mount Point Exists"
else
    echo "❌ Server Mount Point Missing"
    exit 1
fi

echo "-----------------------------------"
echo "✅ End-to-End Workflow Passed"
echo "-----------------------------------"
