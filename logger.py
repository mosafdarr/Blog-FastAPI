import logging
import sys

logger = logging.getLogger()

formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("app.log", mode='a')

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers = [stream_handler, file_handler]

logging.getLogger('bcrypt').setLevel(logging.ERROR)
logger.setLevel(logging.INFO)
