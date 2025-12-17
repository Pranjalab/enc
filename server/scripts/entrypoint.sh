#!/bin/sh
set -e

# Defaults
ADMIN_PASSWORD=${ADMIN_PASSWORD:-adminpassword}

echo "Setting up admin user..."
# Unlock the user (if locked) and set password
echo "admin:$ADMIN_PASSWORD" | chpasswd

# Generate host keys if missing (Alpine specific)
ssh-keygen -A

echo "Starting SSHD..."
/usr/sbin/sshd -D
