import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG, filename="backend.log", filemode="a")
logger = logging.getLogger()

import backend.history

logger.debug("Starting Program")
backend.history.Update_History()
logger.debug("Program finished")

