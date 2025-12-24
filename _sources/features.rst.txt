Features & Roadmap
==================

ENC is built from the ground up to solve the specific problem of code security in untrusted environments.

Core Features
-------------

🔒 Encryption at Rest
~~~~~~~~~~~~~~~~~~~~~
All project files are stored as **AES-256 encrypted ciphertexts** on the server's disk using ``gocryptfs``. Even if an attacker gains physical access to the server's hard drive, your code is unreadable without the specific project key.

⚡ Secure Runtime (In-Memory Decryption)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When you mount a project or run code, files are decrypted **only in memory**. They never touch the server's disk in plaintext. This ensures that your intellectual property remains secure throughout its lifecycle.

🛡️ SSH Tunneling
~~~~~~~~~~~~~~~~
All communication between the client (your laptop) and the ENC server happens over an encrypted **SSH tunnel**. We leverage the battle-tested security of SSH for authentication and transport.

Roadmap
-------

We represent the future of secure coding. Here is what we are building next:

🔄 GitHub Auto-Sync (Coming Soon)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Imagine mounting your project, making edits, and having them automatically pushed to a private GitHub repository the moment you unmount—encrypted or plaintext, based on your policy.
*   **Status**: In Design
*   **Goal**: Seamless version control integration.

💻 VS Code Extension (Coming Soon)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A native VS Code extension to manage ENC projects directly from your editor.
*   **Features**:
    *   One-click Connect/Disconnect
    *   Visual Project Explorer
    *    Integrated Terminal for ``enc`` commands
*   **Status**: Planned

🚀 Hosted ENC Server
~~~~~~~~~~~~~~~~~~~~
A managed service where you can spin up ENC environments instantly, without managing your own VPS.
