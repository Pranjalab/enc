Project Management
==================

Managing encrypted projects is the core function of ENC. Each project is an isolated vault.

Creating a Project
------------------

To initialize a new project vault:

.. code-block:: bash

    enc project init <project-name>

You will be prompted to create a **Project Password**.
This password is used to derive the master encryption key for the vault.

.. warning::
    **Do not lose this password.** The server administrator cannot recover it for you. If lost, the data is permanently inaccessible.

Mounting a Project
------------------

To work on your project, you must "mount" it. This decrypts the files on-the-fly and makes them accessible in a local folder.

1.  **Create a local directory**:

    .. code-block:: bash

        mkdir ./my-work-folder

2.  **Mount the project**:

    .. code-block:: bash

        enc project mount <project-name> ./my-work-folder

3.  **Enter Password**: Provide the project password when prompted.

Once mounted, you can open ``./my-work-folder`` in any IDE. Files saved here are automatically encrypted and stored on the server.

Listing Projects
----------------

To see all projects you have access to:

.. code-block:: bash

    enc project list

This shows the project name, its server-side mount status, and where it is mounted locally (if active).

Unmounting
----------

When finished, you should unmount the project to secure it.

.. code-block:: bash

    enc project unmount <project-name>

Or, simply **Logout**, which will automatically unmount all active projects:

.. code-block:: bash

    enc logout
