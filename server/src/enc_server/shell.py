#!/usr/bin/env python3
import cmd
import os
import sys
import getpass
import subprocess
import shlex

class EncRestrictedShell(cmd.Cmd):
    intro = """
    Welcome to the ENC Secure Environment.
    Type 'help' or '?' to list allowed commands.
    Type 'exit' to disconnect.
    """
    prompt = 'enc> '

    def __init__(self):
        super().__init__()
        self.user = getpass.getuser()

    def do_enc(self, arg):
        """Run ENC commands. Syntax: enc [command] [options]"""
        # Security: Prevent shell injection via subprocess
        # Pass args directly to the installed enc executable
        try:
            command_line = f"enc {arg}"
            # Use shlex to split safely
            args = shlex.split(command_line)
            
            # Execute without shell=True to prevent injections
            subprocess.run(args, check=False)
        except Exception as e:
            print(f"Error executing command: {e}")

    def do_clear(self, arg):
        """Clear the screen."""
        os.system('clear')

    def do_exit(self, arg):
        """Exit the secure shell."""
        print("Goodbye.")
        return True

    def do_EOF(self, arg):
        print()
        return True
        
    # Override default behavior to forbid everything else
    def default(self, line):
        print(f"*** Forbidden command: {line}")
        print("Only 'enc', 'help', 'clear', and 'exit' are allowed.")

    def run(self):
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
            self.run()

if __name__ == '__main__':
    # usage: enc-shell [-c "command"]
    if len(sys.argv) > 1 and sys.argv[1] == '-c':
        if len(sys.argv) > 2:
            cmd_line = sys.argv[2]
            # Restrict to 'enc ' commands only
            if cmd_line.startswith("enc ") or cmd_line == "enc":
                shell = EncRestrictedShell()
                # Run the specific command
                # We strip 'enc ' prefix because do_enc expects the arg
                arg = cmd_line[4:].strip()
                if arg:
                    shell.do_enc(arg)
                else:
                    # Just 'enc' -> run nothing or help?
                    # interactive mode doesn't make sense here.
                    pass
            else:
                 print(f"Restricted shell: Command not allowed: {cmd_line}")
                 sys.exit(1)
        else:
            sys.exit(1)
    else:
        EncRestrictedShell().run()
