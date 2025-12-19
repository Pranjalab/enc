# ENC Server: The Secure Execution Runtime

The **ENC Server** is the heart of the ecosystem. It provides the **Secure Server** management and **Runtime Encrypted Execution** capabilities.

## 🛡️ Feature 1: The Secure Fortress
The server creates a hardened boundary around your code.

- **Encrypted Storage**: Projects stored here are encrypted at rest. Physical access to the server disk yields only gibberish.
- **SSH Bastion**: The only entry point is via SSH on a non-standard port (`2222`).
- **Restricted Environment**: Users are confined to `enc-shell`, preventing unauthorized OS traversal.

## ⚡ Feature 2: Runtime Encrypted Execution
This is the core innovation of ENC. It allows code to run without ever existing as a plaintext file.

### How it Works
1.  **Request**: You request execution (e.g., `enc run my_script.py`).
2.  **Fetch**: The server reads the *encrypted* file from disk.
3.  **Decrypt**: The file is decrypted **directly into a RAM buffer**.
4.  **Execute**: The runtime (Python, Docker, etc.) loads the code from memory.
5.  **Wipe**: Once execution finishes, the memory buffer is zeroed out.

---

## 🏗 Deployment Guide

### Prerequisites
- Docker & Docker Compose
- Port `2222` free on the host

### 1. Launch the Server
```bash
cd server
docker compose up -d --build
```

### 🔑 SSH Configuration
The server uses a unified directory `server/ssh/` to manage identity:

1.  **Your Access**:
    - Add your public key to `server/ssh/authorized_keys`.
    - This allows you to log in as `admin`.
    - [Detailed Guide: Generate SSH Keys](ssh/generate_ssh_key.md)

2.  **Server Identity**:
    - **Note**: The `server/ssh/host_keys/` folder persists the server's unique fingerprint.
    - It prevents "REMOTE HOST IDENTIFICATION HAS CHANGED" warnings after rebuilds.

### 2. Connect
Once launched, connect via:
```bash
ssh -i ~/.ssh/enc_key -p 2222 admin@localhost
```

---

### 3. Verify Security
Check that the container is running and listening strictly on the configured port.
```bash
docker ps
```

---

## 👥 User & Project Management

Use the **ENC CLI** to manage this server remotely.

- **Add Users**: `enc user add <name>`
- **Manage Permissions**: Edit `/etc/enc/policy.json` (or use CLI commands).

---

## 🔒 Security Guarantee
If this server is powered off, seized, or inspected, your source code remains AES-256 encrypted. Only an active, authenticated RAM session can unlock it.
