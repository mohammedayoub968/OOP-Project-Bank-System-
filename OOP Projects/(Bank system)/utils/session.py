# utils/session.py

class SessionManager:
    def __init__(self, root, logout_callback):
        self.root = root
        self.logout_callback = logout_callback
        self.active = False

    def start(self):
        self.active = True
        # Placeholder: Add session timeout logic if needed

    def stop(self):
        self.active = False
        # Placeholder: Add cleanup logic if needed
