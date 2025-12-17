# ENC Client: Secure Remote Access

The **ENC Client** (`enc-cli`) is your secure gateway. It empowers you to access your encrypted projects from anywhere and manages your secure workflow sessions.

## 🌍 Feature 3: Access from Anywhere
Whether you are on a laptop in a cafe or a workstation at home, `enc-cli` connects you securely to your project server.

- **Secure Session Management**:
    - **Login**: Establishes a secure tunnel and unlocks your keys in memory.
    - **Work**: Run commands, edit files, and execute code remotely.
    - **Logout**: Instantly wipes local keys and locks the remote session.

- **Auto-Locking**:
    - Closing your terminal or internet disconnection automatically triggers a session lock, ensuring no unattended access.

## 🔄 Smart Git Synchronization (Beta)
ENC integrates deeply with your workflow to ensure specific version control safety.

When you finish a session (Logout/Close):
1.  **Auto-Commit**: ENC detects changes in your workspace.
2.  **Flexible Modes**:
    *   **Encrypted Mode**: Commits encrypted blobs to public/untrusted repos (safe coding on GitHub).
    *   **Decrypted Mode**: Commits plaintext to internal secure/self-hosted GitLabs.

---

## 🚀 Installation & Setup

### 1. Install
```bash
cd enc-cli
./install.sh
```

### 2. Configure
Point the CLI to your ENC Server.
```bash
enc config init
# URL: http://your-server-ip:2222
# User: your-username
```

### 3. Login
Start your secure session.
```bash
enc login
```

---

## 🛠 Command Reference

| Command | Action |
| :--- | :--- |
| `enc check-connection` | Verify you can reach the server. |
| `enc login` | Authenticate and unlock your secure session. |
| `enc status` | Check if your session is active/secure. |
| `enc projects` | List or switch active projects. |
| `enc exec <cmd>` | Run a command securely on the server. |

---

## 🗑 Uninstallation
```bash
./uninstall.sh
```
