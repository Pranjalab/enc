#!/bin/bash

# install.sh
set -e

APP_NAME="enc"
INSTALL_DIR="$HOME/.enc-cli"
BIN_DIR="$HOME/.local/bin"
SYMLINK_PATH="$BIN_DIR/$APP_NAME"

echo "Installing $APP_NAME..."

# Ensure Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Clean previous install
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing existing installation at $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
fi
mkdir -p "$INSTALL_DIR"

# Create venv
echo "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# Install package
echo "Installing package..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install .

# Create symlink
mkdir -p "$BIN_DIR"
if [ -L "$SYMLINK_PATH" ] || [ -f "$SYMLINK_PATH" ]; then
    echo "Removing existing symlink at $SYMLINK_PATH..."
    rm -f "$SYMLINK_PATH"
fi

echo "Creating symlink..."
ln -s "$INSTALL_DIR/venv/bin/enc" "$SYMLINK_PATH"

# Automate PATH configuration
RC_FILE=""
SHELL_NAME=$(basename "$SHELL")

if [ "$SHELL_NAME" = "zsh" ]; then
    RC_FILE="$HOME/.zshrc"
elif [ "$SHELL_NAME" = "bash" ]; then
    RC_FILE="$HOME/.bashrc"
    if [ "$(uname)" = "Darwin" ] && [ ! -f "$RC_FILE" ]; then
        RC_FILE="$HOME/.bash_profile"
    fi
fi

if [ -n "$RC_FILE" ] && [ -f "$RC_FILE" ]; then
    if ! grep -q "$BIN_DIR" "$RC_FILE"; then
        if [ -w "$RC_FILE" ]; then
            echo "Adding $BIN_DIR to PATH in $RC_FILE..."
            echo "" >> "$RC_FILE"
            echo "# Added by enc-cli installer" >> "$RC_FILE"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$RC_FILE"
        else
            echo "WARNING: Cannot update $RC_FILE automatically (Permission Denied)."
            echo "It seems $RC_FILE is not writable by the current user."
            echo "To complete installation, please run this command manually:"
            echo ""
            echo "  sudo sh -c 'echo \"export PATH=\\\"\$HOME/.local/bin:\$PATH\\\"\" >> $RC_FILE'"
            echo ""
        fi
    else
        echo "$BIN_DIR is already in $RC_FILE"
    fi
else
    echo "Could not detect shell configuration file. Please manually add:"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "to your shell configuration."
fi

echo "Installation complete!"
echo "Run 'enc --help' to verify."
if [ -n "$RC_FILE" ]; then
    echo "If command is not found, restart your terminal or run: source $RC_FILE"
fi
