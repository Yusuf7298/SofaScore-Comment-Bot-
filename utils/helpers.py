import logging
import random
import time
import os

os.makedirs("logs", exist_ok=True)

SUCCESS = 25
TRACE = 15
logging.addLevelName(SUCCESS, "SUCCESS")
logging.addLevelName(TRACE, "TRACE")

logger = logging.getLogger("SofascoreBot")
logger.setLevel(logging.DEBUG)

def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kws)

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kws)

logging.Logger.success = success
logging.Logger.trace = trace

c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('logs/bot.log')

c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

c_format = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
f_format = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

if not logger.handlers:
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

def random_delay(min_seconds=1.0, max_seconds=3.0):
    """Pauses execution for a random amount of time to simulate human behavior."""
    delay = random.uniform(min_seconds, max_seconds)
    logger.trace(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)

