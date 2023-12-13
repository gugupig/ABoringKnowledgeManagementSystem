import logging
import os

class ActivityLogger:
    def __init__(self, log_file='app.log'):
        self.log_file = log_file
        logging.basicConfig(
            filename=self.log_file,
            filemode='a',  # Append to the log file
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.DEBUG
        )

    def log_error(self, message):
        logging.error(message)

    def log_warning(self, message):
        logging.warning(message)

    def log_info(self, message):
        logging.info(message)

