import sys
from typing import Dict, Any

def exec_in_memory(code_str: str, global_vars: Dict[str, Any] = None):
    """
    Execute python code string in memory.
    This simulates 'python file.py' but without the file on disk.
    
    Args:
        code_str: The decrypted source code.
        global_vars: Optional globals dict.
    """
    if global_vars is None:
        global_vars = {"__name__": "__main__"}
        
    # Compile execution
    # mode='exec' compiles module-level code
    code_obj = compile(code_str, filename="<enc_memory>", mode="exec")
    
    # Execute
    exec(code_obj, global_vars)

def run_project_module(decrypted_code: str, module_name: str = "__main__"):
    """
    Run a specific decrypted module string as main.
    """
    globals_dict = {"__name__": module_name}
    exec_in_memory(decrypted_code, globals_dict)
