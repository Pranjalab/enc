#!/bin/bash
set -e

# Ensure FUSE device exists
if [ ! -e /dev/fuse ]; then
    echo "Creating /dev/fuse..."
    mknod -m 666 /dev/fuse c 10 229
fi

# Ensure correct permissions for admin home (in case of volume mounts)
chown -R admin:admin /home/admin

# Start SSHD
echo "Starting SSH Server..."
ssh-keygen -A
/usr/sbin/sshd -D -e
