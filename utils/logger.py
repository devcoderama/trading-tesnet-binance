import logging
import os

def setup_logger(name="trading-bot", level="INFO"):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        logger.addHandler(ch)
        os.makedirs("logs", exist_ok=True)
        fh = logging.FileHandler("logs/bot.log")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger
