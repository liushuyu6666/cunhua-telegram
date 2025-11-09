import datetime


class Logger:
    """
    Logger class for flexible logging with four levels: debug, info, warn, error.
    Only messages at or above the visible_level are printed to the console.
    All messages are written to the log file if provided, regardless of level.

    Usage:
        logger = Logger(visible_level='info')
        logger.print("Message", section_name="main", level="debug", log_file="app.log")
    """

    LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3}
    LEVEL_NAMES = {0: "DEBUG", 1: "INFO", 2: "WARN", 3: "ERROR"}

    def __init__(self, visible_level="debug"):
        self.visible_level = self.LEVELS.get(visible_level, 0)

    def print(self, message, section_name=None, level="info", log_file=None):
        level = level.lower()
        level_num = self.LEVELS.get(level, 1)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        section = section_name if section_name else ""
        log_message = f"{timestamp} [{section} {self.LEVEL_NAMES[level_num]}] {message}"
        # Print to console only if level >= visible_level
        if level_num >= self.visible_level:
            print(log_message)
        # Always write to log file if provided
        if log_file:
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_message + "\n")
            except OSError as e:
                print(f"ERROR [Logger] Failed to write to log file: {e}")
