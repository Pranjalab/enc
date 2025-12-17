import atexit
import signal
import sys
from enc_server.session.session import current_session

def auto_lock():
    """
    Forcefully clear session state.
    """
    if current_session.is_logged_in:
        print("\n[ENC] Auto-locking session...")
        current_session.logout()

def register_hooks():
    """
    Register signal handlers and exit hooks.
    """
    atexit.register(auto_lock)
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
