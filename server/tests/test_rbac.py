import paramiko
import pytest
import time

# Config
HOST = "localhost"
PORT = 2222
USERNAME = "developer1"
PASSWORD = "devpass123"

def test_restricted_shell_commands():
    """Test that the restricted shell blocks forbidden commands."""
    print(f"\n[Test] Connecting as Restricted User ({USERNAME})...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, timeout=5)
        
        # We need an invoke_shell for the REPL interaction or just exec_command?
        # enc_shell.py uses cmd.Cmd which reads specific commands.
        # But `exec_command` usually bypasses the shell if the server allows execution.
        # Wait, if I set shell /bin/enc-shell, does SSH exec_command use it?
        # Usually exec_command runs: /bin/enc-shell -c "command"
        # My enc_shell.py doesn't handle -c yet! It only does REPL.
        # So I must use invoke_shell() to test the interactiveness.
        
        chan = client.invoke_shell()
        buff = ""
        while not buff.endswith("enc> "):
            try:
                chunk = chan.recv(1024).decode()
                buff += chunk
                if not chunk: break
            except:
                time.sleep(0.1)
        
        print(f"[Info] Banner received: {buff.strip()}")
        assert "Welcome to the ENC Secure Environment" in buff
        
        # 1. Test Allowed Command (help)
        chan.send("help\n")
        time.sleep(0.5)
        resp = chan.recv(1024).decode()
        print(f"[Info] 'help' response: {resp.strip()}")
        assert "Documented commands" in resp
        assert "enc" in resp
        assert "exit" in resp
        
        # 2. Test Forbidden Command (ls)
        chan.send("ls\n")
        time.sleep(0.5)
        resp = chan.recv(1024).decode()
        print(f"[Info] 'ls' response: {resp.strip()}")
        assert "*** Forbidden command: ls" in resp
        
        # 3. Test Allowed ENC Command (enc status)
        # Note: 'status' is in allow_all
        chan.send("enc status\n")
        time.sleep(2) # Subprocess might take a moment
        resp = chan.recv(4096).decode()
        print(f"[Info] 'enc status' response: {resp.strip()}")
        # Check if it ran enc. enc status prints "System Locked"
        assert "System Locked" in resp
        
        print("[Pass] RBAC Shell verified.")
        
    except Exception as e:
        pytest.fail(f"RBAC Test Failed: {e}")
    finally:
        client.close()
