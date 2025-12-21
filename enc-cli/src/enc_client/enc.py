import os
import json
import subprocess
import sys
import shlex
import socket
import click
import pexpect
from urllib.parse import urlparse
from rich.console import Console

console = Console()

class Enc:
    def __init__(self):
        self.global_dir = os.path.expanduser("~/.enc")
        self.global_config_file = os.path.join(self.global_dir, "config.json")
        
        # Local config relies on current working directory
        self.local_dir = os.path.join(os.getcwd(), ".enc")
        self.local_config_file = os.path.join(self.local_dir, "config.json")
        
        self.config, self.active_config_path = self.load_config()
        self.config_dir = os.path.dirname(self.active_config_path)

    def load_config(self):
        """
        Load configuration with precedence: Local > Global.
        Returns (merged_config_dict, active_config_path_for_writes)
        """
        cfg = {
            "url": "",
            "username": "",
            "ssh_key": "",
            "session_id": None,
            "context": None
        }
        active_path = self.global_config_file

        # 1. Load Global
        if os.path.exists(self.global_config_file):
            try:
                with open(self.global_config_file, 'r') as f:
                    global_cfg = json.load(f)
                    cfg.update(global_cfg)
            except Exception as e:
                console.print(f"[red]Error loading global config: {e}[/red]")

        # 2. Load Local (Override)
        if os.path.exists(self.local_config_file):
            try:
                with open(self.local_config_file, 'r') as f:
                    local_cfg = json.load(f)
                    # Merge logic: meaningful values override (except maybe None/empty?)
                    # For simplicty, simple update() works well for KV pairs.
                    cfg.update(local_cfg)
                    active_path = self.local_config_file
                    # console.print("[dim]Loaded local project configuration.[/dim]")
            except Exception as e:
                console.print(f"[red]Error loading local config: {e}[/red]")
        
        return cfg, active_path

    def save_config(self, cfg, target_path=None):
        """Save config to specific path or default active path."""
        path = target_path if target_path else self.active_config_path
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(cfg, f, indent=4)
        
        # Reload to ensure state consistency
        self.config, self.active_config_path = self.load_config()

    def init_config(self, url, username, ssh_key="", target_path=None):
        """Initialize config at specific location."""
        # Create fresh config dict for init
        new_cfg = {
            "url": url,
            "username": username,
            "ssh_key": ssh_key,
            "session_id": None
        }
        
        # Note: If we are initing a LOCAL config, we might inherit values from global?
        # User request implies "create local use dir for the project".
        # So usually a fresh start or copy. Fresh start is safer for isolation.
        
        save_target = target_path if target_path else self.global_config_file
        self.save_config(new_cfg, save_target)

    def set_config_value(self, key, value):
        """Set value in the ACTIVE configuration scope."""
        # Load the specific file for the active scope to avoid polluting it with merged data
        # actually save_config overwrites. 
        # CAUTION: If we loaded Merged Config, writing it back to Local File might copy Global values into Local file.
        # This is usually acceptable (pinning dependencies), OR we should only write the delta.
        # For this MVP, writing the Full Merged Config to the Active File is easiest and pin-safe.
        
        self.config[key] = value
        self.save_config(self.config, self.active_config_path)

    def get_config_value(self, key):
        return self.config.get(key)
        
    def _parse_url(self):
        """Helper to parse the configured URL."""
        url = self.config.get("url")
        if not url: return None
        
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port
        
        # Handle "host:port" without scheme
        if not host: 
            if "://" not in url:
                if ":" in url:
                    parts = url.split(":")
                    host = parts[0]
                    if len(parts) > 1 and parts[1].isdigit():
                        port = int(parts[1])
                else:
                    host = url
        
        if not host:
            return None
            
        # Fallback port logic
        if not port:
            if parsed.scheme == "https": port = 443
            elif parsed.scheme == "http": port = 80
            else: port = 22 # Default to SSH
            
        return host, port

    def check_connection(self):
        """Checks if the configured URL is available (reachable)."""
        url_parts = self._parse_url()
        if not url_parts:
            console.print("[red]No URL configured or invalid.[/red]")
            return False
            
        host, port = url_parts
        console.print(f"Checking connection to [cyan]{host}:{port}[/cyan]...")
        
        try:
            sock = socket.create_connection((host, int(port)), timeout=5)
            sock.close()
            console.print("[bold green]Connection Successful![/bold green] Host is reachable.")
            return True
        except Exception as e:
            console.print(f"[bold red]Connection Failed:[/bold red] {e}")
            return False

    def get_ssh_base_cmd(self):
        url_parts = self._parse_url()
        username = self.config.get("username")
        ssh_key = self.config.get("ssh_key")
        
        if not url_parts or not username:
             console.print("[red]Not configured global or local config. Run 'enc config init' first.[/red]")
             return None, None
        
        host, port = url_parts
        cmd = ["ssh"]
        if port:
            cmd.extend(["-p", str(port)])
        
        if ssh_key:
            cmd.extend(["-i", ssh_key])
        
        target = f"{username}@{host}"
        return cmd, target

    def get_remote_cmd(self, sub_cmd):
        """Construct a remote command including the session ID if available."""
        session_id = self.config.get("session_id")
        if session_id:
            return f"enc --session-id {session_id} {sub_cmd}"
        return f"enc {sub_cmd}"

    def login(self):
        """Authenticate with the server and establish a session."""
        base, target = self.get_ssh_base_cmd()
        if not base or not target:
             return

        username = self.config.get("username")
        
        # 1. Call server-login to get session
        cmd = list(base)
        # Force pseudo-tty allocation might be issue for JSON parsing if banners exist
        # We prefer NO TTY for machine-readable output usually, but SSH might need it for password prompts.
        # If we need password prompt, we MUST have TTY or use another method (sshpass, or interactive first).
        # Strategy: Run interactive 'enc login' wrapper? 
        # For now, let's assume if key-based, simple run works. 
        # IF password based, subprocess.run capture_output will HANG waiting for password if no TTY.
        
        # PROPOSED HYBRID APPROACH:
        # We need the user to see the password prompt. 
        # But we need to capture the JSON output. 
        # SSH makes this hard. 
        # Option A: Run interactive SSH to a specific "login shell" script.
        # Option B: Expect the user to have keys set up (User guide says keys optional).
        # Option C: Use a temporary file on server? No.
        
        # Let's try to trust `enc check-connection` established trust/fingerprints.
        # If we assume `ssh_key` is set, we are good.
        # If no key, we rely on standard SSH behavior.
        
        # For this step, I will use `subprocess.run`. If it prompts for password, it might fail to capture stdout cleanly mixed with prompts.
        # However, prompts usually go to TTY/stderr.
        
        console.print(f"Authenticating as {username}...")
        
        login_cmd = ["enc", "server-login", username]
        full_ssh_cmd = cmd + [target] + login_cmd
        
        try:
            # Join command for pexpect spawn
            cmd_safe = " ".join([shlex.quote(x) for x in full_ssh_cmd])
            
            # Spawn SSH process
            child = pexpect.spawn(cmd_safe, encoding='utf-8', timeout=30)
            
            # Expect loop for password or host key or EOF
            while True:
                idx = child.expect(["(?i)password:", "(?i)continue connecting", pexpect.EOF, pexpect.TIMEOUT, "(?i)permission denied"])
                
                if idx == 0: # Password prompt
                    password = click.prompt("Enter Server Password", hide_input=True)
                    child.sendline(password)
                elif idx == 1: # Host key verification
                    child.sendline("yes")
                elif idx == 2: # EOF
                    break
                elif idx == 3: # Timeout
                    console.print(f"[red]Connection timed out. Output received so far:[/red]\n{child.before}")
                    child.close()
                    return
                elif idx == 4: # Permission denied
                     console.print(f"[red]Authentication failed:[/red] Permission denied.")
                     child.close()
                     return

            output = child.before
            child.close()
            
            # Clean up output (sometimes SSH adds banner/motd)
            # We look for the JSON object { "session_id": ... }
            import re
            match = re.search(r'\{.*\}', output, re.DOTALL)
            if match:
                json_str = match.group(0)
                try:
                    session_data = json.loads(json_str)
                    
                    if session_data.get("status") == "error":
                         console.print(f"[red]Login Error:[/red] {session_data.get('message')}")
                         return

                    self._save_local_session(session_data)
                    console.print(f"[bold green]Login Success![/bold green] Session ID: {session_data['session_id']}")
                    
                except json.JSONDecodeError:
                     console.print(f"[red]Failed to parse login response:[/red] {output}")
            else:
                 if child.exitstatus != 0:
                     console.print(f"[red]Login failed:[/red] {output.strip()}")
                     console.print("[yellow]Hint: Check username/password or SSH key configuration.[/yellow]")
                 else:
                     console.print(f"[red]No session data received from server.[/red]")
                     console.print(f"Raw Output: {output}")
                     
        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

    def get_current_session(self):
        """Retrieve the current session data from the local file."""
        session_id = self.config.get("session_id")
        if not session_id:
            return None
            
        sessions_dir = os.path.join(self.config_dir, "sessions")
        session_file = os.path.join(sessions_dir, f"{session_id}.json")
        
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def update_current_session(self, key, value):
        """Update a key in the current session file."""
        session_data = self.get_current_session()
        if not session_data:
            return False
            
        session_data[key] = value
        
        # Save back
        session_id = session_data.get("session_id")
        sessions_dir = os.path.join(self.config_dir, "sessions")
        session_file = os.path.join(sessions_dir, f"{session_id}.json")
        
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=4)
            return True
        except Exception as e:
            console.print(f"[red]Error updating session:[/red] {e}")
            return False

    def _save_local_session(self, session_data):
        session_id = session_data.get("session_id")
        sessions_dir = os.path.join(self.config_dir, "sessions")
        os.makedirs(sessions_dir, exist_ok=True)
        
        # Save session file
        with open(os.path.join(sessions_dir, f"{session_id}.json"), 'w') as f:
            json.dump(session_data, f, indent=4)
            
        # Update current config context
        self.config["session_id"] = session_id
        self.save_config(self.config)

    def user_list(self):
        """Get list of users. Checks local cache first, then server."""
        # 1. Get Session
        session = self.get_current_session()
        if not session:
             console.print("[yellow]No active session. Please login.[/yellow]")
             return None
             
        # 2. Check Permissions
        allowed = session.get("allowed_commands", [])
        # We assume 'user list' is the permission key. 
        # If allowed_commands is empty or doesn't contain it, strictly we should deny.
        # BUT for this task, the requirement is "check if its have this 'user list' in allowed commad".
        
        if "user list" not in allowed:
            console.print("[red]Permission Denied: 'user list' not in allowed commands.[/red]")
            return None
            
        # # 3. Check Cache
        # if "user_list" in session:
        #     # console.print("[dim]Returning cached user list.[/dim]")
        #     return session["user_list"]
            
        # 4. Call Server
        # console.print("[dim]Fetching user list from server...[/dim]")
        base, target = self.get_ssh_base_cmd()
        
        # Construct command
        remote_cmd = self.get_remote_cmd("user list --json")
        full_ssh = cmd = list(base) + [target, remote_cmd]
        
        try:
            res = subprocess.run(full_ssh, capture_output=True, text=True)
            if res.returncode == 0:
                # Expecting JSON list of users or object with "users" key
                try:
                    import re
                    match = re.search(r'\{.*\}|\[.*\]', res.stdout, re.DOTALL)
                    if match:
                        json_str = match.group(0)
                        data = json.loads(json_str)
                        
                        # Handle if wrapped in status object or direct list
                        users = data
                        if isinstance(data, dict):
                            if "users" in data:
                                users = data["users"]
                            elif data.get("status") != "success":
                                console.print(f"[red]Server Error:[/red] {data.get('message')}")
                                return None
                                
                        # 5. Update Cache
                        self.update_current_session("user_list", users)
                        return users
                    else:
                        console.print(f"[red]Invalid Server Response:[/red] {res.stdout}")
                except json.JSONDecodeError:
                    console.print(f"[red]Parse Error:[/red] {res.stdout}")
            else:
                 console.print(f"[red]Server Error:[/red] {res.stderr}")
                 
        except Exception as e:
             console.print(f"[red]Error:[/red] {e}")
             
        return None

    def project_init(self, name, password):
        """Call server to init project vault."""
        base, target = self.get_ssh_base_cmd()
        # To avoid showing password in process list, we must pipe it.
        # ssh user@host "enc server-project-init name --password password"
        # Since I used 'prompt=True' on server, I must pipe input.
        
        cmd = list(base)
        # Construct command
        remote_cmd = self.get_remote_cmd(f"server-project-init {name}")
        full_ssh = cmd + [target, remote_cmd]
        
        try:
            # Popen to write to stdin
            proc = subprocess.Popen(full_ssh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input=f"{password}\n")
            
            if proc.returncode != 0:
                console.print(f"[red]Init Failed:[/red] {stderr}")
                return False
                
            # Parse JSON from stdout
            try:
                import json
                # Grep for JSON block if noise exists
                import re
                match = re.search(r'\{.*\}', stdout, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    if data.get("status") == "success":
                         return True
                    else:
                         console.print(f"[red]Server Error:[/red] {data.get('message')}")
                else:
                    console.print(f"[red]Invalid Response:[/red] {stdout}")
            except Exception as e:
                console.print(f"[red]Parse Error:[/red] {e}")
                
            return False
            
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            return False

    def project_mount(self, name, password):
        """Call server to mount project."""
        base, target = self.get_ssh_base_cmd()
        
        cmd = list(base)
        remote_cmd = self.get_remote_cmd(f"server-project-mount {name}")
        full_ssh = cmd + [target, remote_cmd]
        
        try:
            proc = subprocess.Popen(full_ssh, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input=f"{password}\n")
            
            if proc.returncode != 0:
                console.print(f"[red]Mount Failed:[/red] {stderr}")
                return False

            try:
                import json
                import re
                match = re.search(r'\{.*\}', stdout, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    if data.get("status") == "success":
                         return True
            except:
                pass
            return False
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            return False

    def project_unmount(self, name):
        """Call server to unmount project."""
        base, target = self.get_ssh_base_cmd()
        remote_cmd = self.get_remote_cmd(f"server-project-unmount {name}")
        cmd = list(base) + [target, remote_cmd]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                return True
            return False
        except Exception:
            return False

    def project_sync(self, name, local_path):
        """Sync files using rsync over SSH."""
        base, target = self.get_ssh_base_cmd()
        username = self.config.get("username")
        url_parts = self._parse_url()
        if not url_parts: 
            return False
            
        host, port = url_parts
        
        # Remote path: ~/.enc/run/master/<project>/
        remote_path = f"~/.enc/run/master/{name}/"
        
        # Construct rsync command
        # rsync -avz -e "ssh -p port" local_path user@host:remote_path
        
        # We need absolute local path
        local_path = os.path.abspath(local_path)
        if not local_path.endswith("/"):
             local_path += "/" # Ensure rsync copies CONTENTS, not folder itself if desired. 
                               # Usually 'src/' -> 'dest/'
        
        # Build SSH options string for -e
        ssh_opts = f"ssh -p {port}"
        # Incorporate ssh_key if present
        ssh_key = self.config.get("ssh_key")
        if ssh_key:
             ssh_opts += f" -i {ssh_key}"
        
        # Add strict host key checking off for convenience/test?
        # Maybe: -o StrictHostKeyChecking=no
        if not ssh_key:
             # If using password/default keys, standard ssh behavior.
             pass
        else:
             # Ensure key usage
             ssh_opts += f" -o StrictHostKeyChecking=no"
        
        cmd = [
            "rsync",
            "-avz",
            "-e", ssh_opts,
            local_path,
            f"{username}@{host}:{remote_path}"
        ]
        
        try:
            # We use subprocess.call to allow streaming output to console
            ret = subprocess.call(cmd)
            if ret == 0:
                # Log success to server
                sync_remote = self.get_remote_cmd(f"server-project-sync {name} 'rsync sync completed successfully'")
                subprocess.run(list(base) + [target, sync_remote], capture_output=True)
            return ret == 0
        except Exception as e:
            console.print(f"[red]Sync Error:[/red] {e}")
            return False

    def project_run(self, name, command_str):
        """Execute a command in the remote project directory via server-project-run for logging."""
        base, target = self.get_ssh_base_cmd()
        
        # We use shlex.quote to handle complex commands
        import shlex
        quoted_cmd = shlex.quote(command_str)
        
        remote_cmd = self.get_remote_cmd(f"server-project-run {name} {quoted_cmd}")
        
        cmd = list(base)
        # Use -t for potential interactivity, though server-project-run currently uses subprocess.run
        full_ssh = cmd + ["-t", target, remote_cmd]
        
        try:
            ret = subprocess.call(full_ssh)
            return ret == 0
        except Exception as e:
            console.print(f"[red]Execution Error:[/red] {e}")
            return False

    def logout(self):
        """Clear local session state."""
        # Optional: Call server-logout to invalidate on server side too?
        # Yes, good practice.
        base, target = self.get_ssh_base_cmd()
        username = self.config.get("username")
        
        if base and target and username:
            try:
                remote_cmd = self.get_remote_cmd(f"server-logout {username}")
                logout_cmd = list(base) + [target, remote_cmd]
                subprocess.run(logout_cmd, capture_output=True)
            except: 
                pass # Ignore network errors during logout
        
        # Clear local
        sessions_dir = os.path.join(self.config_dir, "sessions")
        try:
            import glob
            files = glob.glob(os.path.join(sessions_dir, "*.json"))
            for f in files:
                os.remove(f)
            
            self.config["session_id"] = None
            self.save_config(self.config)
            return True
        except Exception as e:
            console.print(f"[red]Error clearing sessions:[/red] {e}")
            return False

    def user_create(self, username, password, role, ssh_key=None):
        """Call enc user create."""
        base, target = self.get_ssh_base_cmd()
        
        # New standardized command
        remote_cmd_str = f"user create {username} --password {password} --role {role} --json"
        
        if ssh_key:
             remote_cmd_str += f' --ssh-key "{ssh_key}"'
             
        cmd = list(base) + [
            target, 
            self.get_remote_cmd(remote_cmd_str)
        ]
        
        try:
            # We assume current session user is admin
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and "success" in res.stdout:
                return True
            else:
                console.print(f"[red]Server Error:[/red] {res.stdout} {res.stderr}")
                return False
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            return False

    def user_delete(self, username):
        """Call enc user remove."""
        base, target = self.get_ssh_base_cmd()
        # New standardized command
        cmd = list(base) + [
            target, 
            self.get_remote_cmd(f"user remove {username} --json")
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and "success" in res.stdout:
                return True
            else:
                 console.print(f"[red]Server Error:[/red] {res.stdout} {res.stderr}")
                 return False
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            return False
