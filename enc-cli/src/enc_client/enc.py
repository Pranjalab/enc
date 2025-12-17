import os
import json
import subprocess
import sys
import shlex
import socket
from urllib.parse import urlparse
from rich.console import Console

console = Console()

class Enc:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.enc")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            return {
                "url": "",
                "username": "",
                "ssh_key": "",
                "session_id": None,
                "context": None
            }
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            return {}

    def save_config(self, cfg):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(cfg, f, indent=4)
        self.config = cfg

    def init_config(self, url, username, ssh_key=""):
        # preserve existing session/context if re-initing? 
        # Usually init wipes clean or just updates fields. Let's update fields.
        self.config["url"] = url
        self.config["username"] = username
        self.config["ssh_key"] = ssh_key
        # Ensure others exist
        if "session_id" not in self.config:
            self.config["session_id"] = None
        if "context" not in self.config:
            self.config["context"] = None
            
        self.save_config(self.config)

    def set_config_value(self, key, value):
        if key not in self.config:
            # Maybe allow setting custom keys, but warn?
            # User requirement implies specific keys.
            pass
        self.config[key] = value
        self.save_config(self.config)

    def get_config_value(self, key):
        return self.config.get(key)
        
    def check_connection(self):
        """Checks if the configured URL is available (reachable)."""
        url = self.config.get("url")
        if not url:
            console.print("[red]No URL configured.[/red]")
            return False

        try:
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
            
            # Fallback port logic
            if not port:
                if parsed.scheme == "https": port = 443
                elif parsed.scheme == "http": port = 80
                else: port = 22 # Default to SSH-like check if not specified
            
            console.print(f"Checking connection to [cyan]{host}:{port}[/cyan]...")
            
            sock = socket.create_connection((host, int(port)), timeout=5)
            sock.close()
            console.print("[bold green]Connection Successful![/bold green] Host is reachable.")
            return True
        except Exception as e:
            console.print(f"[bold red]Connection Failed:[/bold red] {e}")
            return False

    def get_ssh_base_cmd(self):
        url = self.config.get("url")
        username = self.config.get("username")
        ssh_key = self.config.get("ssh_key")
        
        if not url or not username:
             console.print("[red]Not configured. Run 'enc config init' first.[/red]")
             return None, None

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
            console.print(f"[red]Could not parse hostname from URL: {url}[/red]")
            return None, None
            
        cmd = ["ssh"]
        
        if port:
            cmd.extend(["-p", str(port)])
        
        if ssh_key:
            cmd.extend(["-i", ssh_key])
        
        target = f"{username}@{host}"
        
        return cmd, target

    def login(self):
        """Test connection/login workflow."""
        base, target = self.get_ssh_base_cmd()
        if not base or not target:
             return

        # We just want to check connection. 'enc status' is available on server.
        cmd = list(base)
        
        # Force strict checking off for localhost dev/docker envs usually, 
        # but for security tool maybe we like it? 
        # User didn't ask, but it's annoying in docker. 
        # I'll enable checking by default (standard SSH behavior).
        
        # Interactive mode: force PTY to ensure prompts appear nicely if needed
        # cmd.append("-t") 
        # actually for single command execution, prompt might appear on stderr.
        # Removing -t might handle password prompt better if it's not a shell.
        
        cmd.append(target)
        cmd.append("enc status") 
        
        console.print(f"Logging in to {target}...")
        try:
            # allow_interaction=True essentially
            ret = subprocess.call(cmd) 
            if ret == 0:
                console.print("[bold green]Success![/bold green] Login verified.")
            else:
                 console.print(f"[bold red]Login Failed (Exit Code: {ret})[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

    def run_remote(self, base_cmd, args):
        """Forward a command to the remote server."""
        base, target = self.get_ssh_base_cmd()
        if not base or not target:
             return
             
        cmd = list(base)
        
        # Only force PTY if we are interactive (fixes automation issues)
        if sys.stdout.isatty():
            cmd.append("-t")
        
        cmd.append(target)
        
        # Construct remote command: 'enc <base_cmd> <args>'
        remote_cmd = ["enc", base_cmd] + list(args)
        
        # Pass it TO ssh as a quoted command string
        full_remote_str = " ".join(shlex.quote(a) for a in remote_cmd)
        cmd.append(full_remote_str)
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass
