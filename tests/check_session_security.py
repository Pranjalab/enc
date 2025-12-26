import pexpect
import json
import sys
import time

ENC_SERVER = "localhost"
ENC_PORT = "2222"
USER = "admin"
PASSWORD = "secure_admin_pass"

def run_ssh_command(cmd_args, expect_json=True):
    # Construct command: ssh -p 2222 admin@localhost <cmd_args>
    # Add options to strict host checking to avoid interactive prompts
    ssh_cmd = f"ssh -p {ENC_PORT} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {USER}@{ENC_SERVER} {cmd_args}"
    # print(f"Executing: {ssh_cmd}")
    
    child = pexpect.spawn(ssh_cmd, encoding='utf-8')
    
    # Handle password prompt
    i = child.expect(['password:', pexpect.EOF, pexpect.TIMEOUT], timeout=10)
    if i == 0:
        child.sendline(PASSWORD)
    elif i == 2:
        print("Timeout waiting for password prompt")
        return None
        
    # Wait for completion
    child.expect(pexpect.EOF)
    output = child.before.strip()
    
    # Remove password echo if present
    lines = output.split('\n')
    clean_lines = [l for l in lines if PASSWORD not in l]
    output = '\n'.join(clean_lines)
    
    if expect_json:
        # Find JSON in output (it might be surrounded by SSH banner junk)
        try:
            # Look for start of JSON object or list
            start = output.find('{')
            if start == -1:
                 # Try finding explicit error message if not json
                 return output
            json_str = output[start:]
            return json.loads(json_str)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {output}")
            return output
    return output

def test_session_security():
    print("========================================")
    print("SESSION SECURITY TEST (PYTHON)")
    print("========================================")

    # 1. Login
    print("1. Logging in...")
    login_res = run_ssh_command(f"server-login {USER}")
    if not isinstance(login_res, dict) or "session_id" not in login_res:
        print("FAILED: Login failed or invalid response")
        print(login_res)
        sys.exit(1)
        
    session_id = login_res["session_id"]
    print(f"Valid Session ID: {session_id}")

    # 2. Valid Session Check
    print("2. Verifying valid session access...")
    res = run_ssh_command(f"server-project-list --session-id {session_id}")
    if isinstance(res, dict) and res.get("status") == "success":
        print("SUCCESS: Valid session accepted.")
    else:
        print("FAILED: Valid session rejected.")
        print(res)
        sys.exit(1)

    # 3. Invalid Session Check
    fake_id = "fake-session-uuid-1234"
    print(f"3. Attempting access with FAKE session ID: {fake_id}")
    res = run_ssh_command(f"server-project-list --session-id {fake_id}")
    
    # Check if response indicates error
    if isinstance(res, dict) and "Session Verification Failed" in res.get("message", ""):
        print("SUCCESS: Fake session rejected.")
    else:
        print("FAILED: Fake session was NOT rejected or output mismatch.")
        print(res)
        sys.exit(1)

    # 4. Logout
    print("4. Logging out...")
    run_ssh_command(f"server-logout {session_id}")
    
    # 5. Expired Session Check
    print("5. Attempting access with EXPIRED session ID...")
    res = run_ssh_command(f"server-project-list --session-id {session_id}")
    
    if isinstance(res, dict) and "Session Verification Failed" in res.get("message", ""):
        print("SUCCESS: Expired session rejected.")
    else:
        print("FAILED: Expired session was NOT rejected.")
        print(res)
        sys.exit(1)
        
    print("========================================")
    print("✅ SESSION SECURITY VERIFIED")
    print("========================================")

if __name__ == "__main__":
    test_session_security()
