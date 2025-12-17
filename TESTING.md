# Global Testing Guide

This project includes a comprehensive test suite covering both the **Server** infrastructure and the **Client** CLI.

## Quick Start

To run **ALL** tests (Server + Client Integration), execute the helper script:

```bash
./run_tests.sh
```

## Structure

1.  **Server Tests** (`server/tests/`):
    *   Directly test the docker container's SSH and RBAC logic using `paramiko`.
    *   Independent of the `enc-cli` client.

2.  **Client Tests** (`tests/`):
    *   Integration tests that execute the installed `enc` CLI command.
    *   Verifies that the client correctly forwards commands to the server and handles the response.

## Prerequisites
*   Docker Container (`enc_ssh_server`) must be running.
*   `enc-cli` must be installed locally (`pip install enc-cli/`).
*   Config must be initialized (`enc config init`).
