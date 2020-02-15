import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG, filename="portfolio.log", filemode="a")
logger = logging.getLogger()

import backend.portfolio_view as portfolio
import pandas as pd

# portfolio.LoadPortfolioView() 

logger.info("Updating Portfolio View Table")
portfolio.UpdatePortfolioView()


