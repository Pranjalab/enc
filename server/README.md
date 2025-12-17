# ENC Server Setup & User Management Guide

This guide explains how to host the secure ENC SSH Bastion and manage access using the ENC CLI.

## 1. Hosting the Server

The server is a lightweight Alpine Linux container running OpenSSH.

### Start the Server
```bash
cd server
docker compose up -d --build
```

### Check Status
```bash
docker ps
# Ensure 'enc_ssh_server' is running on port 2222
```

---

## 2. Managing Users (RBAC)

Previously, we used scripts or manual edits. Now, the **ENC CLI** manages users directly.

### Prerequisites
*   You must be logged in as the `admin` user (via SSH).
*   The `admin` has `sudo` privileges to manage system users.

### User Roles
*   **admin**: Full system access, runs `bash` shell.
*   **Users**: Restricted access, runs `enc-shell`. Restricted to specific `enc` commands.

### Commands

#### 1. Add a New User
```bash
# Syntax: enc user add <username>
enc user add developer1
```
*   You will be prompted for a **Password** and **SSH Key**.
*   This creates a Linux user and updates the permission policy.

#### 2. List Users
```bash
enc user list
```
*   Displays a table of all managed users and their allowed commands.

#### 3. Remove a User
```bash
enc user remove developer1
```
*   **Warning**: This deletes the user and their home directory/data immediately.

---

## 3. SSH Connectivity

### Connecting as Admin
```bash
ssh -p 2222 admin@localhost
```

### Connecting as Restricted User
```bash
ssh -p 2222 developer1@localhost
```
*   You will see a restricted prompt `enc>`.
*   Standard commands like `ls` or `cd` are **BLOCKED**.
*   Only valid `enc` commands are allowed.

---

## 4. Verification & Testing

We have built automated test suites to verify the security and functionality of the server.

### Run All Tests
From the project root:
```bash
pytest -s
```

### Specific Test Scenarios

#### 1. Basic SSH Connectivity
Verifies that the SSH server accepts passwords and keys for the admin.
```bash
pytest -s server/tests/test_ssh.py
```

#### 2. Restricted Shell & RBAC
Verifies that restricted users cannot run forbidden commands (like `ls`) and receive the correct secured shell.
```bash
pytest -s server/tests/test_rbac.py
```

#### 3. User Lifecycle (CRUD)
Verifies the full administrative flow: Adding, Listing, and Removing users via the CLI.
```bash
pytest -s server/tests/test_user_lifecycle.py
```

---
