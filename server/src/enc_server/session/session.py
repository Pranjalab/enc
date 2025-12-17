from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class Session:
    is_logged_in: bool = False
    master_key: Optional[bytes] = None
    active_project: Optional[str] = None
    project_keys: Dict[str, bytes] = field(default_factory=dict)
    
    def login(self, master_key: bytes):
        self.is_logged_in = True
        self.master_key = master_key
        
    def logout(self):
        self.is_logged_in = False
        self.master_key = None
        self.active_project = None
        self.project_keys.clear()

# Global session instance
# Note: In a real process-based CLI, this resets every command unless 
# we use a daemon or shared memory (which ENC avoids).
# For now, this represents the state *during* a command execution
# or would be used if we spawn a shell.
current_session = Session()
