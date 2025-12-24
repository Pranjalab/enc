Quick Start
===========

Get up and running with ENC in minutes. This guide covers the fastest way to deploy the server and install the client.

.. note::
   Don't want to set up a server? We are working on a **Hosted ENC Server** for users to experiment with zero setup. Stay tuned!

1. Deploy the Server
--------------------

On your remote server (Ubuntu/Debian recommended):

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/Pranjalab/enc.git
   cd enc/server

   # Run the deployment script (Docker required)
   sudo ./deploy.sh

This will verify dependencies, build the ``enc-server`` Docker image, and start the service on port 2222.

2. Install the Client
---------------------

On your local machine (macOS/Linux):

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/Pranjalab/enc.git
   cd enc/enc-cli

   # Run the installer
   ./install.sh

This installs the ``enc`` command to ``/usr/local/bin``.

3. Initialize Your First Project
--------------------------------

Now, create a user and start your first secure project:

.. code-block:: bash

   # 1. Create your user on the server (requires admin access or first run)
   # (On the server)
   docker exec -it enc-server enc user create <your-username>

   # 2. Add your local SSH key to the server
   enc config add-key <your-private-key-path>

   # 3. Initialize a new encrypted project
   enc project init my-secure-algo

   # 4. Mount it locally
   enc project mount my-secure-algo

Your project is now mounted at ``~/enc/projects/my-secure-algo``. Any files you create there are encrypt-on-write!
