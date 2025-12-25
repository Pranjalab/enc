from pathlib import Path
import json
import os
from enc_server.config import PROJECT_ENC_DIR
from enc_server.crypto.key_manager import generate_project_key
from rich.console import Console

console = Console()

def init_project(path: Path = None):
    """
    Initialize a new ENC project in the given path.
    Creates .enc/ directory and initial metadata.
    """
    if path is None:
        path = Path.cwd()
        
    enc_dir = path / PROJECT_ENC_DIR
    
    if enc_dir.exists():
        console.print(f"[bold yellow]Warning:[/bold yellow] Project already initialized in {path}")
        return

    try:
        enc_dir.mkdir(parents=True)
        (enc_dir / "encrypted_files").mkdir()
        
        # Create metadata
        metadata = {
            "version": "1.0",
            "created_at": str(os.times().elapsed), # simplistic timestamp
            "files": {}
        }
        
        with open(enc_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
            
        console.print(f"[bold green]Success:[/bold green] Initialized ENC project in {path}")
        console.print(f"Created {enc_dir}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to initialize project: {e}")
