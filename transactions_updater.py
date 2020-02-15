import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG, filename="portfolio.log", filemode="a")
logger = logging.getLogger()

import backend.bank_input as BankInput


## CSV Import of account transactions


## Updating the main transaction repository 

logger.debug("Starting Transactions update")
BankInput.UpdateTransactions()


#BankInput.LoadTransactions() in case the portfolio.csv file is corrupted

