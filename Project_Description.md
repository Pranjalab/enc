ENC — Secure, Memory-Only Encryption for Code Execution

What is ENC?

ENC is a developer-first encryption layer that protects your source code at rest, during execution, and across sessions.

Traditional deployments store source code as plain text on disk—whether on local machines, servers, containers, or CI systems. Even with OS permissions and access controls, decrypted code often remains readable on disk, leaving it vulnerable to leaks, misconfiguration, insider access, or forensic recovery.

ENC eliminates this risk by keeping your code encrypted at rest and decrypting it only in memory, strictly for the duration of an authenticated session.

Once your ENC session ends—by logout, terminal close, SSH disconnect, or container exit—your code is automatically re-encrypted and never left behind in plain text.

⸻

Why ENC Exists

Modern development environments face several unavoidable realities:
	•	Servers are shared
	•	Containers are ephemeral but inspectable
	•	Build pipelines touch sensitive code
	•	SSH access is often broader than intended
	•	Plain-text source files are easy to copy, snapshot, or leak

ENC addresses these risks without changing how developers work.

You still use:
	•	Your terminal
	•	Your editor
	•	Your deployment workflows

But underneath, ENC ensures your source code is:
	•	Unreadable when not in use
	•	Never written to disk in decrypted form
	•	Automatically secured when your session ends

⸻

Core Design Philosophy

ENC is built on a few strict principles:
	•	CLI-first: no background daemons, no hidden services
	•	Memory-only execution: decrypted code never touches disk
	•	Explicit sessions: security state is always visible
	•	Auto-locking: no reliance on user discipline
	•	Minimal trust: assume servers, containers, and pipelines are not fully trusted

⸻

Key Advantages

🔐 Encrypted at Rest

All project files are stored in encrypted form. Even if someone gains filesystem access, the contents remain unreadable without the correct keys.

🧠 Memory-Only Decryption

Code is decrypted only in RAM, executed directly from memory, and never written as plain text files.

This protects against:
	•	Disk inspection
	•	Snapshots and backups
	•	Container layer inspection
	•	Accidental commits or copies

🚪 Session-Based Security

ENC introduces explicit security sessions:
	•	Master login (enc login)
	•	Per-project access (enc <project-name>)
	•	Automatic re-encryption on logout or terminal close

You always know your security state from the terminal prompt.

⚡ Zero Workflow Disruption

ENC integrates into your existing workflow:
	•	Works with normal terminals
	•	Compatible with Docker and SSH
	•	No custom editors required
	•	No vendor lock-in

🧩 Modular & Extensible

ENC is designed to grow:
	•	Local development today
	•	Secure server-side collaboration tomorrow
	•	Editor integrations (VS Code) next
	•	Team-based encrypted workflows later

⸻

Safety & Security Model

What ENC Protects Against

ENC is designed to protect your code from:
	•	Unauthorized filesystem access
	•	Accidental plaintext persistence
	•	Container inspection
	•	Shared server risks
	•	Session leftovers after logout
	•	Snapshot and backup leakage
	•	Insider access without keys

What ENC Does Not Claim

ENC is intentionally honest about its limits. It does not protect against:
	•	A fully compromised kernel
	•	Active memory dumping during an unlocked session
	•	Malicious code executed within your ENC session
	•	Hardware-level attacks

ENC focuses on practical, real-world protection, not theoretical absolutes.

⸻

Key Safety Guarantees

✔ Decrypted code is never written to disk
✔ All encrypted data uses strong, modern cryptography
✔ Keys are derived using password-hardening algorithms
✔ Sessions auto-lock on exit or interruption
✔ No background services silently holding secrets
✔ No plaintext leftovers after use

⸻

Visibility Through the Terminal

ENC makes security state visible by design.

Your prompt reflects exactly where you are:

(base) user@server:~/projects
[enc] (base) user@server:~/projects
[project_name] (base) user@server:~/projects

This ensures you always know:
	•	Whether ENC is active
	•	Whether a project is unlocked
	•	When your code is exposed in memory

⸻

Who ENC Is For

ENC is ideal for:
	•	Developers deploying sensitive IP
	•	Teams working on shared servers
	•	Secure CI/CD environments
	•	Cloud and container workloads
	•	Anyone who wants stronger guarantees than file permissions

⸻

The Road Ahead

ENC is an evolving project. Upcoming work includes:
	•	Secure multi-user server collaboration
	•	Encrypted remote execution via SSH
	•	VS Code integration with auto-locking
	•	Team-level project access controls

ENC is designed to be community-driven, auditable, and extensible.

⸻

In One Sentence

ENC keeps your code encrypted everywhere, decrypted nowhere—except in memory, only when you explicitly allow it.

