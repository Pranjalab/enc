#!/bin/bash

# uninstall.sh
set -e

APP_NAME="enc"
INSTALL_DIR="$HOME/.enc-cli"
SYMLINK_PATH="$HOME/.local/bin/$APP_NAME"

echo "Uninstalling $APP_NAME..."

if [ -d "$INSTALL_DIR" ]; then
    echo "Removing $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
fi

if [ -L "$SYMLINK_PATH" ] || [ -f "$SYMLINK_PATH" ]; then
    echo "Removing $SYMLINK_PATH..."
    rm -f "$SYMLINK_PATH"
fi

echo "Uninstallation complete."
