from __future__ import annotations

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
    def timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def __print(msg: str, color: str = 'default'):
        timestamp = Logger.timestamp()
        formatted_msg = f"[{timestamp}] {msg}"

        default = Logger.colors['default']
        color = Logger.colors.get(color, default)
        print(f"{color}{formatted_msg}{default}")
        return Logger

    @staticmethod
    def error(msg: str):
        Logger.__print(f"[ERROR] {msg}", 'red')
        return Logger

    @staticmethod
    def info(msg: str, color: str = 'default'):
        if int(os.getenv('LOG_LEVEL')) > 0:
            Logger.__print(f"[INFO] {msg}", color)
        return Logger

    @staticmethod
    def debug(msg: str):
        if int(os.getenv('LOG_LEVEL')) > 1:
            Logger.__print(f"[DEBUG] {msg}")
        return Logger

    @staticmethod
    def message(msg: str, color: str = 'default'):
        default = Logger.colors['default']
        color = Logger.colors.get(color, default)
        print(f"{color}{msg}{default}")
        return Logger

    @staticmethod
    def input(prompt: str, default=None, default_alias=None, cast: type = str, color: str = 'default'):
        if default is not None:
            if default_alias is not None:
                prompt += f" (default: {default_alias})"
            else:
                prompt += f" (default: {default})"
        prompt += ": "

        default_color = Logger.colors['default']
        color_value = Logger.colors.get(color, default_color)
        user_input = input(f"{color_value}{prompt}{default_color}")

        if user_input == '':
            user_input = default
        return cast(user_input)

    @staticmethod
    def br():
        print()
        return Logger
