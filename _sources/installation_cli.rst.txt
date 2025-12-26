ENC CLI Installation
====================

The ENC Client (`enc-cli`) allows you to connect to an ENC server, manage projects, and run secure executions from your local machine.

Prerequisites
-------------

Before installing, ensure you have:

*   **Python 3.8+**: Verify with ``python3 --version``.
*   **pip**: The Python package installer.
*   **sshfs**: Required for the mounting feature.
    
    .. note:: 
        If mounting fails or `sshfs` is missing, please reinstall it manually:
        ``brew install --cask macfuse && brew install sshfs``

Installation Steps
------------------

The recommended way to install ENC Client is via ``pip``:
    
    .. code-block:: bash
    
        pip install enc-cli
    
    After installing, run the setup wizard to handle dependencies and path configuration:
    
    .. code-block:: bash
    
        enc install
        
    This command will:
    *   Check for ``sshfs`` and install it if missing (requires sudo).
    *   Ensure the ``enc`` executable is in your PATH.
    *   Prompt you to initialize your configuration.

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
    *   **SSH Key Path**: Leaving this blank is fine! You can run ``enc setup ssh-key`` later to auto-generate one.

You can check your configuration at any time with:

.. code-block:: bash

    enc show
