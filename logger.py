import logging

logging.basicConfig(
    filename="server.log",
    filemode='a',
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO)
logger = logging
