#!/bin/bash
set -e

echo "=== ENC GLOBAL TEST SUITE ==="

echo -e "\n[1/2] Running Server Unit Tests (SSH, RBAC, Lifecycle)..."
cd server
# Ensure docker is up?
# docker compose up -d --build  <-- Optional: force rebuild
cd ..
pytest -s server/tests/

# Manage Known Hosts for localhost:2222 (Avoid interactive prompt)
touch ~/.ssh/known_hosts
ssh-keygen -R "[localhost]:2222" > /dev/null 2>&1
ssh-keyscan -p 2222 localhost >> ~/.ssh/known_hosts 2>/dev/null

echo -e "\n[2/2] Running Client Integration Tests..."
pytest -s tests/

echo -e "\n=== ALL TESTS PASSED ==="
