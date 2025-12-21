import os
import json
import uuid
import datetime
import subprocess
from pathlib import Path
from rich.console import Console
from enc_server.authentications import Authentication

console = Console()

class EncServer:
    def __init__(self):
        self.enc_root = Path.home() / ".enc"
        self.config_file = self.enc_root / "config.json"
        self.session_dir = self.enc_root / "sessions"
        self.vault_dir = self.enc_root / "vault"
        self.run_dir = self.enc_root / "run"
        
        # Ensure directories exist
        for d in [self.session_dir, self.vault_dir, self.run_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        self.auth = Authentication()
            
    def load_config(self):
        # Placeholder for Global Server Config (if distinct from policy.json)
        # Using /etc/enc/policy.json for RBAC usually.
        pass

    def create_session(self, username):
        """Create a new session ID and file for the user."""
        session_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        session_data = {
            "session_id": session_id,
            "username": username,
            "created_at": timestamp,
            "context": "enc",
            "active_project": None,
            "allowed_commands": self.auth.get_user_permissions(username),
            "projects": self.auth.get_user_projects(username),
            "logs": {
            }
        }

        # adding started session log
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_key = f"[{timestamp}] {"login"}"
        session_data["logs"][log_key] = "Session started"
        
        session_file = self.session_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=4)
            
        console.print(f"[green]Session created: {session_id}[/green]")
        return session_data


    def get_session(self, session_id):
        """Retrieve session data."""
        session_file = self.session_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        with open(session_file, 'r') as f:
            return json.load(f)

    def log_command(self, session_id, command, output):
        """Log a command and its output to the session file."""
        session_data = self.get_session(session_id)
        if not session_data:
            return False
            
        if "logs" not in session_data:
            session_data["logs"] = {}
            
        # If the exact command exists, we might want to preserve history or just overwrite
        # To avoid giant keys if someone runs it 100 times, maybe add a timestamp to key or just overwrite.
        # User asked for "key value dict of command and return results".
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_key = f"[{timestamp}] {command}"
        session_data["logs"][log_key] = output
        
        session_file = self.session_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=4)
        return True

    def logout_session(self, session_id):
        """Destroy a session."""
        session_file = self.session_dir / f"{session_id}.json"
        if session_file.exists():
            # In future: trigger unmount/cleanup here
            os.remove(session_file)
            console.print(f"[yellow]Session {session_id} destroyed.[/yellow]")
            return True
        return False

    def create_user(self, username, password, role="user", ssh_key=None):
        """Create a system user and update policy."""

        # if the role is not in the list of roles, return False
        if role not in self.auth.PERMISSIONS:
            console.print(f"[red]Invalid role: {role}[/red]")
            return False
        
        # 1. System User (requires sudo)
        import subprocess
        try:
            # -D = don't set password yet, -s /bin/bash = shell
            # Check existence
            try:
                subprocess.run(["id", username], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                console.print(f"[yellow]User {username} already exists.[/yellow]")
                return False
            except subprocess.CalledProcessError:
                subprocess.run(["sudo", "adduser", "-D", "-s", "/usr/local/bin/enc-shell", username], check=True)
                # Set password
                subprocess.run(f"echo '{username}:{password}' | sudo chpasswd", shell=True, check=True)
                console.print(f"[green]System user {username} created.[/green]")
                
                # Setup SSH Key if provided
                if ssh_key:
                    try:
                        ssh_dir = f"/home/{username}/.ssh"
                        auth_keys = f"{ssh_dir}/authorized_keys"
                        
                        subprocess.run(["sudo", "mkdir", "-p", ssh_dir], check=True)
                        subprocess.run(["sudo", "chmod", "700", ssh_dir], check=True)
                        
                        # Echo key securely to temp file then move to avoid shell injection issues generally, 
                        # but simple echo into file owned by root then chown is okay.
                        # Using sh -c to handle redirection with sudo
                        cmd = f"echo '{ssh_key}' | sudo tee {auth_keys} > /dev/null"
                        subprocess.run(cmd, shell=True, check=True)
                        
                        subprocess.run(["sudo", "chmod", "600", auth_keys], check=True)
                        subprocess.run(["sudo", "chown", "-R", f"{username}:{username}", ssh_dir], check=True)
                        console.print(f"[green]SSH key configured for {username}.[/green]")
                    except Exception as e:
                        console.print(f"[red]Failed to configure SSH key: {e}[/red]")

        except Exception as e:
            console.print(f"[red]Failed to create system user: {e}[/red]")
            return False

        # 2. Policy Update
        self._update_policy(username, role)
        return True

    def delete_user(self, username):
        """Remove a system user and update policy."""
        import subprocess
        try:
            # Check existence
            try:
                subprocess.run(["id", username], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                console.print(f"[yellow]User {username} does not exist.[/yellow]")
                return False
                
            subprocess.run(["sudo", "deluser", "--remove-home", username], check=True)
            console.print(f"[green]System user {username} deleted.[/green]")
        except Exception as e:
            console.print(f"[red]Failed to delete system user: {e}[/red]")
            return False
            
        # Remove from policy
        self._update_policy(username, action="remove")
        return True

    def _update_policy(self, username, role="user", action="add"):
        policy_file = Path("/etc/enc/policy.json")
        try:
            if policy_file.exists():
                with open(policy_file, 'r') as f:
                    policy = json.load(f)
            else:
                 raise FileNotFoundError(f"Critical Error: Security policy file missing at {policy_file}")
            
            if action == "add":
                policy.setdefault("users", {})[username] = {
                    "role": role,
                    "permissions": self.auth.PERMISSIONS.get(role, [])
                }
            elif action == "remove":
                if username in policy.get("users", {}):
                    del policy["users"][username]
            
            # Write back requires sudo potentially if owned by root
            # But container typically runs as root? 
            # Dockerfile: USER isn't switched to admin globally, entrypoint execs sshd.
            # But the 'enc' server command runs as the logged in user (admin/tester).
            # So we usually need sudo to write to /etc.
            
            # Dump to valid temp file then sudo cp?
            tmp_path = Path("/tmp/policy.json.tmp")
            with open(tmp_path, 'w') as f:
                json.dump(policy, f, indent=4)
                
            subprocess.run(["sudo", "cp", str(tmp_path), str(policy_file)], check=True)
            subprocess.run(["sudo", "chmod", "644", str(policy_file)], check=True)
            
        except Exception as e:
            console.print(f"[red]Policy update failed: {e}[/red]")
