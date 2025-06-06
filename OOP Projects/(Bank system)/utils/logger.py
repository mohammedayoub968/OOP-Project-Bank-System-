# utils/logger.py
import datetime

def log_action(user_id, action, status):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("logs.txt", "a") as log_file:
        log_file.write(f"[{timestamp}] User ID: {user_id} | Action: {action} | Status: {status}\n")
