# ENC Client (enc-cli)

Secure, memory-only encryption tool for communicating with the ENC Server.

## Installation

```bash
./install.sh
```
This script installs the CLI to `~/.enc-cli` and attempts to add `~/.local/bin` to your PATH.

## Usage

Check version:
```bash
enc --version
```

Configure connection:
```bash
enc config init
```

Test connection:
```bash
enc login
```

## Commands
The CLI forwards standard commands to the server:
- `enc projects ...`
- `enc user ...`
- `enc init ...`

## Uninstallation
```bash
./uninstall.sh
```
