import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from rich.console import Console
from datetime import datetime

# Define Log Levels
LOG_LEVEL_CONSOLE = logging.INFO
LOG_LEVEL_FILE = logging.DEBUG  # Capture everything in files (Edge Cases)

# Constants
LOG_DIR = "logs"
LOG_FORMAT_FILE = "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s"
LOG_FORMAT_CONSOLE = "%(message)s"

class JarvisLogger:
    _instance = None
    _hud_queue = None # For mirroring logs to desktop app

    @classmethod
    def setup_logger(cls, name="Jarvis"):
        """
        Setup global logging configuration.
        Returns a logger instance.
        """
        if cls._instance:
            return cls._instance
        
        # 1. Create Log Directory
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        # 2. Base Logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG) # Catch ALL at root level, filter in handlers
        logger.handlers = [] # Clear default handlers
        
        # 3. File Handler (Rotating: 5MB files, keep 5 backups)
        # We start a new log file for each session for clarity, but also rotate if it gets huge.
        timestamp = datetime.now().strftime("%Y-%m-%d")
        file_path = f"{LOG_DIR}/jarvis_{timestamp}.log"
        
        file_handler = RotatingFileHandler(file_path, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
        file_handler.setLevel(LOG_LEVEL_FILE)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT_FILE))
        logger.addHandler(file_handler)
        
        # 4. Console Handler (Rich)
        console_handler = RichHandler(
            console=Console(width=120), 
            rich_tracebacks=True,
            markup=True,
            show_path=False # We show module name instead usually
        )
        console_handler.setLevel(LOG_LEVEL_CONSOLE)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT_CONSOLE))
        logger.addHandler(console_handler)
        
        cls._instance = logger
        logger.info("📝 Logging System Initialized (File Level: DEBUG)")
        
        # Log Python Version & Environment for Debugging context
        logger.debug(f"Python Version: {sys.version}")
        logger.debug(f"Platform: {sys.platform}")
        
        return logger

    @classmethod
    def get_logger(cls):
        if not cls._instance:
            return cls.setup_logger()
        return cls._instance

    @classmethod
    def register_hud_queue(cls, queue):
        """Allows sending critical logs to the Desktop App HUD"""
        cls._hud_queue = queue

    @classmethod
    def log_hud(cls, level, message):
        """Log to internal logger AND send to HUD"""
        logger = cls.get_logger()
        if level.upper() == "INFO":
            logger.info(message)
        elif level.upper() == "ERROR":
            logger.error(message)
        elif level.upper() == "WARNING":
            logger.warning(message)
        else:
            logger.debug(message)

        # Bridge to Desktop App
        if cls._hud_queue:
            try:
                # Format specific to how the Swift App/HUD parses it
                # Usually: ("Category", "Message")
                cls._hud_queue.put(("LOG", message)) 
            except Exception:
                pass

# Helper for modules to import easily
def get_logger():
    return JarvisLogger.get_logger()
