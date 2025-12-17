import pytest
import subprocess
import shutil
import sys
import os
import json

# Ensure 'enc' is installed and in PATH (Legacy fallback)
ENC_CMD = shutil.which("enc") or "/opt/anaconda3/bin/enc"

def run_enc(*args):
    """Run `enc` command and return stdout/stderr."""
    cmd = [sys.executable, "-m", "enc_client.cli"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)

@pytest.fixture(scope="module", autouse=True)
def setup_config():
    """Ensure valid config exists for testing."""
    config_dir = os.path.expanduser("~/.enc")
    config_file = os.path.join(config_dir, "config.json")
    
    # Always overwrite for integration testing stability
    # In a real user env, we might warn, but here we want to guarantee the test runs against our SSH server
    os.makedirs(config_dir, exist_ok=True)
    key_path = os.path.expanduser("~/.enc/keys/enc_client_key")
    cfg = {
        "host": "localhost",
        "port": "2222",
        "user": "admin",
        "key": key_path
    }
    with open(config_file, 'w') as f:
        json.dump(cfg, f, indent=4)
    print("\n[Setup] Enforced test config.")

def test_01_version():
    """Verify enc is installed."""
    res = run_enc("--version")
    assert res.returncode == 0
    assert "ENC Client" in res.stdout

def test_02_login():
    """Verify login connectivity."""
    res = run_enc("login")
    print(f"\n[Login Output] {res.stdout} {res.stderr}")
    assert res.returncode == 0
    assert "Success" in res.stdout or "ENC Status" in res.stdout or "Encrypted Native Code" in res.stdout

def test_04_list_users():
    """Verify Admin can list users."""
    res = run_enc("user", "list")
    print(f"\n[List Output] {res.stdout} {res.stderr}")
    assert res.returncode == 0
    # Should contain table headers
    assert "Username" in res.stdout
    assert "Role" in res.stdout
    # 'admin' user is system-level and might not be in policy.json.
    # 'developer1' should be there if server setup was correct.
    assert "developer1" in res.stdout
