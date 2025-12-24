Server Setup Guide
==================

The ENC Server handles the secure storage and execution of your projects. It is deployed as a Docker container.

Prerequisites
-------------

*   **Docker Engine**: Install from `docs.docker.com <https://docs.docker.com/engine/install/>`_.
*   **Docker Compose**: usually included with Docker Desktop or modern Docker Engine.
*   **Port 2222**: Ensure port 2222 is open and free on your host machine.

Deployment
----------

1.  **Navigate to the server directory**:

    .. code-block:: bash

        cd server

2.  **Run the deployment script**:

    .. code-block:: bash

        ./deploy.sh

    Or manually using Docker Compose:

    .. code-block:: bash

        docker compose up -d --build

3.  **Verify Status**:

    .. code-block:: bash

        docker ps

    You should see a container named ``enc_ssh_server`` running and listening on port 2222.

Configuration
-------------

The server configuration (volumes, ports) is managed via ``docker-compose.yml``.

*   **Storage**: User data is persisted in the ``enc_server_data`` volume.
*   **SSH Host Keys**: Server keys are persisted in ``./ssh/host_keys/`` to prevent re-keying warnings on clients.
