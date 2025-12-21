
import click
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
import json
from enc_client.enc import Enc

console = Console()

# Initialize logic class
enc_manager = Enc()

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--version', is_flag=True, help="Show version.")
def cli(ctx, version):
    """ENC Client - Secure Remote Access"""
    if version:
        console.print("ENC Client v1.0.0")
        ctx.exit()
    
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())

@cli.group("show")
def show_group():
    """Show configuration or access rights."""
    pass

@show_group.command("config")
def show_config():
    """Display current configuration."""
    cfg = enc_manager.config
    table = Table(title="ENC Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    for k, v in cfg.items():
        table.add_row(k, str(v))
        
    console.print(table)

@show_group.command("access")
def show_access():
    """Show access rights from session file."""
    # Placeholder for session logic
    console.print("[yellow]No active session found.[/yellow]")

@cli.command("set-url")
@click.argument("url")
def set_url(url):
    """Set the ENC Server URL."""
    enc_manager.set_config_value("url", url)
    console.print(f"Set URL to: [green]{url}[/green]")

@cli.command("set-username")
@click.argument("username")
def set_username(username):
    """Set the username."""
    enc_manager.set_config_value("username", username)
    console.print(f"Set Username to: [green]{username}[/green]")

@cli.command("set-ssh-key")
@click.argument("ssh_key")
def set_ssh_key(ssh_key):
    """Set the SSH Private Key path."""
    enc_manager.set_config_value("ssh_key", ssh_key)
    console.print(f"Set SSH Key to: [green]{ssh_key}[/green]")

@cli.command("init")
@click.argument("path", required=False, default=".")
def init(path):
    """Initialize ENC configuration."""
    console.print(Panel("Welcome to ENC Configuration Wizard", title="ENC Init", style="bold cyan"))
    
    # 1. Choose Location
    config_type = Prompt.ask("Initialize Global (~/.enc) or Local (./.enc) config?", choices=["global", "local"], default="global")
    
    target_path = None
    if config_type == "local":
        path = os.path.abspath(path)
        console.print(f"Initializing LOCAL configuration in [cyan]{path}/.enc[/cyan]")
        target_path = os.path.join(path, ".enc", "config.json")
    else:
        console.print("Initializing GLOBAL configuration in [cyan]~/.enc[/cyan]")
        target_path = os.path.expanduser("~/.enc/config.json")
        
    # Check if exists
    if os.path.exists(target_path):
        console.print(f"[yellow]Warning: Configuration already exists at {target_path}[/yellow]")
        if not click.confirm("Do you want to overwrite it?"):
            console.print("[red]Aborted.[/red]")
            return

    # 2. Capture Details
    url = Prompt.ask("Enter ENC Server URL", default="http://localhost:2222")
    username = Prompt.ask("Enter Username")
    ssh_key = Prompt.ask("Enter SSH Key Path", default="")
    
    # 3. Save
    enc_manager.init_config(url, username, ssh_key, target_path=target_path)
    console.print(f"[bold green]Configuration initialized at {target_path}[/bold green]")
    console.print("Run 'enc check-connection' to verify.")

# --- Connection Commands ---

@cli.command("check-connection")
def check_connection():
    """Check connectivity to the configured URL."""
    enc_manager.check_connection()

@cli.command()
def login():
    """Authenticate with the ENC Server."""
    enc_manager.login()

@cli.group("project")
def project_group():
    """Manage projects."""
    pass

@project_group.command("init")
@click.argument("name")
@click.password_option()
def project_init(name, password):
    """Initialize a new encrypted project on server."""
    # Check login first
    if not enc_manager.config.get("session_id"):
        console.print("[yellow]Please login first.[/yellow]")
        return
        
    console.print(f"Initializing project '[cyan]{name}[/cyan]'...")
    if enc_manager.project_init(name, password):
        console.print(f"[bold green]Project '{name}' initialized successfully.[/bold green]")

@project_group.command("dev")
@click.argument("name")
@click.password_option()
def project_dev(name, password):
    """Mount project for development."""
    if not enc_manager.config.get("session_id"):
        console.print("[yellow]Please login first.[/yellow]")
        return
        
    console.print(f"Mounting project '[cyan]{name}[/cyan]'...")
    if enc_manager.project_mount(name, password):
        console.print(f"[bold green]Project mounted.[/bold green]")
        # TODO: Start Sync Logic here
        console.print("[dim]Sync capability to be implemented via rsync/sshfs...[/dim]")

@project_group.command("sync")
@click.argument("name")
@click.argument("local_path", type=click.Path(exists=True))
def project_sync(name, local_path):
    """Sync local files to the remote project."""
    if not enc_manager.config.get("session_id"):
        console.print("[yellow]Please login first.[/yellow]")
        return
        
    console.print(f"Syncing '[cyan]{local_path}[/cyan]' -> '[cyan]{name}[/cyan]'...")
    if enc_manager.project_sync(name, local_path):
        console.print(f"[bold green]Sync Complete.[/bold green]")
    else:
        console.print(f"[bold red]Sync Failed.[/bold red]")

@project_group.command("run")
@click.argument("name")
@click.argument("command", nargs=-1)
def project_run(name, command):
    """Run a command on the remote project."""
    if not command:
        console.print("[yellow]No command provided. Starting interactive shell...[/yellow]")
        # TODO: Interactive shell support
        cmd_str = "bash" # Default to shell
    else:
        cmd_str = " ".join(command) # Naive join, assume user handles quotes or use shlex if needed upstream
    
    console.print(f"Running '[cyan]{cmd_str}[/cyan]' in project '[cyan]{name}[/cyan]'...")
    
    if enc_manager.project_run(name, cmd_str):
        # Return code handles success/fail printing usually
        pass
    else:
        # Failure message handled in manager
        pass

@cli.command()
def logout():
    """Logout and clear local sessions."""
    if enc_manager.logout():
        console.print("[bold green]Logged out successfully.[/bold green] Local sessions cleared.")
    else:
        console.print("[yellow]No active session or error clearing session.[/yellow]")


@cli.group()
def user():
    """Manage users (admin only)."""
    pass

@user.command("list")
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
def user_list(json_output):
    """List users (cached in session)."""
    users = enc_manager.user_list()
    if users:
        table = Table(title="ENC Users")
        table.add_column("Username", style="cyan")
        # If server returns more details (like role/id), we could add them.
        # Assuming simple list of strings OR list of dicts.
        # Implementation in enc.py handles dict/list return, but let's assume dicts if possible, or handle strings.
        
        # Heuristic: inspect first element
        if isinstance(users, list) and len(users) > 0:
            if isinstance(users[0], dict):
                 table.add_column("Role", style="magenta")
                 for u in users:
                     table.add_row(u.get("username", "N/A"), u.get("role", "user"))
            else:
                 for u in users:
                     table.add_row(str(u))
        elif isinstance(users, list) and len(users) == 0:
            if json_output:
                click.echo(json.dumps([]))
            else:
                console.print("[yellow]No users found.[/yellow]")
            return
            
        if json_output:
            click.echo(json.dumps(users))
        else:
            console.print(table)

@user.command("create")
@click.argument("username")
@click.option("--password",  default=None, help="User password")
@click.option("--role", type=click.Choice(["admin", "user"], case_sensitive=False), default=None, help="User role")
@click.option("--ssh-key", default=None, help="Path to public SSH key")
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
def user_create(username, password, role, ssh_key, json_output):
    """Create a new user on the server."""
    
    # 1. Prompt for Role if missing
    if not role:
        role = click.prompt("Select Role", type=click.Choice(["admin", "user"], case_sensitive=False), default="user")
    
    # 2. Prompt for Password if missing
    if not password:
        password = click.prompt("Enter Password", hide_input=True)
    
    # 3. Handle SSH Key
    ssh_key_content = None

    if ssh_key:
         path = os.path.expanduser(ssh_key)
         if os.path.exists(path):
             try:
                with open(path, 'r') as f:
                    ssh_key_content = f.read().strip()
             except Exception as e:
                 console.print(f"[red]Error reading key file: {e}[/red]")
                 return
         else:
             console.print(f"[yellow]Warning: SSH key file not found: {path}[/yellow]")
             return
    else:
         # Interactive prompt
         ssh_key_path = click.prompt("Path to public SSH key (optional, press Enter to skip)", default="", show_default=False)
         if ssh_key_path:
             path = os.path.expanduser(ssh_key_path)
             if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        ssh_key_content = f.read().strip()
                except Exception as e:
                     console.print(f"[red]Error reading key file: {e}[/red]")
                     return
             else:
                 console.print(f"[red]File not found: {path}[/red]")
                 return

    console.print(f"Creating user [cyan]{username}[/cyan] with role [magenta]{role}[/magenta]...")
    if enc_manager.user_create(username, password, role, ssh_key_content):
        if json_output:
             click.echo(json.dumps({"status": "success", "username": username}))
        else:
             console.print(f"[green]User {username} created successfully.[/green]")
    else:
        if json_output:
             click.echo(json.dumps({"status": "error", "message": "Failed"}))
        else:
             console.print(f"[red]Failed to create user.[/red]")

@user.command("remove")
@click.argument("username")
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
def user_delete(username, json_output):
    """Delete a user from the server."""
    if not json_output:
        if not click.confirm(f"Are you sure you want to delete user '{username}'?"):
            return

    console.print(f"Deleting user [cyan]{username}[/cyan]...")
    if enc_manager.user_delete(username):
        if json_output:
             click.echo(json.dumps({"status": "success", "username": username}))
        else:
             console.print(f"[green]User {username} deleted.[/green]")
    else:
        if json_output:
             click.echo(json.dumps({"status": "error", "message": "Failed"}))
        else:
             console.print(f"[red]Failed to delete user.[/red]")


def main():
    cli()

if __name__ == "__main__":
    main()
