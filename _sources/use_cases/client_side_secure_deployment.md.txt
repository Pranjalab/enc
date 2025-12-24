# Client-Side Secure Deployment with RAM-Only Execution

> **Note**: This is an **Upcoming Feature**.

Deploy your code on client premises or untrusted cloud servers without revealing your source code.

## Problem
You are a software vendor deploying a proprietary ML model or trading bot on a client's server. You need the code to run, but you don't want the client to steal your algorithm.

## Workflow (Planned)

### 1. Initialization
You initialize the project on the client's server using ENC.

```bash
enc project init proprietary-algo
```

### 2. Secure Mount
The ENC client mounts the project. The code is decrypted **in-memory** using a FUSE filesystem.

```bash
enc project mount proprietary-algo --read-only
```

### 3. Execution
You point your runtime (Python, Docker, Node.js) to the mounted directory.

```bash
python3 ~/enc/projects/proprietary-algo/main.py
```

### 4. Protection Model
- **Disk**: Identify purely random ciphertext.
- **RAM**: Decrypted code exists only in the volatile memory of the ENC process.
- **Teardown**: When the process stops or `enc project unmount` is called, the memory is wiped.

The client never sees the plaintext source code on their disk storage.
