import backend.history
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG, filename="backend.log", filemode="a")

logger = logging.getLogger()
logger.debug("Starting Program")
backend.history.Update_History()
logger.debug("Program finished")

