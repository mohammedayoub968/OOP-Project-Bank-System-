# utils/validators.py

def validate_password_strength(password):
    # Example: at least 8 chars, 1 digit, 1 uppercase, 1 lowercase
    import re
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True
