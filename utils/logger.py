import logging
import sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Console Formatter with custom level colors."""
    
    FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
    DATE_FORMAT = "%H:%M:%S"

    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)
        formatter = logging.Formatter(f"{color}{self.FORMAT}{Style.RESET_ALL}", datefmt=self.DATE_FORMAT)
        return formatter.format(record)

def get_logger(name: str = "LeadScraper") -> logging.Logger:
    """Returns a logger instance formatted for console output."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)

    return logger

logger = get_logger()
