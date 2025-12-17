# ENC: Secure Code Execution Environment

ENC (Encrypted Native Code) is a secure, memory-only code execution platform designed to protect intellectual property and runtime secrets. It allows developers to execute code remotely without exposing source code or secrets to the disk.

## Project Structure

This project is divided into two main components:

### 1. [Server](./server/README.md)
The **ENC Server** is the secure bastion that hosts the execution environment.
*   **Role**: Host, Execution, User Management.
*   **Security**: SSH only (Port 2222), Role-Based Access Control (RBAC).
*   **Storage**: Manages User DB (`policy.json`) and secure ephemeral storage.

### 2. [Client (enc-cli)](./enc-cli/README.md)
The **ENC Client** is a lightweight CLI tool installed on developer machines.
*   **Role**: Connectivity, Command Forwarding.
*   **Usage**: Connects to the server via SSH to manage projects and run code.

## Quick Start

### 1. Host the Server
Navigate to the `server/` directory and follow the instructions to deploy the Docker container.
```bash
cd server
less README.md
```

### 2. Install the Client
Navigate to the `enc-cli/` directory to install the local tool.
```bash
cd enc-cli
less README.md
```

## Security Model
*   **Single Entry Point**: All access is via SSH on port 2222.
*   **Restricted Shell**: Users never interact with the OS directly; they are confined to the `enc` environment.
*   **RBAC**: Strict separation between Admins (User Managers) and Developers.
