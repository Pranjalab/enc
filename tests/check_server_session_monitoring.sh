#!/bin/bash
set -e

# Setup
TEST_USER="admin"
TEST_PASS="secure_admin_pass"
PROJECT="mon_test_proj"
MOUNT_DIR="./mon_mount_point"

# Ensure enc is in path or alias (assuming global install or alias setup)
# If not, fail fast.
if ! command -v enc &> /dev/null; then
    echo "enc command not found"
    exit 1
fi

echo "========================================"
echo "SESSION MONITORING SHELL TEST"
echo "========================================"

# Cleanup potentially stale session/project
rm -rf "$MOUNT_DIR"
enc logout > /dev/null 2>&1 || true

# 1. Test Command Inactivity Logout
echo "Test 1: Auto-logout after command inactivity (16s > 15s)"
echo "Logging in..."
enc login --password "$TEST_PASS" > /dev/null

echo "Wait 16s..."
sleep 16

echo "Checking status..."
if enc project list 2>&1 | grep -q "Please login first"; then
    echo "SUCCESS: Session closed after inactivity."
else
    echo "FAILED: Session still active."
    exit 1
fi

# 2. Test Mount Activity Keep-Alive & Inactivity Logout
echo "----------------------------------------"
echo "Test 2: Mount Activity Monitoring"
echo "Logging in..."
enc login --password "$TEST_PASS" > /dev/null

# Init project if needed (ignore error if exists)
# check if project exists in list
if ! enc project list | grep -q "$PROJECT"; then
    echo "Creating project $PROJECT..."
    enc project init "$PROJECT" -p "$TEST_PASS" -d . > /dev/null
fi

mkdir -p "$MOUNT_DIR"
echo "Mounting $PROJECT..."
enc project mount "$PROJECT" "$MOUNT_DIR" -p "$TEST_PASS" > /dev/null

# A. Keep-Alive Test
echo "Subtest A: Keep-Alive via File Touch"
echo "Touching file in '$MOUNT_DIR' every 5s for 20s (total > 15s timeout)..."
for i in {1..4}; do
    sleep 5
    touch "$MOUNT_DIR/keep_alive.txt"
    echo "Touched file..."
done

# Check session - should still be valid because of touches
if enc project list > /dev/null 2>&1; then
    echo "SUCCESS: Session kept alive by file activity."
else
    echo "FAILED: Session closed despite file activity."
    exit 1
fi

# B. Auto-Logout No Activity
echo "Subtest B: Auto-logout after NO file activity"
echo "Waiting 16s with NO activity..."
sleep 16

# Check session - should be closed
if enc project list 2>&1 | grep -q "Please login first"; then
    echo "SUCCESS: Session closed after mount inactivity."
else
    echo "FAILED: Session still active (Mount monitor failed to expire session?)."
    exit 1
fi

# Cleanup
# Force unmount if needed (session closed so unmount might fail or need force local cleanup)
# enc project unmount might fail if logged out.
# Manually unmount with fusermount (linux) or umount (mac) just in case
if [[ "$OSTYPE" == "darwin"* ]]; then
    umount "$MOUNT_DIR" > /dev/null 2>&1 || true
else
    fusermount -u "$MOUNT_DIR" > /dev/null 2>&1 || true
fi
rm -rf "$MOUNT_DIR"

echo "========================================"
echo "✅ ALL CHECKS PASSED"
echo "========================================"
