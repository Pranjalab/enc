# ENC System Testing Guide

This document outlines how to verify the **full feature set** of the ENC system, including User Management, Project Lifecycle, and Server Administration.

## 1. Automated Verification (Recommended)

Reliable python scripts are provided to verify the system end-to-end.

### Prerequisites
*   Docker running (Server).
*   Python 3.9+ installed.
*   `enc` client installed.
*   `sshfs` installed (for mount verification).

### A. Lifecycle Verification (New Users)
This script verifies that a new user can be created, logged in, and used to create/sync/run a project.
```bash
cd enc-cli
# Run verification
~/.enc-cli/venv/bin/python tests/verify_user_lifecycle.py
```
**Coverage:**
*   Admin Login.
*   `enc user create` (User Provisioning).
*   User Login (Switch Context).
*   `enc project init` (Encryption).
*   `enc project sync` (Data Transfer).
*   `enc project run` (Remote Execution).
*   `enc user rm` (Cleanup).

### B. Core Feature Verification (Legacy)
Tests the basic flow using a pre-existing `tester` account.
```bash
~/.enc-cli/venv/bin/python tests/verify.py
```

---

## 2. Manual Feature Verification

Perform these steps to manually validate every command in the CLI.

### A. Setup & Configuration
1.  **Install Client**:
    ```bash
    pip install enc-cli
    enc install
    # Ensure ~/.local/bin is in PATH or source rc file
    source ~/.zshrc
    ```
2.  **Configure Admin**:
    ```bash
    enc set-url http://localhost:2222
    enc set-username admin
    enc check-connection
    ```

### B. Admin Operations (User CRUD)
1.  **Login as Admin**:
    ```bash
    enc login
    # Password: adminpass (if reset) or from setup
    ```
2.  **Create New User**:
    ```bash
    enc user create manual_user securepass --role user
    # Output: User manual_user created successfully.
    ```
3.  **Delete User**:
    ```bash
    enc user rm manual_user
    # Output: User manual_user deleted.
    ```

### C. Developer Workflow
1.  **Configure as User**:
    ```bash
    enc set-username manual_user
    ```
2.  **Authentication**:
    ```bash
    enc login
    # Login as 'manual_user' with 'securepass'
    ```
3.  **Project Initialization**:
    ```bash
    enc project init my_secure_app --password vaultpass
    ```
4.  **Synchronization**:
    ```bash
    # Create local content
    mkdir app_src
    echo "print('Secure Hello')" > app_src/main.py
    
    # Sync
    enc project sync my_secure_app ./app_src/
    ```
5.  **Remote Execution**:
    ```bash
    enc project run my_secure_app "python3 main.py"
    # Expected Output: Secure Hello
    ```
6.  **Cleanup**:
    ```bash
    enc logout
    ```

---

## 3. Server Management

### Docker Commands
*   **Rebuild & Start**:
    ```bash
    cd enc-server
    docker-compose build --no-cache
    docker-compose up -d --force-recreate
    ```
*   **Access Shell**:
    ```bash
    docker exec -it enc_ssh_server /bin/bash
    ```
*   **Reset Admin Password** (If forgotten):
    ```bash
    docker exec enc_ssh_server sh -c "echo 'admin:newpassword' | chpasswd"
    ```

### Logs & Debugging
*   **View Server Logs**:
    ```bash
    docker logs -f enc_ssh_server
    ```
*   **Inspect Vaults**:
    ```bash
    docker exec enc_ssh_server ls -R /home/admin/.enc/vault/
    ```

## 4. Known Issues
*   **MacOS Docker FUSE**: `enc project dev` (mount) features are limited on macOS Docker hosts. Validated logic works on Linux.
*   **SSH Host Keys**: If you rebuild the container, you must clear `~/.ssh/known_hosts` for `[localhost]:2222`:
    ```bash
    ssh-keygen -f "~/.ssh/known_hosts" -R "[localhost]:2222"
    ```
