import logging


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def setup_logger(level=logging.INFO,
                 log_file="log.log"):
    print(f"Logging to {log_file}")
    logger = logging.getLogger()
    logger.setLevel(level)
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    logger.addHandler(fh)
    format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format)
    fh.setFormatter(formatter)
    return logger
