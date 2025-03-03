import os
from datetime import datetime

class Logger:
    # ANSI escape codes
    colors = {
        'red': "\033[91m",
        'green': "\033[92m",
        'yellow': "\033[93m",
        'blue': "\033[94m",
        'magenta': "\033[95m",
        'cyan': "\033[96m",
        'white': "\033[97m",
        'default': "\033[0m"
    }

    @staticmethod
    def __timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def __print(msg: str, color: str = 'default'):
        timestamp = Logger.__timestamp()
        formatted_msg = f"[{timestamp}] {msg}"

        default = Logger.colors['default']
        color = Logger.colors.get(color, default)
        print(f"{color}{formatted_msg}{default}")

    @staticmethod
    def error(msg: str):
        Logger.__print(f"[ERROR] {msg}", 'red')

    @staticmethod
    def info(msg: str, color: str = 'default'):
        if int(os.getenv('LOG_LEVEL')) > 0:
            Logger.__print(f"[INFO] {msg}", color)

    @staticmethod
    def debug(msg: str):
        if int(os.getenv('LOG_LEVEL')) > 1:
            Logger.__print(f"[DEBUG] {msg}")