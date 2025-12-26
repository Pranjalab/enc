# Host Your Own ENC Server and Access It from Anywhere

This guide explains how to set up your own ENC server and access your private, encrypted projects from any machine.

## Overview

By hosting your own ENC server, you gain complete control over your data.
- **Server Side**: Runs the ENC server Docker container, handling encrypted storage and user authentication.
- **Client Side**: Your local laptop/workstation that connects via `enc-cli` to work on projects.

## Prerequisite

- A VPS or dedicated server (e.g., AWS EC2, DigitalOcean, or a Raspberry Pi) with:
  - Docker installed
  - Public IP or accessible hostname
  - Unused port (default: 2222)
- A client machine (macOS/Linux) with:
  - Python 3.9+
  - SSH client

## 1. Hosting the ENC Server

Connect to your remote server via SSH:

```bash
ssh user@your-server-ip
```

Clone the repository and run the deployment script:

```bash
git clone https://github.com/Pranjalab/enc.git
cd enc/server
sudo ./deploy.sh
```

This will:
1. Build the `enc-server` Docker image.
2. Start the container on port `2222`.
3. Create the necessary volume `enc_server_data` for persistent storage.

## 2. Client Setup

On your local machine, install the `enc` CLI:

```bash
git clone https://github.com/Pranjalab/enc.git
cd enc/enc-cli
./install.sh
```

## 3. Workflow

### Step A: Create Admin User
The first user created must be done directly on the server container.

```bash
# On your server
docker exec -it enc-server enc user create <your-username>
```

### Step B: Configure Client Access
Add your local SSH key to the ENC configuration. This allows the CLI to authenticate automatically.

```bash
# On your client (laptop)
enc config add-key ~/.ssh/id_rsa
```

### Step C: Initialize a Project
Create a new encrypted project. It will be initialized on the server.

```bash
enc project init my-backend-api
```

### Step D: Access from Anywhere
You can now travel to another city, use a different laptop (after installing the CLI and adding your key), and access your work instantly.

```bash
# Mount the project
enc project mount my-backend-api
```

Your project is now available at `~/enc/projects/my-backend-api`. All files you write here are encrypted before being saved to the server.
