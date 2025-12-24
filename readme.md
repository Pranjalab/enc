<div align="center">
  <img src="docs/_static/enc_icon.png" alt="ENC Logo" width="100"/>
  <h1>ENC: The Encrypted Coding Environment</h1>
  
  [![Documentation Status](https://img.shields.io/badge/docs-live-brightgreen)](https://pranjalab.github.io/enc/)
  [![GitHub Release](https://img.shields.io/github/v/tag/Pranjalab/enc?label=version)](https://github.com/Pranjalab/enc/tags)
</div>

![ENC Poster](docs/_static/enc_poster.png)

> **Ever wondered how secure your projects and algorithms really are while development and deployment on a server?**

When you deploy code to a standard server, it sits there in plaintext—accessible to anyone with root access, physical access to the disk, or a lucky exploit. 

To solve this problem, we’re excited to introduce the **ENC Project**—a secure, encrypted execution environment that ensures only **you** can access and manage your projects, from anywhere.

---

## 🌟 Overview

ENC is designed to protect your intellectual property and sensitive logic by ensuring your code is **always encrypted at rest** and only decrypted **in memory** during active execution.

![ENC Architecture](docs/_static/enc_architecture.png)

The system consists of two main components:

- **🔐 ENC Server**: A hardened, SSH-based fortress that hosts your encrypted vaults. It can be deployed anywhere (AWS, VPS, On-Prem) and ensures that even the server administrator cannot peek into your project files.
- **💻 ENC Client (`enc-cli`)**: A powerful CLI tool that runs on your local machine. It creates a secure tunnel to the server, managing encryption keys and allowing you to work on your projects seamlessly.

---

## ✨ Key Features

- **🛡️ End-to-End Security**: All communication is secured via SSH tunnels.
- **🔒 Project-Level Encryption**: Each project is an independent encrypted vault (using `gocryptfs`). Keys are never stored on the server's disk.
- **👁️ Session Monitoring**: Active sessions are monitored. Closing your terminal locks the session instantly.
- **🚀 Runtime Encryption**: Code is decrypted on-the-fly into a secure RAM buffer for execution and wiped immediately after.
- **⚡ SSHFS Integration**: Mount your remote encrypted projects locally to edit them with your favorite IDE (VS Code, Vim, etc.) as if they were on your machine.
- [x] **Role-Based Access Control**: Granular permission management for Admins and Developers.

---

## 🔮 Roadmap & Upcoming Features

We are constantly evolving ENC to make it the standard for secure engineering.

- [ ] **Smart Git Synchronization**: Auto-commit logic that encrypts secrets before pushing to public repos.
- [ ] **VS Code Extension**: Native integration to manage, mount, and edit projects directly from your IDE.
- [ ] **Team Vaults**: Shared encrypted workspaces for secure team collaboration.
- [ ] **Compliance Audit Logs**: Detailed, exportable logs of every access event for enterprise compliance.

---

## 📚 Table of Contents

- [**Installation & Setup**](#-installation--setup)
    - [Server Setup](server/README.md)
    - [Client CLI Setup](enc-cli/README.md)
- [**Quick Start Guide**](#-quick-start)
- [**Documentation**](#-documentation)
- [**Contributing**](#-contributing)
- [**License**](#-license)

---

## 🚀 Installation & Setup

### 1. The Server
You need an ENC Server to host your projects. You can run one on your local machine for testing or deploy it to a remote VPS.
👉 **[Read the Server Setup Guide](server/README.md)**

### 2. The Client
Install the `enc` CLI to communicate with your server.
👉 **[Read the Client Installation Guide](enc-cli/README.md)**

---

## ⚡ Quick Start

Once you have both installed:

1.  **Initialize Configuration**:
    ```bash
    enc config init
    # Follow the prompts to set your Username and Server URL
    ```

2.  **Login**:
    ```bash
    enc login
    ```

3.  **Create a New Project**:
    ```bash
    enc project init my-secret-app
    ```

4.  **Mount & Edit**:
    ```bash
    mkdir ./my-app-edit
    enc project mount my-secret-app ./my-app-edit
    ```
    *Now open `./my-app-edit` in VS Code. All files you write are encrypted instantly on the server.*

5.  **Logout**:
    ```bash
    enc logout
    # Safely unmounts all projects and closes the secure tunnel.
    ```

---

## 📖 Documentation

For more detailed instructions, check the component-specific documentation:

*   **[Server Documentation](server/README.md)**: Deployment, User Management, Architecture.
*   **[Client Documentation](enc-cli/README.md)**: Command Reference, Configuration, SSH Keys.

### 📚 Use Cases

| Use Case | Description | Status | Documentation |
| :--- | :--- | :--- | :--- |
| **Host Your Own Server** | Run your ENC server and access projects securely from anywhere. | ✅ Available | [Guide](https://pranjalab.github.io/enc/use_cases/host_your_own_server.html) |
| **Secure Collaboration** | Provide limited access to interns/contributors without IP leakage. | ✅ Available | [Guide](https://pranjalab.github.io/enc/use_cases/secure_collaboration.html) |
| **Client-Side Deployment** | Execute encrypted projects on client servers using RAM-only decryption. | 🚧 Upcoming | [Guide](https://pranjalab.github.io/enc/use_cases/client_side_secure_deployment.html) |
| **Git Synchronization** | Auto-commit ENC project changes to Git repositories. | 🚧 Upcoming | [Guide](https://pranjalab.github.io/enc/use_cases/git_sync.html) |

### 🌐 Full Documentation

We provide a complete, searchable documentation site built with Sphinx.
**[View Live Documentation](https://pranjalab.github.io/enc/)**

#### Quick Links
*   **[🚀 Quick Start](https://pranjalab.github.io/enc/quick_start.html)**: Get up and running in minutes.
*   **[✨ Features & Roadmap](https://pranjalab.github.io/enc/features.html)**: Learn about our security model and upcoming VS Code integration.
*   **[🤝 Collaboration](https://pranjalab.github.io/enc/collaboration.html)**: Read our origin story and how to contribute.

**Build and Host Locally:**

```bash
cd docs
pip install sphinx sphinx_rtd_theme
make html
# Open the docs:
open docs/_build/html/index.html
```

---

## 🤝 Contributing

We welcome contributions! Whether it's reporting a bug, suggesting a feature, or writing code, your help is appreciated.

1.  **Fork the Project**
2.  **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3.  **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4.  **Push to the Branch** (`git push origin feature/AmazingFeature`)
5.  **Open a Pull Request**

### Contributors

<a href="https://github.com/pranjalab" align="center">
  <img src="https://github.com/pranjalab.png" alt="Pranjal" width="100" height="100" style="border-radius:50%;" />
</a>  
  
**Pranjal Bhaskare** 

### Acknowledgements
Special thanks to the open-source tools that make this possible:
*   [gocryptfs](https://github.com/rfjakob/gocryptfs)
*   [sshfs](https://github.com/libfuse/sshfs)
*   [Rich](https://github.com/Textualize/rich)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
