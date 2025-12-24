# Git Synchronization with ENC Projects

> **Note**: This is an **Upcoming Feature**.

Automate your version control workflow by integrating ENC directly with Git.

## Concept
ENC projects are normally isolated from standard version control because they are encrypted. This feature bridges that gap.

## Workflow (Planned)

### 1. Configuration
Link a Git repository to your ENC project.

```bash
enc config git-remote https://github.com/my-org/my-project.git
```

### 2. Auto-Sync on Unmount
When you finish your work session:

```bash
enc project unmount my-project
```

ENC will optionally:
1. Detect file changes in the decrypted mount.
2. Automatically commit them with a generic or prompted message.
3. Push to the remote repository.

### 3. Encrypted vs Decrypted Push
- **Decrypted Mode**: Pushes plaintext to a private repo (GitHub/GitLab). Useful for team collaboration.
- **Encrypted Mode**: Pushes ciphertext blobs to a public repo. Useful for secure backups on untrusted platforms.
