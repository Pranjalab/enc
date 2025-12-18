
import pexpect
import sys
import time
import os
import subprocess

GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def log(msg, color=NC):
    sys.stdout.write(f"{color}{msg}{NC}\n")

def run_command(cmd, password=None, expect_pattern=None, timeout=10):
    log(f"Running: {cmd}", YELLOW)
    child = pexpect.spawn(cmd, encoding='utf-8', timeout=timeout)
    
    if password:
        # Expect password prompt
        idx = child.expect(['password:', 'Password:', pexpect.EOF, pexpect.TIMEOUT])
        if idx == 0 or idx == 1:
            child.sendline(password)
        elif idx == 2:
            pass # EOF
        elif idx == 3:
            log("Timeout waiting for password", RED)
            return False, child.before

    try:
        if expect_pattern:
            child.expect(expect_pattern)
        
        # Read remaining
        output = child.read()
        child.close()
        return child.exitstatus == 0, output
    except Exception as e:
        log(f"Error: {e}", RED)
        return False, str(e)

def main():
    log("=== ENC System Verification (Python/Pexpect) ===", GREEN)
    
    # 1. Config
    log("1. Configuring...", NC)
    subprocess.run("enc set-url http://localhost:2222", shell=True)
    subprocess.run("enc set-username tester", shell=True)
    # Clear session
    subprocess.run("rm -f ~/.enc/sessions/*.json", shell=True)
    
    # 2. Login
    log("2. Testing Login...", NC)
    child = pexpect.spawn("enc login", encoding='utf-8')
    try:
        i = child.expect(['password:', 'Success!', 'Login Success', pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        if i == 0:
            log("   -> Sending password...", YELLOW)
            child.sendline("pass123") 
            i = child.expect(['Success!', 'Login Success', 'Permission denied', 'Login failed', 'password:'], timeout=10)
        
        if i == 0 or i == 1: 
             log("   -> Login OK", GREEN)
        elif i == 2 or i == 3:
             log("   -> Login Failed: Permission denied (Check password)", RED)
             sys.exit(1)
        elif i == 4:
             log("   -> Reprompt for password (Auth Failed)", RED)
             sys.exit(1)
        else:
             log(f"   -> Login Failed unexpected output: {child.before}", RED)
             sys.exit(1)
    except Exception as e:
         log(f"   -> Login Exception: {e}", RED)
         if "Success" in child.before or "session_id" in child.before:
             log("   -> Login OK (Fallback check)", GREEN)
         else:
             sys.exit(1)

    # 3. Project Init
    project_name = f"verify_{int(time.time())}"
    log(f"3. Init Project '{project_name}'...", NC)
    cmd = f"enc project init {project_name} --password clientsecret"
    
    child = pexpect.spawn(cmd, encoding='utf-8')
    try:
        i = child.expect(['password:', 'initialized successfully', pexpect.EOF, pexpect.TIMEOUT])
        if i == 0:
             log("   -> SSH Password Prompt (Sending 'pass123')", YELLOW)
             child.sendline("pass123")
             child.expect('initialized successfully')
             log("   -> Project Init OK", GREEN)
        elif i == 1:
             log("   -> Project Init OK (No SSH Prompt)", GREEN)
        else:
             log("   -> Project Init Failed", RED)
             print(child.before, child.after)
             sys.exit(1)
    except Exception as e:
        log(f"   -> Init Error: {e}", RED)
        sys.exit(1)

    # 4. Mount
    log("4. Project Mount...", NC)
    cmd = f"enc project dev {project_name} --password clientsecret"
    child = pexpect.spawn(cmd, encoding='utf-8')
    try:
        i = child.expect(['password:', 'Project mounted', 'Mount Failed', pexpect.EOF])
        if i == 0:
            child.sendline("pass123")
            i = child.expect(['Project mounted', 'Mount Failed', pexpect.EOF])
        
        output = child.before + (child.after if isinstance(child.after, str) else "")
        if "Project mounted" in output:
             log("   -> Mount OK", GREEN)
        elif "Mount Failed" in output:
             log("   -> Mount Failed (Expected on Mac)", YELLOW)
        else:
             log("   -> Unknown State", RED)
             print(output)
    except Exception as e:
        log(f"   -> Mount Exception: {e}", RED)

    # 5. Sync
    log("5. Testing Sync...", NC)
    with open("test_sync.txt", "w") as f:
        f.write("Hello Encrypted World")
    
    cmd = f"enc project sync {project_name} ."
    child = pexpect.spawn(cmd, encoding='utf-8')
    try:
        i = child.expect(['password:', 'Sync Complete', 'Sync Failed', pexpect.EOF], timeout=15)
        if i == 0:
            # If prompt due to no keys (sync uses -o StrictHostKeyChecking=no but needs pass if no key)
            child.sendline("pass123") 
            i = child.expect(['Sync Complete', 'Sync Failed', pexpect.EOF], timeout=15)
        
        if i == 0 or (i==1 and "Sync Complete" in child.before):
             log("   -> Sync CLI Reported Success", GREEN)
        else:
             log("   -> Sync Command Failed", RED)
             print(child.before, child.after)
    except Exception as e:
        log(f"   -> Sync CLI Exception: {e}", RED)

    # Verify file on server
    # We verify the previous step before RUN step
    verify_cmd = f"ssh -p 2222 tester@localhost 'cat ~/.enc/run/master/{project_name}/test_sync.txt'"
    child = pexpect.spawn(verify_cmd, encoding='utf-8')
    try:
        i = child.expect(['password:', 'Hello Encrypted World', pexpect.EOF])
        if i == 0:
            child.sendline("pass123")
            i = child.expect(['Hello Encrypted World', pexpect.EOF])
        
        if i == 0 or (i==1 and "Hello Encrypted World" in child.before):
             log("   -> Remote File Verified Content!", GREEN)
        else:
             log("   -> Remote File Check Failed", RED)
             print(child.before)
    except Exception as e:
         log(f"   -> Verification Exception: {e}", RED)

    # 6. Run Execution
    log("6. Testing Execution...", NC)
    # Check CWD: 'enc project run <name> pwd' should return path ending in <name>
    cmd = f"enc project run {project_name} pwd"
    child = pexpect.spawn(cmd, encoding='utf-8')
    try:
        i = child.expect(['password:', f'/{project_name}', pexpect.EOF], timeout=15)
        if i == 0:
            child.sendline("pass123")
            i = child.expect([f'/{project_name}', pexpect.EOF], timeout=15)
        
        if i == 0 or (i==1 and f"/{project_name}" in child.before):
             log("   -> Execution CWD Verified", GREEN)
        else:
             log("   -> Execution Failed (CWD mismatch)", RED)
             print(child.before)
    except Exception as e:
        log(f"   -> Execution Exception: {e}", RED)

    # 7. Logout
    log("7. Testing Logout...", NC)
    child = pexpect.spawn("enc logout", encoding='utf-8')
    try:
        # It calls server-logout, might prompt for password
        i = child.expect(['password:', 'Logged out successfully', pexpect.EOF], timeout=15)
        if i == 0:
            child.sendline("pass123")
            i = child.expect(['Logged out successfully', pexpect.EOF], timeout=15)
            
        if i == 0 or (i==1 and "Logged out successfully" in child.before):
             log("   -> Logout Command Success", GREEN)
        else:
             # It might fail network access but still clear local session?
             # Check output
             if "Logged out successfully" in child.before + (child.after if isinstance(child.after, str) else ""):
                 log("   -> Logout Success (Async)", GREEN)
             else:
                 log("   -> Logout CLI Output mismatch", YELLOW)
                 print(child.before)
                 
    except Exception as e:
        log(f"   -> Logout Exception: {e}", RED)

    if not os.path.exists(os.path.expanduser("~/.enc/sessions")):
         log("   -> Sessions cleared OK", GREEN) 
    else:
         # Check if empty
         import glob
         if not glob.glob(os.path.expanduser("~/.enc/sessions/*.json")):
             log("   -> Sessions cleared OK", GREEN)
         else:
             log("   -> Logout Failed (Session files remain)", RED)

    log("=== Verification Finished ===", GREEN)

if __name__ == "__main__":
    main()
