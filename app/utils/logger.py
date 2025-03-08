import os

import logging


# Define log directory and file path
LOG_DIR = "logs"
log_file = os.path.join(LOG_DIR, "app.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler to store logs
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create console handler to show logs in terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Define log format
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s | %(message)s"
)


# Set formatter for handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


