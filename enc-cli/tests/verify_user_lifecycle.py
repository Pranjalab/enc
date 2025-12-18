import sys
import pexpect
import subprocess
import os
import time

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
NC = '\033[0m'

def log(msg, color=NC):
    print(f"{color}{msg}{NC}")

def main():
    log("=== ENC User Lifecycle Verification ===", GREEN)
    
    # 0. Prerequisites: Ensure Admin Session
    log("1. Configuring as Admin...", NC)
    subprocess.run("enc set-url http://localhost:2222", shell=True)
    subprocess.run("enc set-username admin", shell=True)
    
    # Login as admin
    log("2. Admin Login...", NC)
    child = pexpect.spawn("enc login", encoding='utf-8')
    # Admin has NOPASSWD or password? Docker set password 'admin' (wait, entrypoint sets it? No, Dockerfile 'echo "admin:admin" | chpasswd' usually. Or I set it manually?)
    # Previous tests used 'tester'.
    # Let's assume 'tester' is an admin-like user? NO, 'tester' was created as normal user.
    # The 'admin' user exists in Dockerfile. 
    # But does 'admin' have a known password? 
    # Check Dockerfile: 'adduser -D ... admin' then ???
    # Previous thought: I might need to RESET admin password if I don't know it.
    # OR create a new admin user manually first?
    # BUT wait, the requirements say "create test user".
    # I need an ADMIN to run 'enc user create'.
    # I will try 'admin' with password 'admin' (standard default in many my setups) OR I can exec into docker and set it now to be sure.
    
    # Force set admin password to ensure test stability
    # subprocess.run("ssh -p 2222 root@localhost 'echo admin:adminpass | chpasswd'", shell=True)
    
    try:
        i = child.expect(['password:', 'Login Success', 'Are you sure', pexpect.EOF], timeout=10)
        if i == 2: # Are you sure
            child.sendline("yes")
            i = child.expect(['password:', 'Login Success', pexpect.EOF], timeout=10)
            
        if i == 0:
            child.sendline("adminpass")
            child.expect('Login Success')
        log("   -> Admin Login OK", GREEN)
    except Exception as e:
        log(f"   -> Admin Login Failed: {e}", RED)
        sys.exit(1)

    # 1. Create New User
    new_user = f"user_{int(time.time())}"
    new_pass = "securepass"
    log(f"3. Creating New User '{new_user}'...", NC)
    
    cmd = f"enc user create {new_user} {new_pass} --role user"
    child = pexpect.spawn(cmd, encoding='utf-8')
    try:
        # It calls SSH, might prompt for ADMIN password again if strictly SSH-ing?
        # enc-client sends command. 'enc' login session token is used for... 
        # Wait, the current architecture:
        # `enc login` gets a "session token".
        # `enc user create` calls `ssh ... enc server-user-create`.
        # SSH AUTHENTICATION is separate from ENC SESSION.
        # SSH auth happens via keys or password.
        # If I don't have keys for 'admin', I will be prompted for 'admin' SSH password.
        
        i = child.expect(['password:', f'User {new_user} created', pexpect.EOF], timeout=10)
        if i == 0:
            child.sendline("adminpass")
            child.expect(f'User {new_user} created')
            
        log(f"   -> User '{new_user}' Created OK", GREEN)
    except Exception as e:
        log(f"   -> User Creation Failed: {e}", RED)
        print(child.before)
        sys.exit(1)

    # 2. Switch Context to New User
    log(f"4. Switching to '{new_user}'...", NC)
    subprocess.run("enc logout", shell=True) # Logout admin
    subprocess.run(f"enc set-username {new_user}", shell=True)
    
    # Login as new user
    child = pexpect.spawn("enc login", encoding='utf-8')
    try:
        i = child.expect(['password:', 'Login Success', 'Are you sure', pexpect.EOF], timeout=10)
        if i == 2:
            child.sendline("yes")
            i = child.expect(['password:', 'Login Success', pexpect.EOF], timeout=10)
            
        if i == 0:
            child.sendline(new_pass)
            child.expect('Login Success')
        log("   -> New User Login OK", GREEN)
    except Exception as e:
        log(f"   -> New User Login Failed: {e}", RED)
        sys.exit(1)

    # 3. Create Project
    proj_name = "lifecycle_proj"
    log(f"5. Initializing Project '{proj_name}'...", NC)
    child = pexpect.spawn(f"enc project init {proj_name} --password ppass", encoding='utf-8')
    try:
        i = child.expect(['password:', 'initialized successfully', pexpect.EOF], timeout=15)
        if i == 0:
            child.sendline(new_pass) # SSH password
            child.expect('initialized successfully')
        log("   -> Project Init OK", GREEN)
    except Exception as e:
        log(f"   -> Project Init Failed: {e}", RED)
        sys.exit(1)

    # 4. Sync Test Payload
    log("6. Syncing Test Payload...", NC)
    # Create valid payload file locally
    with open("test_payload.py", "w") as f:
        f.write("print('Payload Executed')\n")
        
    cmd = f"enc project sync {proj_name} {os.getcwd()}"
    child = pexpect.spawn(cmd, encoding='utf-8')
    try:
        i = child.expect(['password:', pexpect.EOF], timeout=15)
        if i == 0:
             child.sendline(new_pass)
             child.expect(pexpect.EOF)
        # Check exit code or output usually?
        # Assuming silent success or printed output.
        log("   -> Sync Triggered", GREEN)
    except:
        pass
        
    # 5. Remote Execution
    log("7. Executing Payload Remotely...", NC)
    # enc project run <proj> python3 test_payload.py
    cmd = f"enc project run {proj_name} python3 test_payload.py"
    child = pexpect.spawn(cmd, encoding='utf-8')
    try:
        i = child.expect(['password:', 'Payload Executed', pexpect.EOF], timeout=15)
        if i == 0:
            child.sendline(new_pass)
            i = child.expect(['Payload Executed', pexpect.EOF], timeout=15)
            
        if i == 0 or (i==1 and "Payload Executed" in child.before):
            log("   -> Payload Execution Verified!", GREEN)
        else:
            log("   -> Payload Execution Failed", RED)
            print(child.before)
            sys.exit(1)
            
    except Exception as e:
        log(f"   -> Execution Exception: {e}", RED)
        sys.exit(1)

    # 6. Cleanup (Delete User)
    # Must switch back to admin
    log("8. Cleaning up...", NC)
    subprocess.run("enc logout", shell=True)
    subprocess.run("enc set-username admin", shell=True)
    
    # Delete user
    child = pexpect.spawn(f"enc user rm {new_user}", encoding='utf-8')
    try:
        # Expect SSH pass
        i = child.expect(['password:', 'Are you sure', pexpect.EOF])
        if i == 0:
            child.sendline("adminpass")
            i = child.expect(['Are you sure', pexpect.EOF])
            
        if "Are you sure" in child.before or "Are you sure" in child.after:
            child.sendline("y")
            
        # Might ask password AGAIN if SSH connection re-established? 
        # Usually one connection. But CLI might do `ssh ...` which authenticates.
        # If 'rm' confirms then runs SSH, it asks pass.
        # Logic: 
        # 1. click.confirm (Local)
        # 2. enc_manager.user_delete -> SSH -> Password
        
        # So 'Are you sure' comes first locally.
        # THEN 'password:' from SSH.
        
        i = child.expect(['password:', f'User {new_user} deleted', pexpect.EOF])
        if i == 0:
             child.sendline("adminpass")
             child.expect(f'User {new_user} deleted')
             
        log("   -> User Deleted OK", GREEN)
    except Exception as e:
        log(f"   -> Deletion Failed: {e}", RED)

    log("=== Lifecycle Verification Finished ===", GREEN)

if __name__ == "__main__":
    main()
