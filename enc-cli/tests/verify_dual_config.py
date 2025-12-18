import pexpect
import shutil
import os
import sys

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
NC = '\033[0m'

def log(msg, color=NC):
    print(f"{color}{msg}{NC}")

def cleanup():
    log("Cleaning up configs...", NC)
    # Remove Global
    enc_dir = os.path.expanduser("~/.enc")
    if os.path.exists(enc_dir):
        shutil.rmtree(enc_dir)
    # Remove Local
    local_enc = os.path.abspath(".enc")
    if os.path.exists(local_enc):
        shutil.rmtree(local_enc)

def test_global_init():
    log("--- Test 1: Global Init ---", NC)
    child = pexpect.spawn("enc init", encoding='utf-8')
    try:
        # Prompt: "Initialize Global (~/.enc) or Local (./.enc) config?"
        child.expect(r"Initialize Global.*or Local")
        child.sendline("global")
        
        child.expect("Enter ENC Server URL")
        child.sendline("http://localhost:2222")
        
        child.expect("Enter Username")
        child.sendline("global_user")
        
        child.expect("Enter SSH Key Path")
        child.sendline("")
        
        child.expect("Configuration initialized at .*config.json")
        log("   -> Global Init Wizard Completed", GREEN)
        
        # Verify content
        res = pexpect.run("enc show config", encoding='utf-8')
        if "global_user" in res:
             log("   -> Verified 'global_user' in defaults", GREEN)
        else:
             log(f"   -> Failed to verify global config. Output:\n{res}", RED)
             return False
             
        return True
    except Exception as e:
        log(f"   -> Global Init Failed: {e}", RED)
        print(child.before)
        return False

def test_local_init():
    log("--- Test 2: Local Init ---", NC)
    child = pexpect.spawn("enc init", encoding='utf-8')
    try:
        child.expect(r"Initialize Global.*or Local")
        child.sendline("local")
        
        child.expect("Enter ENC Server URL")
        child.sendline("http://localhost:2222")
        
        child.expect("Enter Username")
        child.sendline("local_user")
        
        child.expect("Enter SSH Key Path")
        child.sendline("")
        
        child.expect("Configuration initialized at .*config.json")
        
        # Verify local file exists
        if os.path.exists(".enc/config.json"):
             log("   -> .enc/config.json created", GREEN)
        else:
             log("   -> .enc/config.json missing!", RED)
             return False
             
        # Verify Precedence (Local override)
        res = pexpect.run("enc show config", encoding='utf-8')
        if "local_user" in res:
             log("   -> Verified 'local_user' overrides global", GREEN)
        else:
             log(f"   -> Failed precedence check. Output:\n{res}", RED)
             return False
             
        return True
    except Exception as e:
        log(f"   -> Local Init Failed: {e}", RED)
        print(child.before)
        return False

def main():
    cleanup()
    
    if not test_global_init():
        sys.exit(1)
        
    if not test_local_init():
        sys.exit(1)
        
    log("=== Dual Config Verification PASSED ===", GREEN)
    cleanup()

if __name__ == "__main__":
    main()
