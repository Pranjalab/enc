#!/bin/bash
set -e

# Setup executable permissions
chmod +x check_admin_login.sh
chmod +x check_dev_user.sh

# Create logs directory
mkdir -p logs

# Define log file name with timestamp
LOG_FILE="logs/test_$(date +%Y%m%d_%H%M%S).txt"

echo "Logging results to: $LOG_FILE"

# Use a subshell or grouping to redirect everything to tee
(
    echo "========================================"
    echo "RUNNING ADMIN TEST SUITE"
    echo "========================================"
    echo -e "\n"
    ./check_admin_login.sh
    echo -e "\n"

    echo "========================================"
    echo "RUNNING DEV USER TEST SUITE"
    echo "========================================"
    ./check_dev_user.sh
    echo -e "\n"

    echo "========================================"
    echo "RUNNING SESSION SPOOFING TEST"
    echo "========================================"
    chmod +x check_session_spoof.sh
    ./check_session_spoof.sh
    echo -e "\n"

    echo "========================================"
    echo "RUNNING SESSION MONITORING TEST"
    echo "========================================"
    chmod +x check_server_session_monitoring.sh
    ./check_server_session_monitoring.sh
    echo -e "\n"

    echo "✅ ALL TESTS PASSED"
) 2>&1 | tee "$LOG_FILE"

# Preserve exit code from the test subshell
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    exit 1
fi
