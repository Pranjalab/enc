Security
========

ENC is built on a "Zero Trust" architecture for code execution.

Architecture Overview
---------------------

1.  **Encrypted at Rest**: All project files are stored as encrypted ciphertexts using `gocryptfs` (AES-256-GCM). The keys to decrypt these files are **never** stored on the server's disk.
2.  **SSH Tunneling**: All client-server communication happens over an encrypted SSH tunnel.
3.  **InMemory Decryption**: When a project is "mounted", it is decrypted virtually into RAM. If the server loses power, the decrypted view vanishes instantly.

Why SSH Keys?
-------------

We use SSH keys (Ed25519 recommended) for authentication because they are:

*   **Cryptographically Strong**: Much harder to brute-force than passwords.
*   **Non-Phishable**: The private key never leaves your local machine.
*   **Auditable**: The server can track exactly which key accessed which resource.

Session Security
----------------

ENC implements a multi-layered session monitoring system to ensure integrity and automatic cleanup.

Session Monitoring Protocols
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**1. Server-Side Monitoring**

*   **Inactivity Timeout**: Sessions are strictly limited. If no CLI commands are executed or no file activity is detected for **10 minutes** (600 seconds), the session is automatically closed.
*   **Mount Activity Keep-Alive**: The server monitors active mounts. As long as you are reading or writing files in the mounted project, the session stays alive.
*   **Closure Conditions**:
    *   **Command Timeout**: > 10 mins idle.
    *   **Mount Timeout**: > 10 mins without file IO.
    *   **Explicit Logout**: `enc logout`.

**2. Client-Side Monitoring**

*   **Project Integrity Monitor**: The CLI checks every **3 seconds** to ensure your local mount point is valid. If the connection drops or the directory is tampered with, it forces a local unmount to prevent stale handles.
*   **Session Watchdog**: A background process monitors your terminal window (Parent PID). If you close the terminal or kill the shell, the watchdog immediately triggers a secure logout sequence, ensuring no session is left dangling.

**3. Isolation**

*   **Auto-Lock**: If the SSH connection drops, the server automatically unmounts the decrypted project view.
*   **Sandboxing**: Each user runs in a restricted shell environment, preventing lateral movement within the server OS.
