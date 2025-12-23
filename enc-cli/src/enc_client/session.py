import os
import json
from rich.console import Console

console = Console()

class Session:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.sessions_dir = os.path.join(self.config_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)

    def get_session_path(self, session_id):
        return os.path.join(self.sessions_dir, f"{session_id}.json")

    def load_session(self, session_id):
        """Load session data from the session file."""
        if not session_id:
            return None
            
        session_file = self.get_session_path(session_id)
        if not os.path.exists(session_file):
            return None
            
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def save_session(self, session_data):
        """Save session data to file."""
        session_id = session_data.get("session_id")
        if not session_id:
            return False

        session_file = self.get_session_path(session_id)
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=4)
            return True
        except Exception as e:
            console.print(f"[red]Error saving session:[/red] {e}")
            return False

    def update_session_key(self, session_id, key, value):
        """Update a specific key in the session file."""
        data = self.load_session(session_id)
        if not data:
            return False
        
        data[key] = value
        return self.save_session(data)

    def update_project_info(self, session_id, project_name, local_dir=None, server_mount=None, exec_point=None):
        """Add or update project information in the session."""
        data = self.load_session(session_id)
        if not data:
            return False

        if "projects" not in data:
            data["projects"] = {}
        
        # Handle legacy list format from server sync
        if isinstance(data["projects"], list):
            # Convert list of content to empty dicts, preserving names as keys
            # Assuming list elements are strings (project names)
            new_projects = {}
            for p in data["projects"]:
                if isinstance(p, str):
                    new_projects[p] = {}
                elif isinstance(p, dict) and "name" in p:
                    new_projects[p["name"]] = p
            data["projects"] = new_projects
            
        if project_name not in data["projects"]:
            data["projects"][project_name] = {}
            
        proj = data["projects"][project_name]
        if local_dir is not None: 
            proj["local_mount_point"] = local_dir
        if server_mount is not None: 
            proj["server_mount_point"] = server_mount
        if exec_point is not None:
            proj["exec_entry_point"] = exec_point
            
        # Ensure we don't hold onto stale "mounted" state if local_dir is explicitly set to None/Empty?
        # If unmounting, caller should probably set local_dir="" or remove entry.
        # Let's add specific remove method or handle it here?
        # User implies unmount removes it from "active".
        
        return self.save_session(data)

    def get_project_by_path(self, session_id, path):
        """Find project name by local mount path."""
        data = self.load_session(session_id)
        if not data or "projects" not in data:
            return None

        # Check for list format
        if isinstance(data["projects"], list):
            # Cannot do lookup by path if it's just a list of names
            # But we can try to find if path matches? No, list has no path info.
            return None
        
        abs_path = os.path.abspath(path)
        for name, info in data["projects"].items():
             if info.get("local_mount_point") == abs_path:
                 return name
        return None

    def remove_project_mount(self, session_id, project_name):
        """Mark project as unmounted locally."""
        data = self.load_session(session_id)
        if not data or "projects" not in data:
            return False
            
        if project_name in data["projects"]:
            # We don't delete the project info (server metadata), just clear local mount
            data["projects"][project_name]["local_mount_point"] = None
            return self.save_session(data)
        return False

    def remove_project(self, session_id, project_name):
        """Permanently remove project from session."""
        data = self.load_session(session_id)
        if not data or "projects" not in data:
            return False
            
        if project_name in data["projects"]:
            del data["projects"][project_name]
            return self.save_session(data)
        return False

    def clear_all_sessions(self):
        """Remove all session files."""
        try:
            import glob
            files = glob.glob(os.path.join(self.sessions_dir, "*.json"))
            for f in files:
                os.remove(f)
            return True
        except Exception as e:
            console.print(f"[red]Error clearing sessions:[/red] {e}")
            return False

    def is_project_active(self, session_id, project_name):
        """Check if a project is locally active (mounted)."""
        data = self.load_session(session_id)
        if not data or "projects" not in data:
            return False
            
        projects = data["projects"]
        if isinstance(projects, list):
            return False
            
        if project_name in projects:
            # Consistent with project_list logic: if local_mount_point is set, it's active
            return bool(projects[project_name].get("local_mount_point"))
            
        return False

    def get_active_projects(self, session_id):
        """Return a list of active project names."""
        data = self.load_session(session_id)
        if not data or "projects" not in data:
            return []
            
        projects = data["projects"]
        if isinstance(projects, list):
            return []
            
        active_list = []
        for name, info in projects.items():
            if info.get("local_mount_point"):
                active_list.append(name)
        return active_list
