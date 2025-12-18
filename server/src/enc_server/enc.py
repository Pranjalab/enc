import os
import json
import uuid
import datetime
from pathlib import Path
from rich.console import Console

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
            "active_project": None,
            "access_rights": self._get_access_rights(username) 
        }
        
        session_file = self.session_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=4)
            
        console.print(f"[green]Session created: {session_id}[/green]")
        return session_data

    def _get_access_rights(self, username):
        """Read RBAC from policy.json."""
        policy_file = Path("/etc/enc/policy.json")
        if not policy_file.exists():
            return []
            
        try:
            with open(policy_file, 'r') as f:
                policy = json.load(f)
            
            user_record = policy.get("users", {}).get(username, {})
            if isinstance(user_record, dict):
                return user_record.get("permissions", [])
            elif isinstance(user_record, list): # Legacy
                return user_record
        except Exception as e:
            console.print(f"[red]Error reading policy: {e}[/red]")
            
        return []

    def get_session(self, session_id):
        """Retrieve session data."""
        session_file = self.session_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        with open(session_file, 'r') as f:
            return json.load(f)

    def logout_session(self, session_id):
        """Destroy a session."""
        session_file = self.session_dir / f"{session_id}.json"
        if session_file.exists():
            # In future: trigger unmount/cleanup here
            os.remove(session_file)
            console.print(f"[yellow]Session {session_id} destroyed.[/yellow]")
            return True
        return False

    def create_user(self, username, password, role="user"):
        """Create a system user and update policy."""
        # 1. System User (requires sudo)
        import subprocess
        try:
            # -D = don't set password yet, -s /bin/bash = shell
            # Check existence
            try:
                subprocess.run(["id", username], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                console.print(f"[yellow]User {username} already exists.[/yellow]")
            except subprocess.CalledProcessError:
                subprocess.run(["sudo", "adduser", "-D", "-s", "/bin/bash", username], check=True)
                # Set password
                subprocess.run(f"echo '{username}:{password}' | sudo chpasswd", shell=True, check=True)
                console.print(f"[green]System user {username} created.[/green]")
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
                policy = {"users": {}, "allow_all": []}
            
            if action == "add":
                policy.setdefault("users", {})[username] = {
                    "role": role,
                    "permissions": ["project", "login", "logout"] # Defaults
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
