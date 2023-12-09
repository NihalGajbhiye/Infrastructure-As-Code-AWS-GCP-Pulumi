import logging, os, sys
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from statsd import StatsClient


db = SQLAlchemy()
bcrpyt = Bcrypt()


def setup_logging(level = logging.INFO):
    """setup logging for app"""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Set up a simple console logger as a fallback
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    # For non-Windows environments, attempt to set up file logging
    if not sys.platform.startswith("win"):
        log_directory = "/var/log/flask"
        info_log_file = "info.log"
        error_log_file = "error.log"
        max_log_size = 10 * 1024 * 1024
        backup_count = 5

        # Attempt to create the log directory
        try:
            os.makedirs(
                log_directory, exist_ok=True
            )  # create the log directory if it doesn't exist
            # Setup handlers for file logging
            info_log_path = os.path.join(log_directory, info_log_file)
            info_handler = RotatingFileHandler(
                info_log_path, maxBytes=max_log_size, backupCount=backup_count
            )
            info_handler.setLevel(logging.INFO)
            info_handler.setFormatter(formatter)
            root_logger.addHandler(info_handler)

            error_log_path = os.path.join(log_directory, error_log_file)
            error_handler = RotatingFileHandler(
                error_log_path, maxBytes=max_log_size, backupCount=backup_count
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            root_logger.addHandler(error_handler)

        except PermissionError as e:
            print(f"Failed to create log directory '{log_directory}'. {e}")
        except OSError as e:
            print(f"Failed to create log directory '{log_directory}'. {e}")

    return root_logger

logger = setup_logging()
if logger:
    logger.info("Logging setup complete.")
else:
    print("Failed to setup file-based logging, falling back to console logging.")

statsd = StatsClient(host="localhost", port=8125, prefix="webapp")



