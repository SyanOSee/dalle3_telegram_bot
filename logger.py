# Standard
import logging
import os

# Project
import config as cf


class Logger:
    """
    Class for logging messages to a file and console.

    Attributes:
    - name: Name of the logger
    - logging_path: Path to the log file
    """

    def __init__(self, name, logging_path: str):
        """
        Initialize the logger with the given name and logging path.

        Args:
        - name: Name of the logger
        - logging_path: Path to the log file
        """
        self.__logging_path = logging_path
        self.log = logging.getLogger(name)  # Unique logger per instance
        self.log.setLevel(logging.INFO)

        # Create file handler which logs messages to the specified file
        file_handler = logging.FileHandler(logging_path)
        file_handler.setLevel(logging.INFO)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                                      datefmt='%Y-%m-%d:%H:%M:%S')
        file_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.log.addHandler(file_handler)

    def clear_log_file(self):
        """
        Clear the content of the log file by opening it in write mode.

        Returns:
        - Empty string if successful
        """
        if self.__logging_path:
            with open(self.__logging_path, "w") as f:
                f.write("")
            return ""

    def info(self, msg: str):
        """
        Log an info message and print it to the console.

        Args:
        - msg: Message to log
        """
        print(msg)  # Show in console
        self.log.info(msg)

    def warning(self, msg: str):
        """
        Log a warning message and print it to the console.

        Args:
        - msg: Message to log
        """
        print(msg)  # Show in console
        self.log.warning(msg)

    def error(self, msg: str):
        """
        Log an error message and print it to the console.

        Args:
        - msg: Message to log
        """
        print(msg)  # Show in console
        self.log.error(msg)


def create_log_folder() -> str:
    """
    Create a log folder if it doesn't exist and return the path

    Returns:
    str: Path of the log folder
    """
    path = cf.BASE / 'logs'
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path


# Create loggers for different components
logging_folder = create_log_folder()

# Logger for the bot
bot_logger = Logger(name='bot', logging_path=os.path.join(logging_folder, 'bot_log.log'))
bot_logger.clear_log_file()

# Logger for the database
database_logger = Logger(name='database', logging_path=os.path.join(logging_folder, 'database_log.log'))
database_logger.clear_log_file()

# Logger for the server
server_logger = Logger(name='server', logging_path=os.path.join(logging_folder, 'server_log.log'))
server_logger.clear_log_file()

# Logger for the gpt
gpt_logger = Logger(name='gpt', logging_path=os.path.join(logging_folder, 'gpt_log.log'))
gpt_logger.clear_log_file()
