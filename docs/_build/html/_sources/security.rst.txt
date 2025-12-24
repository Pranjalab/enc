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

*   **Auto-Lock**: If the SSH connection drops (e.g., laptop sleep, network fail), the server automatically unmounts the decrypted project view.
*   **Isolation**: Each user runs in a sandboxed shell environment, preventing lateral movement within the server OS.
