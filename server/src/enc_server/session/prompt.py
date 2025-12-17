from enc_server.session.session import current_session

def get_prompt_prefix() -> str:
    """
    Return the prompt prefix based on session state.
    Examples:
    [enc]
    [project_name]
    """
    if not current_session.is_logged_in:
        return ""
        
    if current_session.active_project:
        return f"[{current_session.active_project}] "
        
    return "[enc] "
