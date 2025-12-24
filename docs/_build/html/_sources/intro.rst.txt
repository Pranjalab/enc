Introduction
============

Ever wondered how secure your scripts and algorithms really are once they’re deployed on a server?

When you deploy code to a standard server, it sits there in plaintext—accessible to anyone with root access, physical access to the disk, or a lucky exploit.

To solve this problem, we’re excited to introduce the **ENC Project**—a secure, encrypted execution environment that ensures only **you** can access and manage your projects, from anywhere.

.. image:: _static/enc_architecture.png
   :alt: ENC Architecture
   :align: center
   :width: 100%

Components
----------

The system consists of two main components:

ENC Server
    A hardened, SSH-based fortress that hosts your encrypted vaults. It can be deployed anywhere (AWS, VPS, On-Prem) and ensures that even the server administrator cannot peek into your project files.

ENC Client (enc-cli)
    A powerful CLI tool that runs on your local machine. It creates a secure tunnel to the server, managing encryption keys and allowing you to work on your projects seamlessly.
