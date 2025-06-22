import os
from datetime import datetime
def init_log_file(folder_path):
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(folder_path, f"{today}.txt")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            pass
    return log_path

def read_logged_errors(log_path):
    if not os.path.exists(log_path):
        return set()
    with open(log_path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def append_log(log_path, stock_no, stock_name, error_message=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Stock: {stock_no}_{stock_name} - Error: {error_message}\n")
