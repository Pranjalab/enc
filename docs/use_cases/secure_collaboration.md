# Secure Collaboration with Interns or Contributors

Provide limited, secure access to your intellectual property without risking data theft.

## The Problem
When you hire interns or contractors, you often have to give them access to your codebase. If they copy the code to a USB drive or upload it to their personal cloud, your IP is compromised.

## The ENC Solution
With ENC, contributors work in a "Zero-Trust" environment.
1. The code resides on your encrypted server.
2. It is decrypted seamlessly on their machine **only in memory** (RAM).
3. Once they unmount (or if you revoke access), the decrypted text vanishes. The files on their disk are useless encryption blobs.

## Workflow

### 1. Admin Setup
As the admin, you create a user account for your intern on your hosted ENC server.

```bash
# On the server
docker exec -it enc-server enc user create intern-alice --role user
```

### 2. Contributor Self-Onboarding
The intern installs the ENC CLI and logs in with the password you provided. They then secure their own access.

```bash
# Intern's Machine
enc login
enc setup ssh-key
```

**Security Benefit**: You (the admin) never need to see, touch, or manage their private SSH keys. The system handles the handshake securely.

### 3. Access Control
You can create a project specifically for them or add them to an existing one.

```bash
# Create a project
enc project init new-feature-module
```

*(Currently, ENC supports user-owned projects. Shared project collaboration is on the roadmap.)*

### 4. Revocation
When the internship ends, you simply remove their user from the server or revoke their key.

```bash
docker exec -it enc-server enc user remove intern-alice
```

They instantly lose access. Any encrypted files they might have copied are mathematically impossible to open without the server's master key and their valid session.
