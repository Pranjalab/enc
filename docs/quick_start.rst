Quick Start
===========

Get up and running with ENC in minutes. This guide covers the fastest way to deploy the server and install the client.

.. note::
   Don't want to set up a server? We are working on a **Hosted ENC Server** for users to experiment with zero setup. Stay tuned!

1. Clone the Repository
-----------------------

Clone the project along with its submodules:

.. code-block:: bash

   git clone --recurse-submodules https://github.com/Pranjalab/enc.git
   cd enc

2. Server Setup
---------------

Navigate to the server directory and configure your environment:

.. code-block:: bash

   cd enc-server

   # 1. Setup Environment Variables
   # Create a .env file
   echo "ADMIN_PASSWORD=your_secure_password" > .env
   echo "ENC_SESSION_TIMEOUT=600" >> .env

   # 2. Setup SSH Host Keys Volume
   mkdir -p ssh/host_keys

   # 3. Deploy
   docker compose up --build -d

The server is now running on port **2222** (default).

3. Client CLI Setup
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

4. Initialize & Login
---------------------

Connect your client to the server:

.. code-block:: bash

   # 1. Configure the connection
   enc init
   # Follow prompts:
   # URL: http://localhost:2222
   # Username: admin

   # 2. Login
   enc login
   # Enter your ADMIN_PASSWORD

   # 3. Setup SSH Key (Recommended)
   enc setup ssh-key

   # 4. Create & Mount Project
   enc project init my-app
   mkdir ./my-app-edit
   enc project mount my-app ./my-app-edit
