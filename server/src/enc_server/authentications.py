import json
import os
import getpass
from pathlib import Path

class Authentication:
    POLICY_FILE = "/etc/enc/policy.json"
    
    # Roles
    ROLE_SUPER_ADMIN = "super-admin"
    ROLE_ADMIN = "admin"
    ROLE_DEV = "user"
    
    # Permissions mapping
    PERMISSIONS = {
        # ROLE_SUPER_ADMIN: ["*"],
        ROLE_ADMIN: [
            "status", "server-login", "server-logout", 
            "user add", "user list", "user remove", 
            "init", "server-project-init", "server-project-mount", "server-project-unmount", "server-project-sync", "server-project-run",
            "show users", "server-user-create", "server-user-delete", "server-user-list",
            "server-project-list", "project list"
        ],
        ROLE_DEV: [
            "status", "server-login", "server-logout",
            "init", "server-project-init", "server-project-mount", "server-project-unmount", "server-project-sync", "server-project-run",
            "server-project-list", "project list"
        ]
    }

    def __init__(self, policy_file=None):
        if policy_file:
            self.POLICY_FILE = policy_file
        self.policy = self._load_policy()

    def _load_policy(self):
        if not os.path.exists(self.POLICY_FILE):
             raise FileNotFoundError(f"Critical Error: Security policy file missing at {self.POLICY_FILE}")

        try:
            with open(self.POLICY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            # If permission error or other read error, try sudo
            import subprocess
            res = subprocess.run(["sudo", "cat", self.POLICY_FILE], capture_output=True, text=True)
            if res.returncode == 0:
                try:
                    return json.loads(res.stdout)
                except json.JSONDecodeError as e:
                     raise RuntimeError(f"Critical Error: Security policy file contains invalid JSON: {e}")
            raise RuntimeError(f"Critical Error: Could not load security policy from {self.POLICY_FILE} even with sudo.")

    def save_policy(self):
        """Persist the current policy to disk using sudo if necessary."""
        policy_json = json.dumps(self.policy, indent=4)
        try:
            with open(self.POLICY_FILE, 'w') as f:
                f.write(policy_json)
        except PermissionError:
            import subprocess
            proc = subprocess.Popen(["sudo", "tee", self.POLICY_FILE], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
            proc.communicate(input=policy_json.encode())

    def get_all_users(self):
        """Get all users from the policy."""
        return self.policy.get("users", {})

    def get_user_role(self, username):
        """Determine the role of a user."""
        user_record = self.policy.get("users", {}).get(username)
        if isinstance(user_record, dict):
            return user_record.get("role", self.ROLE_DEV)
        return None

    def get_user_projects(self, username):
        """Get the list of project names for a user."""
        user_record = self.policy.get("users", {}).get(username)
        if isinstance(user_record, dict):
            projs = user_record.get("projects", [])
            if isinstance(projs, dict):
                return list(projs.keys())
            return projs
        return []

    def get_user_project_metadata(self, username):
        """Get the detailed project dictionary for a user."""
        user_record = self.policy.get("users", {}).get(username)
        if isinstance(user_record, dict):
            projs = user_record.get("projects", {})
            if isinstance(projs, list):
                # Convert legacy list to dict if needed for viewing
                return {p: {"mount_path": None, "vault_path": None, "exec": None} for p in projs}
            return projs
        return {}

    def get_user_permissions(self, username):
        """Get all permissions (commands) for a user."""
        role = self.get_user_role(username)
        if role == self.ROLE_SUPER_ADMIN:
            return ["*"]
            
        perms = set(self.PERMISSIONS.get(role, []))
        perms.update(self.policy.get("allow_all", []))
        
        user_record = self.policy.get("users", {}).get(username)
        if isinstance(user_record, dict):
            perms.update(user_record.get("permissions", []))
        elif isinstance(user_record, list):
            perms.update(user_record)
            
        return sorted(list(perms))

    def add_user_project(self, username, project_name, metadata=None):
        """Add a project (with optional metadata) to a user's list."""
        if username == "admin":
             # Admin can technically have projects too now that we standardized
             pass
            
        if "users" not in self.policy:
            self.policy["users"] = {}
        if username not in self.policy["users"]:
            self.policy["users"][username] = {"role": self.ROLE_DEV, "permissions": self.PERMISSIONS[self.ROLE_DEV], "projects": {}}
        
        user_record = self.policy["users"][username]
        
        # Legacy conversion for user record itself
        if isinstance(user_record, list): 
             self.policy["users"][username] = {"role": self.ROLE_DEV, "permissions": user_record, "projects": {}}
             user_record = self.policy["users"][username]

        if "projects" not in user_record:
            user_record["projects"] = {}
        
        # Prepare default metadata
        if metadata is None:
             metadata = {"mount_path": None, "vault_path": None, "exec": None}

        # Add or Update
        if project_name not in user_record["projects"]:
            user_record["projects"][project_name] = metadata
            self.save_policy()
        else:
            # Update existing metadata
            user_record["projects"][project_name].update(metadata)
            self.save_policy()

    def remove_user_project(self, username, project_name):
        """Remove a project from a user's list."""
        user_record = self.policy.get("users", {}).get(username)
        if isinstance(user_record, dict) and "projects" in user_record:
            projects = user_record["projects"]
            
            # Dict removal
            if project_name in projects:
                del projects[project_name]
                self.save_policy()

    def has_project_access(self, username, project_name):
        """Check if a user has access to a project."""
        projects = self.get_user_projects(username)
        return project_name in projects

    def _check_user_in_policy(self, username):
        """Check if a user is in the policy."""
        return username in self.policy.get("users", {})

    def is_allowed(self, username, command):
        """Check if a user is allowed to run a specific command."""
        
        # check if user in the policy
        if not self._check_user_in_policy(username):
            return False
        
        role = self.get_user_role(username)
        
        # SUPER_ADMIN is a role defined in the policy
        if role and role == self.ROLE_SUPER_ADMIN:
            return True
            
        if command in self.policy.get("allow_all", []):
            return True
            
        role_perms = self.PERMISSIONS.get(role, [])
        if "*" in role_perms or command in role_perms:
            return True
            
        user_record = self.policy.get("users", {}).get(username)
        if isinstance(user_record, dict):
            user_perms = user_record.get("permissions", [])
            if "*" in user_perms or command in user_perms:
                return True
        elif isinstance(user_record, list):
            if command in user_record:
                return True
                
        return False

    def can_manage_role(self, current_user, target_role):
        """Check if current_user can manage a user with target_role."""
        curr_role = self.get_user_role(current_user)
        
        if curr_role == self.ROLE_SUPER_ADMIN:
            return True
            
        if curr_role == self.ROLE_ADMIN:
            if target_role in [self.ROLE_ADMIN, self.ROLE_DEV]:
                return True
                
        return False
