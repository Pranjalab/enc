Managing SSH Keys
=================

ENC relies heavily on SSH for secure communication. Proper key management ensures a smooth experience.

Generating an SSH Key
---------------------

If you do not have an SSH key pair, generate one using ``ssh-keygen``:

.. code-block:: bash

    ssh-keygen -t ed25519 -C "your_email@example.com"

*   **Key Type**: We recommend ``ed25519`` for security and performance.
*   **File Location**: Default is usually ``~/.ssh/id_ed25519``.

Adding Keys to ENC
------------------

The ENC CLI needs to know which private key to use for the connection.

Option 1: Automated Setup (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The easiest way is to let ENC handle it. Log in with your password and run:

.. code-block:: bash

    enc setup ssh-key

This will:
*   Generate a secure key pair locally (if none exists).
*   Send the public key to the server over the encrypted session.
*   Configure your local client to use this key automatically.

Option 2: Using SSH Agent
~~~~~~~~~~~~~~~~~~~~~~~~~
Add your key to the SSH agent for automatic authentication:

.. code-block:: bash

    ssh-add ~/.ssh/id_ed25519

Option 3: Configuring Manual Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tell ENC explicitly which key file to use:

.. code-block:: bash

    enc config init
    # When prompted for "path to ssh key", enter: /Users/you/.ssh/id_ed25519

Authorizing Keys on Server
--------------------------
For a user to log in, their **Public Key** (``.pub`` file) must be added to the server's authorized list.

1.  **Copy Public Key**:
    
    .. code-block:: bash
    
        cat ~/.ssh/id_ed25519.pub

2.  **Add to Server**:
    *   **During Creation**: Provide the key string when the admin runs ``enc user create``.
    *   **Manual**: Append the string to ``/home/<username>/.ssh/authorized_keys`` on the server container.
