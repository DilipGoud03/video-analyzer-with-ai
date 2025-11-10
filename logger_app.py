import logging

# ------------------------------------------------------------
# Method: setup_logger
# Description:
#   Configures and returns a logger that outputs debug-level
#   logs to the console with timestamps, logger names, and
#   log levels included in the format.
#   Logs every action for audit and debugging purposes.
# ------------------------------------------------------------


def setup_logger(file: str = __name__):
    logger = logging.getLogger(file)
    logger.setLevel(logging.DEBUG)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Add formatter to ch
    ch.setFormatter(formatter)
    # Add ch to logger
    logger.addHandler(ch)
    return logger
