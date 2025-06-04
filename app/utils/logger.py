import logging
import socket
from pythonjsonlogger import jsonlogger
from app.config import settings

logger = logging.getLogger("notifyme")
logger.setLevel(logging.INFO)

logstash_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()

logstash_handler.setFormatter(formatter)
logger.addHandler(logstash_handler)
