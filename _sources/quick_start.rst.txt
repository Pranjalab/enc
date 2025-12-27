Quick Start
===========

Get up and running with ENC in minutes. This guide covers the fastest way to deploy the server and install the client.

.. note::
   Don't want to set up a server? We are working on a **Hosted ENC Server** for users to experiment with zero setup. Stay tuned!

1. Generate SSH Key (Pre-requisite)
------------------------------------

If you don't already have an SSH key, generate one:

.. code-block:: bash

   ssh-keygen -t ed25519 -f ~/.ssh/enc_admin_key -N ""

2. Clone the Repository
-----------------------

Clone the project along with its submodules:

.. code-block:: bash

   git clone --recurse-submodules https://github.com/Pranjalab/enc.git
   cd enc

3. Server Setup
---------------

Navigate to the server directory and configure your environment:

.. code-block:: bash

   cd enc-server

   # 1. Setup Environment Variables
   # Create a .env file
   echo "ADMIN_PASSWORD=your_secure_password" > .env
   echo "ENC_SESSION_TIMEOUT=600" >> .env

   # 2. Setup SSH Keys
   mkdir -p ssh/host_keys
   touch ssh/authorized_keys
   chmod 600 ssh/authorized_keys

   # 3. Add your Public Key to Server (Crucial!)
   cat ~/.ssh/enc_admin_key.pub >> ssh/authorized_keys

   # 4. Deploy
   docker compose up --build -d

The server is now running on port **2222** (default) and has authorized your key.

4. Client CLI Setup
-------------------

Install the client on your local machine:

.. code-block:: bash

   cd ../enc-cli

   # 1. Install the CLI
   # Use 'pip install .' for standard or '-e .' for editable
   pip install .

   # 2. Install Dependencies & Setup
   # Checks for SSHFS and sets up config directories
   enc install

5. Initialize & Login
---------------------

Connect your client to the server:

.. code-block:: bash

   # 1. Configure the connection
   enc init
   # Follow prompts:
   # URL: http://localhost:2222
   # Username: admin
   # SSH Key: /path/to/private/key (e.g., ~/.ssh/enc_admin_key)

   # 2. Login
   enc login
   # Enter your ADMIN_PASSWORD

   # 3. Explore
   enc --help
