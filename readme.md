# ENC: Encrypted Native Code

> **"Secure your code at rest, execute it in memory, access it from anywhere."**

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Status: Beta](https://img.shields.io/badge/Status-Beta-orange.svg)

**ENC** is a comprehensive security ecosystem designed to protect your intellectual property. It ensures that your source code is never exposed on disk, providing a secure lifecycle from storage to execution to remote access.

---

## 🌟 Core Features

### 1. 🛡️ Secure Project Management
**Manage your projects from an SSH-secured bastion that locks down your code.**
*   **Zero-Trust Storage**: All project files are stored locally encrypted (AES-256). No admin or intruder can read your source code on the disk.
*   **RBAC Secured**: Access is strictly managed via Role-Based Access Control on a hardened SSH server (Port 2222).
*   **Isolation**: Each project exists in a secure container, isolated from the host OS.

### 2. ⚡ Runtime Encrypted Execution
**Deploy and run code directly from RAM, bypassing the disk entirely.**
*   **Memory-Only Decryption**: When you run a script, ENC decrypts it strictly into memory buffers.
*   **Supported Runtimes**: Execute secure code using **Python**, **Docker**, or internal **APIs**.
*   **No Forensic Trace**: If the server pulls the plug, your code vanishes. No temporary files found in `/tmp` or swap.

### 3. 🌍 Secure Remote Access & Workflow
**Work from anywhere using the `enc-cli` with a session-managed workflow.**
*   **Secure Sessions**: Login via the CLI to start a secure usage session.
*   **Auto-Locking**: When you logout or your session times out, all memory is wiped and keys are dropped.
*   **Smart Git Sync**: (Optional) Automatically commits your work to your Git repository when your session closes—choose between storing **Encrypted** (for public repos) or **Decrypted** (for private secure repos) backups.

---

## 🏗 Architecture

| Component | Role |
| :--- | :--- |
| **[Server (The Vault)](./server/README.md)** | Hosts the encrypted projects and handles the Runtime Encrypted Execution. Manages user identities and git synchronization. |
| **[Client (The Key)](./enc-cli/README.md)** | Your secure gateway. Connects from anywhere via SSH to manage sessions, configuration, and project access. |

---

## 🚀 Quick Start in 5 Minutes

### 1. Deploy the Server
Start the secure execution environment using Docker.
```bash
cd server
docker compose up -d --build
# Secure Bastion active on localhost:2222
```

### 2. Install the User Client
Get the tool to access your server.
```bash
cd ../enc-cli
./install.sh
source ~/.zshrc
```

### 3. Connect & Secure Your Work
Login to the fortress.
```bash
enc config init
# URL: http://localhost:2222 | User: admin

enc login
# Default Password: secure_admin_pass
```

### 4. Verify Status
Confirm you are in a secure, memory-only session.
```bash
enc status
# > System Secure. Session Active.
```

---

_Protect your code. Trust no disk. execute via RAM._
