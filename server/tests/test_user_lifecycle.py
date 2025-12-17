import paramiko
import pytest
import time

HOST = "localhost"
PORT = 2222
ADMIN_USER = "admin"
ADMIN_PASS = "secure_admin_pass"

TEST_USER = "lifecycle_test_user"
TEST_PASS = "testpass123"

def test_user_lifecycle():
    """
    Test the full lifecycle:
    1. Add User
    2. List User (Verify existence)
    3. Remove User
    4. List User (Verify removal)
    5. Verify Login Fails
    """
    print(f"\n[Test] Connecting as Admin...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=ADMIN_USER, password=ADMIN_PASS, timeout=5)
    
    chan = client.invoke_shell()
    time.sleep(1) # Wait for prompt
    chan.recv(4096) # Clear banner

    # 1. ADD USER
    print(f"[Action] Adding {TEST_USER}...")
    chan.send(f"enc user add {TEST_USER}\n")
    time.sleep(1)
    chan.send(f"{TEST_PASS}\n") # Password
    time.sleep(0.5)
    chan.send("\n") # SSH Key (Empty)
    time.sleep(1)
    
    resp = chan.recv(8192).decode()
    print(f"[Output] {resp}")
    # Relaxed check for color codes
    assert "User" in resp and "created" in resp

    # 2. LIST USER
    print(f"[Action] Listing users...")
    chan.send("enc user list\n")
    time.sleep(1)
    
    resp = chan.recv(8192).decode()
    print(f"[Output] {resp}")
    assert TEST_USER in resp
    assert "init" in resp # Default permission shown in table

    # 3. REMOVE USER
    print(f"[Action] Removing {TEST_USER}...")
    chan.send(f"enc user remove {TEST_USER}\n")
    time.sleep(1)
    
    resp = chan.recv(8192).decode()
    print(f"[Output] {resp}")
    assert "Success" in resp and "removed" in resp

    # 4. LIST USER AGAIN
    print(f"[Action] Listing users (Verify removal)...")
    chan.send("enc user list\n")
    time.sleep(1)
    
    resp = chan.recv(8192).decode()
    print(f"[Output] {resp}")
    assert TEST_USER not in resp

    client.close()
    
    # 5. VERIFY LOGIN FAILURE
    print(f"[Test] Attempting login as removed user...")
    removed_client = paramiko.SSHClient()
    removed_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    with pytest.raises(paramiko.AuthenticationException):
        removed_client.connect(HOST, port=PORT, username=TEST_USER, password=TEST_PASS, timeout=5)
        
    print("[Pass] Login failed as expected.")
