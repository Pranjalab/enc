
import click
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
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

@user.command("create")
@click.argument("username")
@click.argument("password")
@click.option("--role", default="user", help="User role (admin/user)")
def user_create(username, password, role):
    """Create a new user on the server."""
    console.print(f"Creating user [cyan]{username}[/cyan]...")
    if enc_manager.user_create(username, password, role):
        console.print(f"[green]User {username} created successfully.[/green]")
    else:
        console.print(f"[red]Failed to create user.[/red]")

@user.command("rm")
@click.argument("username")
def user_delete(username):
    """Delete a user from the server."""
    if click.confirm(f"Are you sure you want to delete user '{username}'?"):
        if enc_manager.user_delete(username):
             console.print(f"[green]User {username} deleted.[/green]")
        else:
             console.print(f"[red]Failed to delete user.[/red]")


def main():
    cli()

if __name__ == "__main__":
    main()
