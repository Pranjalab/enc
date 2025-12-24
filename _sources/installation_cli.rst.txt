ENC CLI Installation
====================

The ENC Client (`enc-cli`) allows you to connect to an ENC server, manage projects, and run secure executions from your local machine.

Prerequisites
-------------

Before installing, ensure you have:

*   **Python 3.8+**: Verify with ``python3 --version``.
*   **pip**: The Python package installer.
*   **sshfs**: Required for the mounting feature (install via your package manager, e.g., ``brew install sshfs`` or ``apt install sshfs``).

Installation Steps
------------------

We provide an automated installer script that sets up a virtual environment and installs all dependencies.

1.  **Navigate to the client directory**:

    .. code-block:: bash

        cd enc-cli

2.  **Run the installation script**:

    .. code-block:: bash

        ./install.sh

    This script will:
    *   Create a virtual environment in ``~/.enc-cli/venv``.
    *   Install Python dependencies (`rich`, `click`, `pexpect`, etc.).
    *   Symlink the ``enc`` executable to a directory in your PATH (e.g., ``~/.local/bin``).

3.  **Verify Installation**:

    .. code-block:: bash

        enc --version

Configuration
-------------

Once installed, you must configure the CLI to point to your server.

1.  Run the initialization command:

    .. code-block:: bash

        enc config init

2.  Follow the prompts:
    *   **Server URL**: Enter the full URL (e.g., ``http://your-server.com:2222``).
    *   **Username**: Your assigned username.
    *   **SSH Key Path**: Path to your private SSH key (e.g., ``~/.ssh/id_ed25519``).

You can check your configuration at any time with:

.. code-block:: bash

    enc show
