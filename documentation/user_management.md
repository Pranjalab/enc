# User Management Guide

This document outlines the procedures and protocols for managing users in the ENC system using the `enc-cli`.

## Overview

User management is restricted to users with the **admin** role. Commands are executed from the client and processed on the server via secure SSH communication.

## Protocols for Administrator

### 1. Connecting to the Server

Before managing users, ensure you are logged in as an administrator:
```bash
enc login
```
*You will be prompted for your password if an SSH key is not configured.*

---

### 2. SSH Key Management (Recommended)

Using SSH keys is recommended for non-interactive administration and automation.

#### A. Generating an SSH Key
To generate a new SSH key for a user (e.g., `.test_key`):
```bash
ssh-keygen -t ed25519 -N "" -f .test_key
```
This generates:
*   `.test_key` (Private key - Keep secure)
*   `.test_key.pub` (Public key - Share with server)

#### B. Configuring your Administrator account to use a Key
If you want to use a key for your own admin session, update your local config:
```bash
enc init
```
When prompted for **SSH Key Path**, provide the absolute path to your private key (e.g., `/path/to/.test_key`).

---

### 3. Creating a New User

Admins can create users using two primary methods:

#### A. Interactive Mode
Ideal for manual administration. The system will guide you through the required fields.
```bash
enc user create <username>
```
**Prompts will cover:**
*   **Role Selection**: Choose between `admin` or `user`.
*   **Password**: Assign an initial password for the user.
*   **SSH Public Key (Optional)**: Provide a path to the user's `.pub` file to enable key-based login.

#### B. Automated/Argument Mode
Ideal for scripts or rapid provisioning.
```bash
enc user create <username> \
  --role [admin|user] \
  --password <secure_password> \
  --ssh-key </path/to/key.pub> \
  --json
```
*Note: The `--json` flag provides machine-readable output and suppresses unnecessary formatting.*

---

### 4. Listing Users

To view all managed users and their roles:

#### Default View (Table)
```bash
enc user list
```

#### JSON View (Automation)
```bash
enc user list --json
```

---

### 5. Removing a User

To remove a user's access from the system:

#### Interactive Confirmation
```bash
enc user remove <username>
```
*The system will ask for confirmation before deleting the user.*

#### Force/JSON Mode
```bash
enc user remove <username> --json
```
*This will bypass the confirmation prompt and return a JSON status.*

---

## Technical Security Notes

*   **Authentication**: All user management commands require authenticating as an admin user on the underlying SSH server.
*   **RBAC**: Permissions are enforced on the server-side via `policy.json`.
*   **Logging**: All user management actions are logged in the active session file on the server for auditing.
