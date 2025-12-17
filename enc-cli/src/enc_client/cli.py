import click
from rich.console import Console
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

# --- Config Group ---

@cli.group()
def config():
    """Configure Client Settings."""
    pass

@config.command("init")
def config_init():
    """Interactive configuration wizard."""
    console.print("[bold cyan]ENC Client Configuration[/bold cyan]")
    
    current = enc_manager.config
    
    url = Prompt.ask("ENC Server URL", default=current.get("url", "https://api.enc-server.com"))
    username = Prompt.ask("Username", default=current.get("username", "admin"))
    
    confirm_key = "y" if current.get("ssh_key") else "n"
    # Logic to ask for key
    # If key exists, show it exists?
    # Simple prompt:
    key = Prompt.ask("SSH Key Path (optional)", default=current.get("ssh_key", ""))
    
    enc_manager.init_config(url, username, key)
    console.print("[bold green]Configuration saved![/bold green]")

@config.command("show")
def config_show():
    """Display current configuration."""
    cfg = enc_manager.config
    table = Table(title="ENC Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    for k, v in cfg.items():
        # Mask session/context slightly? or just show type
        # For now, show plain
        table.add_row(k, str(v))
        
    console.print(table)

@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a specific configuration value."""
    enc_manager.set_config_value(key, value)
    console.print(f"Set [cyan]{key}[/cyan] to [green]{value}[/green]")


# --- Connection Commands ---

@cli.command("check-connection")
def check_connection():
    """Check connectivity to the configured URL."""
    enc_manager.check_connection()

@cli.command()
def login():
    """Test connection to the server (SSH login)."""
    enc_manager.login()

# --- Forwarding Commands ---

@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument('args', nargs=-1)
def projects(args):
    """Forward 'projects' commands to server."""
    enc_manager.run_remote("projects", args)

@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument('args', nargs=-1)
def user(args):
    """Forward 'user' commands to server."""
    enc_manager.run_remote("user", args)
    
@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument('args', nargs=-1)
def init(args):
    """Forward 'init' commands to server."""
    enc_manager.run_remote("init", args)

@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument('subcommand', required=False)
@click.argument('args', nargs=-1)
def exec(subcommand, args):
    """Execute generic ENC commands on the server."""
    cmd = []
    if subcommand:
        cmd.append(subcommand)
    cmd.extend(args)
    enc_manager.run_remote(cmd[0] if cmd else "", cmd[1:])

def main():
    cli()

if __name__ == "__main__":
    main()
