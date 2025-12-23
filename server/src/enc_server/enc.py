import os
import json
import uuid
import datetime
import subprocess
from pathlib import Path
from rich.console import Console
from enc_server.authentications import Authentication
from enc_server.session import Session

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
        self.session = Session()
            
    def load_config(self):
        # Placeholder for Global Server Config (if distinct from policy.json)
        # Using /etc/enc/policy.json for RBAC usually.
        pass

    def create_session(self, username):
        """Create a new session ID and file for the user."""
        return self.session.create_session(username, self.auth)

    def get_session(self, session_id):
        """Retrieve session data."""
        return self.session.get_session(session_id)

    def log_command(self, session_id, command, output):
        """Log a command and its output to the session file."""
        return self.session.log_command(session_id, command, output)

    def logout_session(self, session_id):
        """Destroy a session."""
        return self.session.logout_session(session_id)

    def project_init(self, project_name, password, session_id, project_dir):
        """Initialize encrypted project vault and manage session/access."""
        session_data = self.session.get_session(session_id)
        if not session_id or not session_data or not self.session.check_session_id(session_id):
            console.print("[bold red]Session Error:[/bold red] Invalid or expired session.")
            return False, {"status": "error", "message": "Invalid or expired session"}
            
        username = session_data.get("username")

        from enc_server.gocryptfs_handler import GocryptfsHandler
        handler = GocryptfsHandler()
        
        # Check if project exists first
        if (handler.vault_root / project_name).exists():
             return False, {"status": "error", "message": f"Project '{project_name}' already exists on the server."}

        success = handler.init_project(project_name, password)

        if success:
            self.session.start_session_monitoring()

            # Construct paths (matching GocryptfsHandler defaults)
            vault_path = f"/home/{username}/.enc/vault/master/{project_name}"
            mount_point = f"/home/{username}/.enc/run/master/{project_name}"
            
            metadata = {
                "mount_path": mount_point,
                "vault_path": vault_path,
                "exec": None
            }

            # Add project to user's list with metadata
            self.auth.add_user_project(username, project_name, metadata=metadata)
            return True, {"status": "success", "project": project_name, "mount_point": mount_point}
        else:
            return False, {"status": "error", "message": "Failed to init project"}

    def project_list(self, session_id):
        """Get the list of projects and their metadata for the current user."""
        session_data = self.session.get_session(session_id)
        if not session_id or not session_data or not self.session.check_session_id(session_id):
            return False, {"status": "error", "message": "Invalid or expired session"}
            
        username = session_data.get("username")
        raw_projects = self.auth.get_user_project_metadata(username)
        
        # Filter out sensitive vault_path from the response
        filtered_projects = {}
        for name, meta in raw_projects.items():
            filtered_projects[name] = {
                "mount_path": meta.get("mount_path"),
                "exec": meta.get("exec")
            }
        
        return True, {"status": "success", "projects": filtered_projects}

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

    def delete_project(self, project_name, session_id):
        """Remove a project from the system (files and policy)."""
        import shutil
        
        # 1. Identify User from Session
        username = self.get_username_from_session(session_id)
        if not username:
             return {"status": "error", "message": "Invalid Session"}

        # 2. Check Access/Ownership
        # Explicit admin check OR ownership check.
        # Currently policy stores projects under users.
        # If user is admin, they can delete any project IF we passed target user.
        # BUT for now, let's assume user deletes THEIR project.
        # Admin deletion of other's projects requires different args (target_user).
        
        # For this iteration: User deletes their OWN project.
        if not self.auth.has_project_access(username, project_name):
             return {"status": "error", "message": "Access Denied"}

        # 3. Unmount if mounted
        try:
             # Check if mounted by trying to unmount or check mount result
             from enc_server.gocryptfs_handler import GocryptfsHandler
             handler = GocryptfsHandler()
             # We blindly attempt unmount; if not mounted it fails gracefully or we ignore
             handler.unmount_project(project_name)
        except Exception:
             pass 

        # 4. Remove Files
        try:
            vault_path = os.path.expanduser(f"~/.enc/vault/master/{project_name}")
            run_path = os.path.expanduser(f"~/.enc/run/master/{project_name}")
            
            if os.path.exists(vault_path):
                shutil.rmtree(vault_path)
            
            if os.path.exists(run_path):
                shutil.rmtree(run_path)
                
        except Exception as e:
            return {"status": "error", "message": f"File deletion failed: {e}"}

        # 5. Update Policy
        self.auth.remove_user_project(username, project_name)

        return {"status": "success", "message": f"Project {project_name} deleted."}

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
