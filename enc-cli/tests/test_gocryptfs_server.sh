#!/bin/bash
set -e

echo "Testing Server-Side Gocryptfs Init..."

PROJECT_NAME="test_project_$(date +%s)"
PASSWORD="secure_test_pass"

# We simulate what the client WOULD do:
# ssh admin@localhost -p 2222 "enc server-project-init <name>" with password via stdin?
# The command uses `prompt=True` and `hide_input=True`.
# This is hard to automate without expect.
# BUT, we can use `printf` to pipe input if we don't force TTY.

# NOTE: The server command `enc server-project-init` reads from click prompt.
# Click prompts read from stdin.
# So: echo "password\npassword" | ssh ...
# (Click confirms password? No, I didn't add confirmation option `confirmation_prompt=True`)

echo "Initializing project '$PROJECT_NAME'..."

# Using sshpass or just raw ssh with key
# We pipe the password to the command.
# Server command expects ONE password input.

# We must be careful about how SSH handles Stdin.
# ssh user@host command  < input_file
CMD="enc server-project-init $PROJECT_NAME --password $PASSWORD"

# Wait, I defined:
# @click.option("--password", prompt=True, hide_input=True)
# If I pass --password arg, it won't prompt.
# Ah, I should have defined it as option that CAN be passed.
# Click option behavior: if passed, no prompt.
# So I can just run: `enc server-project-init <name> --password <pass>`
# BUT, passing password in CLI args is insecure in process list (ps aux).
# That's why I used prompt=True.
# If I use prompt=True, I must pipe it.

# Let's try piping.
# First, re-establish known hosts if needed (container recreated).
ssh-keyscan -p 2222 -H localhost >> ~/.ssh/known_hosts 2>/dev/null

# Attempt Init
# Click prompt reads from stdin.
printf "$PASSWORD\n" | ssh -i /tmp/test_admin_key -p 2222 admin@localhost "enc server-project-init $PROJECT_NAME" > /tmp/init_output.txt 2>&1

cat /tmp/init_output.txt

if grep -q "success" /tmp/init_output.txt; then
    echo "✅ Project Init Success"
else
    echo "❌ Project Init Failed"
    exit 1
fi

# Verify Vault Creation
echo "Verifying Vault Directory on Server..."
docker exec enc_ssh_server ls -la /home/admin/.enc/vault/master/$PROJECT_NAME
if [ $? -eq 0 ]; then
     echo "✅ Vault dir exists."
else
     echo "❌ Vault dir missing."
     exit 1
fi
