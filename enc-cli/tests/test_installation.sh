#!/bin/bash

# tests/test_installation.sh
set -e

echo "--- Testing enc-cli Rebuild ---"

# 1. Uninstall logic (ensure clean slate)
./uninstall.sh

# 2. Install
./install.sh

# 3. Verify
echo "--- Verifying 'enc' command ---"
# Force usage of local bin in case path not updated in current shell
ENC_CMD="$HOME/.local/bin/enc"

if [ ! -x "$ENC_CMD" ]; then
    echo "FAILURE: $ENC_CMD not found."
    exit 1
fi

OUTPUT=$("$ENC_CMD" --help)
if [[ "$OUTPUT" == *"Usage: cli"* ]] || [[ "$OUTPUT" == *"Usage: enc"* ]]; then
    echo "SUCCESS: enc --help works"
else
    echo "FAILURE: enc --help unexpected output:"
    echo "$OUTPUT"
    exit 1
fi

# 4. Clean up
./uninstall.sh

echo "SUCCESS: All tests passed."
