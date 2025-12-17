import paramiko
import pytest
import time
import socket
import os
from pathlib import Path

# Configuration
HOST = "localhost"
PORT = 2222
USERNAME = "admin"
PASSWORD = "secure_admin_pass" # Matches docker-compose.yml
SSH_KEYS_DIR = Path("server/ssh_keys")
AUTHORIZED_KEYS_FILE = SSH_KEYS_DIR / "authorized_keys"

def wait_for_port(host, port, timeout=5):
    """Wait for a TCP port to open."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.5)
    return False

@pytest.fixture(scope="module")
def ensure_server_reachable():
    """Ensure the SSH server is reachable before running tests."""
    if not wait_for_port(HOST, PORT, timeout=5):
        pytest.fail(f"SSH Server ({HOST}:{PORT}) is NOT reachable. Is Docker running?")

def test_ssh_password_auth(ensure_server_reachable):
    """Test SSH connection using Password Authentication."""
    print(f"\n[Test] Password Auth to {HOST}:{PORT}...")
    print(f"[Info] Connecting with username='{USERNAME}' and password='{PASSWORD}'")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, timeout=5)
        print("[Info] Connection established successfully.")
        
        # Verify
        print("[Info] Executing remote command: echo 'Password Auth Success'")
        stdin, stdout, stderr = client.exec_command("echo 'Password Auth Success'")
        output = stdout.read().decode().strip()
        print(f"[Info] Remote command output: '{output}'")
        
        assert output == "Password Auth Success"
        print("[Pass] Password Authentication verified.")
        
    except Exception as e:
        print(f"[Fail] Password Auth Failed: {e}")
        pytest.fail(f"Password Auth Failed: {e}")
    finally:
        client.close()

def test_ssh_key_auth(ensure_server_reachable, tmp_path):
    """Test SSH connection using Key-Based Authentication."""
    print(f"\n[Test] Key Auth to {HOST}:{PORT}...")

    # 1. Generate specific test key pair
    key = paramiko.RSAKey.generate(2048)
    private_key_path = tmp_path / "test_id_rsa"
    key.write_private_key_file(str(private_key_path))
    public_key = f"{key.get_name()} {key.get_base64()} test_key"

    # 2. Add public key to server/ssh_keys/authorized_keys (mounted volume)
    # Ensure directory exists
    SSH_KEYS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Append key
    with open(AUTHORIZED_KEYS_FILE, "a") as f:
        f.write(f"\n{public_key}\n")
    
    print(f"[Setup] Appended test key to {AUTHORIZED_KEYS_FILE}")

    # 3. Connect using the Private Key
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"[Info] Connecting with username='{USERNAME}' and generated SSH key")
        client.connect(
            HOST, 
            port=PORT, 
            username=USERNAME, 
            pkey=key,            # Pass the key object directly
            timeout=5,
            look_for_keys=False, # Disable searching default keys
            allow_agent=False    # Disable SSH agent
        )
        print("[Info] Connection established successfully using Key Auth.")
        
        # Verify
        print("[Info] Executing remote command: echo 'Key Auth Success'")
        stdin, stdout, stderr = client.exec_command("echo 'Key Auth Success'")
        output = stdout.read().decode().strip()
        print(f"[Info] Remote command output: '{output}'")
        
        assert output == "Key Auth Success"
        print("[Pass] Key Authentication verified.")

    except Exception as e:
        print(f"[Fail] Key Auth Failed: {e}")
        pytest.fail(f"Key Auth Failed: {e}")
    finally:
        client.close()
        
        # 4. Cleanup (Best effort to remove the key lines)
        # Note: In a real environment, we'd want to be more careful not to delete others' keys.
        # For this test artifact, we can leave it or try to clean.
        pass
