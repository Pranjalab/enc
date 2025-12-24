User Management
===============

This section covers how to manage users on the ENC server. These actions generally require Admin privileges.

System Admin vs. ENC Users
--------------------------

*   **System Admin**: This is the default user (commonly ``admin``) configured during server deployment. They have SSH access to the container and root-level permissions.
*   **ENC Users**: These are restricted users created for developers. They are confined to the ``enc-shell`` and cannot modify system configurations.

Creating a New User
-------------------

The most convenient way to create users is via the ENC CLI.

1.  **Login as Admin**:

    .. code-block:: bash

        enc login
        # Ensure you are logged in with an account that has 'admin' permissions

2.  **Run the Create Command**:

    .. code-block:: bash

        enc user create <username> --role user

    You will be prompted to set a password for the new user.

3.  **SSH Key Assignment (Optional)**:
    You can optionally provide a public SSH key during creation to pre-authorize the user.

Managing Permissions
--------------------

Permissions are currently managed via a global policy file on the server at ``/etc/enc/policy.json``.

To modifying roles manually:

1.  SSH into the server/container:

    .. code-block:: bash

        docker exec -it enc_ssh_server /bin/bash

2.  Edit the policy file:

    .. code-block:: bash

        vi /etc/enc/policy.json
