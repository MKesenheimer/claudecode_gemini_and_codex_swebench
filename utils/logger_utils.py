"""
Shared logging module for the SWE-bench benchmark project.
Provides a logging mechanism with different verbosity levels and command-line argument support.
"""

import logging
import sys
import argparse
from pathlib import Path
from typing import Optional


# Verbosity levels mapping
VERBOSE_LEVELS = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}

# Verbosity display names
VERBOSE_NAMES = {
    logging.ERROR: 'error',
    logging.WARNING: 'warning',
    logging.INFO: 'info',
    logging.DEBUG: 'debug',
}


class VerboseFormatter(logging.Formatter):
    """Custom formatter that adds color to log messages based on level."""

    # ANSI color codes
    COLORS = {
        logging.DEBUG: '\033[36m',       # Cyan
        logging.INFO: '\033[32m',        # Green
        logging.WARNING: '\033[33m',     # Yellow
        logging.ERROR: '\033[31m',       # Red
    }

    RESET = '\033[0m'

    def format(self, record):
        # Get color for this level
        color = self.COLORS.get(record.levelno, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class Logger:
    """Singleton logger with verbosity control."""

    _instance = None
    _logger = None
    _verbose_level = logging.INFO
    _log_file: Optional[Path] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger (idempotent)."""
        if self._logger is not None:
            return

        # Set up logging
        self._setup_logging()

    def _setup_logging(self):
        """Configure the logging system."""
        self._logger = logging.getLogger('swe_bench')
        self._logger.handlers = []  # Clear existing handlers
        self._logger.setLevel(logging.DEBUG)  # Always capture all levels

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self._verbose_level)
        console_handler.setFormatter(VerboseFormatter('%(levelname)s - %(message)s'))
        self._logger.addHandler(console_handler)

        # File handler for detailed logs
        if self._log_file and self._log_file.exists():
            file_handler = logging.FileHandler(self._log_file, mode='a')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(VerboseFormatter('%(asctime)s - %(levelname)s - %(message)s'))
            self._logger.addHandler(file_handler)

    def set_verbose_level(self, level_str: str):
        """Set the verbosity level from a string."""
        level_str = level_str.lower()
        if level_str in VERBOSE_LEVELS:
            self._verbose_level = VERBOSE_LEVELS[level_str]
            self._logger.setLevel(self._verbose_level)
            # Update existing handlers
            for handler in self._logger.handlers:
                handler.setLevel(self._verbose_level)
        else:
            raise ValueError(f"Invalid verbosity level: {level_str}. Choose from: {list(VERBOSE_LEVELS.keys())}")

    def set_log_file(self, log_file: Path):
        """Set the log file for detailed logging."""
        self._log_file = log_file
        if log_file.exists() and self._log_file:
            # Reconfigure file handler with new file
            for handler in self._logger.handlers:
                if isinstance(handler, logging.FileHandler) and handler.baseFilename == str(log_file):
                    handler.close()
                    break
            if self._log_file and self._log_file.exists():
                file_handler = logging.FileHandler(self._log_file, mode='a')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(VerboseFormatter('%(asctime)s - %(levelname)s - %(message)s'))
                self._logger.addHandler(file_handler)

    def _log(self, level: int, message: str):
        """Internal logging method."""
        if level <= self._verbose_level:
            self._logger.log(level, message)

    def debug(self, message: str):
        """Log a debug message."""
        self._log(logging.DEBUG, message)

    def info(self, message: str):
        """Log an info message."""
        self._log(logging.INFO, message)

    def warning(self, message: str):
        """Log a warning message."""
        self._log(logging.WARNING, message)

    def error(self, message: str):
        """Log an error message."""
        self._log(logging.ERROR, message)

    def is_debug(self) -> bool:
        """Check if debug level is enabled."""
        return self._verbose_level >= logging.DEBUG

    def is_info(self) -> bool:
        """Check if info level is enabled."""
        return self._verbose_level >= logging.INFO

    def is_warning(self) -> bool:
        """Check if warning level is enabled."""
        return self._verbose_level >= logging.WARNING

    def is_error(self) -> bool:
        """Check if error level is enabled."""
        return self._verbose_level >= logging.ERROR


# Global logger instance
logger = Logger()


def setup_argument_parser(parser: argparse.ArgumentParser, add_verbose: bool = True):
    """Add verbose argument to the argument parser."""
    if add_verbose:
        parser.add_argument(
            '--verbose', '-v',
            type=str,
            default='info',
            choices=list(VERBOSE_LEVELS.keys()),
            help='Set verbosity level (error, warning, info, debug). Default: info'
        )
    return parser


def configure_logging_from_args(verbose_level: str = 'info', log_file: Optional[Path] = None):
    """Configure logging based on verbosity level and log file."""
    if verbose_level is None:
        return
    logger.set_verbose_level(verbose_level)
    if log_file:
        logger.set_log_file(log_file)


def get_current_verbose_level() -> str:
    """Get the current verbosity level as a string."""
    return VERBOSE_NAMES.get(logger._verbose_level, 'info')


def main():
    """Demo of the logging system."""
    parser = argparse.ArgumentParser(description='Logging System Demo')
    setup_argument_parser(parser)
    args = parser.parse_args()

    configure_logging_from_args(args.verbose)

    logger.info("\nLogging system initialized with verbosity: {get_current_verbose_level()}")
    logger.info("=" * 50)

    # Demo different log levels
    logger.info("This is an info message - shown at info level and above")
    logger.warning("This is a warning message - shown at warning level and above")
    logger.error("This is an error message - shown at error level and above")

    if args.verbose == 'debug':
        logger.debug("This is a debug message (only shown with --verbose debug)")
    else:
        logger.debug("This is a debug message (hidden with current verbosity)")

    logger.info("\n" + "=" * 50)


if __name__ == "__main__":
    main()
