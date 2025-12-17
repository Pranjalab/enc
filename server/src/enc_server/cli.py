import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from enc_server.config import get_enc_dir, load_config, save_config, get_server_url
import requests

console = Console()

@click.group()
def cli():
    """ENC — Secure, Memory-Only Encryption for Code Execution"""
    # Ensure config dir exists on any command
    get_enc_dir()

def check_server_permission(ctx):
    """Check permissions if running in Server Mode."""
    import os
    import json
    import getpass
    
    if os.environ.get("ENC_MODE") != "SERVER":
        return

    # In Server Mode, we check local policy
    user = getpass.getuser()
    cmd_name = ctx.command.name
    
    # Defaults
    policy_file = "/etc/enc/policy.json"
    allowed = False
    
    if user == "admin":
        allowed = True
    elif os.path.exists(policy_file):
        try:
            with open(policy_file, 'r') as f:
                policy = json.load(f)
            
            # Retrieve user record. Could be list (old schema) or dict (new schema)
            user_record = policy.get("users", {}).get(user)
            
            if cmd_name in policy.get("allow_all", []):
                allowed = True
            elif user_record:
                # Handle Dict (New Schema)
                if isinstance(user_record, dict):
                    permissions = user_record.get("permissions", [])
                    role = user_record.get("role", "user")
                    
                    # Admins allow everything
                    if role == "admin":
                        allowed = True
                    elif cmd_name in permissions:
                        allowed = True
                
                # Handle List (Old Schema Compatibility)
                elif isinstance(user_record, list):
                    if cmd_name in user_record:
                        allowed = True
                        
        except Exception:
            pass # Fail safe -> allowed=False

    if not allowed:
        console.print(f"[bold red]Access Denied:[/bold red] User '{user}' is not allowed to run '{cmd_name}'.")
        ctx.exit(1)

def ensure_admin(ctx):
    """Explicitly check if current user is admin."""
    import getpass
    import os
    import json
    
    if os.environ.get("ENC_MODE") != "SERVER":
        return

    user = getpass.getuser()
    if user == "admin":
        return

    # Check policy for admin role
    try:
        with open("/etc/enc/policy.json", 'r') as f:
            policy = json.load(f)
        record = policy.get("users", {}).get(user)
        if isinstance(record, dict) and record.get("role") == "admin":
            return
    except:
        pass
        
    console.print(f"[bold red]Permission Error:[/bold red] Only admins can perform this action.")
    ctx.exit(1)

@click.group()
def cli():
    """ENC — Secure, Memory-Only Encryption for Code Execution"""
    # Ensure config dir exists on any command
    get_enc_dir()

@cli.group()
def config():
    """Manage ENC configuration."""
    pass

@config.command("set-server")
@click.argument("url")
def set_server(url):
    """Set the ENC Server URL."""
    cfg = load_config()
    cfg["server_url"] = url
    save_config(cfg)
    console.print(f"[bold green]Success:[/bold green] Server URL set to {url}")

@config.command("get-server")
def get_server():
    """Get the current ENC Server URL."""
    url = get_server_url()
    console.print(f"Current Server URL: [bold blue]{url}[/bold blue]")

@cli.command()
def login():
    """Authenticate with the ENC Server."""
    server_url = get_server_url()
    console.print(f"Connecting to ENC Server at: [bold blue]{server_url}[/bold blue]")
    
    # 1. Attempt connection / Check for SSH Keys (Stub for logic)
    # For now, we fall back to password auth directly
    
    username = Prompt.ask("Username")
    password = Prompt.ask("Password", password=True)
    
    try:
        # Assuming server has /users/login endpoint
        # NOTE: In real world, we'd exchange keys or get a token.
        # This matches the 'basic User Model' we built.
        resp = requests.post(f"{server_url}/users/login", json={"username": username, "password": password})
        
        if resp.status_code == 200:
            console.print(Panel(f"Login successful as {username}", title="ENC Login", style="bold green"))
            # Initializing local session state...
            from enc_server.session.session import current_session
            # Stub: we use password as key material for local master key unlocking
            # In a real flow, we'd fetch the user's encrypted master key from the server
            # and unlock it here.
        else:
            console.print(f"[bold red]Login Failed:[/bold red] {resp.text}")
            
    except Exception as e:
        console.print(f"[bold red]Connection Error:[/bold red] {e}")

@cli.command()
def logout():
    """Logout and clear all session secrets from memory."""
    from enc_server.session.session import current_session
    current_session.logout()
    console.print("[bold green]Logged out.[/bold green] Secrets cleared from memory.")

@cli.command()
@click.pass_context
def init(ctx):
    check_server_permission(ctx)
    """Initialize a new ENC project in the current directory."""
    from enc_server.projects.init import init_project
    init_project()

@cli.command()
@click.argument('project_name')
@click.pass_context
def project(ctx, project_name):
    check_server_permission(ctx)
    """Activate a specific project."""
    console.print(f"[bold yellow]Activating project:[/bold yellow] {project_name}")

@cli.command()
def deactivate():
    """Deactivate the current session and lock everything."""
    console.print("[bold red]Deactivating session...[/bold red]")

@cli.group()
def user():
    """Manage ENC users."""
    pass

@user.command("add")
@click.argument("username")
@click.pass_context
def add_user(ctx, username):
    """Add a new restricted user."""
    # Check if admin permission is available (either running as root/admin or permitted)
    check_server_permission(ctx)
    ensure_admin(ctx)
    
    import subprocess
    import json
    import os

    console.print(f"[bold]Creating user: {username}[/bold]")
    password = Prompt.ask("Password (leave empty for key-only)", password=True, default="")
    ssh_key = Prompt.ask("SSH Public Key (optional)", default="")

    try:
        # 1. Create System User
        shell_path = "/usr/local/bin/enc-shell"
        subprocess.run(["sudo", "adduser", "-D", "-s", shell_path, username], check=True)
        
        # 2. Set Password
        if password:
            proc = subprocess.Popen(["sudo", "chpasswd"], stdin=subprocess.PIPE)
            proc.communicate(input=f"{username}:{password}".encode())
            if proc.returncode != 0:
                raise Exception("Failed to set password")
        else:
            subprocess.run(["sudo", "passwd", "-l", username], check=False)

        # 3. Setup SSH
        user_home = f"/home/{username}"
        ssh_dir = f"{user_home}/.ssh"
        subprocess.run(["sudo", "mkdir", "-p", ssh_dir], check=True)
        
        if ssh_key:
            auth_file = f"{ssh_dir}/authorized_keys"
            # Write key using tee to handle sudo write
            proc = subprocess.Popen(["sudo", "tee", "-a", auth_file], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
            proc.communicate(input=f"{ssh_key}\n".encode())
            
        # Fix permissions
        subprocess.run(["sudo", "chown", "-R", f"{username}:{username}", user_home], check=True)
        subprocess.run(["sudo", "chmod", "700", ssh_dir], check=True)
        if ssh_key:
            subprocess.run(["sudo", "chmod", "600", f"{ssh_dir}/authorized_keys"], check=True)
            
        # 4. Update Policy
        policy_file = "/etc/enc/policy.json"
        
        # We need to read/write policy. Since we might not own it, we use sudo cat/tee logic
        # But this script runs primarily as 'admin' who has NOPASSWD sudo.
        # Python's open() might fail if not root, so we use sudo.
        
        current_policy = {"allow_all": [], "users": {}}
        if os.path.exists(policy_file):
            try:
                # Read using cat
                res = subprocess.run(["sudo", "cat", policy_file], capture_output=True, text=True)
                if res.returncode == 0:
                    current_policy = json.loads(res.stdout)
            except:
                pass

        # Add user with default permissions if not present
    # Persist with new schema
        if username not in current_policy.get("users", {}):
            if "users" not in current_policy:
                current_policy["users"] = {}
            
            # Default to 'user' role
            current_policy["users"][username] = {
                "role": "user",
                "permissions": ["init", "project", "status"]
            }
            
            # Write back
            policy_json = json.dumps(current_policy, indent=4)
            proc = subprocess.Popen(["sudo", "tee", policy_file], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
            proc.communicate(input=policy_json.encode())

        console.print(f"[bold green]Success:[/bold green] User '{username}' created.")

    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error:[/bold red] System command failed: {e}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@user.command("list")
@click.pass_context
def list_users(ctx):
    """List all managed users."""
    check_server_permission(ctx)
    from rich.table import Table
    import json
    import subprocess
    import os

    try:
        policy_file = "/etc/enc/policy.json"
        
        # Read policy logic
        policy = {"users": {}}
        if os.path.exists(policy_file):
             # Try sudo cat if needed, else normal read
             try:
                 with open(policy_file, 'r') as f:
                     policy = json.load(f)
             except PermissionError:
                  res = subprocess.run(["sudo", "cat", policy_file], capture_output=True, text=True)
                  if res.returncode == 0:
                      policy = json.loads(res.stdout)

        table = Table(title="ENC Users")
        table.add_column("Username", style="cyan")
        table.add_column("Role", style="magenta")
        table.add_column("Permissions")

        for user, record in policy.get("users", {}).items():
            if isinstance(record, dict):
                role = record.get("role", "user")
                perms = ", ".join(record.get("permissions", []))
                table.add_row(user, role, perms)
            elif isinstance(record, list):
                table.add_row(user, "legacy", ", ".join(record))
            
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@user.command("remove")
@click.argument("username")
@click.pass_context
def remove_user(ctx, username):
    """Remove a restricted user."""
    check_server_permission(ctx)
    import subprocess
    import json
    import os
    
    if username == "admin":
        console.print("[bold red]Cannot remove admin user.[/bold red]")
        ctx.exit(1)

    console.print(f"[bold red]Removing user: {username}[/bold red]")
    
    try:
        # 1. Remove System User
        subprocess.run(["sudo", "deluser", "--remove-home", username], check=True)
        
        # 2. Update Policy
        policy_file = "/etc/enc/policy.json"
        # Since we modify, we need read then write-back logic
        # Re-using the logic from 'add' would be better refactoring, but inline for now.
        
        current_policy = {}
        # Read
        try:
             with open(policy_file, 'r') as f:
                 current_policy = json.load(f)
        except PermissionError:
              res = subprocess.run(["sudo", "cat", policy_file], capture_output=True, text=True)
              if res.returncode == 0:
                  current_policy = json.loads(res.stdout)

        if username in current_policy.get("users", {}):
            del current_policy["users"][username]
            
            # Write back
            policy_json = json.dumps(current_policy, indent=4)
            proc = subprocess.Popen(["sudo", "tee", policy_file], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
            proc.communicate(input=policy_json.encode())

        console.print(f"[bold green]Success:[/bold green] User '{username}' removed.")

    except subprocess.CalledProcessError:
        console.print(f"[bold yellow]Warning:[/bold yellow] System user might not exist or failed to remove.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
def status():
    """Show the current security status."""
    console.print(Panel("System Locked", title="ENC Status", style="red"))

def main():
    # Hook checking into individual commands or group execution
    # Click doesn't have a simple global pre-invoke for groups without custom class
    # So we call it explicitly or use a callback. 
    # For simplicity in this refactor, let's just make the commands call it.
    cli()
